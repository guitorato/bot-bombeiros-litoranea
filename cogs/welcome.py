import discord
from discord.ext import commands
import config

class Welcome(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):

        channel = self.bot.get_channel(config.WELCOME_CHANNEL_ID)

        civil_role = member.guild.get_role(config.CARGO_CIVIL)

        if civil_role:
            await member.add_roles(civil_role)

        embed = discord.Embed(
            title="🚒 Novo cidadão chegou!",
            description=f"{member.mention} entrou no servidor.",
            color=discord.Color.red()
        )

        if channel:
            await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Welcome(bot))