import discord
from discord.ext import commands
from config import *
from colorama import Back, Fore, Style
import os
import time
import platform
from filefunctions import *

intents = discord.Intents.all()
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='.', intents = intents)

    async def on_ready(self):
        prfx = (Back.BLACK + Fore.GREEN + time.strftime("%H:%M:%S UTC", time.gmtime()) + Back.RESET + Fore.WHITE + Style.BRIGHT)
        print(prfx + " Logged in as " + Fore.YELLOW + f"{bot.user}")
        print(prfx + " Bot ID " + Fore.YELLOW + f"{bot.user.id}")
        print(prfx + " Discord Version " + Fore.YELLOW + discord.__version__)
        print(prfx + " Python Version " + Fore.YELLOW + str(platform.python_version()))
        CreateSongList()
        await self.wait_until_ready()

    async def setup_hook(self):
        for name in os.listdir('cogs'):
            if name.endswith('.py'):
                try:
                    await self.load_extension(f"cogs.{name[:-3]}")
                    print(f'Loaded: cog.{name[:-3]}')
                except Exception as error:
                    print(f'cog.{name[:-3]} cannot be loaded - {error}')


bot = MyBot()


bot.run(TOKEN)
