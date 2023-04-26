#--#
#AUDIO COMMANDS
#--#

#IMPORTS

import asyncio
import yt_dlp
import discord
from discord.ext import commands

#--#

class CMDAudio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}

    async def play_song(self, ctx, song_url):
        voice_client = ctx.guild.voice_client
        if voice_client is None:
            voice_channel = ctx.author.voice.channel
            voice_client = await voice_channel.connect()

        with yt_dlp.YoutubeDL({'format': 'bestaudio/best'}) as ydl:
            info = ydl.extract_info(song_url, download=False)
            audio_url = info['url']

        audio_source = discord.FFmpegOpusAudio(audio_url)
        voice_client.play(audio_source, after=lambda e: self.bot.loop.create_task(self.song_finished(ctx)))

    async def song_finished(self, ctx):
        if len(self.queues[ctx.guild.id]) > 0:
            next_song_url = self.queues[ctx.guild.id].pop(0)
            await self.play_song(ctx, next_song_url)

    @commands.command()
    async def play(self, ctx, *, search: str):
        if ctx.author.voice is None:
            await ctx.send("You need to be in a voice channel to use this command.")
            return
    
        ydl_opts = {'noplaylist': True}
        if "youtube.com" in search or "youtub.be" in search:
            ydl_opts['format'] = 'bestaudio/best'
            video_url = search
        else:
            ydl_opts['default_search'] = 'ytsearch'
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(search, download=False)
                video_url = info['entries'][0]['webpage_url']
    
        if ctx.guild.voice_client and ctx.guild.voice_client.is_playing():
            if ctx.guild.id not in self.queues:
                self.queues[ctx.guild.id] = []
            self.queues[ctx.guild.id].append(video_url)
            await ctx.send(f"Added to the queue: {info['entries'][0]['title']}")
        else:
            await self.play_song(ctx, video_url)
            await ctx.send(f"Now playing: {info['entries'][0]['title']}")

    @commands.command()
    async def skip(self, ctx):
        voice_client = ctx.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            await ctx.send("Skipped the current song.")
        else:
            await ctx.send("There's no song playing right now.")

    @commands.command()
    async def q(self, ctx):
        queue = self.queues.get(ctx.guild.id, [])
        if not queue:
            await ctx.send("There are no songs in the queue.")
            return

        queue_text = "Songs in the queue:\n"
        for idx, song_url in enumerate(queue, start=1):
            with yt_dlp.YoutubeDL({}) as ydl:
                info = ydl.extract_info(song_url, download=False)
                queue_text += f"{idx}. {info['title']}\n"

        await ctx.send(queue_text)

    @commands.command()
    async def stop(self, ctx):
        voice_client = ctx.guild.voice_client
        if voice_client:
            await voice_client.disconnect()
        else:
            await ctx.send("I'm not connected to a voice channel.")

#--#
async def setup(bot):
    await bot.add_cog(CMDAudio(bot))