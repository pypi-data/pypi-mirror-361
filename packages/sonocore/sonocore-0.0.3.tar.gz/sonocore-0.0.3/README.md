# sonocore_new

A powerful and advanced Lavalink client for Python, built from the ground up to leverage Lavalink v4 and Lavasrc capabilities. This client is designed for high performance, robust error handling, and seamless integration with various music sources.

## Features

-   **Lavalink v4 Support:** Fully compatible with the latest Lavalink API, utilizing its REST and WebSocket functionalities.
-   **Lavasrc Integration:** Supports a wide range of music sources (Spotify, Apple Music, Deezer, YouTube, etc.) through Lavasrc, enabling playback from diverse platforms.
-   **Advanced Player Controls:** Comprehensive controls for playback, including play, pause, stop, skip, seek, volume adjustment, and queue management.
-   **Audio Filters:** Apply various audio filters like equalizer, karaoke, timescale, tremolo, vibrato, rotation, distortion, channel mix, and low pass.
-   **Robust Error Handling:** Detailed error logging and custom exceptions for better debugging and stability.
-   **Event-Driven Architecture:** Dispatches events for track start, end, exceptions, and WebSocket status changes, allowing for flexible bot development.
-   **Automatic Reconnection:** Handles WebSocket disconnections and attempts to reconnect with exponential backoff and session resuming.
-   **Optimized Performance:** Efficient handling of Lavalink communication and player state updates.

## Installation

To use `sonocore`, ensure you have Python 3.8+ and `aiohttp` installed.

```bash
pip install aiohttp
```

## Usage

### Basic Example (within a Discord bot)

