from __future__ import annotations

import asyncio
import logging
import random
from typing import TYPE_CHECKING, Any, Coroutine, Dict, List, Optional

import aiohttp

from .errors import (
    AuthorizationFailed,
    LavalinkException,
    NodeOccupied,
    NoResultsFound,
)
from .events import (
    TrackEndEvent,
    TrackExceptionEvent,
    TrackStartEvent,
    TrackStuckEvent,
    WebSocketClosedEvent,
)
from .models import PlayerUpdate, Stats, Track
from .player import Player

if TYPE_CHECKING:
    from .client import Client

log = logging.getLogger(__name__)


class Node:
    """
    Represents a connection to a Lavalink node.

    This class handles the WebSocket connection to the Lavalink node, sends commands,
    and processes events.
    """

    def __init__(
        self,
        client: Client,
        host: str,
        port: int,
        password: str,
        region: str,
        identifier: str,
    ):
        self.client = client
        self.host = host
        self.port = port
        self.password = password
        self.region = region
        self.identifier = identifier

        self.session_id: Optional[str] = None
        self.ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self.stats: Optional[Stats] = None
        self._connection_attempts = 0

    @property
    def is_connected(self) -> bool:
        """Whether the node is currently connected to Lavalink."""
        return self.ws is not None and not self.ws.closed

    @property
    def penalty(self) -> int:
        """Calculates a penalty score for the node based on its stats."""
        if not self.is_connected or not self.stats:
            return 9999

        return self.stats["playingPlayers"] + (
            self.stats["cpu"]["systemLoad"] // self.stats["cpu"]["cores"]
        ) * 100

    async def connect(self):
        """Establishes a connection to the Lavalink node."""
        headers = {
            "Authorization": self.password,
            "User-Id": str(self.client.bot_id),
            "Client-Name": "sonocore",
        }
        if self.session_id:
            headers["Session-Id"] = self.session_id

        try:
            self.ws = await self.client.session.ws_connect(
                f"ws://{self.host}:{self.port}/v4/websocket", headers=headers
            )
            self._connection_attempts = 0
        except aiohttp.ClientConnectorError as e:
            log.error(f"Failed to connect to node {self.identifier}: {e}")
            await self.reconnect()

        asyncio.create_task(self._listener())

    async def reconnect(self):
        """Attempts to reconnect to the node with exponential backoff and jitter."""
        if self.is_connected:
            return

        self._connection_attempts += 1

        base_backoff = 5  # Start with 5 seconds
        max_backoff = 60  # Max 1 minute

        # Exponential backoff
        backoff = min(
            base_backoff * (2 ** (self._connection_attempts - 1)), max_backoff
        )

        # Jitter: add random value up to 1 second
        sleep_time = backoff + random.uniform(0, 1)

        log.info(f"Reconnecting to node {self.identifier} in {sleep_time:.2f} seconds...")
        await asyncio.sleep(sleep_time)
        await self.connect()

    async def _listener(self):
        """Listens for messages from the Lavalink node."""
        while self.is_connected:
            try:
                msg = await self.ws.receive()
                if msg.type == aiohttp.WSMsgType.TEXT:
                    await self.on_message(msg.json())
                elif msg.type in (
                    aiohttp.WSMsgType.CLOSED,
                    aiohttp.WSMsgType.CLOSE,
                    aiohttp.WSMsgType.CLOSING,
                ):
                    log.warning(f"WebSocket to node {self.identifier} closed.")
                    await self.reconnect()
                    break
            except asyncio.CancelledError:
                break
            except Exception as e:
                log.error(
                    f"Error in WebSocket listener for node {self.identifier}: {e}"
                )
                await self.reconnect()
                break

    async def on_message(self, data: Dict[str, Any]):
        """Handles incoming messages from the Lavalink node."""
        op = data.get("op")
        log.debug(f"Received message from Lavalink: {data}")

        if op == "ready":
            self.session_id = data["sessionId"]
            log.info(
                f"Node {self.identifier} is ready with session ID {self.session_id}"
            )
            await self.configure_resuming()
        elif op == "stats":
            self.stats = Stats(**data)
        elif op == "event":
            await self.handle_event(data)
        elif op == "playerUpdate":
            guild_id = int(data["guildId"])
            if player := self.client.players.get(guild_id):
                player.update_state(PlayerUpdate(**data["state"]))

    async def handle_event(self, data: Dict[str, Any]):
        """Handles incoming events from the Lavalink node."""
        event_type = data["type"]
        guild_id = int(data["guildId"])
        player = self.client.players.get(guild_id)
        if not player:
            log.warning(f"Received event for a guild with no player: {guild_id}")
            return

        log.info(f"Handling event {event_type} for guild {guild_id}")

        if event_type == "TrackStartEvent":
            event = TrackStartEvent(player, player.current)
            await self.dispatch("track_start", event)
        elif event_type == "TrackEndEvent":
            ended_track = player.current
            player.current = None  # Set current to None as track has ended.

            event = TrackEndEvent(player, ended_track, data["reason"])
            await self.dispatch("track_end", event)

            if player.loop_track and ended_track:
                player.current = ended_track  # Restore for looping
                return await player.play()

            if player.loop_queue and ended_track:
                player.add(ended_track)

            await player.play()

        elif event_type == "TrackExceptionEvent":
            event = TrackExceptionEvent(player, player.current, data["exception"])
            log.error(
                f"Track exception event for guild {guild_id}: {data['exception']}"
            )
            await self.dispatch("track_exception", event)
        elif event_type == "TrackStuckEvent":
            event = TrackStuckEvent(player, player.current, data["thresholdMs"])
            log.warning(f"Track stuck event for guild {guild_id}")
            await self.dispatch("track_stuck", event)
        elif event_type == "WebSocketClosedEvent":
            event = WebSocketClosedEvent(
                player, data["code"], data["reason"], data["byRemote"]
            )
            log.warning(f"WebSocket closed for guild {guild_id}: {data['reason']}")
            await self.dispatch("websocket_closed", event)

    async def dispatch(self, event_name: str, *args: Any, **kwargs: Any):
        """Dispatches an event to the client."""
        if hasattr(self.client, f"on_{event_name}"):
            await getattr(self.client, f"on_{event_name}")(*args, **kwargs)

    async def send(self, payload: Dict[str, Any]):
        """Sends a payload to the Lavalink node."""
        if self.is_connected:
            log.debug(f"Sending payload to Lavalink: {payload}")
            await self.ws.send_json(payload)

    async def configure_resuming(self, timeout: int = 60):
        """Configures session resuming for the node."""
        payload = {
            "op": "configureResuming",
            "key": str(self.session_id),
            "timeout": timeout,
        }
        await self.send(payload)

    async def get_tracks(self, query: str) -> List[Track]:
        """Loads tracks from the Lavalink node."""
        headers = {"Authorization": self.password}
        params = {"identifier": query}
        async with self.client.session.get(
            f"http://{self.host}:{self.port}/v4/loadtracks",
            headers=headers,
            params=params,
        ) as resp:
            if resp.status == 401:
                raise AuthorizationFailed("Incorrect Lavalink password.")
            if resp.status != 200:
                raise LavalinkException(f"Failed to get tracks. Status: {resp.status}")

            data = await resp.json()

            if data["loadType"] == "NO_MATCHES":
                raise NoResultsFound("No tracks found for your query.")
            if data["loadType"] == "LOAD_FAILED":
                raise LavalinkException(
                    f"Failed to load tracks: {data['data']['message']}"
                )

            if data["loadType"] == "TRACK_LOADED":
                return [data["data"]]
            if data["loadType"] == "PLAYLIST_LOADED":
                return data["data"]["tracks"]
            if data["loadType"] == "SEARCH_RESULT":
                return data["data"]

        return []

    async def get_player(self, guild_id: int) -> Optional[Player]:
        """Gets a player from the Lavalink node."""
        async with self.client.session.get(
            f"http://{self.host}:{self.port}/v4/sessions/{self.session_id}/players/{guild_id}",
            headers={"Authorization": self.password},
        ) as resp:
            if resp.status == 404:
                return None
            if resp.status != 200:
                raise LavalinkException(f"Failed to get player. Status: {resp.status}")

            data = await resp.json()
            player = self.client.get_player(guild_id)
            player.position = data["state"]["position"]
            player.connected = data["state"]["connected"]
            player.current = data.get("track")
            player.volume = data["volume"]
            player.paused = data["paused"]
            return player

    async def update_player(self, guild_id: int, **kwargs) -> Optional[Player]:
        """Updates a player on the Lavalink node."""
        async with self.client.session.patch(
            f"http://{self.host}:{self.port}/v4/sessions/{self.session_id}/players/{guild_id}",
            headers={"Authorization": self.password},
            json=kwargs,
        ) as resp:
            if resp.status == 404:
                return None
            if resp.status != 200:
                raise LavalinkException(f"Failed to update player. Status: {resp.status}")

            data = await resp.json()
            player = self.client.get_player(guild_id)
            player.position = data["state"]["position"]
            player.connected = data["state"]["connected"]
            player.current = data.get("track")
            player.volume = data["volume"]
            player.paused = data["paused"]
            return player

    async def destroy_player(self, guild_id: int):
        """Destroys a player on the Lavalink node."""
        async with self.client.session.delete(
            f"http://{self.host}:{self.port}/v4/sessions/{self.session_id}/players/{guild_id}",
            headers={"Authorization": self.password},
        ) as resp:
            if resp.status != 204:
                raise LavalinkException(f"Failed to destroy player. Status: {resp.status}")
