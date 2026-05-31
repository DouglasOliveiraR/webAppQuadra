import pytest
import time
from domain.eventos.entities import Evento
from domain.eventos.enums import StatusEvento
from domain.financeiro.entities import Financeiro
from domain.financeiro.enums import StatusPagamento
from application.eventos.atualizar_mensalidade_use_case import AtualizarMensalidadeUseCase
from datetime import datetime, date

class MockEventoRepo:
    async def buscar_por_id(self, evento_id):
        return Evento(id=evento_id, data_jogo=date.today(), hora_inicio=datetime.now().time(), hora_fim=datetime.now().time(), status_evento=StatusEvento.AGENDADO, flag_churrasco=False, valor_churrasco=0.0, valor_mensalidade=10.0)
    async def salvar(self, evento):
        return evento

class MockFinanceiroRepo:
    def __init__(self, registros):
        self.registros = registros
        self.salvar_count = 0
        self.salvar_lote_count = 0

    async def listar_todos(self):
        return self.registros

    async def salvar(self, registro):
        self.salvar_count += 1
        return registro

    async def salvar_lote(self, registros):
        self.salvar_lote_count += 1
        return registros

@pytest.mark.asyncio
async def test_benchmark_atualizar_mensalidade():
    # Setup 1000 registros
    registros = []
    mes_ref = date.today().strftime("%Y-%m")
    for i in range(10000):
        registros.append(Financeiro(id=i, usuario_id=1, tipo="MENSALIDADE", valor=10.0, status_pagamento=StatusPagamento.PENDENTE, mes_referencia=mes_ref))

    financeiro_repo = MockFinanceiroRepo(registros)
    evento_repo = MockEventoRepo()

    use_case = AtualizarMensalidadeUseCase(evento_repo, financeiro_repo)

    start_time = time.perf_counter()
    await use_case.executar(1, 20.0)
    end_time = time.perf_counter()

    print(f"\nTime taken: {end_time - start_time:.4f} seconds")
    print(f"salvar calls: {financeiro_repo.salvar_count}")
    print(f"salvar_lote calls: {financeiro_repo.salvar_lote_count}")
    assert financeiro_repo.salvar_count == 10000 or financeiro_repo.salvar_lote_count == 1
