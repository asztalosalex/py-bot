import asyncio
import functools
import os
from typing import Deque, Dict, Optional, Tuple

import discord
from discord.ext import commands

try:
    import yt_dlp as ytdlp
except Exception: 
    ytdlp = None


YDL_OPTS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "default_search": "ytsearch",
    "skip_download": True,
}

FFMPEG_OPTS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}


class GuildMusicState:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queue: asyncio.Queue[Tuple[str, str]] = asyncio.Queue()
        self.current: Optional[Tuple[str, str]] = None  # (title, url)
        self.player_task: Optional[asyncio.Task] = None
        self.voice: Optional[discord.VoiceClient] = None
        self.lock = asyncio.Lock()

    async def ensure_player(self):
        async with self.lock:
            if self.player_task is None or self.player_task.done():
                self.player_task = asyncio.create_task(self.player_loop())

    async def player_loop(self):
        while True:
            try:
                # Wait for next item with an idle timeout; disconnect if idle
                item = await asyncio.wait_for(self.queue.get(), timeout=60)
                self.current = item
                title, stream_url = item
                if not self.voice or not self.voice.is_connected():
                    self.current = None
                    continue

                source = discord.FFmpegPCMAudio(stream_url, **FFMPEG_OPTS)
                self.voice.play(source)

                while self.voice.is_playing():
                    await asyncio.sleep(0.5)

                self.current = None
            except asyncio.TimeoutError:
                # No new items for a while; leave if not playing/paused
                if self.voice and self.voice.is_connected() and not (
                    self.voice.is_playing() or self.voice.is_paused()
                ):
                    await self.voice.disconnect()
                break
            except asyncio.CancelledError:
                break
            except Exception:
                self.current = None
                await asyncio.sleep(0.5)



class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.guild_states: Dict[int, GuildMusicState] = {}

    def get_state(self, guild: discord.Guild) -> GuildMusicState:
        state = self.guild_states.get(guild.id)
        if not state:
            state = GuildMusicState(self.bot)
            self.guild_states[guild.id] = state
        return state
    
    async def ensure_connected(self, ctx: commands.Context) -> GuildMusicState:
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError("Csatlakozz egy hangcsatornához előbb.")
        state = self.get_state(ctx.guild)
        if not state.voice or not state.voice.is_connected():
            state.voice = await ctx.author.voice.channel.connect(reconnect=True)
        return state

    @commands.command(name="join", description="Csatlakozik a hangcsatornához")
    async def join(self, ctx: commands.Context):
        state = await self.ensure_connected(ctx)
        await ctx.reply(f"Csatlakoztam: {state.voice.channel.name}")

    @commands.command(name="leave", aliases=["disconnect"], description="Lecsatlakozik a hangcsatornáról") 
    async def leave(self, ctx: commands.Context):
        state = self.get_state(ctx.guild)
        if state.voice and state.voice.is_connected():
            await state.voice.disconnect()
        if state.player_task and not state.player_task.done():
            state.player_task.cancel()
        state.queue = asyncio.Queue()
        state.current = None
        await ctx.reply("Lecsatlakoztam.")

    @commands.command(name="play", description="Lejátsz egy számot")
    async def play(self, ctx: commands.Context, *, query: str):
        state = await self.ensure_connected(ctx)
        if ytdlp is None:
            await ctx.reply("Hiányzik a yt-dlp csomag.")
            return

        loop = asyncio.get_running_loop()

        def extract_info():
            with ytdlp.YoutubeDL(YDL_OPTS) as ydl:
                info = ydl.extract_info(query, download=False)
                if "entries" in info:
                    info = info["entries"][0]
                return info.get("title") or "Untitled", info["url"]

        try:
            title, stream_url = await loop.run_in_executor(None, extract_info)
        except Exception as e:
            await ctx.reply(f"Nem sikerült lekérni: {e}")
            return

        await state.queue.put((title, stream_url))
        await state.ensure_player()
        await ctx.reply(f"Hozzáadva a sorhoz: {title}")

    @commands.command(name="pause", description="Szünetelteti a lejátszást")
    async def pause(self, ctx: commands.Context):
        state = self.get_state(ctx.guild)
        if state.voice and state.voice.is_playing():
            state.voice.pause()
            await ctx.reply("Szüneteltetve.")
        else:
            await ctx.reply("Nincs lejátszás.")

    @commands.command(name="resume", description="Folytatja a lejátszást")
    async def resume(self, ctx: commands.Context):
        state = self.get_state(ctx.guild)
        if state.voice and state.voice.is_paused():
            state.voice.resume()
            await ctx.reply("Folytatva.")
        else:
            await ctx.reply("Nincs mit folytatni.")

    @commands.command(name="skip", description="Kihagy egy számot")
    async def skip(self, ctx: commands.Context):
        state = self.get_state(ctx.guild)
        if state.voice and (state.voice.is_playing() or state.voice.is_paused()):
            state.voice.stop()
            await ctx.reply("Kihagyva.")
        else:
            await ctx.reply("Nincs szám.")

    @commands.command(name="stop", description="Leállítja a lejátszást")
    async def stop(self, ctx: commands.Context):
        state = self.get_state(ctx.guild)
        if state.player_task and not state.player_task.done():
            state.player_task.cancel()
        if state.voice and (state.voice.is_playing() or state.voice.is_paused()):
            state.voice.stop()
        state.queue = asyncio.Queue()
        state.current = None
        await ctx.reply("Lejátszás leállítva és sor törölve.")

    @commands.command(name="queue", description="Megjeleníti a sorban lévő számokat")
    async def show_queue(self, ctx: commands.Context):
        state = self.get_state(ctx.guild)
        items = list(state.queue._queue)  # type: ignore[attr-defined]
        description = []
        if state.current:
            description.append(f"Most szól: {state.current[0]}")
        if items:
            for idx, (title, _) in enumerate(items, start=1):
                description.append(f"{idx}. {title}")
        if not description:
            description = ["Üres a sor."]
        await ctx.reply("\n".join(description))


async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))


