import discord
from discord.ext import commands
import enum, random
import sys
from copy import deepcopy
from config import path
import json

playerpath = musicpath = f'{path}/charinfo.json'
f = open(playerpath, "r")
characterinfo = json.load(f)

"""converts to a class depending on the string provided"""
def str_to_class(classname):
    return getattr(sys.modules[__name__], classname)


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

        if battling != None:
            enemy_class = str_to_class(battling["enemy"])
            self.battling = enemy_class()
            self.battling.rehydrate(**battling)
        else:
            self.battling = None

        self.user_id = user_id

    """picks a random enemy based on your character level"""
    def hunt(self):
        while True:
            enemy_type = random.choice(Enemy.__subclasses__())

            if enemy_type.min_level <= self.level:
                break
        enemy = enemy_type()
        self.mode = GameMode.BATTLE
        self.battling = enemy
        self.save_to_db()
        return enemy

    """returns the winner based on the fight!"""
    def fight(self, enemy):
        winner = super().fight(enemy)
        self.save_to_db()
        return winner

    """allows you to try and run from a fight"""
    def flee(self, enemy):
        if random.randint(0, 1+self.defense):
            damage = 0
        else:
            damage = enemy.attack/2
            self.hp -= damage

        self.battling = None
        self.mode = GameMode.ADVENTURE
        self.save_to_db()
        return damage, self.hp <= 0

    """function after an enemy is defeated to gain xp"""
    def defeat(self, enemy):
        if self.level < self.level_cap:
            self.xp += enemy.xp
        self.gold += enemy.gold
        self.battling = None
        self.mode = GameMode.ADVENTURE
        ready, _ = self.level_up_check()
        self.save_to_db()

        return enemy.xp, enemy.gold, ready

    """levels up your character based on xp gained"""
    def level_up_check(self):
        if self.level == self.level_cap:
            return False, 0
        xp_needed = self.level*10
        return self.xp >= xp_needed, xp_needed-self.xp

    """give you levels based on xp gained"""
    def level_up(self, stat):
        ready, _ = self.level_up_check()
        if not ready:
            return False, self.level
        self.level += 1
        setattr(self, stat, getattr(self, stat)+1)
        self.hp = self.max_hp
        self.save_to_db()

        return True, self.level

    """when death occurs"""
    def dead(self, player_id):
        if self.user_id in characterinfo["characters"].keys():
            characterinfo.pop(self.user_id)


    """saves the character information into a json file"""
    def save_to_db(self):
        character_info = deepcopy(vars(self))
        if self.battling != None:
            character_info["battling"] = deepcopy(vars(self.battling))
        with open('charinfo.json', 'w') as f:
            json.dump(character_info, f, indent=4)


class Enemy(Actor):
    def __init__(self, name, max_hp, attack, defense, xp, gold):
        super().__init__(name, max_hp, max_hp, attack, defense, xp, gold)
        self.enemy = self.__class__.__name__

    def rehydrate(self, name, hp, max_hp, attack, defense, xp, gold, enemy):
        self.name = name
        self.hp = hp
        self.max_hp = max_hp
        self. attack = attack
        self.defense = defense
        self.xp = xp
        self.gold = gold


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
