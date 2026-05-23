from typing import List
from domain.financeiro.repositories import FinanceiroRepository
from domain.financeiro.enums import StatusPagamento
from domain.financeiro.entities import Financeiro
from core.exceptions import RecursoNaoEncontradoError

class ListarFinanceiroUseCase:
    def __init__(self, financeiro_repo: FinanceiroRepository):
        self.financeiro_repo = financeiro_repo

    async def executar(self, usuario_id: int) -> List[Financeiro]:
        return await self.financeiro_repo.listar_por_usuario(usuario_id)

class BaixarPagamentoUseCase:
    def __init__(self, financeiro_repo: FinanceiroRepository):
        self.financeiro_repo = financeiro_repo

    async def executar(self, pagamento_id: int) -> Financeiro:
        pagamento = await self.financeiro_repo.buscar_por_id(pagamento_id)
        if not pagamento:
            raise RecursoNaoEncontradoError("Pagamento não encontrado")
        
        pagamento.status_pagamento = StatusPagamento.PAGO
        return await self.financeiro_repo.salvar(pagamento)
