import pytest
import time
from unittest.mock import Mock, AsyncMock
from domain.financeiro.entities import Financeiro
from domain.financeiro.enums import StatusPagamento
from domain.usuarios.entities import Usuario
from domain.usuarios.enums import PerfilUsuario, StatusUsuario
from domain.eventos.entities import Evento
from domain.presencas.entities import Presenca
from application.financeiro.listar_todos_financeiro_use_case import ListarTodosFinanceiroUseCase

@pytest.mark.asyncio
async def test_benchmark_listar_todos_financeiro_use_case():
    financeiro_repo = Mock()
    usuario_repo = Mock()
    evento_repo = Mock()
    presenca_repo = Mock()

    # Generate a large number of irrelevant financeiro records and a small number of relevant ones
    mes_referencia = "2023-10"
    mes_outro = "2023-09"

    registros_financeiros = [
        Financeiro(
            id=i,
            usuario_id=1,
            tipo="MENSALIDADE",
            valor=60.0,
            status_pagamento=StatusPagamento.PAGO,
            mes_referencia=mes_outro
        ) for i in range(1, 100001)
    ]
    registros_financeiros.extend([
        Financeiro(
            id=i,
            usuario_id=1,
            tipo="MENSALIDADE",
            valor=60.0,
            status_pagamento=StatusPagamento.PENDENTE,
            mes_referencia=mes_referencia
        ) for i in range(100001, 100011)
    ])

    financeiro_repo.listar_todos = AsyncMock(return_value=registros_financeiros)
    financeiro_repo.listar_por_mes = AsyncMock(return_value=[r for r in registros_financeiros if r.mes_referencia == mes_referencia])

    usuario_repo.listar_todos = AsyncMock(return_value=[
        Usuario(id=1, nome="User 1", telefone="11999999999", perfil=PerfilUsuario.MENSALISTA, status=StatusUsuario.ATIVO, senha_hash="hash", nota_admin=0, nota_galera_media=0.0, pontos_ranking=0)
    ])

    evento_repo.listar_todos = AsyncMock(return_value=[])
    presenca_repo.listar_por_eventos = AsyncMock(return_value=[])

    use_case = ListarTodosFinanceiroUseCase(
        financeiro_repo=financeiro_repo,
        usuario_repo=usuario_repo,
        evento_repo=evento_repo,
        presenca_repo=presenca_repo
    )

    start_time = time.perf_counter()
    resultados = await use_case.executar(mes_referencia)
    end_time = time.perf_counter()

    print(f"\nExecution time (baseline): {end_time - start_time:.6f} seconds")
    assert len(resultados) == 10
