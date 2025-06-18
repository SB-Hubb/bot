from dotenv import load_dotenv
import os
import discord
import random
import asyncio
import requests
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='v', intents=intents)

@bot.event
async def on_ready():
    print(f"Bot giriş yaptı: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} komut senkronize edildi.")
    except Exception as e:
        print(f"Komut senkronizasyon hatası: {e}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.attachments:
        attachment = message.attachments[0]
        if attachment.filename.endswith(".txt"):
            content = await attachment.read()
            lines = content.decode("utf-8").splitlines()
            await message.channel.send(f"{attachment.filename} dosyasındaki hesaplar alındı. Sayı: {len(lines)}")

            is_premium = "premium" in message.content.lower()
            platform = message.content.split()[1] if len(message.content.split()) > 1 else "bilinmeyen"

            file_name = "accountspr.txt" if is_premium else "accounts.txt"
            with open(file_name, "a", encoding="utf-8") as f:
                for line in lines:
                    if line.strip():
                        f.write(f"{platform} - {line.strip()}\n")

            await message.channel.send(f"✅ {platform} için {len(lines)} hesap kaydedildi.")

    await bot.process_commands(message)

@bot.command()
async def roll(ctx):
    await asyncio.sleep(1)
    await ctx.send(f'Zar attın, {random.randint(1, 6)} geldi 🎲')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong! 🏓')
    await ctx.send(f'Bot gecikmesi: {round(bot.latency * 1000)} ms')

@commands.has_permissions(administrator=True)
@bot.command()
async def clear(ctx, amount: int):
    if amount < 1 or amount > 500:
        await ctx.send('1-500 arası sayı girin.❗')
        return
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f'{len(deleted)} mesaj silindi.🧹', delete_after=5)

# ✅ HATA BURADAYDI — async olarak düzeltilmiş hali:
@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send('Yönetici olmalısın.🧑‍💼')

@bot.command()
async def genpremium(ctx, platform: str):
    allowed_roles = ['Premium', 'Booster', 'VIP']
    if not any(role.name in allowed_roles for role in ctx.author.roles):
        await ctx.send("Bu komutu kullanmak için premium role sahip olmalısın.👑")
        return

    with open('accountspr.txt', 'r', encoding='utf-8') as f:
        accounts = [line.strip() for line in f if line.strip().startswith(platform)]

    if not accounts:
        await ctx.send(f"{platform} için premium hesap yok.❌")
        return

    account = random.choice(accounts)
    await ctx.author.send(f"{platform} premium hesabı: {account}")
    await ctx.send(f"{ctx.author.mention} hesabın DM kutuna gönderildi.📩")

@bot.command()
async def genfree(ctx, platform: str):
    with open('accounts.txt', 'r', encoding='utf-8') as f:
        accounts = [line.strip() for line in f if line.strip().startswith(platform)]

    if not accounts:
        await ctx.send(f"{platform} için hesap bulunamadı.❌")
        return

    account = random.choice(accounts)
    await ctx.author.send(f"{platform} hesabı: {account}")
    await ctx.send(f"{ctx.author.mention} hesabın DM kutuna gönderildi.📩")

@bot.command()
async def stok(ctx):
    with open('accounts.txt', 'r', encoding='utf-8') as f:
        normal_count = len([line for line in f if line.strip()])
    with open('accountspr.txt', 'r', encoding='utf-8') as f:
        premium_count = len([line for line in f if line.strip()])
    embed = discord.Embed(title="Stok Durumu", description=f"🆓 Free: {normal_count}\n👑 Premium: {premium_count}", color=discord.Color.blue())
    await ctx.send(embed=embed)

@bot.command()
async def havadurumu(ctx, *, city: str):
    url = f"https://wttr.in/{city}?format=3&lang=tr"
    response = requests.get(url)
    if response.status_code == 200:
        await ctx.send(f"Hava durumu: {response.text}")
    else:
        await ctx.send("Hava bilgisi alınamadı.❌")

@bot.command()
async def yardım(ctx):
    embed = discord.Embed(title="Yardım Menüsü", color=discord.Color.blue())
    embed.add_field(name="vgenfree <platform>", value="Ücretsiz hesap al.", inline=False)
    embed.add_field(name="vgenpremium <platform>", value="Premium hesap al (rol gerek).", inline=False)
    embed.add_field(name="vstok", value="Stok durumunu göster.", inline=False)
    embed.add_field(name="vhavadurumu <şehir>", value="Hava durumunu getir.", inline=False)
    embed.add_field(name="vroll", value="Zar atar.", inline=False)
    embed.add_field(name="vping", value="Bot gecikmesini gösterir.", inline=False)
    await ctx.send(embed=embed)

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
bot.run(token)
