
from __future__ import annotations

from typing import List, Optional, TypedDict


class Stats(TypedDict):
    op: str
    players: int
    playingPlayers: int
    uptime: int
    memory: MemoryStats
    cpu: CpuStats
    frameStats: Optional[FrameStats]


class MemoryStats(TypedDict):
    free: int
    used: int
    allocated: int
    reservable: int


class CpuStats(TypedDict):
    cores: int
    systemLoad: float
    lavalinkLoad: float


class FrameStats(TypedDict):
    sent: int
    nulled: int
    deficit: int


class PlayerUpdate(TypedDict):
    time: int
    position: int
    connected: bool


class Track(TypedDict):
    encoded: str
    info: TrackInfo


class TrackInfo(TypedDict):
    identifier: str
    isSeekable: bool
    author: str
    length: int
    isStream: bool
    position: int
    title: str
    uri: str
    sourceName: str

