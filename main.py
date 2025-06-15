from flask import Flask
from threading import Thread
import discord
from discord.ext import commands
from discord import app_commands
import os
import time
import random
from dotenv import load_dotenv

# Ortam değişkenlerini yükle (.env dosyasından)
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Flask uygulaması (UptimeRobot için)
app = Flask('')

@app.route('/')
def home():
    return "Bot AKTİF!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Bot tanımı
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix='/', intents=intents)
tree = bot.tree

# Stoklar
free_stock = {"steam": []}
premium_stock = {"steam": []}
last_used = {}
kullanim_gecmisi = {}

AUTHORIZED_ADMINS = [1284167857231364118, 1230072380467056710]
LOG_CHANNEL_NAME = "log"

async def log_message(interaction, message):
    log_channel = discord.utils.get(interaction.guild.text_channels, name=LOG_CHANNEL_NAME)
    if log_channel:
        await log_channel.send(message)

# /freegen komutu
@tree.command(name="freegen", description="Free hesap alırsın.")
@app_commands.describe(platform="Platform ismi (örnek: steam)")
async def freegen(interaction: discord.Interaction, platform: str):
    await interaction.response.defer(ephemeral=True)
    now = time.time()
    user_id = interaction.user.id

    if user_id not in AUTHORIZED_ADMINS:
        if user_id in last_used and now - last_used[user_id] < 600:
            remaining = int(600 - (now - last_used[user_id]))
            await interaction.followup.send(f"⏳ {remaining} saniye beklemelisin.")
            return
        last_used[user_id] = now

    if free_stock.get(platform):
        hesap = random.choice(free_stock[platform])
        await interaction.user.send(f"🔓 Free {platform} hesabın: `{hesap}`")
        await interaction.followup.send("✅ Hesabın DM'den gönderildi.")
        kullanim_gecmisi.setdefault(user_id, []).append(hesap)
        await log_message(interaction, f"📤 {interaction.user} kişisine Free {platform} hesabı gönderildi: `{hesap}`")
    else:
        await interaction.followup.send("⚠️ Stokta hesap yok.")

# /premiumgen komutu
@tree.command(name="premiumgen", description="Premium hesap alırsın (Premium rolün olmalı).")
@app_commands.describe(platform="Platform ismi (örnek: steam)")
async def premiumgen(interaction: discord.Interaction, platform: str):
    await interaction.response.defer(ephemeral=True)
    premium_role = discord.utils.get(interaction.guild.roles, name="Premium")
    if premium_role not in interaction.user.roles and not interaction.user.guild_permissions.administrator:
        await interaction.followup.send("❌ Bu komutu sadece Premium üyeler veya adminler kullanabilir.")
        return

    if premium_stock.get(platform):
        hesap = random.choice(premium_stock[platform])
        premium_stock[platform].remove(hesap)
        await interaction.user.send(f"🔐 Premium {platform} hesabın: `{hesap}`")
        await interaction.followup.send("✅ Hesabın DM'den gönderildi.")
        await log_message(interaction, f"📤 {interaction.user} kişisine Premium {platform} hesabı gönderildi ve stoktan silindi: `{hesap}`")
    else:
        await interaction.followup.send("⚠️ Premium stokta hesap yok.")

