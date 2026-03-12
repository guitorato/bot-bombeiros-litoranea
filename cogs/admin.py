import discord
from discord.ext import commands
from discord import app_commands
import config


def is_recrutador(interaction: discord.Interaction):
    return any(role.id == config.CARGO_RECRUTADOR for role in interaction.user.roles)


class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    # ---------------------------------
    # LISTAR INSCRITOS
    # ---------------------------------
    @app_commands.command(name="listar-inscritos", description="Lista os candidatos inscritos")
    async def listar_inscritos(self, interaction: discord.Interaction):

        if not is_recrutador(interaction):
            await interaction.response.send_message(
                "❌ Você não tem permissão para usar este comando.",
                ephemeral=True
            )
            return

        role = interaction.guild.get_role(config.CARGO_INSCRITO)

        membros = role.members if role else []

        if not membros:
            await interaction.response.send_message(
                "Nenhum inscrito encontrado.",
                ephemeral=True
            )
            return

        lista = "\n".join([f"{m.mention} - {m.nick}" for m in membros])

        embed = discord.Embed(
            title="📋 Lista de Inscritos",
            description=lista,
            color=discord.Color.blue()
        )

        await interaction.response.send_message(embed=embed)


    # ---------------------------------
    # APROVAR INSCRIÇÃO
    # ---------------------------------
    @app_commands.command(name="aprovar", description="Aprovar inscrição")
    async def aprovar(self, interaction: discord.Interaction, membro: discord.Member):

        if not is_recrutador(interaction):
            await interaction.response.send_message(
                "❌ Você não tem permissão para usar este comando.",
                ephemeral=True
            )
            return

        role_inscrito = interaction.guild.get_role(config.CARGO_INSCRITO)
        role_aprovado = interaction.guild.get_role(config.CARGO_INSCRICAO_REALIZADA)

        if role_aprovado:
            await membro.add_roles(role_aprovado)

        if role_inscrito:
            await membro.remove_roles(role_inscrito)

        nick = membro.nick

        if nick:
            nick = nick.replace("[INS]", "[INS-OK]")

            if len(nick) > 32:
                nick = nick[:32]

            await membro.edit(nick=nick)

        await interaction.response.send_message(
            f"✅ {membro.mention} foi aprovado no processo de inscrição."
        )


    # ---------------------------------
    # REPROVAR INSCRIÇÃO
    # ---------------------------------
    @app_commands.command(name="reprovar", description="Reprovar inscrição")
    async def reprovar(self, interaction: discord.Interaction, membro: discord.Member):

        if not is_recrutador(interaction):
            await interaction.response.send_message(
                "❌ Você não tem permissão para usar este comando.",
                ephemeral=True
            )
            return

        role_inscrito = interaction.guild.get_role(config.CARGO_INSCRITO)

        if role_inscrito:
            await membro.remove_roles(role_inscrito)

        await membro.edit(nick=None)

        await interaction.response.send_message(
            f"❌ {membro.mention} teve sua inscrição reprovada."
        )


async def setup(bot):
    await bot.add_cog(Admin(bot))