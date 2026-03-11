import discord
from discord.ext import commands
import os
import config

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


@bot.event
async def on_ready():
    print(f"🚒 Bot conectado como {bot.user}")
    print("Sistema de monitoramento iniciado.")


# ----------------------------
# ENTRADA DE MEMBRO
# ----------------------------
@bot.event
async def on_member_join(member):

    channel = bot.get_channel(config.WELCOME_CHANNEL_ID)

    if channel:
        embed = discord.Embed(
            title="🚒 Novo recruta chegou!",
            description=f"{member.mention} entrou no servidor.",
            color=discord.Color.red()
        )

        embed.add_field(
            name="Corporação",
            value="Corpo de Bombeiros Militar - Litorânea RP",
            inline=False
        )

        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)

        await channel.send(embed=embed)


# ----------------------------
# SAÍDA DE MEMBRO
# ----------------------------
@bot.event
async def on_member_remove(member):

    log_channel = bot.get_channel(config.LOG_CHANNEL_ID)

    if not log_channel:
        return

    guild = member.guild
    action = "Saiu do servidor"

    # verificar kick
    async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.kick):
        if entry.target.id == member.id:
            action = f"Expulso por {entry.user}"
            break

    # verificar ban
    async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.ban):
        if entry.target.id == member.id:
            action = f"Banido por {entry.user}"
            break

    embed = discord.Embed(
        title="📋 Registro de saída",
        color=discord.Color.orange()
    )

    embed.add_field(
        name="Usuário",
        value=f"{member} ({member.id})",
        inline=False
    )

    embed.add_field(
        name="Ação",
        value=action,
        inline=False
    )

    embed.set_thumbnail(url=member.avatar.url if member.avatar else None)

    await log_channel.send(embed=embed)


bot.run(TOKEN)