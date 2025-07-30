
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from .player import Player
    from .models import Track


class LavalinkEvent:
    def __init__(self, player: Player):
        self.player = player


class TrackStartEvent(LavalinkEvent):
    def __init__(self, player: Player, track: Track):
        super().__init__(player)
        self.track = track


class TrackEndEvent(LavalinkEvent):
    def __init__(self, player: Player, track: Track, reason: str):
        super().__init__(player)
        self.track = track
        self.reason = reason


class TrackExceptionEvent(LavalinkEvent):
    def __init__(self, player: Player, track: Track, exception: Dict[str, Any]):
        super().__init__(player)
        self.track = track
        self.exception = exception


class TrackStuckEvent(LavalinkEvent):
    def __init__(self, player: Player, track: Track, threshold_ms: int):
        super().__init__(player)
        self.track = track
        self.threshold_ms = threshold_ms


class WebSocketClosedEvent(LavalinkEvent):
    def __init__(self, player: Player, code: int, reason: str, by_remote: bool):
        super().__init__(player)
        self.code = code
        self.reason = reason
        self.by_remote = by_remote
