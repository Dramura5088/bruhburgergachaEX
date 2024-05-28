import discord
from discord.ext import tasks, commands
from discord.ext.commands import has_permissions, MissingPermissions
from discord.ui import Button, View
import json
import os
import math
import random
import datetime
from numpy.random import choice
import pytz
from pytz import timezone
from pathlib import Path

intents = discord.Intents.all()
client = commands.Bot(command_prefix="$", intents=intents)


#
#
#
#BURGER SECTION
class Burger:

  def __init__(self, rarity, name, id, mods=[], circulation={}):
    self.id = id
    self.rarity = rarity
    self.name = name
    self.mods = mods
    self.circulation = circulation

  def to_json(self):
    return self.__dict__


def get_burgerstorage_data():
  with open("burgerstorage.json", "r") as file:
    json_burgers = json.load(file)

    burgers = {}
    for json_burger in json_burgers:
      circulation = {}
      for type in json_burger["circulation"].keys():
        #Reconstructs circulation to make users into int again
        circulation[type] = {}
        for user in json_burger["circulation"][type].keys():
          circulation[type][int(user)] = json_burger["circulation"][type][user]
      burger = Burger(json_burger["rarity"], json_burger["name"],
                      json_burger["id"], json_burger["mods"], circulation)
      burgers[json_burger["id"]] = burger
    return burgers


def write_burgerstorage_data():
  with open("burgerstorage.json", "w") as file:
    json_burgers = []

    for burger in _burgers.values():
      json_burger = burger.to_json()
      json_burgers.append(json_burger)

    json.dump(json_burgers, file, indent=3)
    global _burger_rarity
    _burger_rarity = generate_burger_rarity_table()


#
#
#
#USER SECTION
class User:

  def __init__(self, currency=0, burgers={}, spins=5):
    self.currency = currency
    self.burgers = burgers
    self.spins = spins

  def to_json(self):
    return self.__dict__


def get_userstorage_data():
  with open("userstorage.json", "r") as file:
    json_users = json.load(file)
    users = {}

    for json_user in json_users:
      currency = json_users[json_user]["currency"]
      burgers = {}
      for key in json_users[json_user]["burgers"].keys():
        burgers[int(key)] = json_users[json_user]["burgers"][key]
        #Making burger id's back into int

      spins = json_users[json_user]["spins"]

      users[int(json_user)] = User(currency, burgers, spins)
    return users


def write_userstorage_data():
  with open("userstorage.json", "w") as f:
    json_users = {}
    for user in _users:
      json_users[user] = _users[user].to_json()
      #json_users[]

    json.dump(json_users, f, indent=3)


def generate_burger_rarity_table():
  burger_rarity = {}
  for rarity in _rarity:
    burger_rarity[rarity] = []
  for burger in _burgers.values():
    burger_rarity[burger.rarity].append(burger.id)
  return burger_rarity


async def update_user_storage():
  _users = get_userstorage_data()


#
#
#
# GLOBALS !
_burgers = get_burgerstorage_data()
_users = get_userstorage_data()

_rarity = [
  "Common", "Uncommon", "Rare", "Super Rare", "Super Super Rare", "Legendary"
]
_probabilities = [0.5905, 0.25, 0.10, 0.054, 0.005, 0.0005]

_burger_rarity = generate_burger_rarity_table()

_admins_id = [241629815931797505, 460684769718566913, 1105115900086071326]


#
#
#
# EVENTS
@client.event
async def on_ready():
  print("Let the addiction begin!")
  automatedBackup.start()


#
#
#
#LOOPS


@tasks.loop(hours=2)
async def automatedBackup():
  print("Started Automated Backup")
  createBackup()
  print("Finished Automated Backup")


def createBackup():

  timezone_cet = timezone("Europe/Stockholm")
  ft = "%Y-%m-%dT%H:%M:%S%z"
  cur_time = datetime.datetime.now(tz=timezone_cet).strftime(ft)
  os.makedirs(f"Backup/{cur_time}", exist_ok=True)
  burger_backup = open(f"Backup/{cur_time}/burgerstorage.json", "w")
  user_backup = open(f"Backup/{cur_time}/userstorage.json", "w")

  #write burgers
  json_burgers = []

  for burger in _burgers.values():
    json_burger = burger.to_json()
    json_burgers.append(json_burger)

  json.dump(json_burgers, burger_backup, indent=3)

  #write users
  json_users = {}
  for user in _users:
    json_users[user] = _users[user].to_json()
    #json_users[]

  json.dump(json_users, user_backup, indent=3)

  user_backup.close
  burger_backup.close


