import discord
from discord.ext import commands
import config

class FormModal(discord.ui.Modal, title="Inscrição Bombeiros"):

    nome = discord.ui.TextInput(label="Nome In-Game")
    idade = discord.ui.TextInput(label="Idade")
    passaporte = discord.ui.TextInput(label="Passaporte")
    telefone = discord.ui.TextInput(label="Telefone In-Game")
    pagamento = discord.ui.TextInput(label="Pagamento realizado? (SIM/NÃO)")

    async def on_submit(self, interaction: discord.Interaction):

        guild = interaction.guild
        member = interaction.user

        nickname = f"[INS] {self.passaporte} | {self.nome}"

        if len(nickname) > 32:
            excesso = len(nickname) - 32
            nome_cortado = self.nome.value[:-excesso]
            nickname = f"[INS] {self.passaporte} | {nome_cortado}"

        await member.edit(nick=nickname)

        role = guild.get_role(config.CARGO_INSCRITO)

        if role:
            await member.add_roles(role)

        await interaction.response.send_message(
            "Inscrição enviada com sucesso.",
            ephemeral=True
        )

class InscricaoView(discord.ui.View):

    @discord.ui.button(label="Realizar Inscrição", style=discord.ButtonStyle.red)
    async def inscrever(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(FormModal())

class Recrutamento(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def publicar_edital(self, ctx):

        if ctx.channel.id != config.EDITAL_CHANNEL_ID:
            return

        embed = discord.Embed(
            title="🚒 EDITAL DE RECRUTAMENTO",
            description=config.EDITAL_TEXTO,
            color=discord.Color.red()
        )

        await ctx.send(embed=embed, view=InscricaoView())

    @commands.command()
    async def confirmar(self, ctx, member: discord.Member):

        if ctx.channel.id != config.CONFIRMAR_INSCRICAO_CHANNEL_ID:
            return

        nick = member.nick

        if not nick:
            return

        nick = nick.replace("[INS]", "[INS-OK]")

        if len(nick) > 32:
            nick = nick[:32]

        await member.edit(nick=nick)

        role = ctx.guild.get_role(config.CARGO_INSCRICAO_REALIZADA)

        if role:
            await member.add_roles(role)

        await ctx.send(f"Inscrição confirmada para {member.mention}")

async def setup(bot):
    await bot.add_cog(Recrutamento(bot))