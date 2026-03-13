import time

import discord
from discord.ext import commands

import config


QUESTOES_PROVA = [
    {
        "pergunta": "Quanto é 12 + 8?",
        "opcoes": {"A": "18", "B": "20", "C": "22", "D": "24"},
        "correta": "B",
    },
    {
        "pergunta": "Quanto é 25 - 9?",
        "opcoes": {"A": "14", "B": "15", "C": "16", "D": "17"},
        "correta": "C",
    },
    {
        "pergunta": "Quanto é 7 + 6?",
        "opcoes": {"A": "12", "B": "13", "C": "14", "D": "15"},
        "correta": "B",
    },
    {
        "pergunta": "Quanto é 30 - 12?",
        "opcoes": {"A": "16", "B": "17", "C": "18", "D": "19"},
        "correta": "C",
    },
    {
        "pergunta": "Quanto é 14 + 11?",
        "opcoes": {"A": "24", "B": "25", "C": "26", "D": "27"},
        "correta": "B",
    },
    {
        "pergunta": "Quanto é 40 - 18?",
        "opcoes": {"A": "21", "B": "22", "C": "23", "D": "24"},
        "correta": "B",
    },
    {
        "pergunta": "Quanto é 9 + 15?",
        "opcoes": {"A": "22", "B": "23", "C": "24", "D": "25"},
        "correta": "C",
    },
    {
        "pergunta": "Quanto é 27 - 8?",
        "opcoes": {"A": "17", "B": "18", "C": "19", "D": "20"},
        "correta": "C",
    },
    {
        "pergunta": "Quanto é 16 + 7?",
        "opcoes": {"A": "22", "B": "23", "C": "24", "D": "25"},
        "correta": "B",
    },
    {
        "pergunta": "Quanto é 50 - 21?",
        "opcoes": {"A": "27", "B": "28", "C": "29", "D": "30"},
        "correta": "C",
    },
    {
        "pergunta": "Quanto é 13 + 9?",
        "opcoes": {"A": "21", "B": "22", "C": "23", "D": "24"},
        "correta": "B",
    },
    {
        "pergunta": "Quanto é 34 - 16?",
        "opcoes": {"A": "17", "B": "18", "C": "19", "D": "20"},
        "correta": "B",
    },
    {
        "pergunta": "Quanto é 18 + 5?",
        "opcoes": {"A": "22", "B": "23", "C": "24", "D": "25"},
        "correta": "B",
    },
    {
        "pergunta": "Quanto é 45 - 19?",
        "opcoes": {"A": "24", "B": "25", "C": "26", "D": "27"},
        "correta": "C",
    },
    {
        "pergunta": "Quanto é 11 + 14?",
        "opcoes": {"A": "24", "B": "25", "C": "26", "D": "27"},
        "correta": "B",
    },
    {
        "pergunta": "Quanto é 38 - 13?",
        "opcoes": {"A": "24", "B": "25", "C": "26", "D": "27"},
        "correta": "B",
    },
    {
        "pergunta": "Quanto é 6 + 17?",
        "opcoes": {"A": "22", "B": "23", "C": "24", "D": "25"},
        "correta": "B",
    },
    {
        "pergunta": "Quanto é 29 - 11?",
        "opcoes": {"A": "16", "B": "17", "C": "18", "D": "19"},
        "correta": "C",
    },
    {
        "pergunta": "Quanto é 10 + 12?",
        "opcoes": {"A": "21", "B": "22", "C": "23", "D": "24"},
        "correta": "B",
    },
    {
        "pergunta": "Quanto é 33 - 15?",
        "opcoes": {"A": "17", "B": "18", "C": "19", "D": "20"},
        "correta": "B",
    },
]


class ProvaModal(discord.ui.Modal, title="Início da Prova Escrita"):
    nome = discord.ui.TextInput(label="Nome In-Game")
    passaporte = discord.ui.TextInput(label="Passaporte")

    def __init__(self, prova_cog: "Prova"):
        super().__init__()
        self.prova_cog = prova_cog

    async def on_submit(self, interaction: discord.Interaction):
        self.prova_cog.candidatos[interaction.user.id] = {
            "nome": self.nome.value,
            "passaporte": self.passaporte.value,
        }

        embed = discord.Embed(
            title="📘 Instruções da Prova",
            description=(
                "Você fará **20 questões** de múltipla escolha (A, B, C, D).\n"
                "• Tempo limite: **30 minutos**\n"
                "• Aprovação: **70%** de acerto (14 de 20)\n\n"
                "Ao clicar em **Estou de Acordo**, sua prova será iniciada."
            ),
            color=discord.Color.orange(),
        )

        await interaction.response.send_message(
            embed=embed,
            view=ConfirmacaoProvaView(self.prova_cog),
            ephemeral=True,
        )


