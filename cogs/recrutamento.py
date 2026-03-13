import discord
from discord.ext import commands
import config


def montar_apelido(prefixo: str, nome: str, passaporte: str) -> str:
    apelido = f"{prefixo} {nome} | {passaporte}"

    if len(apelido) <= 32:
        return apelido

    excesso = len(apelido) - 32
    nome_cortado = nome[:-excesso] if excesso < len(nome) else ""

    return f"{prefixo} {nome_cortado} | {passaporte}"[:32]


# -----------------------------
# MODAL DE INSCRIÇÃO
# -----------------------------
class InscricaoModal(discord.ui.Modal, title="Inscrição Bombeiros"):

    nome = discord.ui.TextInput(label="Nome In-Game")
    idade = discord.ui.TextInput(label="Idade")
    passaporte = discord.ui.TextInput(label="Passaporte")
    telefone = discord.ui.TextInput(label="Telefone In-Game")
    pagamento = discord.ui.TextInput(label="Pagamento realizado? (SIM/NÃO)")

    async def on_submit(self, interaction: discord.Interaction):

        guild = interaction.guild
        member = interaction.user

        # -----------------------------
        # ALTERAR NICKNAME
        # -----------------------------
        nickname = montar_apelido("[INS]", self.nome.value, self.passaporte.value)

        try:
            await member.edit(nick=nickname)
        except (discord.Forbidden, discord.HTTPException):
            pass

        # -----------------------------
        # ADICIONAR CARGO INSCRITO
        # -----------------------------
        role = guild.get_role(config.CARGO_INSCRITO)

        if role:
            await member.add_roles(role)

        # -----------------------------
        # ENVIAR PARA PAINEL DE CONFIRMAÇÃO
        # -----------------------------
        canal_confirmacao = guild.get_channel(config.CONFIRMAR_INSCRICAO_CHANNEL_ID)

        embed = discord.Embed(
            title="📋 Nova Inscrição",
            color=discord.Color.orange()
        )

        embed.add_field(name="Candidato", value=member.mention, inline=False)
        embed.add_field(name="Nome", value=self.nome.value)
        embed.add_field(name="Passaporte", value=self.passaporte.value)
        embed.add_field(name="Idade", value=self.idade.value)
        embed.add_field(name="Telefone", value=self.telefone.value)
        embed.add_field(name="Pagamento", value=self.pagamento.value)

        await canal_confirmacao.send(
            embed=embed,
            view=PainelRecrutamento(member, self.nome.value, self.passaporte.value)
        )

        await interaction.response.send_message(
            "✅ Sua inscrição foi enviada com sucesso.",
            ephemeral=True
        )


# -----------------------------
# BOTÕES DE APROVAÇÃO
# -----------------------------
class PainelRecrutamento(discord.ui.View):

    def __init__(self, membro, nome, passaporte):
        super().__init__(timeout=None)
        self.membro = membro
        self.nome = nome
        self.passaporte = passaporte
        self.decisao_realizada = False

    async def _finalizar_painel(self):
        self.decisao_realizada = True

        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True


    # -----------------------------
    # APROVAR
    # -----------------------------
    @discord.ui.button(label="Aprovar", style=discord.ButtonStyle.green)
    async def aprovar(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not any(role.id == config.CARGO_RECRUTADOR for role in interaction.user.roles):
            await interaction.response.send_message(
                "❌ Você não tem permissão.",
                ephemeral=True
            )
            return

        if self.decisao_realizada:
            await interaction.response.send_message(
                "⚠️ Esta inscrição já foi analisada.",
                ephemeral=True
            )
            return

        guild = interaction.guild

        role_inscrito = guild.get_role(config.CARGO_INSCRITO)
        role_aprovado = guild.get_role(config.CARGO_INSCRICAO_REALIZADA)

        if role_inscrito:
            await self.membro.remove_roles(role_inscrito)

        if role_aprovado:
            await self.membro.add_roles(role_aprovado)

        nick = montar_apelido("[INS-OK]", self.nome, self.passaporte)

        try:
            await self.membro.edit(nick=nick)
        except (discord.Forbidden, discord.HTTPException):
            pass

        await self._finalizar_painel()
        await interaction.message.edit(view=self)

        await interaction.response.send_message(
            f"✅ {self.membro.mention} foi aprovado."
        )


    # -----------------------------
    # REPROVAR
    # -----------------------------
    @discord.ui.button(label="Reprovar", style=discord.ButtonStyle.red)
    async def reprovar(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not any(role.id == config.CARGO_RECRUTADOR for role in interaction.user.roles):
            await interaction.response.send_message(
                "❌ Você não tem permissão.",
                ephemeral=True
            )
            return

        if self.decisao_realizada:
            await interaction.response.send_message(
                "⚠️ Esta inscrição já foi analisada.",
                ephemeral=True
            )
            return

        role_inscrito = interaction.guild.get_role(config.CARGO_INSCRITO)

        if role_inscrito:
            await self.membro.remove_roles(role_inscrito)

        try:
            await self.membro.edit(nick=None)
        except (discord.Forbidden, discord.HTTPException):
            pass

        await self._finalizar_painel()
        await interaction.message.edit(view=self)

        await interaction.response.send_message(
            f"❌ {self.membro.mention} foi reprovado."
        )


# -----------------------------
# BOTÃO DO EDITAL
# -----------------------------
class EditalView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Realizar Inscrição", style=discord.ButtonStyle.red)
    async def inscrever(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(InscricaoModal())


# -----------------------------
# COG PRINCIPAL
# -----------------------------
class Recrutamento(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    # -----------------------------
    # CRIAR EDITAL AUTOMÁTICO
    # -----------------------------
    @commands.Cog.listener()
    async def on_ready(self):

        guild = self.bot.get_guild(config.SERVIDOR_ID)

        if not guild:
            return

        canal = guild.get_channel(config.EDITAL_CHANNEL_ID)

        if not canal:
            print("❌ Canal do edital não encontrado")
            return

        async for msg in canal.history(limit=100):
            if msg.author == self.bot.user and msg.embeds:
                if msg.embeds[0].title == "🚒 EDITAL DE RECRUTAMENTO":
                    await msg.delete()

        embed = discord.Embed(
            title="🚒 EDITAL DE RECRUTAMENTO",
            description="""
Processo seletivo do **Corpo de Bombeiros de Litorânea**.

📘 **1ª Etapa — Prova Escrita**
• 20 questões de múltipla escolha  
• mínimo de **70% de acerto**

💪 **2ª Etapa — Teste de Aptidão Física**
• avaliação de comportamento  
• respeito à hierarquia  
• desempenho físico

💰 **Taxa de inscrição**
Passaporte **1460**  
Valor **R$200**

Clique no botão abaixo para realizar sua inscrição.
""",
            color=discord.Color.red()
        )

        await canal.send(embed=embed, view=EditalView())

        print("✅ Edital enviado automaticamente")


async def setup(bot):
    await bot.add_cog(Recrutamento(bot))
