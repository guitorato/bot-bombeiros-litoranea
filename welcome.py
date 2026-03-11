import discord
from discord.ext import commands

TOKEN = "MTQ4MTMxNDc2MDg4Nzc2NzE5MQ.Gg3aDa.lsyXu1eRkejLHpdoK3UvUJw24LV6tuWNHYZcXU"

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