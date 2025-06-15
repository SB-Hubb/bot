import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask
from threading import Thread
import os
import time
import random
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)
tree = bot.tree

admin_ids = [123456789012345678]  # <- Buraya admin ID'lerini ekle

free_stock = {}
premium_stock = {}

# Flask ile Replit keep-alive
app = Flask('')

@app.route('/')
def home():
    return "Bot AKTİF!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# BOT AÇILDIĞINDA
@bot.event
async def on_ready():
    await tree.sync()
    print(f"{bot.user} olarak giriş yapıldı!")

# /dosyaileekle
@tree.command(name="dosyaileekle", description="Dosya ile hesap ekle (admin)")
@app_commands.describe(platform="Platform adı (örn: steam)", dosya="Lütfen bir .txt dosya ekleyin", tip="Stok tipi: free veya premium")
@app_commands.choices(tip=[
    app_commands.Choice(name="free", value="free"),
    app_commands.Choice(name="premium", value="premium")
])
async def dosyaileekle(interaction: discord.Interaction, platform: str, dosya: discord.Attachment, tip: app_commands.Choice[str]):
    if interaction.user.id not in admin_ids:
        await interaction.response.send_message("❌ Bu komutu kullanma iznin yok.", ephemeral=True)
        return

    if not dosya.filename.endswith(".txt"):
        await interaction.response.send_message("❌ Lütfen bir `.txt` dosyası yükleyin.", ephemeral=True)
        return

    content = (await dosya.read()).decode("utf-8")
    lines = content.strip().splitlines()
    clean_lines = [line.strip() for line in lines if line.strip()]

    if tip.value == "free":
        free_stock.setdefault(platform, []).extend(clean_lines)
    elif tip.value == "premium":
        premium_stock.setdefault(platform, []).extend(clean_lines)

    await interaction.response.send_message(f"✅ `{platform}` için {len(clean_lines)} adet {tip.value} hesap başarıyla eklendi!", ephemeral=True)

# /freegen
@tree.command(name="freegen", description="Free hesap alırsın.")
@app_commands.describe(platform="Platform adı (örn: steam)")
async def freegen(interaction: discord.Interaction, platform: str):
    stoklar = free_stock.get(platform, [])
    if not stoklar:
        await interaction.response.send_message("❌ Bu platform için free stok bulunamadı.", ephemeral=True)
        return

    hesap = random.choice(stoklar)
    free_stock[platform].remove(hesap)
    await interaction.user.send(f"🎁 İşte hesabın: `{hesap}`")
    await interaction.response.send_message("✅ Hesabın özel mesaj olarak gönderildi!", ephemeral=True)

# /premiumgen
@tree.command(name="premiumgen", description="Premium hesap alırsın (Premium rolün olmalı).")
@app_commands.describe(platform="Platform adı (örn: steam)")
async def premiumgen(interaction: discord.Interaction, platform: str):
    premium_role = discord.utils.get(interaction.guild.roles, name="Premium")
    if not premium_role or premium_role not in interaction.user.roles:
        await interaction.response.send_message("❌ Bu komutu kullanmak için Premium rolüne sahip olmalısın.", ephemeral=True)
        return

    stoklar = premium_stock.get(platform, [])
    if not stoklar:
        await interaction.response.send_message("❌ Bu platform için premium stok bulunamadı.", ephemeral=True)
        return

    hesap = random.choice(stoklar)
    premium_stock[platform].remove(hesap)
    await interaction.user.send(f"💎 Premium hesabın: `{hesap}`")
    await interaction.response.send_message("✅ Premium hesabın özel mesaj olarak gönderildi!", ephemeral=True)

# /stoklar
@tree.command(name="stoklar", description="Tüm mevcut stokları gösterir.")
async def stoklar(interaction: discord.Interaction):
    mesaj = "📦 **Mevcut Stoklar**\n"
    for platform, stoklar in free_stock.items():
        mesaj += f"Free - {platform}: {len(stoklar)} adet\n"
    for platform, stoklar in premium_stock.items():
        mesaj += f"Premium - {platform}: {len(stoklar)} adet\n"

    if mesaj == "📦 **Mevcut Stoklar**\n":
        mesaj += "Stok bulunamadı."

    await interaction.response.send_message(mesaj, ephemeral=True)

# /yardım
@tree.command(name="yardim", description="Komutları gösterir.")
async def yardim(interaction: discord.Interaction):
    embed = discord.Embed(title="📖 Komut Listesi", color=0x5865F2)
    embed.add_field(name="/freegen", value="Free hesap alırsın.", inline=False)
    embed.add_field(name="/premiumgen", value="Premium hesap alırsın. (Premium rolün olmalı)", inline=False)
    embed.add_field(name="/stoklar", value="Mevcut stokları gösterir.", inline=False)
    embed.add_field(name="/dosyaileekle", value="Dosya ile hesap ekler. (Admin)", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

# KEEP ALIVE VE BOT BAŞLAT
keep_alive()
bot.run(TOKEN)
