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

class Character(Actor):

    level_cap = 10

    def __init__(self, name, hp, max_hp, attack, defense, mana, level, xp, gold, inventory, mode, battling, user_id):
        super().__init__(name, hp, max_hp, attack, defense, xp, gold)
        self.mana = mana
        self.level = level

        self.inventory = inventory

        self.mode = mode
        self.battling = battling
        self.user_id = user_id


class Enemy(Actor):
    def __init__(self, name, max_hp, attack, defense, xp, gold):
        super().__init__(name, max_hp, max_hp, attack, defense, xp, gold)


class LadyBug(Enemy):
    min_level = 1
    def __init__(self):
        super().__init__("🐞 Lady Bug", 2, 1, 1, 1, 1) # HP, attack, defense, XP, gold


class GiantSpider(Enemy):
    min_level = 1
    def __init__(self):
        super().__init__("🕷️ Giant Spider", 3, 2, 1, 1, 2) # HP, attack, defense, XP, gold


class Bat(Enemy):
    min_level = 1
    def __init__(self):
        super().__init__("🦇 Bat", 4, 2, 1, 2, 1) # HP, attack, defense, XP, gold


class Llama(Enemy):
    min_level = 2
    def __init__(self):
        super().__init__("🦙 Evil Llama", 5, 3, 1, 2, 2) # HP, attack, defense, XP, gold


class Fred(Enemy):
    min_level = 2
    def __init__(self):
        super().__init__("🦸‍♂️ Fred", 6, 3, 2, 2, 2) # HP, attack, defense, XP, gold


class Timmy(Enemy):
    min_level = 3
    def __init__(self):
        super().__init__("👨‍🦼 Timmy", 7, 4, 1, 3, 3) # HP, attack, defense, XP, gold


class LanceArmstrong(Enemy):
    min_level = 3
    def __init__(self):
        super().__init__("🚴‍♀️ Lance Armstrong", 8, 4, 2, 3, 3) # HP, attack, defense, XP, gold


class Vampire(Enemy):
    min_level = 4
    def __init__(self):
        super().__init__("🧛‍♂️Vampire", 9, 5, 1, 4, 4) # HP, attack, defense, XP, gold


class HackerMan(Enemy):
    min_level = 5
    def __init__(self):
        super().__init__("👨‍💻 HackerMan", 10, 6, 2, 5, 5) # HP, attack, defense, XP, gold


async def setup(bot):
    await bot.add_cog(RPG(bot))
