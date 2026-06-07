import pytest
from unittest.mock import AsyncMock
from datetime import date, time

from application.eventos.cancelar_evento_use_case import CancelarEventoUseCase
from domain.eventos.entities import Evento
from domain.eventos.enums import StatusEvento
from core.exceptions import RegraDeNegocioError

@pytest.mark.asyncio
async def test_cancelar_evento_sucesso():
    evento_repo = AsyncMock()

    evento = Evento(
        id=1,
        data_jogo=date(2026, 6, 1),
        hora_inicio=time(19, 0),
        hora_fim=time(21, 0),
        status_evento=StatusEvento.PRESENCA_ABERTA,
        flag_churrasco=False,
        valor_churrasco=0.0
    )

    evento_repo.buscar_por_id.return_value = evento

    use_case = CancelarEventoUseCase(evento_repo)
    resultado = await use_case.executar(evento_id=1)

    assert resultado.id == 1
    assert resultado.status_evento == StatusEvento.CANCELADO
    evento_repo.buscar_por_id.assert_called_once_with(1)
    evento_repo.salvar.assert_called_once_with(evento)

@pytest.mark.asyncio
async def test_cancelar_evento_nao_encontrado_erro():
    evento_repo = AsyncMock()
    evento_repo.buscar_por_id.return_value = None

    use_case = CancelarEventoUseCase(evento_repo)

    with pytest.raises(RegraDeNegocioError, match="Evento não encontrado"):
        await use_case.executar(evento_id=999)

    evento_repo.buscar_por_id.assert_called_once_with(999)
    evento_repo.salvar.assert_not_called()
