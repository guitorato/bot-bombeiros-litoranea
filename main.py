import discord
from discord.ext import commands
import os
import asyncio
import config

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

@bot.event
async def on_ready():
    print(f"🚒 Bot online: {bot.user}")

    guild = discord.Object(id=config.SERVIDOR_ID)

    try:
        synced = await bot.tree.sync(guild=guild)
        print(f"✅ Slash commands sincronizados: {len(synced)}")
    except Exception as e:
        print(f"Erro ao sincronizar: {e}")


async def load_cogs():
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            await bot.load_extension(f"cogs.{file[:-3]}")
            print(f"Cog carregada: {file}")


async def main():
    async with bot:
        await load_cogs()
        await bot.start(os.getenv("TOKEN"))


asyncio.run(main())