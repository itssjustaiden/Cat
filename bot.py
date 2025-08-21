import os
import time
import random
import threading
import asyncio
import datetime
import requests
import aiohttp
import discord
from discord.ext import tasks
from discord.ext import commands
from discord.ui import View, Button
from flask import Flask
from threading import Thread
import json

app = Flask('')

@app.route('/')
def home():
    return "Aiden was here"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run_flask).start()


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="$", intents=intents)
bot.remove_command("help")

kitty_active = False
Allowed_Users = [1343941910309634078, 1276629095077249077]
CAT_MESSAGES = ["meow", "zzz time", "purr", "hiss", "mraw"]
THREAD_ID = 1407466187377348750  
CARSH_CHANNEL_ID = [1400123331335688332, 1406641982033498183]
DATA_FILE = "carsh_data.json"
STEAL_FILE = "steal_data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_steal():
    if not os.path.exists(STEAL_FILE):
        return {}
    with open(STEAL_FILE, "r") as f:
        return json.load(f)

def save_steal(data):
    with open(STEAL_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_balance(user_id):
    return load_data().get(str(user_id), 0)

def set_balance(user_id, amount):
    data = load_data()
    data[str(user_id)] = amount
    save_data(data)

def change_balance(user_id, amount):
    bal = get_balance(user_id) + amount
    set_balance(user_id, max(bal,0))
    return bal

def has_luckycoin(user_id):
    return active_effects["luckycoin"].get(user_id,0) > int(time.time())
    
def channel_check(ctx):
    return ctx.channel.id in CARSH_CHANNEL_ID

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    spam_cats.start()















@bot.command()
async def slots(ctx,amount:int):
 if not channel_check(ctx):
  return
 if amount<=0:
  await ctx.send("bet a real amount pls")
  return
 bal=get_balance(ctx.author.id)
 if bal<amount:
  await ctx.send("u broke cuh, get sum Carsh")
  return

 symbols=["🍒","🍊","🍎","🍇","💎"]
 weights=[50,44,10,5,1]
 payouts={"🍒":2,"🍊":5,"🍎":10,"🍇":25,"💎":50}

 if has_luckycoin(ctx.author.id):
  weights=[int(w*1.25) for w in weights]  # 25% boost

 spin=random.choices(symbols,weights=weights,k=3)
 result=" | ".join(spin)
 payout=0
 if spin[0]==spin[1]==spin[2]:
  payout=amount*payouts.get(spin[0],0)

 change_balance(ctx.author.id,-amount)
 if payout>0:
  change_balance(ctx.author.id,payout)
  await ctx.send(f"You rolled {result} 🎰 and WON {payout} Carsh")
 else:
  await ctx.send(f"You rolled {result} 🎰 and LOST {amount} Carsh")


@bot.command()
async def total(ctx, user: discord.Member = None):
    if not channel_check(ctx):
        return
    user = user or ctx.author
    bal = get_balance(user.id)
    await ctx.send(f"{user.name} has {bal} Carsh")

@bot.command()
async def gamble(ctx,amount:int):
 if not channel_check(ctx):
  return
 if amount<=0 or get_balance(ctx.author.id)<amount:
  await ctx.send("invalid amount or not enough Carsh")
  return

 base_chance=0.5
 if has_luckycoin(ctx.author.id):
  base_chance+=0.25  # 25% boost

 win=random.random() < base_chance

 if win:
  change_balance(ctx.author.id,amount)
  await ctx.send(f"{ctx.author.mention} won +{amount} Carsh")
 else:
  change_balance(ctx.author.id,-amount)
  await ctx.send(f"{ctx.author.mention} lost -{amount} Carsh")

@bot.command()
async def plinko(ctx,amount:int):
 if not channel_check(ctx):
  return
 if amount<=0 or get_balance(ctx.author.id)<amount:
  await ctx.send("invalid amount or not enough Carsh")
  return

 board_template=["100","50","10","5","2","0.7","0.5","0.2","0.5","0.7","2","5","10","50","100"]
 weights=[0.5,2,10,20,30,50,60,80,60,50,30,20,10,2,0.5]

 if has_luckycoin(ctx.author.id):
  weights=[w*1.25 for w in weights]  # 25% boost

 ball_index=random.choices(range(len(board_template)),weights=weights,k=1)[0]
 visual=" | ".join(f"[{slot}]" if idx==ball_index else slot for idx,slot in enumerate(board_template))
 multi=float(board_template[ball_index])
 winnings=int(amount*multi)
 change_balance(ctx.author.id,-amount)
 change_balance(ctx.author.id,winnings)

 await ctx.send(f"{ctx.author.mention} played Plinko with {amount} Carsh\nFinal board:\n{visual}\nYou got {winnings} Carsh (x{multi})")


@bot.command()
async def give(ctx, member: discord.Member, amount: int):
    if amount <= 0:
        await ctx.send("invalid amount")
        return

    if get_balance(ctx.author.id) < amount:
        await ctx.send("u broke cuh 😬")
        return

    embed = discord.Embed(
        title="Confirm",
        description=f"Send {amount} to {member.name}?",
        color=discord.Color.purple()
    )

    class GiveView(View):
        def __init__(self):
            super().__init__(timeout=500)

        @discord.ui.button(label="✅", style=discord.ButtonStyle.success)
        async def confirm(self, interaction: discord.Interaction, button: Button):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message("not ur button smh", ephemeral=True)
                return
            change_balance(ctx.author.id, -amount)
            change_balance(member.id, amount)
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Sent!",
                    description=f"{amount} Carsh sent to {member.name}",
                    color=discord.Color.green()
                ),
                view=None
            )

        @discord.ui.button(label="❌", style=discord.ButtonStyle.danger)
        async def cancel(self, interaction: discord.Interaction, button: Button):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message("not ur button smh", ephemeral=True)
                return
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Cancelled",
                    description=f"Transfer cancelled",
                    color=discord.Color.red()
                ),
                view=None
            )

    await ctx.send(embed=embed, view=GiveView())
    
