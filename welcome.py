import discord
from discord.ext import commands
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

@bot.event
async def on_member_join(member):
    canal = discord.utils.get(member.guild.text_channels, name="boas-vindas")

    if canal:
        await canal.send(
            f"🚒 | Bem-vindo {member.mention} ao **Corpo de Bombeiros de Litorânea RP**!"
        )

bot.run(TOKEN)