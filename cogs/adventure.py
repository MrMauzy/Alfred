import os

import discord
from discord.ext import commands
import enum
import random
import sys
from copy import deepcopy
from config import path
import json

playerpath = f'{path}/charinfo.json'
f = open(playerpath, "r")
db = json.load(f)
f.close()

def load_character(user_id):
    """loads character data for the different commands listed below"""
    return Character(**db[str(user_id)])


def status_embed(ctx, character):
    """Gives an embedded messages with the players stats"""
    MODE_COLOR = {
        GameMode.BATTLE: 0x6A329F,
        GameMode.ADVENTURE: 0x9BD21D,
    }
    if character.mode == GameMode.BATTLE:
        mode_text = f"Currently in a battle with the deadly {character.battling.name}"
    elif character.mode == GameMode.ADVENTURE:
        mode_text = f"On an adventure..."

    embed = discord.Embed(title=f"{character.name} status", description=mode_text, color=MODE_COLOR[character.mode])
    embed.set_author(name=ctx.author.name, icon_url=str(ctx.author.display_avatar))

    _, xp_needed = character.level_up_check()
    embed.add_field(name="Stats", value=f"""
        **HP:**     {character.hp}/{character.max_hp}
        **ATTACK**  {character.attack}
        **DEFENSE** {character.defense}
        **MANA**    {character.mana}
        **LEVEL**   {character.level}
        **XP**      {character.xp}/ {character.xp+xp_needed}
        """, inline=True)

    inventory_text = f"Gold: {character.gold}\n"
    if character.inventory:
        inventory_text += "\n".join(character.inventory)
    embed.add_field(name="Inventory", value=inventory_text, inline=True)
    return embed


def str_to_class(classname):
    """converts to a class depending on the string provided"""
    return getattr(sys.modules[__name__], classname)


class RPG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """-------------------Bot Commands-------------------"""

    @commands.command(name="flee", help="Run from the fight")
    async def flee(self, ctx):
        """Flee from battle from hunted creatures"""
        if str(ctx.author.id) not in db:
            await ctx.send(f"To flee, you must first '.create' a character.")
            return
        character = load_character(ctx.author.id)
        if character.mode != GameMode.BATTLE:
            await ctx.send("No monster to flee, try 'hunt'ing one.")
            return
        enemy = character.battling
        damage, killed = character.flee(enemy)
        if killed:
            character.dead()
            await ctx.send(f"{character.name} died running away from {enemy.name}")
        elif damage:
            await ctx.send(f"{character.name} got away but took {damage} point of damage.")
        else:
            await ctx.send(f"{character.name} got away without a scratch from the {enemy.name}.")


    @commands.command(name="fight", help="Fight a monster")
    async def fight(self, ctx):
        """command to fight a hunted monster"""
        if str(ctx.author.id) not in db:
            await ctx.send(f"You must first '.create' a character.")
            return
        character = load_character(ctx.author.id)

        if character.mode != GameMode.BATTLE:
            await ctx.send("No monster to fight, try 'hunt'ing one.")
            return
        enemy = character.battling

        damage, killed = character.fight(enemy)
        if damage:
            await ctx.send(f"{character.name} attacks the wild {enemy.name}, for {damage} damage!")
        else:
            await ctx.send(f"Ouch, {character.name} hit nothing but air. 😹😹😹")

        if killed:
            xp, gold, level_up_check = character.defeat(enemy)
            await ctx.send(f"{character.name} defeated the dreadful {enemy.name}. Getting {xp} xp, {gold} gold.")
            await ctx.send(f"and.. they still have {character.hp} health left.")
            if level_up_check:
                await ctx.send(f"{character.name} is ready to level up to level {character.level+1}. Type '.levelup' to continue.")
            return

        damage, killed = enemy.fight(character)
        if damage:
            await ctx.send(f"{enemy.name} just hit {character.name} with a whopping {damage} damage!")
        else:
            await ctx.send(f"A swing and a miss by the {enemy.name}")
        character.save_to_db()

        if killed:
            character.dead()

            await ctx.send(f"{character.name} was killed by {enemy.name}. GAMEOVER")
            return

        await ctx.send(f"The {enemy.name} lives on, do you fight or flee??")


    @commands.command(name="levelup", help="Pick a stat to level up to the next level - (H)P, (A)TTACK, (D)EFENSE")
    async def levelup(self, ctx, increase):
        character = load_character(ctx.author.id)
        if character.mode == GameMode.BATTLE:
            await ctx.send("You must finish this fight first.")
            return
        ready, xp_needed = character.level_up_check()
        if not ready:
            await ctx.send(f"You need {xp_needed} xp to get to level {character.level+1}")
            return
        if not increase:
            await ctx.send("Please specify a stat to increase (H)P, (A)TTACK, (D)EFENSE")

        increase = increase.lower()
        if increase == "h" or increase == "hp":
            increase = "max_hp"
        elif increase == "a" or increase == "attack":
            increase = "attack"
        elif increase == "d" or increase == "defense":
            increase = "defense"

        success, new_level = character.level_up(increase)
        if success:
            await ctx.send(f"{character.name} has stepped up their game and reached level {new_level}.")
            await ctx.send(f"They also gained some extra {increase}")
        else:
            await ctx.send(f"{character.name} has failed to level up...")


    @commands.command(name="hunt", help="Go looking for a fight")
    async def hunt(self, ctx):
        """command to pick out a monster to battle"""
        if str(ctx.author.id) not in db:
            await ctx.send(f"You must first '.create' a character.")
            return
        character = load_character(ctx.author.id)

        if character.mode != GameMode.ADVENTURE:
            await ctx.send("Watch out, you are already in a battle!!!")
            return
        enemy = character.hunt()
        await ctx.send(f"You have found a wild {enemy.name}. Do you '.fight' or '.flee'??")

    """shows the players status"""
    @commands.command(name="status", help="Get information about your character.")
    async def status(self, ctx):
        if str(ctx.author.id) not in db:
            await ctx.send("You do not have a character. Use '.create' to make one.")
        else:
            character = load_character(ctx.author.id)

            embed = status_embed(ctx, character)
            await ctx.channel.send(None, embed=embed)



    """the create a character function"""
    @commands.command(name="create", help="Create a character")
    async def create(self, ctx, name=None):
        user_id = ctx.author.id

        if not name:
            name = ctx.author.name

        if str(user_id) not in db:
            character = Character(**{
                "name": name,
                "hp": 13,
                "max_hp": 13,
                "attack": 2,
                "defense": 1,
                "mana": 0,
                "level": 1,
                "xp": 0,
                "gold": 0,
                "inventory": [],
                "mode": GameMode.ADVENTURE,
                "battling": None,
                "user_id": user_id
            })
            character.save_to_db()
            await ctx.send(f"New level 1 character created, {name}. Welcome.")
        else:
            await ctx.send("You already have a character.")


    @commands.command(name="restart", help="Start over with a new character")
    async def restart(self, ctx):
        character = load_character(ctx.author.id)
        character.dead()
        await ctx.send(f"{character.name} has gone to greener pastures. Use .create to try again...")


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
        self.max_hp +=(self.level*2)
        self.hp = self.max_hp
        self.save_to_db()

        return True, self.level

    """when death occurs"""
    def dead(self):
        global db
        if str(self.user_id) in db.keys():
            del db[str(self.user_id)]
        with open('charinfo.json', 'w') as f:
            json.dump(db, f, indent=4)

    """saves the character information into a json file"""
    def save_to_db(self):
        global db
        characterinfo = deepcopy(vars(self))
        if self.battling != None:
            characterinfo["battling"] = deepcopy(vars(self.battling))
        if self.user_id in db.keys():
            del db[self.user_id]
        if str(self.user_id) in db.keys():
            del db[str(self.user_id)]
        db[str(self.user_id)] = characterinfo
        os.remove('charinfo.json')
        with open('charinfo.json', 'w') as f:
            json.dump(db, f, indent=4)


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