#
#
#
# COMMANDS !
@client.command(aliases=["p", "prices", "price"])
async def pricing(ctx):
  view = View()
  em = em = discord.Embed(color=0xffae00)
  name = f"Pricing Packages Table:"
  text = f"Standard **20TB** Contains:\n"
  text += f"~ **1** x Bruhburgergacha spin\n\n"

  text += f"Low Spender **100TB** Contains:\n"
  text += f"~ Permanent Discord Role 'Low Spender'\n"
  text += f"~ **5** x Bruhburgergacha spins\n"
  text += f"~ **1** x ***Bonus*** Bruhburgergacha spins\n\n"

  text += f"Spender **200TB** Contains:\n"
  text += f"~ Permanent Discord Role 'Spender'\n"
  text += f"~ **10** x Bruhburgergacha spins\n"
  text += f"~ **3** x ***Bonus*** Bruhburgergacha spins\n\n"

  text += f"Big Spender **1000TB** Contains:\n"
  text += f"~ Permanent Discord Role 'Big Spender'\n"
  text += f"~ **50** x Bruhburgergacha spins\n"
  text += f"~ **20** x ***Bonus*** Bruhburgergacha spins\n"
  text += f"~ ***BEST VALUE!!! 40% BONUS!!***\n"
  em.add_field(name=name, value=text, inline=False)
  message = await ctx.reply(embed=em, view=view)


@client.command(aliases=["gs"])
async def giveSpins(ctx, user: discord.User, amount: int):
  await register_user(ctx.author)
  await register_user(user)

  if _users[ctx.author.id].spins < amount:
    await ctx.reply("You don't have enough spins!")
    return False
  else:
    _users[ctx.author.id].spins -= amount
    _users[user.id].spins += amount

  write_userstorage_data()
  await ctx.reply(
    f"{ctx.author.mention} now has {_users[ctx.author.id].spins} spins. {user.mention} now has {_users[user.id].spins} spins"
  )
  return True


@client.command(aliases=["inv", "i"])
async def showInventory(ctx, page: int = 0, items_per_page: int = 15):
  await register_user(ctx.author)
  user = _users[ctx.author.id]

  #Make a list of all the different burgers!
  burger_list = []
  for burger_id in user.burgers.keys():
    for burger_mod in user.burgers[burger_id].keys():
      amount = user.burgers[burger_id][burger_mod]

      burger_info = [burger_id, burger_mod, amount]
      burger_list.append(burger_info)

  if len(burger_list) != 0:
    max_pages = math.ceil((len(burger_list) / items_per_page)) - 1
  else:
    max_pages = 0

  #Is the page input out of bounds?
  async def out_of_bounds_check(new_page, max_page):
    if new_page > max_page or new_page < 0:
      return False
    else:
      return True

  if page > max_pages:
    page = max_pages
  elif await out_of_bounds_check(page, max_pages):
    page = 0

  #Generate embed based on which page.
  async def generate_embed(ge_page: int, ge_max_page: int):
    embed = discord.Embed(color=0xffae00)

    name = f"**{ctx.author.display_name}**'s Private Burger Collection Contains:"
    text = ""

    # page flippin loop
    if len(burger_list) != 0:
      itemIndexStart = ge_page * items_per_page

      if itemIndexStart + items_per_page > len(burger_list):
        itemIndexEnd = len(burger_list)
      else:
        itemIndexEnd = itemIndexStart + items_per_page

      last_burger_id = -1
      for x in range(itemIndexStart, itemIndexEnd):

        burger_id = burger_list[x][0]
        burger_mod = burger_list[x][1].split('#')
        burger_amount = burger_list[x][2]
        burger_name = _burgers[burger_id].name

        if last_burger_id != burger_id:
          text += f"\n*{_burgers[burger_id].rarity}* **{burger_name}**:\n"
        for mod in burger_mod:

          if mod != 'Null':
            burger_name += f" {_burgers[burger_id].mods[int(mod)]}"

        text += f" ~ {burger_amount} x {burger_name}\n"
        last_burger_id = burger_id
    else:
      text = "This collection is ***empty!***"

    text += f"\n Spins: **{user.spins}**"
    text += f"\n Page: **{ge_page}**/**{ge_max_page}**"

    if len(text) > 1024:
      embed.add_field(
        name=name,
        value=
        f"Your request was **{len(text)}** letters which is bigger than the maximum of **1024** letters that discord lets us utilise. \n*Better luck next time!*",
        inline=False)
      return embed
    else:
      embed.add_field(name=name, value=text, inline=False)
      return embed

  async def get_page_numbers(interaction):
    txt = interaction.message.embeds[0].fields[0].value
    txt_list = txt.split('Page: ')[1].replace('*', '').split('/')
    cur_page = []
    for number in txt_list:
      cur_page.append(int(number))

    return cur_page

  async def page_backwards(interaction):
    await interaction.response.defer()
    page_numbers = await get_page_numbers(interaction)
    if await out_of_bounds_check(page_numbers[0] - 1, page_numbers[1]):
      await change_page(interaction, page_numbers[0] - 1, page_numbers[1])
    else:
      await change_page(interaction, page_numbers[1], page_numbers[1])

  async def page_forwards(interaction):
    await interaction.response.defer()
    page_numbers = await get_page_numbers(interaction)
    if await out_of_bounds_check(page_numbers[0] + 1, page_numbers[1]):
      await change_page(interaction, page_numbers[0] + 1, page_numbers[1])
    else:
      await change_page(interaction, 0, page_numbers[1])

  async def change_page(interaction, page: int, max_page: int):
    await message.edit(embed=await generate_embed(page, max_page))

  button_backwards = Button(style=discord.ButtonStyle.green, emoji="⬅")
  button_forwards = Button(style=discord.ButtonStyle.green, emoji="➡")

  button_backwards.callback = page_backwards
  button_forwards.callback = page_forwards

  view = View()
  view.add_item(button_backwards)
  view.add_item(button_forwards)

  em = await generate_embed(page, max_pages)
  message = await ctx.reply(embed=em, view=view)


