# sonocore

## The Next Generation Python Lavalink Client

**sonocore** is a cutting-edge, high-performance Lavalink client for Python, meticulously engineered from the ground up to provide unparalleled control over your music bot's audio experience. Designed with robustness, extensibility, and developer-friendliness in mind, sonocore leverages the full power of Lavalink v4 and seamlessly integrates with Lavasrc to support a vast array of music sources.

--- 

### ✨ Key Features

-   **🚀 Blazing Fast & Efficient:** Optimized for speed and minimal resource consumption, ensuring a smooth and responsive audio playback experience.
-   **🎶 Universal Music Source Support:** Thanks to deep Lavasrc integration, play tracks from popular platforms like Spotify, Apple Music, Deezer, YouTube, and more, all through a unified interface.
-   **🎛️ Advanced Audio Filters:** Transform your audio with a comprehensive suite of built-in filters, including:
    -   Equalizer (fine-tune audio frequencies)
    -   Karaoke (remove vocals from tracks)
    -   Timescale (adjust speed, pitch, and rate)
    -   Tremolo & Vibrato (add pulsating and wavering effects)
    -   Rotation (create stereo rotation effects)
    -   Distortion (introduce various distortion types)
    -   Channel Mix (customize audio channel balance)
    -   Low Pass (smooth out high frequencies)
-   **🛡️ Rock-Solid Stability:** Features robust error handling, intelligent reconnection logic with exponential backoff, and detailed logging to ensure maximum uptime and easy debugging.
-   **⚡ Event-Driven Architecture:** React to critical playback events (track start/end, exceptions, WebSocket status) with a flexible and intuitive event system.
-   **🔗 Seamless Discord Integration:** Designed to work flawlessly with `discord.py` and similar libraries, providing a powerful backend for your Discord music bot.

--- 

### 📦 Installation

To get started with `sonocore`, ensure you have Python 3.8+ and `aiohttp` installed.

```bash
pip install aiohttp
```

### 🛠️ Building from Source (for Developers)

If you're contributing or need the absolute latest version, you can build `sonocore` directly:

```bash
# Navigate to the sonocore_new directory
cd C:/CODING/projects/playground/sonocore_new

# Install build tools
pip install build twine

# Build the package
python -m build
```

This will generate `.whl` and `.tar.gz` files in the `dist/` directory.

--- 

### 🚀 Usage (within a Discord Bot Example)

Here's a simplified example demonstrating how to integrate `sonocore` into your `discord.py` bot:

