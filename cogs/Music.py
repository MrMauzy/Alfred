import discord
from discord.ext import commands
import yt_dlp
import asyncio
import json
import os


musicpath = 'C:/Users/MDiGG/PycharmProjects/Alfred/music.json'
f = open(musicpath, "r")
data = json.load(f)
musicList = data['url']
queList = []


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def que(self, ctx):
        queLength = len(musicList) - 1
        if ctx.author.voice.channel:
            if not ctx.guild.voice_client:
                voice_channel = ctx.author.voice.channel
                voice = await voice_channel.connect()
            else:
                voice = ctx.guild.voice_client
            if queLength != -1:
                voice.play(discord.FFmpegPCMAudio(musicList[queLength]),
                    after=lambda e: play_next(ctx, queLength))
                queLength -= 1
            else:
                await ctx.send("Que over... Come again...")
        else:
            await ctx.send("Enter a voice channel bro...")

        def play_next(ctx, ql):
            if ql != -1:
                voice.play(discord.FFmpegPCMAudio(musicList[ql]),
                           after=lambda e: play_next(ctx, ql))
                ql -= 1

    @commands.command(pass_context=True)
    async def play(self, ctx):
        if ctx.author.voice.channel:
            if not ctx.guild.voice_client:
                voice_channel = ctx.author.voice.channel
                voice = await voice_channel.connect()
            else:
                voice = ctx.guild.voice_client
            voice.play(discord.FFmpegPCMAudio("[AMV] SUPER RISER!.webm"),
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
                songs = []
                for i in os.listdir("C:\\Users\\MDiGG\\PycharmProjects\\Alfred"):
                    if i.startswith(title):
                        songs.append(i)
                voice.play(discord.FFmpegPCMAudio(songs[0]),#f"{title}.webm"
                           after=lambda e: check_que())
            else:
                if ctx.voice_client.is_playing():
                    for i in os.listdir("C:\\Users\\MDiGG\\PycharmProjects\\Alfred"):
                        if i.startswith(title):
                            queList.append(i)
                    #ueList.append(title)
                    await ctx.send(f"Added {title} to the que, sir.")
                else:
                    voice = ctx.guild.voice_client
                    voice.play(discord.FFmpegPCMAudio(f"{title}.webm"),
                            after=lambda e: check_que())
        else:
            await ctx.send("Please enter a voice chat first, master.")

        def check_que():
            if queList:
                voice.play(discord.FFmpegPCMAudio(f"{queList[0]}.webm"),
                           after=lambda e: check_que())
                queList.pop(0)
            else:
                pass


async def setup(bot):
    await bot.add_cog(Music(bot))