class Taco(Enemy):
    min_level = 1
    def __init__(self):
        super().__init__("🌮 Taco", 2, 1, 1, 2, 1) # HP, attack, defense, XP, gold


class ConfusedMonkey(Enemy):
    min_level = 1
    def __init__(self):
        super().__init__("🦧 Confused Monkey", 3, 2, 1, 2, 2) # HP, attack, defense, XP, gold


class TacoBell(Enemy):
    min_level = 1
    def __init__(self):
        super().__init__("🚽 Taco Bell Bathroom", 4, 2, 1, 3, 1) # HP, attack, defense, XP, gold


class Llama(Enemy):
    min_level = 2
    def __init__(self):
        super().__init__("🦙 Evil Llama", 5, 3, 1, 3, 2) # HP, attack, defense, XP, gold


class Fred(Enemy):
    min_level = 2
    def __init__(self):
        super().__init__("🦸‍♂️ Guy who asks too many questions", 6, 3, 2, 3, 2) # HP, attack, defense, XP, gold


class Timmy(Enemy):
    min_level = 3
    def __init__(self):
        super().__init__("👨‍🦼 Timmy", 7, 4, 1, 4, 3) # HP, attack, defense, XP, gold


class LanceArmstrong(Enemy):
    min_level = 3
    def __init__(self):
        super().__init__("🚴‍♀️ Lance Armstrong", 8, 4, 2, 4, 3) # HP, attack, defense, XP, gold


class Vampire(Enemy):
    min_level = 4
    def __init__(self):
        super().__init__("🧛‍♂️Count Chocula (except evil)", 9, 5, 1, 5, 4) # HP, attack, defense, XP, gold


class HackerMan(Enemy):
    min_level = 5
    def __init__(self):
        super().__init__("👨‍💻 HackerMan", 10, 6, 2, 6, 5) # HP, attack, defense, XP, gold


async def setup(bot):
    await bot.add_cog(RPG(bot))