@client.command(aliases=["s", "roll"])
async def spin(ctx, amount: str = "1"):
  await register_user(ctx.author)
  global _users
  global _burgers
  user = _users[ctx.author.id]
  spins = user.spins

  if amount.lower() == "all":
    amount = spins
  else:
    try:
      if spins < int(amount):
        view = View()
        em = discord.Embed(color=0xffae00)
        name = f"Range Error"
        text = f"You do not have **{amount}** spins. You have **{spins}** spins."
        em.add_field(name=name, value=text, inline=False)
        message = await ctx.reply(embed=em, view=view)
        return
    except ValueError:
      view = View()
      em = discord.Embed(color=0xffae00)
      name = f"Input Error"
      text = f"The input you gave is not valid. Valid input examples:\n$spin all\n$spin 100"
      em.add_field(name=name, value=text, inline=False)
      message = await ctx.reply(embed=em, view=view)
      return

  amount = int(amount)
  user.spins -= amount

  new_burgers = []

  for i in range(amount):
    new_burgers.append(await rollBurger())

  #Stupid sorting algorithm
  sorted_burgers = {}
  for burger in new_burgers:
    # Voila now readable!
    burger_id = burger[0]
    burger_mods = burger[1]

    if burger_id not in sorted_burgers.keys():
      sorted_burgers[burger_id] = {burger_mods: 1}

    else:  # The burger is in the castle!
      if burger_mods not in sorted_burgers[burger_id].keys():
        sorted_burgers[burger_id][burger_mods] = 1
      else:
        sorted_burgers[burger_id][burger_mods] += 1

  for burger in sorted_burgers.keys():
    for set in sorted_burgers[burger].keys():

      await addBurger(ctx, burger, sorted_burgers[burger][set], set)
  write_burgerstorage_data()
  write_userstorage_data()
  _burgers = get_burgerstorage_data()
  _users = get_userstorage_data()

  #Makes a list out of burgers
  burger_list = []
  for burger_id in sorted_burgers.keys():
    for burger_mod in sorted_burgers[burger_id].keys():
      amount = sorted_burgers[burger_id][burger_mod]

      burger_info = [burger_id, burger_mod, amount]
      burger_list.append(burger_info)

  global current_view
  current_view = 0
  global items_flipped
  items_flipped = {}

  async def generate_embed():
    global current_view
    global items_flipped
    embed = discord.Embed(color=0xffae00)
    name = f"**{ctx.author.display_name}**'s new burgers"
    text = ""
    text_end = f"\n Spins: **{user.spins}**" + f"\n From item **{current_view+1}**/**{len(burger_list)+1}**"
    number_of_letters = len(text_end)

    if len(burger_list) != 0:
      items_flipped_amount = 0
      last_burger_id = -1
      while number_of_letters < 1024:

        if current_view >= len(burger_list):
          #print("heh? v: "+ str(current_view) +" bl: " + str(len(burger_list)))
          break

        burger_text = ""

        burger_id = burger_list[current_view][0]
        burger_mod = burger_list[current_view][1].split('#')
        burger_amount = burger_list[current_view][2]

        burger_name = _burgers[burger_id].name

        if last_burger_id != burger_id:
          burger_text += f"\n*{_burgers[burger_id].rarity}* **{burger_name}**:\n"
        for mod in burger_mod:

          if mod != 'Null':
            burger_name += f" {_burgers[burger_id].mods[int(mod)]}"

        burger_text += f" ~ {burger_amount} x {burger_name}\n"
        last_burger_id = burger_id

        if number_of_letters + len(burger_text) < 1024:
          current_view += 1
          items_flipped_amount += 1
          text += burger_text
          number_of_letters += len(burger_text)
          #print("View: "+str(current_view) + " Letters: " + str(number_of_letters) + " b: " + str(len(burger_text)))
        else:
          #print("xView: "+str(current_view) + " Letters: " + str(number_of_letters) + " b: " + str(len(burger_text)))
          break
      if current_view not in items_flipped:
        items_flipped[current_view] = items_flipped_amount
    else:
      text += "This collection is ***empty!***"

    text += text_end
    embed.add_field(name=name, value=text, inline=False)
    return embed

  async def backwards(interaction):
    global current_view
    global items_flipped
    await interaction.response.defer()

    if current_view in items_flipped:
      current_view -= items_flipped[current_view]
      if current_view in items_flipped:
        current_view -= items_flipped[current_view]
      else:
        current_view = 0
    else:
      current_view = 0
    await message.edit(embed=await generate_embed())

  async def forwards(interaction):
    await interaction.response.defer()
    await message.edit(embed=await generate_embed())

  button_backwards = Button(style=discord.ButtonStyle.green, emoji="⬅")
  button_forwards = Button(style=discord.ButtonStyle.green, emoji="➡")

  button_backwards.callback = backwards
  button_forwards.callback = forwards

  view = View()
  view.add_item(button_backwards)
  view.add_item(button_forwards)

  em = await generate_embed()
  message = await ctx.reply(embed=em, view=view)


