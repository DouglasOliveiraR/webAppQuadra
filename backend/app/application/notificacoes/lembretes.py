import logging
from datetime import datetime
from application.notificacoes.disparar_notificacao import DispararNotificacaoUseCase
from domain.financeiro.repositories import FinanceiroRepository
from domain.financeiro.enums import StatusPagamento
from domain.eventos.repositories import EventoRepository
from domain.eventos.enums import StatusEvento
from domain.presencas.repositories import PresencaRepository
from domain.usuarios.repositories import UsuarioRepository
from domain.usuarios.enums import Perfil

logger = logging.getLogger(__name__)

class NotificarMensalidadeAtrasadaUseCase:
    def __init__(self, financeiro_repo: FinanceiroRepository, disparar_notificacao_uc: DispararNotificacaoUseCase):
        self.financeiro_repo = financeiro_repo
        self.disparar_notificacao_uc = disparar_notificacao_uc

    async def executar(self):
        logger.info("Executando job de lembrete de mensalidade...")
        mes_atual = datetime.now().strftime("%Y-%m")
        todos_financeiros = await self.financeiro_repo.listar_todos()
        
        usuarios_pendentes = set()
        for f in todos_financeiros:
            if f.tipo == "MENSALIDADE" and f.mes_referencia == mes_atual and f.status_pagamento == StatusPagamento.PENDENTE:
                if f.usuario_id:
                    usuarios_pendentes.add(f.usuario_id)

        if usuarios_pendentes:
            logger.info(f"Notificando {len(usuarios_pendentes)} usuarios sobre mensalidade atrasada.")
            await self.disparar_notificacao_uc.executar(
                titulo="Mensalidade Pendente 💰",
                corpo="Fala jogador! Não esqueça de acertar a mensalidade deste mês. A pelada agradece!",
                url="/financeiro",
                usuarios_ids=list(usuarios_pendentes)
            )

class NotificarPresencaPendenteUseCase:
    def __init__(
        self, 
        evento_repo: EventoRepository, 
        usuario_repo: UsuarioRepository, 
        presenca_repo: PresencaRepository, 
        disparar_notificacao_uc: DispararNotificacaoUseCase
    ):
        self.evento_repo = evento_repo
        self.usuario_repo = usuario_repo
        self.presenca_repo = presenca_repo
        self.disparar_notificacao_uc = disparar_notificacao_uc

    async def executar(self):
        logger.info("Executando job de lembrete de presença...")
        eventos = await self.evento_repo.listar_todos()
        evento_aberto = next((e for e in eventos if e.status_evento == StatusEvento.PRESENCA_ABERTA), None)

        if not evento_aberto:
            return

        todos_usuarios = await self.usuario_repo.listar_todos()
        usuarios_validos = [u for u in todos_usuarios if u.perfil in [Perfil.MENSALISTA, Perfil.AVULSO]]
        
        presencas = await self.presenca_repo.listar_por_evento(evento_aberto.id)
        usuarios_com_presenca = {p.usuario_id for p in presencas}

        usuarios_pendentes = [u.id for u in usuarios_validos if u.id not in usuarios_com_presenca]

        if usuarios_pendentes:
            logger.info(f"Notificando {len(usuarios_pendentes)} usuarios sobre presença pendente.")
            await self.disparar_notificacao_uc.executar(
                titulo="Confirmar Presença ⚽",
                corpo="A lista de presença já está aberta! Entre no app e confirme se você vai jogar.",
                url="/",
                usuarios_ids=usuarios_pendentes
            )