@bot.command()
async def steal(ctx):
    if not channel_check(ctx):
        return
    user_id = str(ctx.author.id)
    steal_data = load_steal()
    now = int(time.time())
    last = steal_data.get(user_id,0)
    if now - last < 86400:
        remaining = 86400 - (now-last)
        hrs = remaining//3600
        mins = (remaining%3600)//60
        secs = remaining%60
        await ctx.send(f"Steal available in {hrs}h {mins}m {secs}s")
        return
    amount = random.randint(5,20)

    # check for doublesteal effect
    if user_id in active_effects["doublesteal"]:
        effect_end = active_effects["doublesteal"][user_id]
        if now < effect_end:
            amount *= 2

    change_balance(ctx.author.id, amount)
    steal_data[user_id] = now
    save_steal(steal_data)
    await ctx.send(f"{ctx.author.mention} stole {amount} Carsh from the bank!")


@bot.command()
async def lboard(ctx):
    if not channel_check(ctx):
        return
    data = load_data()
    if not data:
        await ctx.send("No one has Carsh yet")
        return
    sorted_data = sorted(data.items(), key=lambda x:x[1], reverse=True)
    embed = discord.Embed(title="Carsh Leaderboard", color=discord.Color.purple())
    for i,(uid,bal) in enumerate(sorted_data[:10], start=1):
        user = ctx.guild.get_member(int(uid))
        name = user.name if user else f"User {uid}"
        embed.add_field(name=f"{i}. {name}", value=f"{bal} Carsh", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def ask(ctx, user: discord.Member, amount: int):
    if not channel_check(ctx):
        return
    if user.id==ctx.author.id or amount<=0:
        await ctx.send("invalid request")
        return
    if get_balance(user.id) < amount:
        await ctx.send(f"{user.mention} does not have enough Carsh")
        return
    embed = discord.Embed(title="Someone is asking for Carsh", description=f"{ctx.author.mention} is asking {user.mention} for {amount} Carsh", color=discord.Color.purple())
    class AskView(View):
        def __init__(self):
            super().__init__(timeout=500)
        @discord.ui.button(label="✅", style=discord.ButtonStyle.success)
        async def give(self, interaction: discord.Interaction, button: Button):
            if interaction.user.id!=user.id:
                await interaction.response.send_message("not your button", ephemeral=True)
                return
            change_balance(user.id, -amount)
            change_balance(ctx.author.id, amount)
            await interaction.response.edit_message(embed=discord.Embed(title="Transfer Complete", description=f"{user.mention} gave {ctx.author.mention} {amount} Carsh", color=discord.Color.green()), view=None)
        @discord.ui.button(label="❌", style=discord.ButtonStyle.danger)
        async def decline(self, interaction: discord.Interaction, button: Button):
            if interaction.user.id!=user.id:
                await interaction.response.send_message("not your button", ephemeral=True)
                return
            await interaction.response.edit_message(embed=discord.Embed(title="Request Declined", description=f"{user.mention} declined {ctx.author.mention}'s request", color=discord.Color.red()), view=None)
    await ctx.send(embed=embed, view=AskView())




@bot.command()
async def GiveM(ctx, user: str, amount: int):
    if ctx.author.id not in Allowed_Users:
        await ctx.send("not allowed")
        return

    if user.lower() in ["@everyone", "@here"]:
        for member in ctx.guild.members:
            if not member.bot:
                change_balance(member.id, amount)
        await ctx.send(f"Gave {amount} Carsh to everyone!")
        return

    member = ctx.guild.get_member(int(user.strip("<@!>")))
    if not member:
        await ctx.send("user not found")
        return
    change_balance(member.id, amount)
    await ctx.send(f"Gave {member.mention} {amount} Carsh")
@bot.command()
async def TakeM(ctx, user: str, amount: int):
    if ctx.author.id not in Allowed_Users:
        await ctx.send("not allowed")
        return

    if user.lower() in ["@everyone", "@here"]:
        for member in ctx.guild.members:
            if not member.bot:
                change_balance(member.id, -amount)
        await ctx.send(f"Took {amount} Carsh from everyone!")
        return

    member = ctx.guild.get_member(int(user.strip("<@!>")))
    if not member:
        await ctx.send("user not found")
        return
    change_balance(member.id, -amount)
    await ctx.send(f"Took {amount} Carsh from {member.mention}")
@tasks.loop(minutes=2)
async def spam_cats():
    thread = await bot.fetch_channel(THREAD_ID)
    await thread.send(random.choice(CAT_MESSAGES))


help_pages = []

embed1 = discord.Embed(title="MEOW - Page 1", description="all commands:", color=discord.Color.purple())
embed1.add_field(name="$ping", value="check if bot is alive", inline=False)
embed1.add_field(name="$getpfp [@user]", value="get a user's profile picture", inline=False)
embed1.add_field(name="$kick @user [reason]", value="kick a user", inline=False)
embed1.add_field(name="$timeout @user <duration> [reason]", value="timeout user (s/m/h/d/w)", inline=False)
embed1.add_field(name="$untimeout @user", value="remove a user's timeout", inline=False)
embed1.add_field(name="$purge <count>", value="delete 1–100 messages", inline=False)
embed1.add_field(name="$purgeuser <user> <count>", value="delete last 1–100 messages from a specific user", inline=False)
embed1.add_field(name="$Gambling1", value="you MIGHT get timeout from this", inline=False)
embed1.add_field(name="$help", value="show this embed", inline=False)
help_pages.append(embed1)

embed2 = discord.Embed(title="MEOW - Page 2", description="more commands:", color=discord.Color.purple())
embed2.add_field(name="$joke", value="gets a random joke", inline=False)
embed2.add_field(name="$ship <user1> <user2>", value="ships user and user!", inline=False)
embed2.add_field(name="$ToD", value="play truth or dare", inline=False)
embed2.add_field(name="$compliment <user>", value="compliment someone", inline=False)
embed2.add_field(name="$catfact", value="gives you a random cat fact", inline=False)
embed2.add_field(name="$eightball <question>", value="eight ball", inline=False)
embed2.add_field(name="$helpcarsh", value="you can GAMBLE even more!", inline=False)
help_pages.append(embed2)

class HelpView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.current_page = 0

    async def update_message(self, interaction):
        total_pages = len(help_pages)
        self.prev_button.label = f"◀️ {self.current_page + 1}/{total_pages}"
        self.next_button.label = f"{self.current_page + 1}/{total_pages} ▶️"
        await interaction.response.edit_message(embed=help_pages[self.current_page], view=self)

    @discord.ui.button(label="◀️ 1/2", style=discord.ButtonStyle.primary)
    async def prev_button(self, interaction: discord.Interaction, button: Button):
        self.current_page = (self.current_page - 1) % len(help_pages)
        await self.update_message(interaction)

    @discord.ui.button(label="1/2▶️", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: Button):
        self.current_page = (self.current_page + 1) % len(help_pages)
        await self.update_message(interaction)



@bot.command()
async def help(ctx):
    view = HelpView()
    await ctx.send(embed=help_pages[0], view=view)

@bot.command()
async def ping(ctx):
    await ctx.send("pong")

@bot.command()
async def getpfp(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(f"{member.name}'s profile picture:")
    await ctx.send(member.avatar.url)

@bot.command()
async def Gambling1(ctx):
    outcome = random.choice(["Lucky", "Unlucky"])
    if outcome == "Lucky":
        embed = discord.Embed(title="Good job!", description="You're lucky...", color=discord.Color.green())
        await ctx.send(embed=embed)
    else:
        try:
            timeout_until = discord.utils.utcnow() + datetime.timedelta(seconds=90)
            await ctx.author.timeout(timeout_until, reason="Never gamble again")
            await ctx.send(f"{ctx.author.name}, you got unlucky!")
        except discord.Forbidden:
            await ctx.send("I cannot timeout you, you're lucky.")

@bot.command()
async def joke(ctx):
    url = "https://v2.jokeapi.dev/joke/Any?blacklistFlags=nsfw,racist,sexist,explicit"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
        if data.get("type") == "single":
            await ctx.send(data.get("joke", "¯\\_(ツ)_/¯"))
        elif data.get("type") == "twopart":
            await ctx.send(data.get("setup", "") + "\n…\n" + data.get("delivery", ""))
        else:
            await ctx.send("hmm something went wrong fetching a joke.")
    except:
        await ctx.send("can't get a joke rn, try again later.")

@bot.command()
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    if ctx.author.guild_permissions.kick_members:
        try:
            await member.kick(reason=reason)
            await ctx.send(f"{member.name} has been kicked. (Reason: {reason})")
        except:
            await ctx.send("I cannot kick this member.")
    else:
        await ctx.send("You don't have permission to kick members.")

@bot.command()
async def timeout(ctx, member: discord.Member, duration: str, *, reason="No reason provided"):
    if not ctx.author.guild_permissions.moderate_members:
        await ctx.send("You don't have permission to timeout members.")
        return
    time_units = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
    if len(duration) < 2:
        await ctx.send("Invalid duration format. Use like 1d, 5h, 30m")
        return
    unit = duration[-1].lower()
    if unit not in time_units:
        await ctx.send("Invalid time unit. Use s/m/h/d/w")
        return
    try:
        time_amount = int(duration[:-1])
    except ValueError:
        await ctx.send("Invalid duration number.")
        return
    timeout_seconds = time_amount * time_units[unit]
    if timeout_seconds > 2419200:
        await ctx.send("Timeout duration cannot exceed 28 days.")
        return
    timeout_until = discord.utils.utcnow() + datetime.timedelta(seconds=timeout_seconds)
    try:
        await member.timeout(timeout_until, reason=reason)
        await ctx.send(f"{member.name} has been timed out for {duration}. (Reason: {reason})")
    except discord.Forbidden:
        await ctx.send("I cannot timeout this member.")
    except Exception as e:
        await ctx.send(f"An unexpected error occurred: {str(e)}")

@bot.command()
async def untimeout(ctx, member: discord.Member):
    if not ctx.author.guild_permissions.moderate_members:
        await ctx.send("You don't have permission to remove timeouts.")
        return
    try:
        await member.timeout(None)
        await ctx.send(f"{member.name} has been un-timed out.")
    except:
        await ctx.send("I cannot untimeout this member.")

@bot.command()
async def purge(ctx, count: int):
    if not ctx.author.guild_permissions.manage_messages:
        await ctx.send("You don't have permission to delete messages.")
        return
    count = max(1, min(100, count))
    await ctx.message.delete()
    deleted = await ctx.channel.purge(limit=count)
    confirmation = await ctx.send(f"Deleted {len(deleted)} messages.")
    await asyncio.sleep(5)
    await confirmation.delete()

@bot.command()
async def purgeuser(ctx, member: discord.Member, count: int):
    if not ctx.author.guild_permissions.manage_messages:
        await ctx.send("You don't have permission to delete messages.")
        return
    count = max(1, min(100, count))
    await ctx.message.delete()
    deleted = 0
    async for msg in ctx.channel.history(limit=200):
        if msg.author == member and deleted < count:
            await msg.delete()
            deleted += 1
        if deleted >= count:
            break
    await ctx.send(f"Deleted {deleted} messages from {member.name}.")
@bot.command()
async def PERISH(ctx):
    if str(ctx.author.id) == "1276629095077249077":
        await ctx.send("https://tenor.com/view/disintegrating-aughhh-gif-24532719")
        await bot.close()
        exit()
    else:
        await ctx.send("fuck you")

@bot.command()
async def activatekitty(ctx):
    global kitty_active
    if ctx.author.id not in Allowed_Users:
        await ctx.send("Access denied.")
        return
    kitty_active = not kitty_active
    state = "enabled" if kitty_active else "disabled"
    await ctx.send(f"kitty is now {state}.")


perfect_matches = [("aiden", "kiara"), ("brokenspawn", "limegirl"), ("aiden", "kia")]

@bot.command()
async def ship(ctx, user1: str, user2: str):
    name1 = user1.strip()
    name2 = user2.strip()
    half1 = name1[:len(name1)//2]
    half2 = name2[len(name2)//2:]
    ship_name = half1 + half2
    matched = any((name1.lower() == p1 and name2.lower() == p2) or (name1.lower() == p2 and name2.lower() == p1) for p1, p2 in perfect_matches)
    compatibility = 100 if matched else random.randint(0, 100)
    bar_length = 10
    filled_length = round(bar_length * compatibility / 100)
    empty_length = bar_length - filled_length
    love_bar = "💖" * filled_length + "🖤" * empty_length
    embed = discord.Embed(title=f"💘 {name1} x {name2}", description=f"**Ship Name:** {ship_name}\n**Compatibility:** {compatibility}%\n{love_bar}", color=discord.Color.purple())
    await ctx.send(embed=embed)

@bot.command()
async def AdminAbuse(ctx):
    if ctx.author.id not in Allowed_Users:
        await ctx.send("You’re not allowed to use this command.")
        return
    embed_admin = discord.Embed(title="⚡ Admin/Troll Commands", description="commands for trolling with cat:3", color=discord.Color.purple())
    embed_admin.add_field(name="$sendmsg <channel> <message>", value="sends a message via bot", inline=False)
    embed_admin.add_field(name="$reactmsg <channel> <emojiname>", value="reacts to last message in the channel with emoji (lowercase)", inline=False)
    embed_admin.add_field(name="$ghostping <user>", value="pings an user then deletes the message", inline=False)
    embed_admin.add_field(name="$reversemsg <channel>", value="reverses the last message example: Hello --> olleH", inline=False)
    await ctx.send(embed=embed_admin)

@bot.command()
async def sendmsg(ctx, channel: discord.TextChannel, *, msg: str):
    if ctx.author.id not in Allowed_Users:
        await ctx.send("access denied.")
        return
    await ctx.message.delete()
    await channel.send(msg)
    conf_msg = await ctx.send(f"sent message in {channel.mention}")
    await asyncio.sleep(1.5)
    await conf_msg.delete()

@bot.command()
async def reactmsg(ctx, channel: discord.TextChannel, emoji_name: str):
    if ctx.author.id not in Allowed_Users:
        await ctx.send("Access denied.")
        return
    try:
        async for last_msg in channel.history(limit=1):
            emoji = discord.utils.get(ctx.guild.emojis, name=emoji_name)
            if not emoji:
                emoji = emoji_name
            await last_msg.add_reaction(emoji)
            msg = await ctx.send(f"Reacted with `{emoji_name}` in {channel.mention}")
            await asyncio.sleep(1.5)
            await msg.delete()
            await ctx.message.delete()
            break
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command()
async def reversemsg(ctx, channel: discord.TextChannel):
    if ctx.author.id not in Allowed_Users:
        await ctx.send("Access denied.")
        return
    try:
        async for last_msg in channel.history(limit=1):
            reversed_content = last_msg.content[::-1]
            await channel.send(reversed_content)
            msg = await ctx.send(f"Reversed the last message in {channel.mention}")
            await asyncio.sleep(1.5)
            await msg.delete()
            await ctx.message.delete()
            break
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command()
async def ghostping(ctx, member: discord.Member, channel: discord.TextChannel = None):
    if ctx.author.id not in Allowed_Users:
        return await ctx.send("Access denied.")
    channel = channel or ctx.channel
    msg = await channel.send((member.mention + " ") * 5)
    await ctx.message.delete()
    await asyncio.sleep(1)
    await msg.delete()
truth_list = []
used_truth = []

dare_list = []
used_dare = []

async def fetch_list(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            text = await resp.text()
            return text.splitlines()

async def get_random_item(lst, used_lst, url):
    if not lst:
        lst.extend(await fetch_list(url))
    available = [i for i in range(len(lst)) if i not in used_lst]
    if not available:
        used_lst.clear()
        available = list(range(len(lst)))
    choice = random.choice(available)
    used_lst.append(choice)
    return lst[choice]

class ToDView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Truth", style=discord.ButtonStyle.primary)
    async def truth_button(self, interaction: discord.Interaction, button: Button):
        text = await get_random_item(truth_list, used_truth, "https://raw.githubusercontent.com/itssjustaiden/SomethingThatsNotCheats/main/Truth.txt")
        embed = interaction.message.embeds[0]
        embed.description = f"**Truth:** {text}"
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="Dare", style=discord.ButtonStyle.primary)
    async def dare_button(self, interaction: discord.Interaction, button: Button):
        text = await get_random_item(dare_list, used_dare, "https://raw.githubusercontent.com/itssjustaiden/SomethingThatsNotCheats/main/Dare.txt")
        embed = interaction.message.embeds[0]
        embed.description = f"**Dare:** {text}"
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger)
    async def stop_button(self, interaction: discord.Interaction, button: Button):
        await interaction.message.delete()
@bot.command()
async def compliment(ctx, member: discord.Member = None):
    member = member or ctx.author
    url = "https://raw.githubusercontent.com/itssjustaiden/SomethingThatsNotCheats/main/Compliments.txt"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                text = await resp.text()
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        if not lines:
            await ctx.send("no compliments available")
            return
        choice = random.choice(lines)
        await ctx.send(f"{member.mention}, {choice}")
    except:
        await ctx.send("can't fetch, try again later.")

@bot.command()
async def ToD(ctx):
    embed = discord.Embed(title="Truth or Dare", description="Choose an option below!", color=discord.Color.purple())
    view = ToDView()
    await ctx.send(embed=embed, view=view)
@bot.command()
async def catfact(ctx):
    url = "https://raw.githubusercontent.com/itssjustaiden/SomethingThatsNotCheats/main/CarFacts.txt"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                text = await resp.text()
                facts = text.splitlines()
                fact = random.choice(facts)
                await ctx.send(f"{fact}")
            else:
                await ctx.send("couldn’t fetch cat facts")

random_string = 1407381269188313099

@bot.event
async def on_message_delete(message):
    if message.author.bot or not message.guild:
        return

    log_channel = bot.get_channel(random_string)
    if log_channel is None:
        return

    deletedEMBED = discord.Embed(
        title="🗑️",
        color=discord.Color.red()
    )
    deletedEMBED.add_field(name="author", value=str(message.author), inline=False)
    deletedEMBED.add_field(name="channel", value=message.channel.mention, inline=False)
    deletedEMBED.add_field(
        name="content",
        value=message.content if message.content else "*no text*",
        inline=False
    )
    if message.attachments:
        urls = "\n".join([a.url for a in message.attachments])
        deletedEMBED.add_field(name="attachments", value=urls, inline=False)

    deletedEMBED.set_footer(text=f"message id: {message.id}")
    await log_channel.send(embed=deletedEMBED)


@bot.event
async def on_message_edit(before, after):
    if before.author.bot or not before.guild:
        return
    if before.content == after.content:
        return

    log_channel = bot.get_channel(random_string)
    if log_channel is None:
        return

    editedEMBED = discord.Embed(
        title="✏️",
        color=discord.Color.orange()
    )
    editedEMBED.add_field(name="author", value=str(before.author), inline=False)
    editedEMBED.add_field(name="channel", value=before.channel.mention, inline=False)
    editedEMBED.add_field(name="before", value=before.content or "*no text*", inline=False)
    editedEMBED.add_field(name="after", value=after.content or "*no text*", inline=False)
    editedEMBED.set_footer(text=f"message id: {before.id}")
    await log_channel.send(embed=editedEMBED)

@bot.command()
async def eightball(ctx, *, question: str):
    responses = [
        "fr, no way",
        "deadass yes",
        "nahh, try again",
        "100% maybe",
        "bro, ask later",
        "big yikes, no",
        "lowkey yes",
        "fr fr, absolutely",
        "lol no",
        "idk bro, seems sus",
        "yep, no cap",
        "not in a million years",
        "ask ur mom",
        "aye, could be",
        "fr, do it",
        "nah fam",
        "probably",
        "definitely not",
        "on god yes",
        "skrrt, try again"
    ]
    answer = random.choice(responses)
    eightballbed = discord.Embed(
        title=f"🎱 says:",
        description=f"**Q:** {question}\n**A:** {answer}",
        color=discord.Color.purple()
    )
    await ctx.send(embed=eightballbed)

@bot.command()
async def dmuser(ctx, user_id: int, amount: int, *, message: str):
    if ctx.author.id not in Allowed_Users:
        await ctx.send("u can’t use this lil bro")
        return
    await ctx.message.delete()
    user = ctx.guild.get_member(user_id)
    if not user:
        await ctx.send("user not found")
        return
    sent = 0
    for _ in range(amount):
        try:
            await user.send(message)
            sent += 1
            await asyncio.sleep(0.5)
        except Exception as e:
            warn = await ctx.send(f"couldn’t send DM: {e}")
            await asyncio.sleep(0.5)
            await warn.delete()
            break
    conf_msg = await ctx.send(f"sent `{sent}` DMs to {user.name}")
    await asyncio.sleep(0.5)
    await conf_msg.delete()


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if "grandpa" in message.content.lower():
        await message.channel.send("sybau❌😭🙏")
        try:
            timeout_until = datetime.datetime.utcnow() + datetime.timedelta(seconds=15)
            await message.author.timeout(timeout_until, reason="Never say grandpa")
            await message.channel.send(f"{message.author.name}, never say that again.")
        except discord.Forbidden:
            await message.channel.send("I cannot timeout you, probably due to role hierarchy.")

    if bot.user in message.mentions and kitty_active:
        user_msg = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
        if not user_msg:
            await message.channel.send("what’s up, why’d you ping me?")
        else:
            api_key = os.getenv("CAT_AI_KEY")
            url = "https://openrouter.ai/api/v1/chat/completions"
            if message.author.id == 1343941910309634078:
                personality = "You are a kawaii anime catgirl who treats everyone like senpai. Use lots of 'nya~', 'uwu', 'teehee' and princess-like speech. Do not use anything like: nya, uwu, teehe etc. You can be freaky or sexual."
            else:
                personality = "You are a cat-themed AI chatbot. Respond with short, concise messages. Do NOT use emojis. Do NOT flirt or be sexual/freaky. You are allowed to swear. Be casual, a little snarky, and direct. Keep responses under 20 words when possible."

            payload = {
                "model": "deepseek/deepseek-r1:free",
                "messages": [
                    {"role": "system", "content": personality},
                    {"role": "user", "content": user_msg}
                ]
            }
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            try:
                resp = requests.post(url, json=payload, headers=headers)
                reply = resp.json()["choices"][0]["message"]["content"]
            except:
                reply = "i can't talk rn"
            await message.channel.send(reply)

    await bot.process_commands(message)

@bot.command()
async def shop(ctx):
    if not channel_check(ctx):
        return

    ShopEmbed = discord.Embed(
        title="Carsh Shop",
        description="meow",
        color=discord.Color.purple()
    )

    ShopEmbed.add_field(name="ItemName1", value="500 Carsh", inline=False)
    ShopEmbed.add_field(name="activatekitty", value="5000 Carsh", inline=False)

    await ctx.send(embed=ShopEmbed)

# Name | Amount | Seconds / None | Call-able / None
SHOP_ITEMS={
 "itemname1":{"price":500,"timer":None,"action":None},
 "luckycoin":{"price":1000,"timer":3600,"action":"luckycoin"},
 "doublesteal":{"price":2500,"timer":43200,"action":"doublesteal"},
 "activatekitty":{"price":5000,"timer":600,"action":"kitty"},
}

active_effects={"luckycoin":{},"doublesteal":{}}

@bot.command()
async def buy(ctx,*,item_name:str):
 item_name=item_name.lower()
 if item_name not in SHOP_ITEMS:
  await ctx.send("item not found")
  return

 item=SHOP_ITEMS[item_name]
 price=item["price"]
 if get_balance(ctx.author.id)<price:
  await ctx.send("You broke cuh get sum Carsh")
  return

 change_balance(ctx.author.id,-price)
 action=item["action"]
 timer=item["timer"]

 if action=="kitty":
  global kitty_active
  kitty_active=True
  await ctx.send(f"{ctx.author.mention} activated kitty mode for {timer//60} minutes")

  async def deactivate_kitty():
   await asyncio.sleep(timer)
   global kitty_active
   kitty_active=False
   await ctx.send("kitty has expired.")

  asyncio.create_task(deactivate_kitty())

 elif action=="luckycoin":
  active_effects["luckycoin"][ctx.author.id]=int(time.time())+timer
  await ctx.send(f"{ctx.author.mention} bought LuckyCoin! +10% chance in gambling for 1 hour.")

 elif action=="doublesteal":
  active_effects["doublesteal"][ctx.author.id]=int(time.time())+timer
  await ctx.send(f"{ctx.author.mention} bought DoubleSteal! Steal bonus active for 12 hours.")

 else:
  await ctx.send(f"{ctx.author.mention} bought **{item_name.title()}** for {price} Carsh")




@bot.command()
async def helpcarsh(ctx):
    if not channel_check(ctx):
        return

    CarshEmbed = discord.Embed(
        title="Carsh Commands",
        description="im losing my sanity",
        color=discord.Color.purple()
    )

    CarshEmbed.add_field(
        name="Main",
        value=(
            "`$total` → shows ur current carsh balance\n"
            "`$ask <user> <amount>` → ask someone for carsh\n"
            "`$steal` → get money if u got 0\n"
            "`$give <user> <amount>` → give someone carsh\n"
            "`$lboard` → check the leaderboard\n"
            "`$shop` → buy/activate things\n"
            "`$buy <itemname>` → buy things or activate things (temporary)"
        ),
        inline=False
    )

    CarshEmbed.add_field(
        name="Games",
        value=(
            "`$gamble <amount>` → 50/50 chance to win or lose\n"
            "`$plinko <amount>` → try ur luck w/ plinko\n"
            "`$slots <amount>` → spin da slot machine"
        ),
        inline=False
    )

    await ctx.send(embed=CarshEmbed)



# ---- Meow! ---- #
token = os.getenv("BOT_TOKEN")
if not token:
    raise ValueError("BOT_TOKEN not set")

bot.run(token)