#
#
#
# ADMIN COMMANDS
@client.command(aliases=["ags"])
async def adminGiveSpins(ctx, user: discord.User, amount: int):
  if not await is_administrator(ctx, ctx.message.author.id):
    return False
  await register_user(user)
  _users[user.id].spins += amount
  write_userstorage_data()
  await ctx.reply(f"{user.mention} now has **{_users[user.id].spins}** spins!")
  return True


@client.command(aliases=["mbm"])
async def makeBurgerMod(ctx, burger_id: int, *mods: str):
  if not await is_administrator(ctx, ctx.message.author.id):
    return False
  print(f"BURGER ID FOR MBM: {burger_id}")
  global _burgers
  _burgers[burger_id].mods.extend(mods)
  print(_burgers[burger_id])
  write_burgerstorage_data()
  await BurgerInfo(ctx, burger_id)
  return True


@client.command(aliases=["bb"])
async def burgers(ctx):
  if not await is_administrator(ctx, ctx.message.author.id):
    return False

  burgers = []
  for rarity in _burger_rarity.values():
    for burger_id in rarity:
      burgers.append(_burgers[burger_id])

  global current_view_bb
  global items_flipped_bb
  current_view_bb = 0
  items_flipped_bb = {}

  async def generate_embed(burgers):
    global current_view_bb
    global items_flipped_bb
    embed = discord.Embed(color=0xffae00)
    name = "Burger List"
    text = ""
    text_end = f" From item **{current_view_bb + 1}**/**{len(burgers)+1}**"
    number_of_letters = len(text_end)

    if len(burgers) != 0:
      items_flipped_amount = 0
      last_burger_rarity = ""
      while number_of_letters < 1024:
        if current_view_bb >= len(burgers):
          break

        burger_text = ""

        burger_id = burgers[current_view_bb].id
        burger_name = burgers[current_view_bb].name
        burger_rarity = burgers[current_view_bb].rarity

        if last_burger_rarity != burger_rarity:
          burger_text += f"\n**{burger_rarity}** burgers:\n"
          last_burger_rarity = burger_rarity
        burger_text += f"~ID:**{burger_id}** |NAME:**{burger_name}**\n"

        if number_of_letters + len(burger_text) < 1024:
          current_view_bb += 1
          items_flipped_amount += 1
          text += burger_text
          number_of_letters += len(burger_text)
        else:
          break
      if current_view_bb not in items_flipped_bb:
        items_flipped_bb[current_view_bb] = items_flipped_amount
    else:
      text += "This collection is ***empty!***"

    text += text_end
    embed.add_field(name=name, value=text, inline=False)
    return embed

  async def backwards(interaction):
    global current_view_bb
    global items_flipped_bb
    await interaction.response.defer()

    if current_view_bb in items_flipped_bb:
      current_view_bb -= items_flipped_bb[current_view_bb]
      if current_view_bb in items_flipped_bb:
        current_view_bb -= items_flipped_bb[current_view_bb]
      else:
        current_view_bb = 0
    else:
      current_view_bb = 0
    await message.edit(embed=await generate_embed(burgers))

  async def forwards(interaction):
    await interaction.response.defer()
    await message.edit(embed=await generate_embed(burgers))

  button_backwards = Button(style=discord.ButtonStyle.green, emoji="⬅")
  button_forwards = Button(style=discord.ButtonStyle.green, emoji="➡")

  button_backwards.callback = backwards
  button_forwards.callback = forwards

  view = View()
  view.add_item(button_backwards)
  view.add_item(button_forwards)

  em = await generate_embed(burgers)
  message = await ctx.reply(embed=em, view=view)


