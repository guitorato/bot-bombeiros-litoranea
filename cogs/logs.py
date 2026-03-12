import discord
from discord.ext import commands
import config

class Logs(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member):

        log_channel = self.bot.get_channel(config.LOG_CHANNEL_ID)

        if not log_channel:
            return

        action = "Saiu do servidor"

        guild = member.guild

        async for entry in guild.audit_logs(limit=5):
            if entry.target.id == member.id:

                if entry.action == discord.AuditLogAction.kick:
                    action = f"Expulso por {entry.user}"

                if entry.action == discord.AuditLogAction.ban:
                    action = f"Banido por {entry.user}"

        embed = discord.Embed(
            title="Registro de saída",
            color=discord.Color.orange()
        )

        embed.add_field(
            name="Usuário",
            value=f"{member} ({member.id})"
        )

        embed.add_field(
            name="Ação",
            value=action
        )

        await log_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Logs(bot))