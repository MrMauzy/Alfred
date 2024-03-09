import discord
from discord.ext import commands
import yt_dlp
import asyncio
import json
import os

"""
    Used for the music function to search youtube and download and then play a song
    Can also put a song in a que if the player is currently running. 
"""
musicpath = 'C:/Users/MDiGG/PycharmProjects/Alfred/music.json'
f = open(musicpath, "r")
data = json.load(f)
musicList = data['url']
queList = []
ql = len(musicList) - 1

"""Used in the play function. Just uses a song file in local drive, usually Gangnam Style of course..."""
playSong = "Frank Zappa - King Kong (LP version) [v1ZapVqxcug].webm"


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """#skip command: skips to the next song when using the que list"""
    @commands.command()
    async def skip(self, ctx):
        voice = ctx.guild.voice_client
        if voice.is_playing():
            voice.pause()
            if queList:
                voice.play(discord.FFmpegPCMAudio(queList[0]),
                           after=lambda e: self.check_que(ctx))
            else:
                global ql
                voice.play(discord.FFmpegPCMAudio(musicList[ql]),
                           after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop))
                ql -= 1

    @commands.command(pass_context=True)
    async def que(self, ctx):
        #ql = len(musicList) - 1
        global ql
        if ctx.author.voice.channel:
            if not ctx.guild.voice_client:
                voice_channel = ctx.author.voice.channel
                voice = await voice_channel.connect()
            else:
                voice = ctx.guild.voice_client
            if ql != -1:
                voice.play(discord.FFmpegPCMAudio(musicList[ql]),
                    after=lambda e: self.play_next(ctx))
                ql -= 1
            else:
                await ctx.send("Que over... Come again...")
        else:
            await ctx.send("Enter a voice channel bro...")

    async def play_next(self, ctx):
        global ql
        voice = ctx.guild.voice_client
        if ql != -1:
            voice.play(discord.FFmpegPCMAudio(musicList[ql]),
                       after=lambda e: self.play_next(ctx))
            ql -= 1

    @commands.command(pass_context=True)
    async def play(self, ctx):
        if ctx.author.voice.channel:
            if not ctx.guild.voice_client:
                voice_channel = ctx.author.voice.channel
                voice = await voice_channel.connect()
            else:
                voice = ctx.guild.voice_client
            voice.play(discord.FFmpegPCMAudio(playSong),
                       after=lambda e: print('done', e))
        else:
            await ctx.send("Enter a voice channel bro...")

    @commands.command(pass_context=True)
    async def music(self, ctx, *, searchword):
        ydl_optics = {}
        voice = ctx.voice_client
        if searchword[0:4] == "http" or searchword[0:3] == "www":
            with yt_dlp.YoutubeDL(ydl_optics) as ydl:
                info = ydl.extract_info(searchword, download = False)
                title = info["title"] + ' [' + info["id"] + ']'
                url = searchword
        if searchword[0:4] != "http" or searchword[0:3] != "www":
            with yt_dlp.YoutubeDL(ydl_optics) as ydl:
                info = ydl.extract_info(f"ytsearch:{searchword}", download = False)["entries"][0]
                title = info["title"] + ' [' + info["id"] + ']'
                url = info["webpage_url"]

        ydl_opts = {
            'format': 'bestaudio/best',
            "outtmpl": "-o %(title)s.%(ext)s",
            "postprocessors":
                [{"key": "FFmpegExtractAudio", "preferredcodec": "webm", "preferredquality": "192"}],
        }

        def download(url):
            with yt_dlp.YoutubeDL(ydl_optics) as ydl:
                ydl.download([url])
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, download, url)

        if ctx.author.voice.channel:
            if not ctx.guild.voice_client:
                voice_channel = ctx.author.voice.channel
                voice = await voice_channel.connect()
                for i in os.listdir("C:\\Users\\MDiGG\\PycharmProjects\\Alfred"):
                    if i.startswith(title):
                        queList.append(i)
                voice.play(discord.FFmpegPCMAudio(queList[0]),
                           after=lambda e: self.check_que(ctx))
                queList.pop(0)
            else:
                if ctx.voice_client.is_playing():
                    for i in os.listdir("C:\\Users\\MDiGG\\PycharmProjects\\Alfred"):
                        if i.startswith(title):
                            queList.append(i)
                    #ueList.append(title)
                    await ctx.send(f"Added {title} to the que, sir.")
                else:
                    voice = ctx.guild.voice_client
                    voice.play(discord.FFmpegPCMAudio(queList[0]),
                            after=lambda e: self.check_que(ctx))
                    queList.pop(0)
        else:
            await ctx.send("Please enter a voice chat first, master.")

    async def check_que(self, ctx):
        if queList:
            voice = ctx.guild.voice_client
            voice.play(discord.FFmpegPCMAudio(f"{queList[0]}"),
                       after=lambda e: self.check_que(ctx))
            queList.pop(0)
        else:
            await ctx.send("No more harmonious sounds to play.")


async def setup(bot):
    await bot.add_cog(Music(bot))
