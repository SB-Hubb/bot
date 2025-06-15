import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
admin_ids = [1284167857231364118, 1230072380467056710]

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)
tree = app_commands.CommandTree(bot)

app = Flask('')

@app.route('/')
def home():
    return "Bot AKTİF!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# STOK DOSYALARI
stock_files = {
    "free": "free_steam.txt",
    "premium": "premium_steam.txt"
}

# BOT BAĞLANINCA SYNC
@bot.event
async def on_ready():
    await tree.sync()
    print(f"{bot.user} olarak giriş yapıldı!")

# HESAP GÖNDERME
@tree.command(name="freegen", description="Free hesap alın.")
async def freegen(interaction: discord.Interaction):
    await send_account(interaction, "free")

@tree.command(name="premiumgen", description="Premium hesap alın (Premium rolün olmalı).")
async def premiumgen(interaction: discord.Interaction):
    role = discord.utils.get(interaction.user.roles, name="Premium")
    if not role:
        return await interaction.response.send_message("❌ Premium rolün yok!", ephemeral=True)
    await send_account(interaction, "premium")

# HESAP EKLEME
@tree.command(name="freegenekle", description="Free hesap ekle (admin)")
async def freegenekle(interaction: discord.Interaction, hesap: str):
    await add_account(interaction, "free", hesap)

@tree.command(name="premiumgenekle", description="Premium hesap ekle (admin)")
async def premiumgenekle(interaction: discord.Interaction, hesap: str):
    await add_account(interaction, "premium", hesap)

# STOKLARI GÖSTERME
@tree.command(name="stoklar", description="Mevcut hesap stoklarını göster")
async def stoklar(interaction: discord.Interaction):
    free_count = count_lines(stock_files["free"])
    premium_count = count_lines(stock_files["premium"])
    embed = discord.Embed(title="🔹 Mevcut Stoklar", color=discord.Color.gold())
    embed.add_field(name="Free - steam", value=f"{free_count} adet")
    embed.add_field(name="Premium - steam", value=f"{premium_count} adet")
    await interaction.response.send_message(embed=embed, ephemeral=True)

# DOSYA İLE EKLEME
@tree.command(name="dosyaileekle", description=".txt dosyası ile stok ekle (admin)")
@app_commands.describe(platform="Platform (free/premium)", dosya="Lütfen bir .txt dosyası ekle")
async def dosyaileekle(interaction: discord.Interaction, platform: str, dosya: discord.Attachment):
    if interaction.user.id not in admin_ids:
        return await interaction.response.send_message("❌ Bu komutu kullanma iznin yok.", ephemeral=True)

    if platform not in stock_files:
        return await interaction.response.send_message("❌ Geçersiz platform (free/premium).", ephemeral=True)

    if not dosya.filename.endswith(".txt"):
        return await interaction.response.send_message("❌ Lütfen bir .txt dosyası yükleyin.", ephemeral=True)

    veri = await dosya.read()
    metin = veri.decode("utf-8")
    with open(stock_files[platform], "a", encoding="utf-8") as f:
        f.write(metin + "\n")

    await interaction.response.send_message(f"✅ {platform} stoklarına dosya başarıyla eklendi!", ephemeral=True)

# Yardım komutu
@tree.command(name="yardim", description="Tüm komutları gösterir.")
async def yardim(interaction: discord.Interaction):
    embed = discord.Embed(title="⚙️ Komutlar", color=discord.Color.green())
    embed.add_field(name="/freegen", value="Free hesap alır.", inline=False)
    embed.add_field(name="/premiumgen", value="Premium hesap alır. (Premium rol gerekli)", inline=False)
    embed.add_field(name="/stoklar", value="Stokları gösterir.", inline=False)
    embed.add_field(name="/freegenekle", value="Free hesap ekler. (Admin)", inline=False)
    embed.add_field(name="/premiumgenekle", value="Premium hesap ekler. (Admin)", inline=False)
    embed.add_field(name="/dosyaileekle", value=".txt dosyası ile toplu ekleme. (Admin)", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

# DESTEK FONKSİYONLAR
def count_lines(file):
    if not os.path.exists(file):
        return 0
    with open(file, "r", encoding="utf-8") as f:
        return sum(1 for _ in f if _.strip())

async def send_account(interaction, platform):
    file_path = stock_files[platform]
    if not os.path.exists(file_path) or count_lines(file_path) == 0:
        return await interaction.response.send_message(f"❌ {platform.capitalize()} stokta hesap yok.", ephemeral=True)

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    account = lines[0].strip()
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(lines[1:])

    await interaction.user.send(f"✅ İşte {platform} hesabın: `{account}`")
    await interaction.response.send_message(f"📬 {interaction.user.mention} kişisine {platform} steam hesabı gönderildi ve stoktan silindi: `{account}`", ephemeral=False)

async def add_account(interaction, platform, hesap):
    if interaction.user.id not in admin_ids:
        return await interaction.response.send_message("❌ Bu komutu kullanma iznin yok.", ephemeral=True)

    with open(stock_files[platform], "a", encoding="utf-8") as f:
        f.write(hesap + "\n")
    await interaction.response.send_message(f"✅ {platform.capitalize()} stoklarına hesap eklendi!", ephemeral=True)

keep_alive()
bot.run(TOKEN)
