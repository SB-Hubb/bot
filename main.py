import os
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from dotenv import load_dotenv
import aiofiles

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=None, intents=intents)

FREE_GEN_CHANNEL_ID = 1383512554223177852
PREMIUM_GEN_CHANNEL_ID = 1383512556437766456

FREE_FILE = "accounts.txt"
PREMIUM_FILE = "accountspr.txt"

@bot.event
async def on_ready():
    print(f"Bot giriş yaptı: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} komut senkronize edildi.")
    except Exception as e:
        print(f"Komut senkronizasyon hatası: {e}")

# -- txtilekle komutu aynı (geçici pass ile) --
@bot.tree.command(name="txtilekle", description="Hesap ekle (txt dosyası ile)")
@app_commands.describe(platform="Platform adı", premium_free="premium veya free")
async def txtilekle(interaction: discord.Interaction, platform: str, premium_free: str):
    pass  # Buraya gerçek kodunu ekle

# -- genpremium komutu banlı ve kanal kısıtlı --
@bot.tree.command(name="genpremium", description="Premium hesap çek")
@app_commands.describe(platform="Platform adı")
async def genpremium(interaction: discord.Interaction, platform: str):
    if interaction.channel is None or interaction.channel.id != PREMIUM_GEN_CHANNEL_ID:
        if interaction.guild is not None:
            try:
                await interaction.response.send_message(
                    "Bu komutu sadece #premium-gen kanalında kullanabilirsin. Sunucudan yasaklanıyorsun.", ephemeral=True)
                await interaction.guild.ban(interaction.user, reason="Gen komutunu yasaklı kanallar dışında veya DM'de kullandı.")
            except Exception as e:
                print(f"Ban atılırken hata: {e}")
        else:
            await interaction.response.send_message("Gen komutlarını DM'de kullanamazsın!", ephemeral=True)
        return

    allowed_roles = ["Premium", "Booster", "VIP"]
    if not any(role.name in allowed_roles for role in interaction.user.roles):
        await interaction.response.send_message("Bu komutu kullanmak için premium rolde olmalısın.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    async with aiofiles.open(PREMIUM_FILE, "r", encoding="utf-8") as f:
        lines = await f.readlines()
    lines = [line.strip() for line in lines if line.strip().startswith(platform)]
    if not lines:
        await interaction.followup.send(f"{platform} için premium hesap kalmadı.", ephemeral=True)
        return
    account = lines.pop(0)
    async with aiofiles.open(PREMIUM_FILE, "w", encoding="utf-8") as f:
        await f.write("\n".join(lines) + ("\n" if lines else ""))
    try:
        await interaction.user.send(f"{platform} premium hesabı:\n{account}")
        await interaction.followup.send(f"Hesabın DM'ne gönderildi. 📩", ephemeral=True)
    except discord.Forbidden:
        await interaction.followup.send("DM gönderilemiyor, lütfen DM'lerini aç.", ephemeral=True)

# -- genfree komutu banlı ve kanal kısıtlı --
@bot.tree.command(name="genfree", description="Ücretsiz hesap çek")
@app_commands.describe(platform="Platform adı")
async def genfree(interaction: discord.Interaction, platform: str):
    if interaction.channel is None or interaction.channel.id != FREE_GEN_CHANNEL_ID:
        if interaction.guild is not None:
            try:
                await interaction.response.send_message(
                    "Bu komutu sadece #free-gen kanalında kullanabilirsin. Sunucudan yasaklanıyorsun.", ephemeral=True)
                await interaction.guild.ban(interaction.user, reason="Gen komutunu yasaklı kanallar dışında veya DM'de kullandı.")
            except Exception as e:
                print(f"Ban atılırken hata: {e}")
        else:
            await interaction.response.send_message("Gen komutlarını DM'de kullanamazsın!", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    async with aiofiles.open(FREE_FILE, "r", encoding="utf-8") as f:
        lines = await f.readlines()
    lines = [line.strip() for line in lines if line.strip().startswith(platform)]
    if not lines:
        await interaction.followup.send(f"{platform} için ücretsiz hesap kalmadı.", ephemeral=True)
        return
    account = lines.pop(0)
    async with aiofiles.open(FREE_FILE, "w", encoding="utf-8") as f:
        await f.write("\n".join(lines) + ("\n" if lines else ""))
    try:
        await interaction.user.send(f"{platform} hesabı:\n{account}")
        await interaction.followup.send(f"Hesabın DM'ne gönderildi. 📩", ephemeral=True)
    except discord.Forbidden:
        await interaction.followup.send("DM gönderilemiyor, lütfen DM'lerini aç.", ephemeral=True)

# -- stok komutu (geçici pass ile) --
@bot.tree.command(name="stok", description="Hesap stoklarını göster")
async def stok(interaction: discord.Interaction):
    pass  # Buraya gerçek kodunu ekle

# -- yardım komutu (geçici pass ile) --
@bot.tree.command(name="yardım", description="Komutları gösterir")
async def yardım(interaction: discord.Interaction):
    pass  # Buraya gerçek kodunu ekle

# Bot başlatma
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
