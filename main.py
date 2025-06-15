import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask
from threading import Thread
import os
import random
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)
tree = bot.tree

app = Flask('')

@app.route('/')
def home():
    return "Bot AKTİF!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

ADMIN_IDS = [1284167857231364118, 1230072380467056710]
FREE_CHANNEL_ID = 123456789012345678  # free-gen kanal ID'si
PREMIUM_CHANNEL_ID = 234567890123456789  # premium-gen kanal ID'si

# Helper fonksiyonlar
def stok_dosyasi(platform: str, tur: str):
    return f"stoklar/{tur}_{platform}.txt"

def oku(platform: str, tur: str):
    try:
        with open(stok_dosyasi(platform, tur), "r") as f:
            return f.read().splitlines()
    except FileNotFoundError:
        return []

def yaz(platform: str, tur: str, veriler: list):
    with open(stok_dosyasi(platform, tur), "w") as f:
        f.write("\n".join(veriler))

@bot.event
async def on_ready():
    await tree.sync()
    print(f"{bot.user} olarak giriş yapıldı!")

# Komutlar
@tree.command(name="yardim", description="Komutları gösterir.")
async def yardim(interaction: discord.Interaction):
    embed = discord.Embed(title="VaultKey Yardım Menüsü", color=discord.Color.blue())
    embed.add_field(name="/freegen", value="Free hesap alırsın.", inline=False)
    embed.add_field(name="/premiumgen", value="Premium hesap alırsın.", inline=False)
    embed.add_field(name="/stoklar", value="Stokları görüntülersin.", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="stoklar", description="Stokları görüntüle.")
async def stoklar(interaction: discord.Interaction):
    platformlar = set()
    for dosya in os.listdir("stoklar"):
        if "_" in dosya:
            tur, platform = dosya.replace(".txt", "").split("_")
            platformlar.add(platform)
    
    embed = discord.Embed(title="📦 Mevcut Stoklar", color=discord.Color.orange())
    for platform in platformlar:
        free = len(oku(platform, "free"))
        premium = len(oku(platform, "premium"))
        embed.add_field(name=f"Free - {platform}", value=f"{free} adet", inline=False)
        embed.add_field(name=f"Premium - {platform}", value=f"{premium} adet", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="freegen", description="Free hesap alırsın.")
@app_commands.describe(platform="Platform adı (örneğin: steam)")
async def freegen(interaction: discord.Interaction, platform: str):
    if interaction.channel.id != FREE_CHANNEL_ID:
        await interaction.response.send_message("Bu komut sadece #free-gen kanalında kullanılabilir!", ephemeral=True)
        return

    stoklar = oku(platform, "free")
    if not stoklar:
        await interaction.response.send_message("❌ Stokta hesap kalmamış.", ephemeral=True)
        return

    secilen = stoklar.pop(0)
    yaz(platform, "free", stoklar)
    await interaction.user.send(f"🎁 Free {platform} hesabın: `{secilen}`")
    await interaction.response.send_message("✅ Hesap DM'den gönderildi!", ephemeral=True)

@tree.command(name="premiumgen", description="Premium hesap alırsın.")
@app_commands.describe(platform="Platform adı (örneğin: steam)")
async def premiumgen(interaction: discord.Interaction, platform: str):
    if interaction.channel.id != PREMIUM_CHANNEL_ID:
        await interaction.response.send_message("Bu komut sadece #premium-gen kanalında kullanılabilir!", ephemeral=True)
        return

    stoklar = oku(platform, "premium")
    if not stoklar:
        await interaction.response.send_message("❌ Premium stok kalmamış.", ephemeral=True)
        return

    secilen = stoklar.pop(0)
    yaz(platform, "premium", stoklar)
    await interaction.user.send(f"💎 Premium {platform} hesabın: `{secilen}`")
    await interaction.response.send_message("✅ Premium hesap DM'den gönderildi!", ephemeral=True)

@tree.command(name="dosyaileekle", description="Stoklara dosya ile hesap ekle (admin)")
@app_commands.describe(platform="Platform adı (örneğin: steam)", dosya="Lütfen bir .txt dosyası yükleyin")
async def dosyaileekle(interaction: discord.Interaction, platform: str, dosya: discord.Attachment):
    if interaction.user.id not in ADMIN_IDS:
        await interaction.response.send_message("❌ Bu komutu kullanma iznin yok.", ephemeral=True)
        return

    if not dosya.filename.endswith(".txt"):
        await interaction.response.send_message("❌ Sadece .txt dosyaları kabul edilir.", ephemeral=True)
        return

    icerik = (await dosya.read()).decode("utf-8").splitlines()

    tur = "premium" if "premium" in dosya.filename.lower() else "free"

    mevcut = oku(platform, tur)
    mevcut.extend(icerik)
    yaz(platform, tur, mevcut)

    await interaction.response.send_message(f"✅ {len(icerik)} hesap **{platform} ({tur})** stoklarına eklendi!", ephemeral=True)

bot.run(TOKEN)
