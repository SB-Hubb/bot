import os
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from dotenv import load_dotenv
import aiofiles
from collections import Counter  # platform stok sayımı için

# Render için gerekli: Flask ve Threading
from flask import Flask
from threading import Thread

# Flask sunucusunu başlat (Render için)
app = Flask('')

@app.route('/')
def home():
    return "Bot aktif!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Discord bot ayarları
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=None, intents=intents)

FREE_GEN_CHANNEL_ID = 1383512554223177852
PREMIUM_GEN_CHANNEL_ID = 1383512556437766456

FREE_FILE = "accounts.txt"
PREMIUM_FILE = "accountspr.txt"

# Eksik dosyaları oluştur
for filename in [FREE_FILE, PREMIUM_FILE]:
    if not os.path.exists(filename):
        open(filename, "w", encoding="utf-8").close()

@bot.event
async def on_ready():
    print(f"Bot giriş yaptı: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} komut senkronize edildi.")
    except Exception as e:
        print(f"Komut senkronizasyon hatası: {e}")

@bot.tree.command(name="txtilekle", description="Hesap ekle (.txt dosyası ile)")
@app_commands.describe(platform="Platform adı", premium_free="premium veya free")
async def txtilekle(interaction: discord.Interaction, platform: str, premium_free: str):
    if premium_free.lower() not in ["premium", "free"]:
        await interaction.response.send_message("premium veya free olarak belirtmelisin.", ephemeral=True)
        return

    dosya = PREMIUM_FILE if premium_free.lower() == "premium" else FREE_FILE
    await interaction.response.defer(ephemeral=True)

    try:
        await interaction.followup.send(f"{platform} için `{premium_free}` hesap dosyasını (.txt) bu kanala gönder. (1 dakika süren var)")

        def check(m):
            return (
                m.author == interaction.user and 
                m.channel == interaction.channel and 
                m.attachments and 
                m.attachments[0].filename.endswith(".txt")
            )

        msg = await bot.wait_for("message", check=check, timeout=60)
        attachment = msg.attachments[0]
        content = await attachment.read()
        lines = content.decode("utf-8").splitlines()

        lines = [f"{platform} {line.strip()}" for line in lines if line.strip() != ""]

        async with aiofiles.open(dosya, mode="a", encoding="utf-8") as f:
            await f.write("\n".join(lines) + "\n")

        await interaction.followup.send(f"{len(lines)} hesap başarıyla `{dosya}` dosyasına eklendi.", ephemeral=True)

    except asyncio.TimeoutError:
        await interaction.followup.send("Dosya zamanında gönderilmedi, işlem iptal edildi.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"Hata oluştu: {e}", ephemeral=True)

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

@bot.tree.command(name="stok", description="Hesap stoklarını göster")
async def stok(interaction: discord.Interaction):
    await interaction.response.defer()  # görünür mesaj
    try:
        async with aiofiles.open(FREE_FILE, "r", encoding="utf-8") as f:
            free_lines = await f.readlines()
        async with aiofiles.open(PREMIUM_FILE, "r", encoding="utf-8") as f:
            premium_lines = await f.readlines()

        free_lines = [line.strip() for line in free_lines if line.strip()]
        premium_lines = [line.strip() for line in premium_lines if line.strip()]

        free_counter = Counter(line.split()[0] for line in free_lines)
        premium_counter = Counter(line.split()[0] for line in premium_lines)

        msg = "**📦 Stok Durumu**\n"

        if free_counter:
            msg += "\n🟦 **Ücretsiz Hesaplar:**\n"
            for platform, count in free_counter.items():
                msg += f"• `{platform}`: {count} adet\n"
        else:
            msg += "\n🟦 Ücretsiz hesap yok.\n"

        if premium_counter:
            msg += "\n🟨 **Premium Hesaplar:**\n"
            for platform, count in premium_counter.items():
                msg += f"• `{platform}`: {count} adet\n"
        else:
            msg += "\n🟨 Premium hesap yok.\n"

        await interaction.followup.send(msg)

    except Exception as e:
        await interaction.followup.send(f"Hata oluştu: {e}")

@bot.tree.command(name="yardım", description="Komutları gösterir")
async def yardım(interaction: discord.Interaction):
    help_text = (
        "**Komutlar:**\n"
        "/txtilekle platform premium/free : Hesap ekle (.txt dosyası yükle)\n"
        "/genfree platform : Ücretsiz hesap çek\n"
        "/genpremium platform : Premium hesap çek (Premium rolü gerekli)\n"
        "/stok : Hesap stoklarını platformlara göre gösterir\n"
        "/yardım : Bu mesajı gösterir"
    )
    await interaction.response.send_message(help_text, ephemeral=True)

# Bot başlatma
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Keep-alive başlat
keep_alive()

# Bot çalıştır
bot.run(TOKEN)
