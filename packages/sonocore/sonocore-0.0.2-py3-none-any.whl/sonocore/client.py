
import asyncio
from typing import Dict, Optional

import aiohttp

from .node import Node
from .player import Player


class Client:
    def __init__(self, bot_id: int, shard_count: int = 1):
        self.bot_id = bot_id
        self.shard_count = shard_count
        self.nodes: Dict[str, Node] = {}
        self.players: Dict[int, Player] = {}
        self.session = aiohttp.ClientSession()

    async def add_node(
        self,
        host: str,
        port: int,
        password: str,
        region: str = "us_central",
        identifier: Optional[str] = None,
    ):
        node = Node(
            self,
            host,
            port,
            password,
            region,
            identifier or f"{host}:{port}",
        )
        await node.connect()
        self.nodes[node.identifier] = node

    @property
    def best_node(self) -> Optional[Node]:
        if not self.nodes:
            return None
        return sorted(self.nodes.values(), key=lambda n: n.stats.penalty if n.stats else 999999)[0]

    def get_player(self, guild_id: int) -> Player:
        if guild_id in self.players:
            return self.players[guild_id]

        player = Player(self, guild_id)
        self.players[guild_id] = player
        return player

    async def on_socket_response(self, data):
        if data["t"] == "VOICE_STATE_UPDATE":
            guild_id = int(data["d"]["guild_id"])
            if player := self.players.get(guild_id):
                await player.on_voice_state_update(data["d"])
        elif data["t"] == "VOICE_SERVER_UPDATE":
            guild_id = int(data["d"]["guild_id"])
            if player := self.players.get(guild_id):
                await player.on_voice_server_update(data["d"])

    async def dispatch(self, event_name: str, *args, **kwargs):
        if hasattr(self, f"on_{event_name}"):
            await getattr(self, f"on_{event_name}")(*args, **kwargs)

    async def close(self):
        await self.session.close()

