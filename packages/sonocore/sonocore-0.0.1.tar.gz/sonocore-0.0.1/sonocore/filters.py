
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple


class Filters:
    def __init__(self, player) -> None:
        self._player = player
        self._payload: Dict[str, Any] = {}

    def __repr__(self) -> str:
        return f"<sonocore.Filters payload={self._payload}>"

    @property
    def payload(self) -> Dict[str, Any]:
        return self._payload

    def clear(self) -> None:
        """Resets the filters to their default state."""
        self._payload = {}

    def set_equalizer(self, bands: List[Tuple[int, float]]) -> None:
        """Sets the equalizer bands.

        Parameters
        ----------
        bands: List[Tuple[int, float]]
            A list of tuples, where each tuple contains the band number and the gain.
        """
        self._payload["equalizer"] = [{"band": b, "gain": g} for b, g in bands]

    def set_karaoke(self, level: float = 1.0, mono_level: float = 1.0, filter_band: float = 220.0, filter_width: float = 100.0) -> None:
        """Sets the karaoke filter.

        Parameters
        ----------
        level: float
            The karaoke effect level.
        mono_level: float
            The mono level.
        filter_band: float
            The filter band.
        filter_width: float
            The filter width.
        """
        self._payload["karaoke"] = {
            "level": level,
            "monoLevel": mono_level,
            "filterBand": filter_band,
            "filterWidth": filter_width,
        }

    def set_timescale(self, speed: float = 1.0, pitch: float = 1.0, rate: float = 1.0) -> None:
        """Sets the timescale filter.

        Parameters
        ----------
        speed: float
            The playback speed.
        pitch: float
            The pitch.
        rate: float
            The playback rate.
        """
        self._payload["timescale"] = {"speed": speed, "pitch": pitch, "rate": rate}

    def set_tremolo(self, frequency: float = 2.0, depth: float = 0.5) -> None:
        """Sets the tremolo filter.

        Parameters
        ----------
        frequency: float
            The tremolo frequency.
        depth: float
            The tremolo depth.
        """
        self._payload["tremolo"] = {"frequency": frequency, "depth": depth}

    def set_vibrato(self, frequency: float = 2.0, depth: float = 0.5) -> None:
        """Sets the vibrato filter.

        Parameters
        ----------
        frequency: float
            The vibrato frequency.
        depth: float
            The vibrato depth.
        """
        self._payload["vibrato"] = {"frequency": frequency, "depth": depth}

    def set_rotation(self, rotation_hz: float = 0.0) -> None:
        """Sets the rotation filter.

        Parameters
        ----------
        rotation_hz: float
            The rotation frequency in Hz.
        """
        self._payload["rotation"] = {"rotationHz": rotation_hz}

    def set_distortion(self, sin_offset: float = 0.0, sin_scale: float = 1.0, cos_offset: float = 0.0, cos_scale: float = 1.0, tan_offset: float = 0.0, tan_scale: float = 1.0, offset: float = 0.0, scale: float = 1.0) -> None:
        """Sets the distortion filter.

        Parameters
        ----------
        sin_offset: float
            The sin offset.
        sin_scale: float
            The sin scale.
        cos_offset: float
            The cos offset.
        cos_scale: float
            The cos scale.
        tan_offset: float
            The tan offset.
        tan_scale: float
            The tan scale.
        offset: float
            The offset.
        scale: float
            The scale.
        """
        self._payload["distortion"] = {
            "sinOffset": sin_offset,
            "sinScale": sin_scale,
            "cosOffset": cos_offset,
            "cosScale": cos_scale,
            "tanOffset": tan_offset,
            "tanScale": tan_scale,
            "offset": offset,
            "scale": scale,
        }

    def set_channel_mix(self, left_to_left: float = 1.0, left_to_right: float = 0.0, right_to_left: float = 0.0, right_to_right: float = 1.0) -> None:
        """Sets the channel mix filter.

        Parameters
        ----------
        left_to_left: float
            The left to left mix.
        left_to_right: float
            The left to right mix.
        right_to_left: float
            The right to left mix.
        right_to_right: float
            The right to right mix.
        """
        self._payload["channelMix"] = {
            "leftToLeft": left_to_left,
            "leftToRight": left_to_right,
            "rightToLeft": right_to_left,
            "rightToRight": right_to_right,
        }

    def set_low_pass(self, smoothing: float = 20.0) -> None:
        """Sets the low pass filter.

        Parameters
        ----------
        smoothing: float
            The smoothing.
        """
        self._payload["lowPass"] = {"smoothing": smoothing}

    async def apply(self) -> None:
        """Applies the filters to the player."""
        await self._player.node.send(
            {
                "op": "filters",
                "guildId": str(self._player.guild_id),
                **self._payload,
            }
        )