class ConfirmacaoProvaView(discord.ui.View):
    def __init__(self, prova_cog: "Prova"):
        super().__init__(timeout=300)
        self.prova_cog = prova_cog

    @discord.ui.button(label="Estou de Acordo", style=discord.ButtonStyle.green)
    async def de_acordo(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.prova_cog.iniciar_prova(interaction)

    @discord.ui.button(label="Não Concordo", style=discord.ButtonStyle.red)
    async def nao_concordo(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "❌ Você cancelou a prova.",
            ephemeral=True,
        )


class QuestaoView(discord.ui.View):
    def __init__(self, prova_cog: "Prova"):
        super().__init__(timeout=1800)
        self.prova_cog = prova_cog

    async def responder(self, interaction: discord.Interaction, alternativa: str):
        await self.prova_cog.processar_resposta(interaction, alternativa)

    @discord.ui.button(label="A", style=discord.ButtonStyle.secondary)
    async def opcao_a(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.responder(interaction, "A")

    @discord.ui.button(label="B", style=discord.ButtonStyle.secondary)
    async def opcao_b(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.responder(interaction, "B")

    @discord.ui.button(label="C", style=discord.ButtonStyle.secondary)
    async def opcao_c(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.responder(interaction, "C")

    @discord.ui.button(label="D", style=discord.ButtonStyle.secondary)
    async def opcao_d(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.responder(interaction, "D")


class IniciarProvaView(discord.ui.View):
    def __init__(self, prova_cog: "Prova"):
        super().__init__(timeout=None)
        self.prova_cog = prova_cog

    @discord.ui.button(label="Iniciar Prova", style=discord.ButtonStyle.primary, custom_id="iniciar_prova_btn")
    async def iniciar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.channel_id != config.CANAL_PROVA_ID:
            await interaction.response.send_message(
                "❌ Este botão só pode ser usado no canal oficial da prova.",
                ephemeral=True,
            )
            return

        await interaction.response.send_modal(ProvaModal(self.prova_cog))


class Prova(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.candidatos = {}
        self.sessoes = {}

    def _embed_questao(self, user_id: int) -> discord.Embed:
        sessao = self.sessoes[user_id]
        idx = sessao["indice"]
        questao = QUESTOES_PROVA[idx]

        descricao = [f"**{letra})** {texto}" for letra, texto in questao["opcoes"].items()]
        faltam = max(0, int((1800 - (time.time() - sessao["inicio"])) // 60))

        return discord.Embed(
            title=f"📝 Prova - Questão {idx + 1}/20",
            description=f"{questao['pergunta']}\n\n" + "\n".join(descricao),
            color=discord.Color.blurple(),
        ).set_footer(text=f"Tempo restante aproximado: {faltam} minuto(s)")

    async def iniciar_prova(self, interaction: discord.Interaction):
        if interaction.user.id in self.sessoes:
            await interaction.response.send_message(
                "⚠️ Você já possui uma prova em andamento.",
                ephemeral=True,
            )
            return

        self.sessoes[interaction.user.id] = {
            "indice": 0,
            "acertos": 0,
            "inicio": time.time(),
        }

        await interaction.response.send_message(
            embed=self._embed_questao(interaction.user.id),
            view=QuestaoView(self),
            ephemeral=True,
        )

    async def processar_resposta(self, interaction: discord.Interaction, alternativa: str):
        sessao = self.sessoes.get(interaction.user.id)

        if not sessao:
            await interaction.response.send_message(
                "❌ Você não possui prova ativa.",
                ephemeral=True,
            )
            return

        if interaction.channel_id != config.CANAL_PROVA_ID:
            await interaction.response.send_message(
                "❌ A prova deve ser respondida no canal oficial.",
                ephemeral=True,
            )
            return

        if (time.time() - sessao["inicio"]) > 1800:
            await self.finalizar_prova(interaction, expirada=True)
            return

        questao = QUESTOES_PROVA[sessao["indice"]]
        if alternativa == questao["correta"]:
            sessao["acertos"] += 1

        sessao["indice"] += 1

        if sessao["indice"] >= len(QUESTOES_PROVA):
            await self.finalizar_prova(interaction, expirada=False)
            return

        await interaction.response.edit_message(
            embed=self._embed_questao(interaction.user.id),
            view=QuestaoView(self),
        )

    async def finalizar_prova(self, interaction: discord.Interaction, expirada: bool):
        sessao = self.sessoes.pop(interaction.user.id, None)
        if not sessao:
            return

        acertos = sessao["acertos"]
        porcentagem = (acertos / len(QUESTOES_PROVA)) * 100
        aprovado = (not expirada) and porcentagem >= 70

        guild = interaction.guild
        membro = interaction.user

        if aprovado:
            role_etapa1 = guild.get_role(config.CARGO_ETAPA_1_OK)
            role_civil = guild.get_role(config.CARGO_CIVIL)
            roles_manter = {r.id for r in (role_etapa1, role_civil) if r}
            roles_remover = [
                role
                for role in membro.roles
                if role != guild.default_role and role.id not in roles_manter
            ]
            if roles_remover:
                await membro.remove_roles(*roles_remover)

            roles_adicionar = [r for r in (role_etapa1, role_civil) if r and r not in membro.roles]
            if roles_adicionar:
                await membro.add_roles(*roles_adicionar)

            sala_taf = guild.get_channel(config.SALA_TAF_ID)
            sala_atual = getattr(membro.voice, "channel", None)
            if (
                isinstance(sala_taf, discord.VoiceChannel)
                and isinstance(sala_atual, discord.VoiceChannel)
                and sala_atual.id == config.SALA_PROVA_ID
            ):
                try:
                    await membro.move_to(sala_taf)
                except (discord.Forbidden, discord.HTTPException):
                    pass

            if membro.nick:
                novo_nick = membro.nick.replace("[INS-OK]", "[ETP1-OK]")
            else:
                novo_nick = None

            if novo_nick and novo_nick != membro.nick:
                try:
                    await membro.edit(nick=novo_nick[:32])
                except (discord.Forbidden, discord.HTTPException):
                    pass
        else:
            civil = guild.get_role(config.CARGO_CIVIL)
            remover = [r for r in membro.roles if r != guild.default_role and (not civil or r.id != civil.id)]
            if remover:
                await membro.remove_roles(*remover)
            if civil and civil not in membro.roles:
                await membro.add_roles(civil)

        resultado = guild.get_channel(config.CANAL_RESULTADO_PROVA_ID)
        dados = self.candidatos.get(membro.id, {})

        if resultado:
            embed = discord.Embed(
                title="📢 Resultado da Prova Escrita",
                color=discord.Color.green() if aprovado else discord.Color.red(),
            )
            embed.add_field(name="Candidato", value=membro.mention, inline=False)
            embed.add_field(name="Nome", value=dados.get("nome", "Não informado"), inline=True)
            embed.add_field(name="Passaporte", value=dados.get("passaporte", "Não informado"), inline=True)
            embed.add_field(name="Acertos", value=f"{acertos}/20 ({porcentagem:.0f}%)", inline=False)
            embed.add_field(name="Status", value="✅ APROVADO" if aprovado else "❌ REPROVADO", inline=False)
            if expirada:
                embed.set_footer(text="Prova encerrada por tempo limite.")

            await resultado.send(embed=embed)

        mensagem_final = (
            f"✅ Você foi aprovado com **{acertos}/20** ({porcentagem:.0f}%)."
            if aprovado
            else f"❌ Você foi reprovado com **{acertos}/20** ({porcentagem:.0f}%)."
        )

        if expirada:
            mensagem_final += "\n⏰ Sua prova foi finalizada por tempo limite de 30 minutos."

        await interaction.response.edit_message(content=mensagem_final, embed=None, view=None)

    @commands.Cog.listener()
    async def on_ready(self):
        guild = self.bot.get_guild(config.SERVIDOR_ID)
        if not guild:
            return

        canal_prova = guild.get_channel(config.CANAL_PROVA_ID)
        if not canal_prova:
            return

        self.bot.add_view(IniciarProvaView(self))

        async for msg in canal_prova.history(limit=50):
            if msg.author == self.bot.user and msg.components:
                for linha in msg.components:
                    for componente in linha.children:
                        if getattr(componente, "custom_id", None) == "iniciar_prova_btn":
                            return

        embed = discord.Embed(
            title="📘 Prova Escrita - Etapa 1",
            description=(
                "Clique no botão abaixo para iniciar sua prova.\n"
                "Você precisará informar **Nome** e **Passaporte** antes de começar."
            ),
            color=discord.Color.red(),
        )
        await canal_prova.send(embed=embed, view=IniciarProvaView(self))


async def setup(bot: commands.Bot):
    await bot.add_cog(Prova(bot))
