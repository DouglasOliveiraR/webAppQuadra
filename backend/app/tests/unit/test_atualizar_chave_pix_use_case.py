import pytest
from unittest.mock import AsyncMock
from datetime import date, time
from application.eventos.atualizar_chave_pix_use_case import AtualizarChavePixUseCase
from domain.eventos.entities import Evento
from domain.eventos.enums import StatusEvento
from core.exceptions import RegraDeNegocioError

@pytest.mark.asyncio
async def test_atualizar_chave_pix_sucesso():
    evento_repo = AsyncMock()
    evento = Evento(
        id=1,
        data_jogo=date(2026, 6, 1),
        hora_inicio=time(19, 0),
        hora_fim=time(21, 0),
        status_evento=StatusEvento.PRESENCA_ABERTA,
        flag_churrasco=False,
        valor_churrasco=0.0,
        chave_pix="pix_antigo"
    )
    evento_repo.buscar_por_id.return_value = evento

    use_case = AtualizarChavePixUseCase(evento_repo)
    resultado = await use_case.executar(1, "novo_pix")

    assert resultado.chave_pix == "novo_pix"
    evento_repo.buscar_por_id.assert_called_once_with(1)
    evento_repo.salvar.assert_called_once_with(evento)

@pytest.mark.asyncio
async def test_atualizar_chave_pix_evento_nao_encontrado():
    evento_repo = AsyncMock()
    evento_repo.buscar_por_id.return_value = None

    use_case = AtualizarChavePixUseCase(evento_repo)

    with pytest.raises(RegraDeNegocioError, match="Evento não encontrado"):
        await use_case.executar(1, "novo_pix")

    evento_repo.buscar_por_id.assert_called_once_with(1)
    evento_repo.salvar.assert_not_called()
