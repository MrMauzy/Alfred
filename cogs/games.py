import discord
from discord.ext import commands
import random
import asyncio


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['dice'])
    async def roll(self, ctx, num: int = 20):
        number = random.randint(1, num)
        await ctx.send(number)

    @commands.command()
    async def choose(self, ctx, *, args):
        arguments = args.split(",")
        choice = random.choice(arguments)
        thinking = await ctx.send(":clock1: Hmmm...")
        await asyncio.sleep(0.5)
        for i in range(5):
            await thinking.edit(content = f":clock{i + 1}: Hmmmm...")
            await asyncio.sleep(0.4)
        await ctx.send(choice)

    @commands.command()
    async def guess(self, ctx, num: int = 10):
        number = random.randint(1, num)
        await ctx.send(f"Pick a number... Between 1 and {num} and you have 5 tries.")

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.message.channel
        for i in range(5):
            guess = await self.bot.wait_for('message', check=check)
            try:
                int(guess.content)
                if guess.content == str(number):
                    await ctx.send(f"You got it! Congratulations! In only {i+1} tries!")
                elif int(guess.content) >= number:
                    await ctx.send('LOWER!')
                elif int(guess.content) <= number:
                    await ctx.send("HIGHER!")
            except:
                await ctx.send("Please enter a number... Don't hurt yourself...")
        else:
            await ctx.send(f"You have FAILED! It was obviously {number}")


async def setup(bot):
    await bot.add_cog(Games(bot))