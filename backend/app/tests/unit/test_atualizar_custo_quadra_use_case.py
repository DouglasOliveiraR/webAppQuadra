import pytest
from unittest.mock import AsyncMock
from application.eventos.atualizar_custo_quadra_use_case import AtualizarCustoQuadraUseCase
from domain.eventos.entities import Evento
from domain.eventos.enums import StatusEvento
from core.exceptions import RegraDeNegocioError
from datetime import date, time

@pytest.mark.asyncio
async def test_atualizar_custo_quadra_sucesso():
    evento_repo = AsyncMock()

    evento = Evento(
        id=1,
        data_jogo=date(2026, 6, 1),
        hora_inicio=time(19, 0),
        hora_fim=time(21, 0),
        status_evento=StatusEvento.PRESENCA_ABERTA,
        flag_churrasco=False,
        valor_churrasco=0.0,
        custo_quadra=0.0
    )

    evento_repo.buscar_por_id.return_value = evento

    use_case = AtualizarCustoQuadraUseCase(evento_repo)

    evento_atualizado = await use_case.executar(1, 150.0)

    assert evento_atualizado.custo_quadra == 150.0
    evento_repo.buscar_por_id.assert_called_once_with(1)
    evento_repo.salvar.assert_called_once_with(evento)

@pytest.mark.asyncio
async def test_atualizar_custo_quadra_evento_nao_encontrado():
    evento_repo = AsyncMock()

    evento_repo.buscar_por_id.return_value = None

    use_case = AtualizarCustoQuadraUseCase(evento_repo)

    with pytest.raises(RegraDeNegocioError, match="Evento não encontrado"):
        await use_case.executar(999, 150.0)

    evento_repo.buscar_por_id.assert_called_once_with(999)
    evento_repo.salvar.assert_not_called()
