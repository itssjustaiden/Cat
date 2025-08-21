import os
import time
import random
import threading
import asyncio
import datetime
import requests
import aiohttp
import discord
from discord.ext import tasks, commands
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
CARSH_CHANNEL_ID = [1400123331335688332, 1406641982033498183]
DATA_FILE = "carsh_data.json"
STEAL_FILE = "steal_data.json"

SHOP_ITEMS = {
    "itemname1": {"price": 500, "timer": None, "action": None},
    "luckycoin": {"price": 1000, "timer": 3600, "action": "luckycoin"},
    "doublesteal": {"price": 2500, "timer": 43200, "action": "doublesteal"},
    "activatekitty": {"price": 5000, "timer": 600, "action": "kitty"},
}

active_effects = {"luckycoin": {}, "doublesteal": {}}

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
    set_balance(user_id, max(bal, 0))
    return bal

def has_luckycoin(user_id):
    return active_effects["luckycoin"].get(user_id, 0) > int(time.time())

def channel_check(ctx):
    return ctx.channel.id in CARSH_CHANNEL_ID

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
    ShopEmbed = discord.Embed(title="Carsh Shop", description="meow", color=discord.Color.purple())
    for item_name, item_info in SHOP_ITEMS.items():
        ShopEmbed.add_field(name=item_name, value=f"{item_info['price']} Carsh", inline=False)
    await ctx.send(embed=ShopEmbed)

@bot.command()
async def buy(ctx, *, item_name: str):
    item_name = item_name.lower()
    if item_name not in SHOP_ITEMS:
        await ctx.send("item not found")
        return
    item = SHOP_ITEMS[item_name]
    price = item["price"]
    if get_balance(ctx.author.id) < price:
        await ctx.send("You broke cuh get sum Carsh")
        return
    change_balance(ctx.author.id, -price)
    action = item["action"]
    timer = item["timer"]

    if action == "kitty":
        global kitty_active
        kitty_active = True
        await ctx.send(f"{ctx.author.mention} activated kitty mode for {timer//60} minutes")
        async def deactivate_kitty():
            await asyncio.sleep(timer)
            global kitty_active
            kitty_active = False
            await ctx.send("kitty has expired.")
        asyncio.create_task(deactivate_kitty())

    elif action == "luckycoin":
        active_effects["luckycoin"][ctx.author.id] = int(time.time()) + timer
        await ctx.send(f"{ctx.author.mention} bought LuckyCoin! +10% chance in gambling for 1 hour.")

    elif action == "doublesteal":
        active_effects["doublesteal"][ctx.author.id] = int(time.time()) + timer
        await ctx.send(f"{ctx.author.mention} bought DoubleSteal! Steal bonus active for 12 hours.")

    else:
        await ctx.send(f"{ctx.author.mention} bought **{item_name.title()}** for {price} Carsh")

@bot.command()
async def helpcarsh(ctx):
    if not channel_check(ctx):
        return
    CarshEmbed = discord.Embed(title="Carsh Commands", description="im losing my sanity", color=discord.Color.purple())
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

token = os.getenv("BOT_TOKEN")
if not token:
    raise ValueError("BOT_TOKEN not set")

bot.run(token)
