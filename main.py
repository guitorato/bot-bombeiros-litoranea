import discord
from discord.ext import commands
import os
import asyncio

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# ---------------------------------
# QUANDO O BOT INICIAR
# ---------------------------------
@bot.event
async def on_ready():
    print(f"🚒 Bot online: {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"✅ Slash commands sincronizados: {len(synced)}")
    except Exception as e:
        print(f"Erro ao sincronizar comandos: {e}")


# ---------------------------------
# CARREGAR COGS AUTOMATICAMENTE
# ---------------------------------
async def load_cogs():
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            await bot.load_extension(f"cogs.{file[:-3]}")
            print(f"Cog carregada: {file}")


# ---------------------------------
# MAIN
# ---------------------------------
async def main():
    async with bot:
        await load_cogs()
        await bot.start(os.getenv("TOKEN"))


asyncio.run(main())