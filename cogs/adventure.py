import discord
from discord.ext import commands
import enum, random, sys
from copy import deepcopy


class RPG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


class GameMode(enum.IntEnum):
    ADVENTURE = 1
    BATTLE = 2


"""Player Characters"""
class Actor:

    def __init__(self, name, hp, max_hp, attack, defense, xp, gold):
        self.name = name
        self.hp = hp
        self.max_hp = max_hp
        self.attack = attack
        self.defense = defense
        self.xp = xp
        self.gold = gold

    def fight(self, other):
        defense = min(other.defense, 19) #cap defense value
        chance_to_hit = random.randint(0, 20-defense)
        if chance_to_hit:
            damage = self.attack
        else:
            damage = 0
        other.hp -= damage

        return self.attack, other.hp <= 0 #fatal damage


async def setup(bot):
    await bot.add_cog(RPG(bot))
