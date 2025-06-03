import discord
from discord.ext import commands
import os
import json
from dotenv import load_dotenv
from utils import load_data, save_data

load_dotenv()
TOKEN = os.getenv("TOKEN")
MOD_ID = int(os.getenv("MOD_ID"))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")

@bot.command()
async def تحويل(ctx, المبلغ: int):
    if ctx.author.bot:
        return

    if ctx.channel.id != MOD_ID:
        await ctx.send("❌ لازم تحول للكاشير الصحيح.")
        return

    data = load_data()
    user_id = str(ctx.author.id)

    # سجل التحويل
    data["transactions"].append({
        "type": "تحويل",
        "user": user_id,
        "amount": المبلغ
    })

    # أضف كوينز
    data["users"].setdefault(user_id, 0)
    data["users"][user_id] += المبلغ

    save_data(data)
    await ctx.send(f"✅ تم تحويل {المبلغ} كريدت، وأضيفت لك كوينز بنفس القيمة.")

@bot.command()
async def رصيدي(ctx):
    data = load_data()
    coins = data["users"].get(str(ctx.author.id), 0)
    await ctx.send(f"💰 رصيدك الحالي: {coins} كوينز.")

@bot.command()
@commands.has_role("admin")
async def رجع(ctx, عضو: discord.Member, مبلغ: int):
    data = load_data()
    user_id = str(عضو.id)
    data["users"].setdefault(user_id, 0)
    data["users"][user_id] += مبلغ

    data["transactions"].append({
        "type": "استرجاع",
        "user": user_id,
        "amount": مبلغ
    })

    save_data(data)
    await ctx.send(f"🔁 تم استرجاع {مبلغ} كوينز لـ {عضو.mention}.")

@bot.command()
async def سجل(ctx):
    data = load_data()
    user_id = str(ctx.author.id)
    trans = [t for t in data["transactions"] if t["user"] == user_id]
    if not trans:
        await ctx.send("📭 ما عندك أي تحويلات.")
        return

    msg = "\n".join([f"{t['type']} - {t['amount']} كوينز" for t in trans[-5:]])
    await ctx.send(f"📜 آخر عملياتك:\n{msg}")

@bot.command()
async def تكت(ctx):
    guild = ctx.guild
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }
    category = discord.utils.get(guild.categories, name="Tickets")
    if not category:
        category = await guild.create_category("Tickets")

    ticket_channel = await guild.create_text_channel(f"ticket-{ctx.author.name}", overwrites=overwrites, category=category)
    await ticket_channel.send(f"{ctx.author.mention} تم فتح تذكرتك! بنساعدك قريب.")

bot.run(TOKEN)