# /stoklar komutu
@tree.command(name="stoklar", description="Mevcut stokları gösterir.")
async def stoklar(interaction: discord.Interaction):
    embed = discord.Embed(title="📦 Mevcut Stoklar", color=discord.Color.gold())
    for platform, hesaplar in free_stock.items():
        embed.add_field(name=f"Free - {platform}", value=f"{len(hesaplar)} adet", inline=False)
    for platform, hesaplar in premium_stock.items():
        embed.add_field(name=f"Premium - {platform}", value=f"{len(hesaplar)} adet", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

# /yardım komutu
@tree.command(name="yardım", description="Bot komutlarını listeler.")
async def yardım(interaction: discord.Interaction):
    user_id = interaction.user.id
    embed = discord.Embed(title="📘 Yardım Menüsü", color=discord.Color.blue())
    embed.add_field(name="/freegen [platform]", value="Free hesap alırsın (10 dk cooldown).", inline=False)
    embed.add_field(name="/premiumgen [platform]", value="Premium hesabı alırsın (Premium rolü gerekli).", inline=False)
    embed.add_field(name="/stoklar", value="Stoktaki hesap sayılarını listeler.", inline=False)
    if user_id in AUTHORIZED_ADMINS:
        embed.add_field(name="🔐 Admin Komutları", value="Sadece adminler için:", inline=False)
        embed.add_field(name="/freegenekle", value="Free hesap ekle", inline=True)
        embed.add_field(name="/premiumgenekle", value="Premium hesap ekle", inline=True)
        embed.add_field(name="/freegensil", value="Free stokları sil", inline=True)
        embed.add_field(name="/premiumgensil", value="Premium stokları sil", inline=True)
        embed.add_field(name="/dosyaileekle", value="Dosyadan toplu hesap ekle", inline=True)
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Admin komutları
@tree.command(name="freegenekle", description="Free hesap ekler (admin).")
async def freegenekle(interaction: discord.Interaction, platform: str, hesap: str):
    if interaction.user.id not in AUTHORIZED_ADMINS:
        await interaction.response.send_message("❌ Admin yetkin yok.", ephemeral=True)
        return
    free_stock.setdefault(platform, []).append(hesap)
    await interaction.response.send_message(f"✅ Free stock'a eklendi: {platform}", ephemeral=True)

@tree.command(name="premiumgenekle", description="Premium hesap ekler (admin).")
async def premiumgenekle(interaction: discord.Interaction, platform: str, hesap: str):
    if interaction.user.id not in AUTHORIZED_ADMINS:
        await interaction.response.send_message("❌ Admin yetkin yok.", ephemeral=True)
        return
    premium_stock.setdefault(platform, []).append(hesap)
    await interaction.response.send_message(f"✅ Premium stock'a eklendi: {platform}", ephemeral=True)

@tree.command(name="freegensil", description="Free stokları sil (admin).")
async def freegensil(interaction: discord.Interaction, platform: str):
    if interaction.user.id not in AUTHORIZED_ADMINS:
        await interaction.response.send_message("❌ Admin yetkin yok.", ephemeral=True)
        return
    free_stock[platform] = []
    await interaction.response.send_message(f"🗑️ Free stok temizlendi: {platform}", ephemeral=True)

@tree.command(name="premiumgensil", description="Premium stokları sil (admin).")
async def premiumgensil(interaction: discord.Interaction, platform: str):
    if interaction.user.id not in AUTHORIZED_ADMINS:
        await interaction.response.send_message("❌ Admin yetkin yok.", ephemeral=True)
        return
    premium_stock[platform] = []
    await interaction.response.send_message(f"🗑️ Premium stok temizlendi: {platform}", ephemeral=True)

# /dosyaileekle komutu
@tree.command(name="dosyaileekle", description="Free veya Premium hesapları dosya ile ekle (admin).")
@app_commands.describe(platform="Platform ismi (örnek: steam)", tip="free ya da premium", dosya="Hesapları içeren .txt dosyası")
async def dosyaileekle(interaction: discord.Interaction, platform: str, tip: str, dosya: discord.Attachment):
    if interaction.user.id not in AUTHORIZED_ADMINS:
        await interaction.response.send_message("❌ Bu komut sadece adminler içindir.", ephemeral=True)
        return

    if tip not in ["free", "premium"]:
        await interaction.response.send_message("❌ 'tip' sadece 'free' ya da 'premium' olabilir.", ephemeral=True)
        return

    if not dosya.filename.endswith(".txt"):
        await interaction.response.send_message("❌ Lütfen `.txt` uzantılı dosya yükleyin.", ephemeral=True)
        return

    content = await dosya.read()
    try:
        lines = content.decode("utf-8").splitlines()
    except:
        await interaction.response.send_message("❌ UTF-8 kodlaması ile okunamadı.", ephemeral=True)
        return

    sayac = 0
    for line in lines:
        line = line.strip()
        if line:
            if tip == "free":
                free_stock.setdefault(platform, []).append(line)
            else:
                premium_stock.setdefault(platform, []).append(line)
            sayac += 1

    await interaction.response.send_message(
        f"✅ {sayac} adet hesap **{platform} → {tip}** stoklarına eklendi.",
        ephemeral=True
    )

# Bot hazır olduğunda
@bot.event
async def on_ready():
    await tree.sync()
    print(f"{bot.user} olarak giriş yapıldı!")

# Çalıştır
keep_alive()
bot.run(TOKEN)
