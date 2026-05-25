from domain.eventos.repositories import EventoRepository
from domain.financeiro.repositories import FinanceiroRepository
from domain.financeiro.enums import StatusPagamento
from core.exceptions import RegraDeNegocioError
from domain.eventos.entities import Evento

class AtualizarMensalidadeUseCase:
    def __init__(self, evento_repo: EventoRepository, financeiro_repo: FinanceiroRepository):
        self.evento_repo = evento_repo
        self.financeiro_repo = financeiro_repo

    async def executar(self, evento_id: int, valor_mensalidade: float) -> Evento:
        evento = await self.evento_repo.buscar_por_id(evento_id)
        if not evento:
            raise RegraDeNegocioError("Evento não encontrado")

        evento.valor_mensalidade = valor_mensalidade
        await self.evento_repo.salvar(evento)

        # Propaga a alteração de mensalidade para os registros pendentes do mês de referência
        if valor_mensalidade > 0:
            mes_ref = evento.data_jogo.strftime("%Y-%m")
            registros = await self.financeiro_repo.listar_todos()
            for r in registros:
                if r.tipo == "MENSALIDADE" and r.mes_referencia == mes_ref and r.status_pagamento == StatusPagamento.PENDENTE:
                    r.valor = valor_mensalidade
                    await self.financeiro_repo.salvar(r)

        return evento
