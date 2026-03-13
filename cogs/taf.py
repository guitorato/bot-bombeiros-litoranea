import discord
from discord.ext import commands

import config
from cogs.recrutamento import montar_apelido


DESCRICAO_TAF = (
    "A etapa 2 será o **Teste de Aptidão Física (TAF)**.\n\n"
    "Para ser aprovado, o recruta deve manter disciplina, postura e concluir os exercícios conforme orientação do instrutor.\n\n"
    "**1º Exercício**\n"
    "• Fazer **20 flexões** (comando: `e flexao`)\n\n"
    "**2º Exercício**\n"
    "• Fazer **20 barras** (comando: `e malhar2`)\n\n"
    "**3º Exercício — Pista de obstáculos**\n"
    "• **Pista 1:** correr da linha inicial até o final e concluir com **10 flexões**\n"
    "• **Pista 2:** zigue-zague entre os cones, respeitando o limite da linha\n"
    "• **Pista 3:** correr até o fim e concluir com **10 flexões**\n"
    "• **Pista 4:** pular os obstáculos e passar ao lado dos cones\n"
    "• **Pista final:** pular as barras e, ao terminar, aguardar trotando (`e trotar`) até autorização do instrutor para descanso\n\n"
    "Ao confirmar, sua solicitação será enviada para avaliação do recrutador."
)


class MotivoReprovacaoModal(discord.ui.Modal, title="Reprovar TAF"):
    motivo = discord.ui.TextInput(
        label="Motivo da reprovação",
        style=discord.TextStyle.paragraph,
        placeholder="Descreva de forma clara o motivo da reprovação...",
        required=True,
        max_length=500,
    )

    def __init__(self, view: "AvaliacaoTAFView"):
        super().__init__()
        self.view = view

    async def on_submit(self, interaction: discord.Interaction):
        await self.view.reprovar_com_motivo(interaction, self.motivo.value)


class AvaliacaoTAFView(discord.ui.View):
    def __init__(self, membro_id: int, nome: str, passaporte: str):
        super().__init__(timeout=None)
        self.membro_id = membro_id
        self.nome = nome
        self.passaporte = passaporte
        self.decisao_realizada = False

    async def _validar_recrutador(self, interaction: discord.Interaction) -> bool:
        if not any(role.id == config.CARGO_RECRUTADOR for role in interaction.user.roles):
            await interaction.response.send_message("❌ Você não tem permissão.", ephemeral=True)
            return False

        if self.decisao_realizada:
            await interaction.response.send_message("⚠️ Este TAF já foi avaliado.", ephemeral=True)
            return False

        return True

    async def _finalizar(self, interaction: discord.Interaction):
        self.decisao_realizada = True
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        await interaction.message.edit(view=self)

    @discord.ui.button(label="Aprovar", style=discord.ButtonStyle.green)
    async def aprovar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._validar_recrutador(interaction):
            return

        guild = interaction.guild
        membro = guild.get_member(self.membro_id)
        if not membro:
            await interaction.response.send_message("❌ Não foi possível localizar o recruta.", ephemeral=True)
            return

        role_etapa_1 = guild.get_role(config.CARGO_ETAPA_1_OK)
        role_civil = guild.get_role(config.CARGO_CIVIL)
        role_bombeiro = guild.get_role(config.CARGO_BOMBEIRO_MILITAR)
        role_aluno = guild.get_role(config.CARGO_ALUNO)

        remover = [role for role in (role_etapa_1, role_civil) if role and role in membro.roles]
        if remover:
            await membro.remove_roles(*remover)

        adicionar = [role for role in (role_bombeiro, role_aluno) if role and role not in membro.roles]
        if adicionar:
            await membro.add_roles(*adicionar)

        nick = montar_apelido("[Aluno]", self.nome, self.passaporte)
        try:
            await membro.edit(nick=nick)
        except (discord.Forbidden, discord.HTTPException):
            pass

        await self._finalizar(interaction)
        await interaction.response.send_message(f"✅ {membro.mention} foi aprovado no TAF.")

    @discord.ui.button(label="Reprovar", style=discord.ButtonStyle.red)
    async def reprovar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._validar_recrutador(interaction):
            return
        await interaction.response.send_modal(MotivoReprovacaoModal(self))

    async def reprovar_com_motivo(self, interaction: discord.Interaction, motivo: str):
        guild = interaction.guild
        membro = guild.get_member(self.membro_id)
        if not membro:
            await interaction.response.send_message("❌ Não foi possível localizar o recruta.", ephemeral=True)
            return

        role_etapa_1 = guild.get_role(config.CARGO_ETAPA_1_OK)
        if role_etapa_1 and role_etapa_1 in membro.roles:
            await membro.remove_roles(role_etapa_1)

        try:
            await membro.send(
                "❌ Você foi reprovado no **Teste de Aptidão Física (TAF)**.\n"
                f"**Motivo informado:** {motivo}"
            )
        except (discord.Forbidden, discord.HTTPException):
            pass

        await self._finalizar(interaction)
        await interaction.response.send_message(
            f"❌ {membro.mention} foi reprovado no TAF. Motivo registrado e enviado ao recruta.",
            ephemeral=False,
        )


