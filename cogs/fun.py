import discord
from discord.ext import commands
import json
import random


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hello(self, ctx):
        user = ctx.author
        await ctx.send(f'Why hello,  {user.mention}, you doing fine today?')

    @commands.command(aliases=['youknowme'])
    async def ryan(self, ctx):
        user = ctx.author
        await ctx.send('I make a mean tuna fish sandwhich - Ryan Gosling')

    @commands.command()
    async def quote(self, ctx):
        with open('C:\\Users\\MDiGG\\PycharmProjects\\Alfred\\cogs\\Quotes.json', "r", encoding='utf-8-sig') as f:
            file_data = json.load(f)
        q1 = file_data['quotes']
        quotes = random.choice(q1)
        await ctx.send(f'{quotes["text"]} -- {quotes["author"]}')


async def setup(bot):
    await bot.add_cog(Fun(bot))
