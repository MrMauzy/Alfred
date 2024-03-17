import random

import discord
from discord.ext import commands
from config import path #enter your file directory here
import yt_dlp
import asyncio
import json
import os

"""
    Used for the music function to search youtube and download and then play a song
    Can also put a song in a que if the player is currently running. 
"""
musicpath = f'{path}/music.json'
f = open(musicpath, "r")
data = json.load(f)
musicList = data['url']
random.shuffle(musicList)
queList = []
ql = len(musicList) - 1

"""Used in the play function. Just uses a song file in local drive, usually Gangnam Style of course..."""
playSong = "Chocolate Rain Original Song by Tay Zonday [EwTZ2xpQwpA].webm"
order66music = 'Imperial March.webm'


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pause(self, ctx):
        voice = ctx.guild.voice_client
        if voice.is_playing():
            voice.pause()
            await ctx.send("Music is Paused...")

    @commands.command()
    async def resume(self, ctx):
        voice = ctx.guild.voice_client
        if voice.is_paused():
            voice.resume()
            await ctx.send("Music is Resumed...")

    """#skip command: skips to the next song when using the que list"""
    @commands.command(pass_context=True)
    async def skip(self, ctx, num: int = 1):
        voice = ctx.guild.voice_client
        loop = asyncio.get_event_loop()
        if voice.is_playing():
            voice.pause()
            if queList:
                voice.play(discord.FFmpegPCMAudio(queList[0]),
                           after=lambda e: asyncio.run_coroutine_threadsafe(self.check_que(ctx), loop))
                queList.pop(0)
            else:
                global ql
                if num > 1:
                    ql -= (num - 1)
                await self.listSong(ctx)
                voice.play(discord.FFmpegPCMAudio(musicList[ql]),
                           after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), loop))
                ql -= 1

    """#que is used with a json file with already downloaded song in the Music Directory"""
    @commands.command(pass_context=True)
    async def que(self, ctx):
        global ql
        loop = asyncio.get_event_loop()
        if ctx.author.voice.channel:
            if not ctx.guild.voice_client:
                voice_channel = ctx.author.voice.channel
                voice = await voice_channel.connect()
            else:
                voice = ctx.guild.voice_client
            if ql != -1:
                await self.listSong(ctx)
                voice.play(discord.FFmpegPCMAudio(musicList[ql]),
                    after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), loop))
                ql -= 1
            else:
                await ctx.send("Que over... Come again...")
        else:
            await ctx.send("Enter a voice channel bro...")

    """#play next is used when using the que function to play the next song"""
    async def play_next(self, ctx):
        global ql
        loop = asyncio.get_event_loop()
        voice = ctx.guild.voice_client
        if queList:
            await self.check_que(ctx)
        if ql != -1:
            await self.listSong(ctx)
            voice.play(discord.FFmpegPCMAudio(musicList[ql]),
                       after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), loop))
            ql -= 1

    """#music is used to play a special song that all your friends love to hear"""
    @commands.command(pass_context=True)
    async def music(self, ctx, id: int = 1):
        if ctx.author.voice.channel:
            if not ctx.guild.voice_client:
                voice_channel = ctx.author.voice.channel
                voice = await voice_channel.connect()
            else:
                voice = ctx.guild.voice_client
            if id == 1:
                voice.play(discord.FFmpegPCMAudio(playSong),
                           after=lambda e: print('done', e))
            elif voice.is_playing():
                await ctx.send("Music is already on...")
            elif id == 2:
                voice.play(discord.FFmpegPCMAudio(order66music),
                           after=lambda e: print('done', e))
        else:
            await ctx.send("Enter a voice channel master...")

    """#play can be used to input a youtube link or search words that will pull and play a youtube song to play"""
    @commands.command(pass_context=True)
    async def play(self, ctx, *, searchword):
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
                for i in os.listdir(path):
                    if i.startswith(title):
                        queList.append(i)
                voice.play(discord.FFmpegPCMAudio(queList[0]),
                           after=lambda e: asyncio.run_coroutine_threadsafe(self.check_que(ctx), loop))
                queList.pop(0)
            else:
                if ctx.voice_client.is_playing():
                    for i in os.listdir(path):
                        if i.startswith(title):
                            queList.append(i)
                    await ctx.send(f"Added {searchword} to the que, sir.")
                else:
                    voice = ctx.guild.voice_client
                    voice.play(discord.FFmpegPCMAudio(queList[0]),
                            after=lambda e: asyncio.run_coroutine_threadsafe(self.check_que(ctx), loop))
                    queList.pop(0)
        else:
            await ctx.send("Please enter a voice chat first, master.")

    """#checkque is used for the play function to play the next song in the que"""
    async def check_que(self, ctx):
        loop = asyncio.get_event_loop()
        if queList:
            voice = ctx.guild.voice_client
            voice.play(discord.FFmpegPCMAudio(f"{queList[0]}"),
                       after=lambda e: asyncio.run_coroutine_threadsafe(self.check_que(ctx), loop))
            queList.pop(0)
        else:
            await ctx.send("No more harmonious sounds to play.")

    @commands.command()
    async def playlist(self, ctx):
        response = discord.Embed(color=0x595959)
        playtemp = musicList[ql-3:ql+1]
        playrev = playtemp[::-1]
        playlist = []
        if queList:
            playlist = queList
            for i in range(len(playlist)):
                response.add_field(name="", value=f"{playlist[i]} \n", inline=False)
        else:
            for i in range(3):
                playlist.append(playrev[i][44:-19])
                response.add_field(name="", value=f"{playlist[i]} \n", inline=False)
        await ctx.channel.send(None, embed=response)

    """#order66 a fun Star Wars themed command to initiate order 66"""
    @commands.command()
    async def order66(self, ctx):
        await self.pause(ctx)
        await self.music(ctx, 2)
        await ctx.send('Commander Cody, the time has come. Execute Order Sixty-Six.')
        await ctx.send(f'Start with {ctx.author.mention}')

    async def listSong(self, ctx):
        response = discord.Embed(color=0x595959)
        response.add_field(name="Now playing ", value=f"{musicList[ql][44:-19]}")
        await ctx.channel.send(None, embed=response)


async def setup(bot):
    await bot.add_cog(Music(bot))