```python
import asyncio
import logging
import os
import sys

import discord
from discord.ext import commands

# Add the parent directory to the path to import sonocore_new
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sonocore_new")))

import sonocore_new as sonocore
from sonocore.errors import LavalinkException, NoResultsFound, PlayerNotConnected, QueueEmpty
from sonocore.filters import Filters

# Set up logging
logging.basicConfig(level=logging.INFO)

# Define intents
intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
intents.message_content = True


class MusicBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sc_client: sonocore.Client = None
        self.ws_thread: sonocore.DiscordWebSocketThread = None

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        self.sc_client = sonocore.Client(bot_id=self.user.id)
        self.ws_thread = sonocore.DiscordWebSocketThread(self.sc_client, self.http.token)
        self.ws_thread.start()

        await self.sc_client.add_node(
            host="localhost", # Your Lavalink host
            port=2333, # Your Lavalink port
            password="youshallnotpass", # Your Lavalink password
            region="us_central",
        )
        print("Sonocore client connected to Lavalink node.")

    async def on_socket_response(self, payload):
        if self.sc_client:
            await self.sc_client.on_socket_response(payload)

bot = MusicBot(command_prefix="??", intents=intents)

@bot.event
async def on_track_start(event: sonocore.TrackStartEvent):
    if event.player.guild.system_channel:
        await event.player.guild.system_channel.send(f"Now playing: {event.track['info']['title']}")

@bot.event
async def on_track_end(event: sonocore.TrackEndEvent):
    print(f"Track ended: {event.track['info']['title']}. Reason: {event.reason}")

@bot.event
async def on_queue_end(player: sonocore.Player):
    if player.guild.system_channel:
        await player.guild.system_channel.send("The queue has ended.")

@bot.command(name="connect", aliases=["join"])
async def connect(ctx: commands.Context):
    if not ctx.author.voice or not ctx.author.voice.channel:
        return await ctx.send("You are not connected to a voice channel.")

    player = bot.sc_client.get_player(ctx.guild.id)
    if player.is_connected:
        return await ctx.send("I am already connected to a voice channel.")

    try:
        bot.ws_thread.send_voice_state_update(ctx.guild.id, ctx.author.voice.channel.id, self_deaf=True)
        await player.connect(ctx.author.voice.channel.id)
        await ctx.send(f"Connected to **{ctx.author.voice.channel.name}**.")
    except Exception as e:
        await ctx.send(f"Failed to connect to voice channel: {e}")

@bot.command(name="play", aliases=["p"])
async def play(ctx: commands.Context, *, query: str):
    player = bot.sc_client.get_player(ctx.guild.id)

    if not player.is_connected:
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send("You must be in a voice channel to play music.")
        try:
            bot.ws_thread.send_voice_state_update(ctx.guild.id, ctx.author.voice.channel.id, self_deaf=True)
            await player.connect(ctx.author.voice.channel.id)
            await ctx.send(f"Connected to **{ctx.author.voice.channel.name}**.")
        except Exception as e:
            return await ctx.send(f"Failed to connect to voice channel: {e}")

    try:
        await ctx.send(f"Searching for `{query}`...")
        # Use Lavasrc prefixes for various sources
        # Example: "ytsearch:" for YouTube, "scsearch:" for SoundCloud, "spsearch:" for Spotify
        tracks = await bot.sc_client.best_node.get_tracks(f"ytsearch:{query}") # Default to YouTube search
    except NoResultsFound:
        return await ctx.send("No tracks found for your query.")
    except LavalinkException as e:
        return await ctx.send(f"An error occurred while searching for tracks: {e}")
    except Exception as e:
        return await ctx.send(f"An unexpected error occurred: {e}")

    if not tracks or not tracks["data"]:
        return await ctx.send("No tracks found for your query.")

    track_to_add = tracks["data"][0]
    track_to_add["requester"] = ctx.author.mention
    player.add(track_to_add)
    await ctx.send(f"Added to queue: **{track_to_add['info']['title']}**")

    if not player.is_playing:
        try:
            await player.play()
            await ctx.send(f"Now playing: **{track_to_add['info']['title']}**")
        except PlayerNotConnected:
            await ctx.send("Player is not connected to a voice channel. Please use `??connect` first.")
        except Exception as e:
            await ctx.send(f"An error occurred while trying to play: {e}")

@bot.command(name="disconnect", aliases=["leave"])
async def disconnect(ctx: commands.Context):
    player = bot.sc_client.get_player(ctx.guild.id)
    if not player.is_connected:
        return await ctx.send("I am not connected to any voice channel.")

    await player.disconnect()
    bot.ws_thread.send_voice_state_update(ctx.guild.id, None)
    await ctx.send("Disconnected from the voice channel.")

@bot.command(name="skip", aliases=["s"])
async def skip(ctx: commands.Context, count: int = 1):
    player = bot.sc_client.get_player(ctx.guild.id)
    if not player.is_playing:
        return await ctx.send("I am not playing anything.")

    try:
        await player.skip(count)
        await ctx.send(f"Skipped {count} song(s).")
    except ValueError as e:
        await ctx.send(str(e))

@bot.command(name="pause")
async def pause(ctx: commands.Context):
    player = bot.sc_client.get_player(ctx.guild.id)
    if not player.is_playing:
        return await ctx.send("I am not playing anything.")

    await player.set_paused(not player.paused)
    await ctx.send(f"Player is now {'paused' if player.paused else 'resumed'}.")

@bot.command(name="stop")
async def stop(ctx: commands.Context):
    player = bot.sc_client.get_player(ctx.guild.id)
    if not player.is_playing:
        return await ctx.send("I am not playing anything.")

    await player.stop()
    await ctx.send("Stopped the player and cleared the queue.")

@bot.command(name="queue", aliases=["q"])
async def queue(ctx: commands.Context):
    player = bot.sc_client.get_player(ctx.guild.id)
    if not player.queue:
        return await ctx.send("The queue is empty.")

    embed = discord.Embed(title="Queue", color=discord.Color.blue())
    for i, track in enumerate(player.queue):
        embed.add_field(name=f"#{i+1}", value=track['info']['title'], inline=False)

    await ctx.send(embed=embed)

@bot.command(name="shuffle")
async def shuffle(ctx: commands.Context):
    player = bot.sc_client.get_player(ctx.guild.id)
    try:
        player.shuffle()
        await ctx.send("Shuffled the queue.")
    except QueueEmpty:
        await ctx.send("The queue is empty.")

@bot.command(name="loop")
async def loop(ctx: commands.Context, mode: str):
    player = bot.sc_client.get_player(ctx.guild.id)
    if mode.lower() == "track":
        player.loop_track = not player.loop_track
        player.loop_queue = False
        await ctx.send(f"Track loop is now {'enabled' if player.loop_track else 'disabled'}.")
    elif mode.lower() == "queue":
        player.loop_queue = not player.loop_queue
        player.loop_track = False
        await ctx.send(f"Queue loop is now {'enabled' if player.loop_queue else 'disabled'}.")
    else:
        await ctx.send("Invalid loop mode. Use `track` or `queue`.")

@bot.command(name="autoplay")
async def autoplay(ctx: commands.Context):
    player = bot.sc_client.get_player(ctx.guild.id)
    player.autoplay = not player.autoplay
    await ctx.send(f"Autoplay is now {'enabled' if player.autoplay else 'disabled'}.")

@bot.command(name="history")
async def history(ctx: commands.Context):
    player = bot.sc_client.get_player(ctx.guild.id)
    if not player.history:
        return await ctx.send("No history yet.")

    embed = discord.Embed(title="History", color=discord.Color.blue())
    for i, track in enumerate(player.history):
        embed.add_field(name=f"#{i+1}", value=track['info']['title'], inline=False)

    await ctx.send(embed=embed)

@bot.command(name="seek")
async def seek(ctx: commands.Context, position: str):
    player = bot.sc_client.get_player(ctx.guild.id)
    if not player.is_playing:
        return await ctx.send("I am not playing anything.")

    try:
        # Convert position from HH:MM:SS or MM:SS to milliseconds
        parts = list(map(int, position.split(':')))
        if len(parts) == 3:  # HH:MM:SS
            seconds = parts[0] * 3600 + parts[1] * 60 + parts[2]
        elif len(parts) == 2:  # MM:SS
            seconds = parts[0] * 60 + parts[1]
        else:
            return await ctx.send("Invalid position format. Use HH:MM:SS or MM:SS.")

        await player.seek(seconds * 1000)
        await ctx.send(f"Seeked to {position}.")
    except ValueError:
        await ctx.send("Invalid position format. Use HH:MM:SS or MM:SS.")
    except PlayerNotConnected:
        await ctx.send("Player is not connected.")

@bot.command(name="volume")
async def volume(ctx: commands.Context, vol: int):
    player = bot.sc_client.get_player(ctx.guild.id)
    if not player.is_connected:
        return await ctx.send("I am not connected to a voice channel.")

    if not 0 <= vol <= 1000:
        return await ctx.send("Volume must be between 0 and 1000.")

    await player.set_volume(vol)
    await ctx.send(f"Volume set to {vol}.")

@bot.group(name="filters", invoke_without_command=True)
async def filters(ctx: commands.Context):
    await ctx.send("Available filters: `clear`, `equalizer`, `karaoke`, `timescale`, `tremolo`, `vibrato`, `rotation`, `distortion`, `channelmix`, `lowpass`.")

@filters.command(name="clear")
async def filters_clear(ctx: commands.Context):
    player = bot.sc_client.get_player(ctx.guild.id)
    if not player.is_connected:
        return await ctx.send("I am not connected to a voice channel.")

    filters = Filters(player)
    filters.clear()
    await filters.apply()
    await ctx.send("Cleared all filters.")

@filters.command(name="equalizer")
async def filters_equalizer(ctx: commands.Context, band: int, gain: float):
    player = bot.sc_client.get_player(ctx.guild.id)
    if not player.is_connected:
        return await ctx.send("I am not connected to a voice channel.")

    filters = Filters(player)
    filters.set_equalizer([(band, gain)])
    await filters.apply()
    await ctx.send(f"Set equalizer band {band} to gain {gain}.")

@filters.command(name="karaoke")
async def filters_karaoke(ctx: commands.Context, level: float = 1.0, mono_level: float = 1.0, filter_band: float = 220.0, filter_width: float = 100.0):
    player = bot.sc_client.get_player(ctx.guild.id)
    if not player.is_connected:
        return await ctx.send("I am not connected to a voice channel.")

    filters = Filters(player)
    filters.set_karaoke(level, mono_level, filter_band, filter_width)
    await filters.apply()
    await ctx.send("Applied karaoke filter.")

@filters.command(name="timescale")
async def filters_timescale(ctx: commands.Context, speed: float = 1.0, pitch: float = 1.0, rate: float = 1.0):
    player = bot.sc_client.get_player(ctx.guild.id)
    if not player.is_connected:
        return await ctx.send("I am not connected to a voice channel.")

    filters = Filters(player)
    filters.set_timescale(speed, pitch, rate)
    await filters.apply()
    await ctx.send("Applied timescale filter.")

@filters.command(name="tremolo")
async def filters_tremolo(ctx: commands.Context, frequency: float = 2.0, depth: float = 0.5):
    player = bot.sc_client.get_player(ctx.guild.id)
    if not player.is_connected:
        return await ctx.send("I am not connected to a voice channel.")

    filters = Filters(player)
    filters.set_tremolo(frequency, depth)
    await filters.apply()
    await ctx.send("Applied tremolo filter.")

@filters.command(name="vibrato")
async def filters_vibrato(ctx: commands.Context, frequency: float = 2.0, depth: float = 0.5):
    player = bot.sc_client.get_player(ctx.guild.id)
    if not player.is_connected:
        return await ctx.send("I am not connected to a voice channel.")

    filters = Filters(player)
    filters.set_vibrato(frequency, depth)
    await filters.apply()
    await ctx.send("Applied vibrato filter.")

@filters.command(name="rotation")
async def filters_rotation(ctx: commands.Context, rotation_hz: float = 0.0):
    player = bot.sc_client.get_player(ctx.guild.id)
    if not player.is_connected:
        return await ctx.send("I am not connected to a voice channel.")

    filters = Filters(player)
    filters.set_rotation(rotation_hz)
    await filters.apply()
    await ctx.send("Applied rotation filter.")

@filters.command(name="distortion")
async def filters_distortion(ctx: commands.Context, sin_offset: float = 0.0, sin_scale: float = 1.0, cos_offset: float = 0.0, cos_scale: float = 1.0, tan_offset: float = 0.0, tan_scale: float = 1.0, offset: float = 0.0, scale: float = 1.0):
    player = bot.sc_client.get_player(ctx.guild.id)
    if not player.is_connected:
        return await ctx.send("I am not connected to a voice channel.")

    filters = Filters(player)
    filters.set_distortion(sin_offset, sin_scale, cos_offset, cos_scale, tan_offset, tan_scale, offset, scale)
    await filters.apply()
    await ctx.send("Applied distortion filter.")

@filters.command(name="channelmix")
async def filters_channelmix(ctx: commands.Context, left_to_left: float = 1.0, left_to_right: float = 0.0, right_to_left: float = 0.0, right_to_right: float = 1.0):
    player = bot.sc_client.get_player(ctx.guild.id)
    if not player.is_connected:
        return await ctx.send("I am not connected to a voice channel.")

    filters = Filters(player)
    filters.set_channel_mix(left_to_left, left_to_right, right_to_left, right_to_right)
    await filters.apply()
    await ctx.send("Applied channel mix filter.")

@filters.command(name="lowpass")
async def filters_lowpass(ctx: commands.Context, smoothing: float = 20.0):
    player = bot.sc_client.get_player(ctx.guild.id)
    if not player.is_connected:
        return await ctx.send("I am not connected to a voice channel.")

    filters = Filters(player)
    filters.set_low_pass(smoothing)
    await filters.apply()
    await ctx.send("Applied low pass filter.")

if __name__ == "__main__":
    bot.run(config.BOT_TOKEN)
