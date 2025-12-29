#!/usr/bin/env python3
"""
Bandit Music Bot - Discord music bot for Irie Igloo
Uses wavelink 3.x with Lavalink for high-quality audio playback.

Commands:
  !play <query>  - Play a song from YouTube/Spotify/SoundCloud
  !pause         - Pause the current track
  !resume        - Resume playback
  !skip          - Skip to the next track
  !stop          - Stop playback and clear queue
  !queue         - Show the current queue
  !np            - Now playing
  !volume <0-100> - Set volume
  !filters       - Show available audio filters
  !nightcore     - Enable nightcore mode
  !bass          - Boost bass
  !reset         - Reset all filters

Requirements:
  pip install discord.py wavelink python-dotenv
  
Lavalink Server:
  You need a running Lavalink server. Options:
  1. Self-host: https://github.com/lavalink-devs/Lavalink
  2. Free hosted: lava.link (check availability)
"""

import os
import asyncio
import discord
from discord.ext import commands
import wavelink
from dotenv import load_dotenv

load_dotenv()

# Configuration
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
LAVALINK_URI = os.getenv("LAVALINK_URI", "http://localhost:2333")
LAVALINK_PASSWORD = os.getenv("LAVALINK_PASSWORD", "youshallnotpass")

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)


class MusicBot(commands.Cog):
    """Bandit Music Bot cog for Irie Igloo Discord."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    async def cog_load(self):
        """Connect to Lavalink when cog loads."""
        node = wavelink.Node(
            uri=LAVALINK_URI,
            password=LAVALINK_PASSWORD,
        )
        await wavelink.Pool.connect(nodes=[node], client=self.bot)
        print(f"✅ Connected to Lavalink at {LAVALINK_URI}")
    
    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload):
        """Called when Lavalink node is ready."""
        print(f"🎵 Wavelink node ready: {payload.node.identifier}")
    
    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload):
        """Called when a track starts playing."""
        player = payload.player
        track = payload.track
        
        embed = discord.Embed(
            title="🎵 Now Playing",
            description=f"**{track.title}**\nby {track.author}",
            color=discord.Color.magenta()
        )
        if track.artwork:
            embed.set_thumbnail(url=track.artwork)
        embed.add_field(name="Duration", value=self._format_duration(track.length))
        
        if player.channel:
            await player.channel.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload):
        """Called when a track ends."""
        player = payload.player
        
        # Auto-play next track in queue
        if not player.queue.is_empty:
            next_track = player.queue.get()
            await player.play(next_track)
    
    def _format_duration(self, ms: int) -> str:
        """Format milliseconds to mm:ss."""
        seconds = ms // 1000
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"
    
    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx: commands.Context, *, query: str):
        """Play a song from YouTube, Spotify, or SoundCloud."""
        if not ctx.author.voice:
            return await ctx.send("❌ Join a voice channel first!")
        
        # Get or create player
        player = ctx.voice_client
        if not player:
            player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
            player.autoplay = wavelink.AutoPlayMode.enabled
        
        # Search for tracks
        tracks = await wavelink.Playable.search(query)
        if not tracks:
            return await ctx.send(f"❌ No results found for: {query}")
        
        # Handle playlist vs single track
        if isinstance(tracks, wavelink.Playlist):
            added = 0
            for track in tracks.tracks:
                player.queue.put(track)
                added += 1
            await ctx.send(f"📋 Added **{added}** tracks from playlist: {tracks.name}")
        else:
            track = tracks[0]
            player.queue.put(track)
            await ctx.send(f"🎵 Added to queue: **{track.title}**")
        
        # Start playing if not already
        if not player.playing:
            await player.play(player.queue.get())
    
    @commands.command(name="pause")
    async def pause(self, ctx: commands.Context):
        """Pause the current track."""
        player = ctx.voice_client
        if player and player.playing:
            await player.pause(True)
            await ctx.send("⏸️ Paused")
        else:
            await ctx.send("❌ Nothing is playing")
    
    @commands.command(name="resume", aliases=["unpause"])
    async def resume(self, ctx: commands.Context):
        """Resume playback."""
        player = ctx.voice_client
        if player and player.paused:
            await player.pause(False)
            await ctx.send("▶️ Resumed")
        else:
            await ctx.send("❌ Nothing to resume")
    
    @commands.command(name="skip", aliases=["s", "next"])
    async def skip(self, ctx: commands.Context):
        """Skip to the next track."""
        player = ctx.voice_client
        if player and player.playing:
            await player.skip()
            await ctx.send("⏭️ Skipped")
        else:
            await ctx.send("❌ Nothing to skip")
    
    @commands.command(name="stop", aliases=["disconnect", "dc", "leave"])
    async def stop(self, ctx: commands.Context):
        """Stop playback and disconnect."""
        player = ctx.voice_client
        if player:
            await player.disconnect()
            await ctx.send("👋 Disconnected")
        else:
            await ctx.send("❌ Not connected")
    
    @commands.command(name="queue", aliases=["q"])
    async def queue(self, ctx: commands.Context):
        """Show the current queue."""
        player = ctx.voice_client
        if not player:
            return await ctx.send("❌ Not connected")
        
        if player.queue.is_empty and not player.current:
            return await ctx.send("📭 Queue is empty")
        
        embed = discord.Embed(title="🎶 Queue", color=discord.Color.magenta())
        
        if player.current:
            embed.add_field(
                name="Now Playing",
                value=f"**{player.current.title}**",
                inline=False
            )
        
        if not player.queue.is_empty:
            queue_list = []
            for i, track in enumerate(list(player.queue)[:10], 1):
                queue_list.append(f"{i}. {track.title}")
            embed.add_field(
                name=f"Up Next ({len(player.queue)} tracks)",
                value="\n".join(queue_list) or "Empty",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="np", aliases=["nowplaying", "current"])
    async def nowplaying(self, ctx: commands.Context):
        """Show the currently playing track."""
        player = ctx.voice_client
        if not player or not player.current:
            return await ctx.send("❌ Nothing is playing")
        
        track = player.current
        embed = discord.Embed(
            title="🎵 Now Playing",
            description=f"**{track.title}**\nby {track.author}",
            color=discord.Color.magenta()
        )
        if track.artwork:
            embed.set_thumbnail(url=track.artwork)
        
        # Progress bar
        position = player.position
        length = track.length
        progress = int((position / length) * 20)
        bar = "▓" * progress + "░" * (20 - progress)
        embed.add_field(
            name="Progress",
            value=f"{self._format_duration(position)} [{bar}] {self._format_duration(length)}",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="volume", aliases=["vol", "v"])
    async def volume(self, ctx: commands.Context, vol: int = None):
        """Set the volume (0-100)."""
        player = ctx.voice_client
        if not player:
            return await ctx.send("❌ Not connected")
        
        if vol is None:
            return await ctx.send(f"🔊 Current volume: {player.volume}%")
        
        vol = max(0, min(100, vol))
        await player.set_volume(vol)
        await ctx.send(f"🔊 Volume set to {vol}%")
    
    # ─────────────────────────────────────────────────────────────────────────
    # AUDIO FILTERS
    # ─────────────────────────────────────────────────────────────────────────
    
    @commands.command(name="filters")
    async def filters(self, ctx: commands.Context):
        """Show available audio filters."""
        embed = discord.Embed(title="🎛️ Audio Filters", color=discord.Color.magenta())
        embed.add_field(name="!nightcore", value="Speed up + higher pitch", inline=True)
        embed.add_field(name="!bass", value="Boost bass frequencies", inline=True)
        embed.add_field(name="!karaoke", value="Remove vocals", inline=True)
        embed.add_field(name="!slowmo", value="Slow motion audio", inline=True)
        embed.add_field(name="!8d", value="8D audio rotation", inline=True)
        embed.add_field(name="!reset", value="Reset all filters", inline=True)
        await ctx.send(embed=embed)
    
    @commands.command(name="nightcore")
    async def nightcore(self, ctx: commands.Context):
        """Enable nightcore mode (speed + pitch up)."""
        player = ctx.voice_client
        if not player:
            return await ctx.send("❌ Not connected")
        
        filters = player.filters
        filters.timescale.set(speed=1.25, pitch=1.25)
        await player.set_filters(filters)
        await ctx.send("🌙 Nightcore mode enabled!")
    
    @commands.command(name="bass", aliases=["bassboost"])
    async def bass(self, ctx: commands.Context):
        """Boost bass frequencies."""
        player = ctx.voice_client
        if not player:
            return await ctx.send("❌ Not connected")
        
        filters = player.filters
        filters.equalizer.set(
            bands=[
                {"band": 0, "gain": 0.6},
                {"band": 1, "gain": 0.5},
                {"band": 2, "gain": 0.3},
            ]
        )
        await player.set_filters(filters)
        await ctx.send("🔊 Bass boost enabled!")
    
    @commands.command(name="karaoke")
    async def karaoke(self, ctx: commands.Context):
        """Enable karaoke mode (reduce vocals)."""
        player = ctx.voice_client
        if not player:
            return await ctx.send("❌ Not connected")
        
        filters = player.filters
        filters.karaoke.set(level=1.0, mono_level=1.0, filter_band=220.0, filter_width=100.0)
        await player.set_filters(filters)
        await ctx.send("🎤 Karaoke mode enabled!")
    
    @commands.command(name="slowmo", aliases=["slow"])
    async def slowmo(self, ctx: commands.Context):
        """Slow motion audio."""
        player = ctx.voice_client
        if not player:
            return await ctx.send("❌ Not connected")
        
        filters = player.filters
        filters.timescale.set(speed=0.75, pitch=0.9)
        await player.set_filters(filters)
        await ctx.send("🐌 Slow motion enabled!")
    
    @commands.command(name="8d", aliases=["rotation"])
    async def rotation(self, ctx: commands.Context):
        """Enable 8D audio rotation."""
        player = ctx.voice_client
        if not player:
            return await ctx.send("❌ Not connected")
        
        filters = player.filters
        filters.rotation.set(rotation_hz=0.2)
        await player.set_filters(filters)
        await ctx.send("🔄 8D rotation enabled!")
    
    @commands.command(name="reset", aliases=["clearfilters"])
    async def reset_filters(self, ctx: commands.Context):
        """Reset all audio filters."""
        player = ctx.voice_client
        if not player:
            return await ctx.send("❌ Not connected")
        
        filters = player.filters
        filters.reset()
        await player.set_filters(filters)
        await ctx.send("🔄 Filters reset!")


@bot.event
async def on_ready():
    """Called when bot is ready."""
    print(f"=" * 50)
    print(f"🎵 BANDIT MUSIC BOT")
    print(f"=" * 50)
    print(f"Logged in as: {bot.user}")
    print(f"Servers: {len(bot.guilds)}")
    print(f"=" * 50)
    
    # Set status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name="!play | Irie Igloo 🧊"
        )
    )


async def main():
    """Main entry point."""
    if not DISCORD_TOKEN:
        print("❌ Error: DISCORD_BOT_TOKEN not set")
        print("Set it in .env file or environment variable")
        return
    
    async with bot:
        await bot.add_cog(MusicBot(bot))
        await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
