from __future__ import annotations

import asyncio
import random
from typing import TYPE_CHECKING, Any, Deque, Dict, List, Optional

from .errors import PlayerNotConnected, QueueEmpty
from .models import PlayerUpdate, Track

if TYPE_CHECKING:
    from collections import deque

    from .client import Client
    from .node import Node


class Player:
    """
    Represents the audio player for a single Discord guild.

    This class handles everything related to audio playback, including managing the track queue,
    connecting to voice channels, and sending audio-related commands to the Lavalink node.
    """

    def __init__(self, client: Client, guild_id: int):
        self.client = client
        self.guild_id = guild_id
        self.node: Optional[Node] = None
        self.channel_id: Optional[int] = None

        self.current: Optional[Track] = None
        self.queue: Deque[Track] = deque()
        self.history: Deque[Track] = deque(maxlen=25)

        self.paused: bool = False
        self.volume: int = 100
        self.position: int = 0
        self.connected: bool = False

        # Loop modes
        self.loop_track: bool = False
        self.loop_queue: bool = False
        self.autoplay: bool = False

        self._voice_state: Dict[str, Any] = {}
        self._voice_server: Dict[str, Any] = {}

    @property
    def is_playing(self) -> bool:
        """Whether the player is currently playing a track."""
        return self.connected and self.current is not None

    @property
    def is_connected(self) -> bool:
        """Whether the player is connected to a voice channel."""
        return self.channel_id is not None

    async def on_voice_state_update(self, data: Dict[str, Any]):
        """Handles voice state updates from Discord."""
        self._voice_state.update(data)
        if data["user_id"] == str(self.client.bot_id):
            self.channel_id = int(data["channel_id"]) if data["channel_id"] else None
            if "session_id" in data:
                self._voice_state["session_id"] = data["session_id"]
                await self._dispatch_voice_update()

    async def on_voice_server_update(self, data: Dict[str, Any]):
        """Handles voice server updates from Discord."""
        self._voice_server.update(data)
        await self._dispatch_voice_update()

    async def _dispatch_voice_update(self):
        """Dispatches the voice update to the Lavalink node."""
        if "session_id" in self._voice_state and "token" in self._voice_server:
            if self.node and self.node.is_connected:
                await self.node.send(
                    {
                        "op": "voiceUpdate",
                        "guildId": str(self.guild_id),
                        "sessionId": self._voice_state["session_id"],
                        "event": self._voice_server,
                    }
                )

    def update_state(self, state: PlayerUpdate):
        """Updates the player's state from a Lavalink player update."""
        self.position = state["position"]
        self.connected = state["connected"]

    async def connect(self, channel_id: int):
        """Connects the player to a voice channel."""
        self.node = self.client.best_node
        if not self.node:
            raise RuntimeError("No available Lavalink nodes.")

        self.channel_id = channel_id

    async def disconnect(self):
        """Disconnects the player from the voice channel."""
        if not self.is_connected:
            return

        if self.node and self.node.is_connected:
            await self.node.destroy_player(self.guild_id)

        self.channel_id = None
        self.current = None
        self.queue.clear()

    async def play(
        self,
        track: Optional[Track] = None,
        start_time: int = 0,
        end_time: int = 0,
        no_replace: bool = False,
    ):
        """
        Plays a track. If no track is provided, plays the next track in the queue.
        """
        if not self.node:
            raise PlayerNotConnected("Player is not connected to a node.")

        if track:
            self.current = track
        elif not self.current:
            if not self.queue:
                if self.autoplay and self.history:
                    await self._play_autoplay()
                else:
                    await self.stop(dispatch_event=True)
                return
            else:
                self.current = self.queue.popleft()

        if self.current and self.current not in self.history:
            self.history.append(self.current)

        payload = {
            "op": "play",
            "guildId": str(self.guild_id),
            "track": {"encoded": self.current["encoded"]},
            "startTime": str(start_time),
            "noReplace": no_replace,
        }
        if end_time > 0:
            payload["endTime"] = str(end_time)

        await self.node.send(payload)

    async def _play_autoplay(self):
        last_track = self.history[-1]
        query = f"ytsearch:{last_track['info']['author']} - {last_track['info']['title']}"
        try:
            tracks = await self.node.get_tracks(query)
            if tracks:
                self.current = tracks[0]
                await self.play()
            else:
                await self.stop(dispatch_event=True)
        except Exception:
            await self.stop(dispatch_event=True)

    async def stop(self, dispatch_event: bool = False):
        """Stops the current track and clears the queue."""
        if not self.node:
            raise PlayerNotConnected("Player is not connected to a node.")

        await self.node.send({"op": "stop", "guildId": str(self.guild_id)})
        self.current = None

        if dispatch_event:
            await self.client.dispatch("queue_end", self)

    async def set_paused(self, paused: bool):
        """Pauses or resumes the player."""
        if not self.node:
            raise PlayerNotConnected("Player is not connected to a node.")

        await self.node.update_player(self.guild_id, paused=paused)
        self.paused = paused

    async def set_volume(self, volume: int):
        """Sets the player's volume (0-1000)."""
        if not self.node:
            raise PlayerNotConnected("Player is not connected to a node.")

        self.volume = max(0, min(1000, volume))
        await self.node.update_player(self.guild_id, volume=self.volume)

    async def seek(self, position: int):
        """Seeks to a specific position in the current track (in milliseconds)."""
        if not self.node:
            raise PlayerNotConnected("Player is not connected to a node.")

        await self.node.update_player(self.guild_id, position=position)

    def add(self, track: Track):
        """Adds a track to the queue."""
        self.queue.append(track)

    def clear(self):
        """Clears the queue."""
        self.queue.clear()

    def shuffle(self):
        """Shuffles the queue."""
        if not self.queue:
            raise QueueEmpty("The queue is empty.")
        random.shuffle(self.queue)

    async def skip(self, count: int = 1):
        """Skips the current track or multiple tracks."""
        if not self.is_playing:
            raise PlayerNotConnected("Not playing anything.")

        if count > 1:
            if len(self.queue) < count - 1:
                raise ValueError("Cannot skip more tracks than are in the queue.")
            for _ in range(count - 1):
                self.queue.popleft()

        if self.loop_track and self.current:
            pass  # Don't skip if looping a single track
        elif self.loop_queue and self.current:
            self.add(self.current)

        if self.queue or (self.autoplay and self.history):
            await self.play()
        else:
            await self.stop(dispatch_event=True)