@client.command(aliases=["rr"])
async def rarities(ctx):
  if not await is_administrator(ctx, ctx.message.author.id):
    return False
  view = View()
  em = discord.Embed(color=0xffae00)
  name = "Rarities List"
  text = ""

  for i in range(len(_rarity)):
    text += f"ID: **{i}** | NAME: ***{_rarity[i]}*** | PROBABILITY: **{round(_probabilities[i] * 100,4)}%**\n"

  em.add_field(name=name, value=text, inline=False)
  message = await ctx.reply(embed=em, view=view)


@client.command(aliases=["bi"])
async def BurgerInfo(ctx, burger_id: int):
  if not await is_administrator(ctx, ctx.message.author.id):
    return False
  view = View()
  em = em = discord.Embed(color=0xffae00)
  name = f"Burger Info for **{_burgers[burger_id].name}**"
  text = f"ID: **{burger_id}**\nRARITY: ***{_burgers[burger_id].rarity}***\nMods:\n"
  for mod in _burgers[burger_id].mods:
    text += f"   ~ **{mod}**\n"

  em.add_field(name=name, value=text, inline=False)
  message = await ctx.reply(embed=em, view=view)
  return True


@client.command(aliases=["mb"])
async def makeBurger(ctx, rarity: int, name):
  global _burgers
  if not await is_administrator(ctx, ctx.message.author.id):
    return False
  burger = Burger(rarity_check(rarity), name, len(_burgers))
  _burgers[len(_burgers)] = burger
  write_burgerstorage_data()
  _burgers = get_burgerstorage_data()
  await BurgerInfo(ctx, burger.id)
  return True