class ConfirmacaoTAFView(discord.ui.View):
    def __init__(self, taf_cog: "TAF", nome: str, passaporte: str):
        super().__init__(timeout=300)
        self.taf_cog = taf_cog
        self.nome = nome
        self.passaporte = passaporte

    @discord.ui.button(label="Estou de acordo", style=discord.ButtonStyle.green)
    async def de_acordo(self, interaction: discord.Interaction, button: discord.ui.Button):
        canal_avaliacao = interaction.guild.get_channel(config.CANAL_AVALIAR_TAF_ID)
        if not canal_avaliacao:
            await interaction.response.send_message("❌ Canal de avaliação do TAF não encontrado.", ephemeral=True)
            return

        embed = discord.Embed(title="🏋️ Avaliação de TAF", color=discord.Color.orange())
        embed.add_field(name="Recruta", value=interaction.user.mention, inline=False)
        embed.add_field(name="Nome", value=self.nome, inline=True)
        embed.add_field(name="Passaporte", value=self.passaporte, inline=True)
        embed.add_field(name="Status", value="Aguardando avaliação do recrutador", inline=False)

        await canal_avaliacao.send(
            embed=embed,
            view=AvaliacaoTAFView(interaction.user.id, self.nome, self.passaporte),
        )

        await interaction.response.send_message(
            "✅ Sua solicitação de TAF foi enviada para o canal de avaliação.",
            ephemeral=True,
        )

    @discord.ui.button(label="Não estou de acordo", style=discord.ButtonStyle.red)
    async def nao_de_acordo(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "❌ Você cancelou a solicitação de avaliação do TAF.",
            ephemeral=True,
        )


class IniciarTAFView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Iniciar TAF", style=discord.ButtonStyle.primary, custom_id="iniciar_taf_btn")
    async def iniciar_taf(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.channel_id != config.CANAL_TAF_ID:
            await interaction.response.send_message(
                "❌ Este botão só pode ser usado no canal oficial do TAF.",
                ephemeral=True,
            )
            return

        nome, passaporte = self._extrair_dados_recruta(interaction.user)

        embed = discord.Embed(
            title="🏋️ Etapa 2 - Teste de Aptidão Física",
            description=DESCRICAO_TAF,
            color=discord.Color.blurple(),
        )
        embed.set_footer(text="Leia com atenção antes de confirmar.")

        await interaction.response.send_message(
            embed=embed,
            view=ConfirmacaoTAFView(interaction.client.get_cog("TAF"), nome, passaporte),
            ephemeral=True,
        )

    @staticmethod
    def _extrair_dados_recruta(membro: discord.Member) -> tuple[str, str]:
        nome_padrao = membro.display_name
        passaporte_padrao = "Não informado"

        if not membro.display_name or "|" not in membro.display_name:
            return nome_padrao, passaporte_padrao

        esquerda, direita = membro.display_name.rsplit("|", maxsplit=1)
        passaporte = direita.strip() or passaporte_padrao
        partes_nome = esquerda.strip().split(" ", maxsplit=1)
        nome = partes_nome[1].strip() if len(partes_nome) > 1 else esquerda.strip()

        return nome or nome_padrao, passaporte


class TAF(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        guild = self.bot.get_guild(config.SERVIDOR_ID)
        if not guild:
            return

        canal_taf = guild.get_channel(config.CANAL_TAF_ID)
        if not canal_taf:
            return

        self.bot.add_view(IniciarTAFView())

        async for msg in canal_taf.history(limit=50):
            if msg.author != self.bot.user or not msg.components:
                continue

            for linha in msg.components:
                for componente in linha.children:
                    if getattr(componente, "custom_id", None) == "iniciar_taf_btn":
                        return

        embed = discord.Embed(
            title="🏋️ Etapa 2 - TAF",
            description="Clique no botão abaixo para iniciar as instruções do Teste de Aptidão Física.",
            color=discord.Color.red(),
        )
        await canal_taf.send(embed=embed, view=IniciarTAFView())


async def setup(bot: commands.Bot):
    await bot.add_cog(TAF(bot))
