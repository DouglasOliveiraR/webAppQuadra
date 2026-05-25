from domain.financeiro.repositories import FinanceiroRepository
from domain.financeiro.enums import StatusPagamento
from domain.eventos.repositories import EventoRepository

class ObterTransparenciaUseCase:
    def __init__(self, financeiro_repo: FinanceiroRepository, evento_repo: EventoRepository):
        self.financeiro_repo = financeiro_repo
        self.evento_repo = evento_repo

    async def executar(self, mes: str) -> dict:
        todos = await self.financeiro_repo.listar_todos()
        do_mes = [r for r in todos if r.mes_referencia == mes and r.status_pagamento == StatusPagamento.PAGO]
        
        arrecadado = sum(r.valor for r in do_mes)
        
        custo_quadra = 0.0
        eventos = await self.evento_repo.listar_todos()
        if eventos:
            eventos_do_mes = [e for e in eventos if e.data_jogo.strftime("%Y-%m") == mes]
            if eventos_do_mes:
                eventos_ordenados = sorted(eventos_do_mes, key=lambda e: e.id, reverse=True)
                ultimo = eventos_ordenados[0]
                custo_quadra = ultimo.custo_quadra or 0.0
                
        saldo = arrecadado - custo_quadra
        return {
            "arrecadado": arrecadado,
            "custo_quadra": custo_quadra,
            "saldo": saldo,
            "mes_referencia": mes
        }