@client.command(aliases=["cc"])
async def creationCompanion(ctx):
  if ctx.message.author.id not in _admins_id:
    await ctx.reply("You do not have permission to use this command.")
    return False
  view = View()
  em = em = discord.Embed(color=0xffae00)
  name = f"***C**reation **C**ompanion*"
  text = f"I'm here to guide you in how to create your own splendid burger!\n"
  text += f"Let us start off by calling **$rr** (aka $rarities) to get a list of rarities to pick between!\n"
  text += f'Then let us simply call **$mb** *(Rarity ID)* *"name"*!\n'
  text += f'   *Here is an example, **$mb 4 "Awaburger"**\n\n'
  text += f"Let's create some mods for your new burger!\n"
  text += f"Mods are **single word** additions to your burger!\n"
  text += f"You can create **1** or **several** mods using the same command!\n"
  text += f"Simply call **$mbm** *(Burger ID) (mod1) (mod2)... so on\n"
  text += f"   *Here's an example, **$mbm 4 Hero Lazy Smart Fast***\n\n"
  text += f"The example would create 4 new mods for the burger with the ID=4.\n"
  text += f"The mods themselves would be, **Hero**, **Lazy**, **Smart** and **Fast**.\n"
  text += f"Remember that you can always check your burger using $bi (Burger ID)\n"
  text += f"This is all for now! "
  text += f"\n\n *Related Commands:* $mbm, $mb, $bi, $bb, $rr"

  em.add_field(name=name, value=text, inline=False)

  message = await ctx.reply(embed=em, view=view)
  Context = await client.get_context(message)
  await rarities(Context)
  await burgers(Context)


@client.command(aliases=["ab"])
async def backup(ctx):
  if not await is_administrator(ctx, ctx.message.author.id):
    return False
  createBackup()
  await ctx.reply("Backup Created!")


#
#
#
# HELPER FUNCTIONS !
async def is_administrator(ctx, user_id: discord.User.id):
  if user_id not in _admins_id:
    await ctx.reply("You do not have permission to use this command.")
    return False
  return True


async def register_user(user):
  if user.id in _users:
    return False
  else:
    _users[user.id] = User()
    write_userstorage_data()
  return True


async def rollBurger():
  roll = choice(_rarity, p=_probabilities)
  print(f"Roll: {roll}")
  burgerIndex = _burger_rarity[roll][random.randrange(
    0, len(_burger_rarity[roll]))]
  mods = []
  if random.randrange(1, 101) <= (5 * (1 + rarity_string_to_int(roll))):
    mods.append(str(random.randrange(0, len(_burgers[burgerIndex].mods))))
    if random.randrange(1, 101) <= (5 * (1 + rarity_string_to_int(roll))):
      mods.append(str(random.randrange(0, len(_burgers[burgerIndex].mods))))
      if random.randrange(1, 101) <= (5 * (1 + rarity_string_to_int(roll))):
        mods.append(str(random.randrange(0, len(_burgers[burgerIndex].mods))))
    mods = ("#".join(mods))
  else:
    mods = "Null"

  str_mods = str(mods)
  burger = [burgerIndex, str_mods]
  return burger


async def addBurger(ctx, burgerIndex: int, amount: int = 1, key="Null"):
  await register_user(ctx.author)
  #ADD TO _burgers !
  if key not in _burgers[burgerIndex].circulation.keys():
    #_burgers[burgerIndex].circulation[key] = {}
    _burgers[burgerIndex].circulation[key] = {ctx.author.id: amount}

  else:  #mod type already exists
    temp_amount = amount
    if ctx.author.id in _burgers[burgerIndex].circulation[key].keys():
      temp_amount += _burgers[burgerIndex].circulation[key][ctx.author.id]
    _burgers[burgerIndex].circulation[key][ctx.author.id] = temp_amount

  #ADD TO _users !
  if burgerIndex not in _users[ctx.author.id].burgers.keys():
    #_users[ctx.author.id].burgers[burgerIndex] = {}
    _users[ctx.author.id].burgers[burgerIndex] = {key: amount}
  else:
    if key not in _users[ctx.author.id].burgers[burgerIndex].keys():
      _users[ctx.author.id].burgers[burgerIndex][key] = amount
    else:
      _users[ctx.author.id].burgers[burgerIndex][key] += amount


def truncate(f, n):
  s = '{}'.format(f)
  if 'e' in s or 'E' in s:
    return '{0:.{1}f}'.format(f, n)
  i, p, d = s.partition('.')
  return '.'.join([i, (d + '0' * n)[:n]])


#
#
#
# RARITY HELPER
def rarity_string_to_int(input: str):
  index = 0
  for rarity in _rarity:
    if input == _rarity[index]:
      return index
    index += 1
  return 0


def rarity_int_to_string(input: int):
  return _rarity[input]


def rarity_check(input: int):
  return rarity_int_to_string(input)


#
#
#
# You can't read this!... >:)
client.run(os.getenv('EXTOKEN'))