```python
import asyncio
import logging
import os
import sys

import discord
from discord.ext import commands

# IMPORTANT: Adjust this path if your sonocore_new directory is located elsewhere
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sonocore_new")))

import sonocore_new as sonocore
from sonocore.errors import LavalinkException, NoResultsFound, PlayerNotConnected, QueueEmpty
from sonocore.filters import Filters

# Configure logging for better insights
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Define Discord Intents (essential for voice and messages)
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
        # Pass the bot's HTTP token for Discord WebSocket connection
        self.ws_thread = sonocore.DiscordWebSocketThread(self.sc_client, self.http.token)
        self.ws_thread.start()

        # Add your Lavalink node details here
        await self.sc_client.add_node(
            host="localhost", # Your Lavalink host (e.g., 'localhost' or IP address)
            port=2333, # Your Lavalink port (default is 2333)
            password="youshallnotpass", # Your Lavalink password
            region="us_central", # Optional: Node region
        )
        print("Sonocore client connected to Lavalink node.")

    async def on_socket_response(self, payload):
        # Forward Discord voice state/server updates to sonocore
        if self.sc_client:
            await self.sc_client.on_socket_response(payload)

bot = MusicBot(command_prefix="??", intents=intents)

# --- Bot Commands and Event Handlers ---

@bot.event
async def on_track_start(event: sonocore.TrackStartEvent):
    if event.player.guild.system_channel:
        await event.player.guild.system_channel.send(f"Now playing: **{event.track['info']['title']}**")

@bot.event
async def on_track_end(event: sonocore.TrackEndEvent):
    print(f"Track ended: {event.track['info']['title']}. Reason: {event.reason}")

@bot.event
async def on_queue_end(player: sonocore.Player):
    # Assuming 'guild' attribute is available on the player for sending messages
    # You might need to store the guild object in your Player class or pass it around
    if hasattr(player, 'guild') and player.guild.system_channel:
        await player.guild.system_channel.send("The queue has ended.")

@bot.command(name="connect", aliases=["join"])
async def connect(ctx: commands.Context):
    if not ctx.author.voice or not ctx.author.voice.channel:
        return await ctx.send("Please connect to a voice channel first.")

    player = bot.sc_client.get_player(ctx.guild.id)
    if player.is_connected:
        return await ctx.send("I am already connected to a voice channel.")

    try:
        # Send voice state update to Discord via sonocore's WebSocket thread
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
        await ctx.send(f"Searching for `{query}`... This might take a moment.")
        # Use Lavasrc prefixes for various sources (e.g., "ytsearch:", "scsearch:", "spsearch:")
        # For example, to search Spotify: `spsearch:your song title`
        # Defaulting to YouTube search if no prefix is provided
        tracks_result = await bot.sc_client.best_node.get_tracks(query)
    except NoResultsFound:
        return await ctx.send("No tracks found for your query. Try a different search term or add a source prefix (e.g., `ytsearch:`, `spsearch:`).")
    except LavalinkException as e:
        return await ctx.send(f"An error occurred while searching for tracks: {e}")
    except Exception as e:
        return await ctx.send(f"An unexpected error occurred during track search: {e}")

    if not tracks_result or not tracks_result["data"]:
        return await ctx.send("No tracks found for your query.")

    # Lavasrc returns a LoadResult object, access tracks via ['data']
    track_to_add = tracks_result["data"][0] # Take the first track from the results
    track_to_add["requester"] = ctx.author.mention # Add requester info
    player.add(track_to_add)
    await ctx.send(f"Added to queue: **{track_to_add['info']['title']}** by {track_to_add['info']['author']}.")

    if not player.is_playing:
        try:
            await player.play()
            await ctx.send(f"Now playing: **{track_to_add['info']['title']}**")
        except PlayerNotConnected:
            await ctx.send("Player is not connected to a voice channel. Please use `??connect` first.")
        except Exception as e:
            await ctx.send(f"An error occurred while trying to play the track: {e}")

@bot.command(name="disconnect", aliases=["leave"])
async def disconnect(ctx: commands.Context):
    player = bot.sc_client.get_player(ctx.guild.id)
    if not player.is_connected:
        return await ctx.send("I am not connected to any voice channel.")

    try:
        await player.disconnect()
        # Send voice state update to Discord to disconnect bot from voice channel
        bot.ws_thread.send_voice_state_update(ctx.guild.id, None)
        await ctx.send("Disconnected from the voice channel. See you next time!")
    except Exception as e:
        await ctx.send(f"An error occurred during disconnection: {e}")

@bot.command(name="skip", aliases=["s"])
async def skip(ctx: commands.Context, count: int = 1):
    player = bot.sc_client.get_player(ctx.guild.id)
    if not player.is_playing:
        return await ctx.send("I am not playing anything to skip.")

    try:
        await player.skip(count)
        await ctx.send(f"Skipped {count} song(s).")
    except ValueError as e:
        await ctx.send(str(e))
    except PlayerNotConnected:
        await ctx.send("Player is not connected.")
    except Exception as e:
        await ctx.send(f"An unexpected error occurred while skipping: {e}")

@bot.command(name="pause")
async def pause(ctx: commands.Context):
    player = bot.sc_client.get_player(ctx.guild.id)
    if not player.is_playing:
        return await ctx.send("I am not playing anything to pause.")

    try:
        await player.set_paused(not player.paused)
        await ctx.send(f"Player is now {'paused' if player.paused else 'resumed'}.")
    except PlayerNotConnected:
        await ctx.send("Player is not connected.")
    except Exception as e:
        await ctx.send(f"An unexpected error occurred while pausing/resuming: {e}")

@bot.command(name="stop")
async def stop(ctx: commands.Context):
    player = bot.sc_client.get_player(ctx.guild.id)
    if not player.is_playing:
        return await ctx.send("I am not playing anything to stop.")

    try:
        await player.stop()
        await ctx.send("Stopped the player and cleared the queue.")
    except PlayerNotConnected:
        await ctx.send("Player is not connected.")
    except Exception as e:
        await ctx.send(f"An unexpected error occurred while stopping: {e}")

@bot.command(name="queue", aliases=["q"])
async def queue(ctx: commands.Context):
    player = bot.sc_client.get_player(ctx.guild.id)
    if not player.queue:
        return await ctx.send("The queue is currently empty. Add some songs!")

    embed = discord.Embed(title="🎵 Current Queue", color=discord.Color.blue())
    # Display up to 10 tracks for brevity
    for i, track in enumerate(list(player.queue)[:10]):
        embed.add_field(name=f"#{i+1}: {track['info']['title']}", value=f"Artist: {track['info']['author']}", inline=False)
    
    if len(player.queue) > 10:
        embed.set_footer(text=f"And {len(player.queue) - 10} more tracks...")

    await ctx.send(embed=embed)

@bot.command(name="shuffle")
async def shuffle(ctx: commands.Context):
    player = bot.sc_client.get_player(ctx.guild.id)
    try:
        player.shuffle()
        await ctx.send("🔀 Queue shuffled!")
    except QueueEmpty:
        await ctx.send("The queue is empty, nothing to shuffle.")
    except Exception as e:
        await ctx.send(f"An unexpected error occurred while shuffling: {e}")

@bot.command(name="loop")
async def loop(ctx: commands.Context, mode: str):
    player = bot.sc_client.get_player(ctx.guild.id)
    mode = mode.lower()
    if mode == "track":
        player.loop_track = not player.loop_track
        player.loop_queue = False
        await ctx.send(f"🔁 Track loop is now {'enabled' if player.loop_track else 'disabled'}.")
    elif mode == "queue":
        player.loop_queue = not player.loop_queue
        player.loop_track = False
        await ctx.send(f"🔁 Queue loop is now {'enabled' if player.loop_queue else 'disabled'}.")
    elif mode == "off":
        player.loop_track = False
        player.loop_queue = False
        await ctx.send("Looping is now disabled.")
    else:
        await ctx.send("Invalid loop mode. Use `track`, `queue`, or `off`.")

@bot.command(name="autoplay")
async def autoplay(ctx: commands.Context):
    player = bot.sc_client.get_player(ctx.guild.id)
    player.autoplay = not player.autoplay
    await ctx.send(f"▶️ Autoplay is now {'enabled' if player.autoplay else 'disabled'}.")

@bot.command(name="history")
async def history(ctx: commands.Context):
    player = bot.sc_client.get_player(ctx.guild.id)
    if not player.history:
        return await ctx.send("No playback history yet. Start playing some music!")

    embed = discord.Embed(title="📜 Playback History", color=discord.Color.greyple())
    for i, track in enumerate(reversed(list(player.history))): # Show most recent first
        embed.add_field(name=f"#{len(player.history) - i}: {track['info']['title']}", value=f"Artist: {track['info']['author']}", inline=False)

    await ctx.send(embed=embed)

@bot.command(name="seek")
async def seek(ctx: commands.Context, position: str):
    player = bot.sc_client.get_player(ctx.guild.id)
    if not player.is_playing:
        return await ctx.send("I am not playing anything to seek in.")

    try:
        # Convert position from HH:MM:SS or MM:SS to milliseconds
        parts = list(map(int, position.split(':')))
        seconds = 0
        if len(parts) == 3:  # HH:MM:SS
            seconds = parts[0] * 3600 + parts[1] * 60 + parts[2]
        elif len(parts) == 2:  # MM:SS
            seconds = parts[0] * 60 + parts[1]
        elif len(parts) == 1: # SS
            seconds = parts[0]
        else:
            return await ctx.send("Invalid position format. Use `HH:MM:SS`, `MM:SS`, or `SS`.")

        if seconds * 1000 > player.current['info']['length']:
            return await ctx.send("Cannot seek beyond the track's length.")

        await player.seek(seconds * 1000)
        await ctx.send(f"⏩ Seeked to {position}.")
    except ValueError:
        await ctx.send("Invalid position format. Use `HH:MM:SS`, `MM:SS`, or `SS`.")
    except PlayerNotConnected:
        await ctx.send("Player is not connected.")
    except Exception as e:
        await ctx.send(f"An unexpected error occurred while seeking: {e}")

@bot.command(name="volume")
async def volume(ctx: commands.Context, vol: int):
    player = bot.sc_client.get_player(ctx.guild.id)
    if not player.is_connected:
        return await ctx.send("I am not connected to a voice channel.")

    if not 0 <= vol <= 1000:
        return await ctx.send("Volume must be between 0 and 1000.")

    try:
        await player.set_volume(vol)
        await ctx.send(f"🔊 Volume set to {vol}.")
    except PlayerNotConnected:
        await ctx.send("Player is not connected.")
    except Exception as e:
        await ctx.send(f"An unexpected error occurred while setting volume: {e}")

@bot.group(name="filters", invoke_without_command=True)
async def filters(ctx: commands.Context):
    await ctx.send("Available filters: `clear`, `equalizer`, `karaoke`, `timescale`, `tremolo`, `vibrato`, `rotation`, `distortion`, `channelmix`, `lowpass`. Use `??filters <filter_name> [parameters]`.")

@filters.command(name="clear")
async def filters_clear(ctx: commands.Context):
    player = bot.sc_client.get_player(ctx.guild.id)
    if not player.is_connected:
        return await ctx.send("I am not connected to a voice channel.")

    try:
        filters = Filters(player)
        filters.clear()
        await filters.apply()
        await ctx.send("✨ Cleared all filters.")
    except PlayerNotConnected:
        await ctx.send("Player is not connected.")
    except Exception as e:
        await ctx.send(f"An unexpected error occurred while clearing filters: {e}")

@filters.command(name="equalizer")
async def filters_equalizer(ctx: commands.Context, band: int, gain: float):
    player = bot.sc_client.get_player(ctx.guild.id)
    if not player.is_connected:
        return await ctx.send("I am not connected to a voice channel.")

    if not 0 <= band <= 14:
        return await ctx.send("Equalizer band must be between 0 and 14.")
    if not -0.25 <= gain <= 1.0:
        return await ctx.send("Gain must be between -0.25 and 1.0.")

    try:
        filters = Filters(player)
        filters.set_equalizer([(band, gain)])
        await filters.apply()
        await ctx.send(f"🎚️ Set equalizer band {band} to gain {gain}.")
    except PlayerNotConnected:
        await ctx.send("Player is not connected.")
    except Exception as e:
        await ctx.send(f"An unexpected error occurred while setting equalizer: {e}")

@filters.command(name="karaoke")
async def filters_karaoke(ctx: commands.Context, level: float = 1.0, mono_level: float = 1.0, filter_band: float = 220.0, filter_width: float = 100.0):
    player = bot.sc_client.get_player(ctx.guild.id)
    if not player.is_connected:
        return await ctx.send("I am not connected to a voice channel.")

    try:
        filters = Filters(player)
        filters.set_karaoke(level, mono_level, filter_band, filter_width)
        await filters.apply()
        await ctx.send("🎤 Applied karaoke filter.")
    except PlayerNotConnected:
        await ctx.send("Player is not connected.")
    except Exception as e:
        await ctx.send(f"An unexpected error occurred while applying karaoke filter: {e}")

@filters.command(name="timescale")
async def filters_timescale(ctx: commands.Context, speed: float = 1.0, pitch: float = 1.0, rate: float = 1.0):
    player = bot.sc_client.get_player(ctx.guild.id)
    if not player.is_connected:
        return await ctx.send("I am not connected to a voice channel.")

    try:
        filters = Filters(player)
        filters.set_timescale(speed, pitch, rate)
        await filters.apply()
        await ctx.send("⏱️ Applied timescale filter.")
    except PlayerNotConnected:
        await ctx.send("Player is not connected.")
    except Exception as e:
        await ctx.send(f"An unexpected error occurred while applying timescale filter: {e}")

@filters.command(name="tremolo")
async def filters_tremolo(ctx: commands.Context, frequency: float = 2.0, depth: float = 0.5):
    player = bot.sc_client.get_player(ctx.guild.id)
    if not player.is_connected:
        return await ctx.send("I am not connected to a voice channel.")

    try:
        filters = Filters(player)
        filters.set_tremolo(frequency, depth)
        await filters.apply()
        await ctx.send("🌊 Applied tremolo filter.")
    except PlayerNotConnected:
        await ctx.send("Player is not connected.")
    except Exception as e:
        await ctx.send(f"An unexpected error occurred while applying tremolo filter: {e}")

@filters.command(name="vibrato")
async def filters_vibrato(ctx: commands.Context, frequency: float = 2.0, depth: float = 0.5):
    player = bot.sc_client.get_player(ctx.guild.id)
    if not player.is_connected:
        return await ctx.send("I am not connected to a voice channel.")

    try:
        filters = Filters(player)
        filters.set_vibrato(frequency, depth)
        await filters.apply()
        await ctx.send("🌀 Applied vibrato filter.")
    except PlayerNotConnected:
        await ctx.send("Player is not connected.")
    except Exception as e:
        await ctx.send(f"An unexpected error occurred while applying vibrato filter: {e}")

@filters.command(name="rotation")
async def filters_rotation(ctx: commands.Context, rotation_hz: float = 0.0):
    player = bot.sc_client.get_player(ctx.guild.id)
    if not player.is_connected:
        return await ctx.send("I am not connected to a voice channel.")

    try:
        filters = Filters(player)
        filters.set_rotation(rotation_hz)
        await filters.apply()
        await ctx.send("🔄 Applied rotation filter.")
    except PlayerNotConnected:
        await ctx.send("Player is not connected.")
    except Exception as e:
        await ctx.send(f"An unexpected error occurred while applying rotation filter: {e}")

@filters.command(name="distortion")
async def filters_distortion(ctx: commands.Context, sin_offset: float = 0.0, sin_scale: float = 1.0, cos_offset: float = 0.0, cos_scale: float = 1.0, tan_offset: float = 0.0, tan_scale: float = 1.0, offset: float = 0.0, scale: float = 1.0):
    player = bot.sc_client.get_player(ctx.guild.id)
    if not player.is_connected:
        return await ctx.send("I am not connected to a voice channel.")

    try:
        filters = Filters(player)
        filters.set_distortion(sin_offset, sin_scale, cos_offset, cos_scale, tan_offset, tan_scale, offset, scale)
        await filters.apply()
        await ctx.send("💥 Applied distortion filter.")
    except PlayerNotConnected:
        await ctx.send("Player is not connected.")
    except Exception as e:
        await ctx.send(f"An unexpected error occurred while applying distortion filter: {e}")

@filters.command(name="channelmix")
async def filters_channelmix(ctx: commands.Context, left_to_left: float = 1.0, left_to_right: float = 0.0, right_to_left: float = 0.0, right_to_right: float = 1.0):
    player = bot.sc_client.get_player(ctx.guild.id)
    if not player.is_connected:
        return await ctx.send("I am not connected to a voice channel.")

    try:
        filters = Filters(player)
        filters.set_channel_mix(left_to_left, left_to_right, right_to_left, right_to_right)
        await filters.apply()
        await ctx.send("🎚️ Applied channel mix filter.")
    except PlayerNotConnected:
        await ctx.send("Player is not connected.")
    except Exception as e:
        await ctx.send(f"An unexpected error occurred while applying channel mix filter: {e}")

@filters.command(name="lowpass")
async def filters_lowpass(ctx: commands.Context, smoothing: float = 20.0):
    player = bot.sc_client.get_player(ctx.guild.id)
    if not player.is_connected:
        return await ctx.send("I am not connected to a voice channel.")

    try:
        filters = Filters(player)
        filters.set_low_pass(smoothing)
        await filters.apply()
        await ctx.send("🔊 Applied low pass filter.")
    except PlayerNotConnected:
        await ctx.send("Player is not connected.")
    except Exception as e:
        await ctx.send(f"An unexpected error occurred while applying low pass filter: {e}")

if __name__ == "__main__":
    # Replace "YOUR_BOT_TOKEN" with your actual bot token from Discord Developer Portal
    bot.run("YOUR_BOT_TOKEN")
```

--- 

### ⚙️ Configuration

Before running your bot, ensure your `config.py` (or similar configuration) has the correct Lavalink server details:

```python
# config.py example
BOT_TOKEN = "YOUR_BOT_TOKEN" # Replace with your Discord bot token
LAVALINK_HOST = "localhost" # Your Lavalink server host
LAVALINK_PORT = 2333 # Your Lavalink server port
LAVALINK_PASSWORD = "youshallnotpass" # Your Lavalink server password
```

Make sure your Lavalink server is running and has the Lavasrc plugin installed and configured correctly to enable playback from various sources.

--- 

### 🤝 Contributing

We welcome contributions! Feel free to open issues or submit pull requests on our GitHub repository.

### 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for details.