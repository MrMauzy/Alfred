import discord
from discord import Color
from discord.ext import commands
import yt_dlp
import asyncio


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def shutdown(self, ctx):
        await ctx.send("Shutting down... Goodbye....")
        await exit()

    @commands.command()
    async def serverinfo(self, ctx):
        embed = discord.Embed(title=f"{ctx.guild.name}", color=Color.random(), timestamp=ctx.message.created_at)
        text = len(ctx.guild.text_channels)
        voice = len(ctx.guild.voice_channels)
        categories = len(ctx.guild.categories)
        channel = text + voice

        embed.set_thumbnail(url=str(ctx.guild.icon))
        embed.add_field(name=f"", value=f""":white_small_square: ID: **{ctx.guild.id}
            :white_small_square: Owner: <@{ctx.guild.owner_id}>
            :white_small_square: Creation: **{ctx.guild.created_at.strftime('%a %d %B %Y,%I:%M %p UTC')}**
            :white_small_square: Members: **{ctx.guild.member_count}**
            :white_small_square: Channels: **{channel}** | # - **{text}**, V - **{voice}**
            :white_small_square: Categories: **{categories}**
            :white_small_square: Verification: **{str(ctx.guild.verification_level)}**
            :white_small_square: Features: {', '.join(f'{x}' for x in ctx.guild.features)}
            :white_small_square: Splash: **{ctx.guild.splash}**
            """)
        embed.set_footer(text=f'Requested by {ctx.author.name}', icon_url=str(ctx.author.display_avatar))
        await ctx.send(embed=embed)

    @commands.command(pass_context=True)
    async def clear(self, ctx, amount: str):
        if amount == 'all':
            await ctx.channel.purge()
        else:
            await ctx.channel.purge(limit=(int(amount) + 1))

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.id == self.bot.user.id:
            return
        elif before.channel is None:
            voice = after.channel.guild.voice_client
            time = 0
            while True:
                await asyncio.sleep(1)
                time += 1
                if voice.is_playing() and not voice.is_paused():
                    time = 0
                if time == 300:
                    await voice.disconnect()
                if not voice.is_connected():
                    break


async def setup(bot):
    await bot.add_cog(Utility(bot))
