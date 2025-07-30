
import asyncio
import json
import logging
import threading
from typing import Any, Dict, Optional

import aiohttp

log = logging.getLogger(__name__)


class WebSocket:
    def __init__(self, client, bot_token: str):
        self.client = client
        self.bot_token = bot_token
        self.ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._last_sequence: Optional[int] = None

    async def connect(self):
        self.ws = await self.client.session.ws_connect(
            "wss://gateway.discord.gg/?v=10&encoding=json"
        )
        hello = await self.ws.receive_json()
        self._heartbeat_interval = hello["d"]["heartbeat_interval"] / 1000
        self._heartbeat_task = asyncio.create_task(self._heartbeat())

        await self.identify()

        async for msg in self.ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                await self.on_message(msg.json())
            elif msg.type in (
                aiohttp.WSMsgType.CLOSED,
                aiohttp.WSMsgType.CLOSE,
                aiohttp.WSMsgType.CLOSING,
            ):
                break

    async def on_message(self, data: Dict[str, Any]):
        op = data["op"]
        self._last_sequence = data.get("s")

        if op == 10:  # Hello
            return
        if op == 11:  # Heartbeat ACK
            return

        if data["t"] in ("VOICE_STATE_UPDATE", "VOICE_SERVER_UPDATE"):
            await self.client.on_socket_response(data)

    async def identify(self):
        payload = {
            "op": 2,
            "d": {
                "token": self.bot_token,
                "intents": 0,
                "properties": {
                    "$os": "linux",
                    "$browser": "sonocore",
                    "$device": "sonocore",
                },
            },
        }
        await self.ws.send_json(payload)

    async def _heartbeat(self):
        while not self.ws.closed:
            await self.ws.send_json({"op": 1, "d": self._last_sequence})
            await asyncio.sleep(self._heartbeat_interval)

    async def send(self, data: Dict[str, Any]):
        if self.ws and not self.ws.closed:
            await self.ws.send_json(data)
