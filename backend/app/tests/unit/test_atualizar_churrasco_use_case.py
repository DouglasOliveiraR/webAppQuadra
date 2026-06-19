import pytest
from unittest.mock import AsyncMock
from datetime import date, time
from application.eventos.atualizar_churrasco_use_case import AtualizarChurrascoUseCase
from domain.eventos.entities import Evento
from domain.eventos.enums import StatusEvento
from domain.usuarios.entities import Usuario
from domain.usuarios.enums import PerfilUsuario, StatusUsuario
from core.exceptions import RegraDeNegocioError

@pytest.fixture
def mock_evento():
    return Evento(
        id=1,
        data_jogo=date(2026, 6, 1),
        hora_inicio=time(19, 0),
        hora_fim=time(21, 0),
        status_evento=StatusEvento.PRESENCA_ABERTA,
        flag_churrasco=False,
        valor_churrasco=0.0,
        chave_pix="pix_antigo"
    )

@pytest.fixture
def mock_usuarios():
    return [
        Usuario(id=1, nome="Admin", telefone="11", senha_hash="x", perfil=PerfilUsuario.ADMIN, status=StatusUsuario.ATIVO, nota_admin=10, nota_galera_media=10.0, pontos_ranking=0),
        Usuario(id=2, nome="Mensalista", telefone="22", senha_hash="x", perfil=PerfilUsuario.MENSALISTA, status=StatusUsuario.ATIVO, nota_admin=10, nota_galera_media=10.0, pontos_ranking=0),
        Usuario(id=3, nome="Avulso", telefone="33", senha_hash="x", perfil=PerfilUsuario.AVULSO, status=StatusUsuario.ATIVO, nota_admin=10, nota_galera_media=10.0, pontos_ranking=0)
    ]

@pytest.mark.asyncio
async def test_atualizar_churrasco_evento_nao_encontrado():
    evento_repo = AsyncMock()
    evento_repo.buscar_por_id.return_value = None
    usuario_repo = AsyncMock()

    use_case = AtualizarChurrascoUseCase(evento_repo, usuario_repo)

    with pytest.raises(RegraDeNegocioError, match="Evento não encontrado"):
        await use_case.executar(1, True, 50.0)

    evento_repo.buscar_por_id.assert_called_once_with(1)
    evento_repo.salvar.assert_not_called()

@pytest.mark.asyncio
async def test_atualizar_churrasco_sucesso_com_notificacao(mock_evento, mock_usuarios):
    evento_repo = AsyncMock()
    evento_repo.buscar_por_id.return_value = mock_evento

    usuario_repo = AsyncMock()
    usuario_repo.listar_todos.return_value = mock_usuarios

    notificacao_uc = AsyncMock()

    use_case = AtualizarChurrascoUseCase(evento_repo, usuario_repo, notificacao_uc)
    resultado = await use_case.executar(1, True, 50.0)

    assert resultado.flag_churrasco is True
    assert resultado.valor_churrasco == 50.0

    evento_repo.buscar_por_id.assert_called_once_with(1)
    evento_repo.salvar.assert_called_once_with(mock_evento)

    usuario_repo.listar_todos.assert_called_once()
    notificacao_uc.executar.assert_called_once_with(
        titulo="Vai ter Churras! 🍖🍻",
        corpo="O admin ativou o churrasco da pelada no valor de R$50.00. Acesse o app para confirmar se vai!",
        url="/",
        usuarios_ids=[1, 2]
    )

@pytest.mark.asyncio
async def test_atualizar_churrasco_sucesso_sem_alvos(mock_evento):
    evento_repo = AsyncMock()
    evento_repo.buscar_por_id.return_value = mock_evento

    usuario_repo = AsyncMock()
    usuario_repo.listar_todos.return_value = [
        Usuario(id=3, nome="Avulso", telefone="33", senha_hash="x", perfil=PerfilUsuario.AVULSO, status=StatusUsuario.ATIVO, nota_admin=10, nota_galera_media=10.0, pontos_ranking=0)
    ]

    notificacao_uc = AsyncMock()

    use_case = AtualizarChurrascoUseCase(evento_repo, usuario_repo, notificacao_uc)
    resultado = await use_case.executar(1, True, 50.0)

    assert resultado.flag_churrasco is True
    assert resultado.valor_churrasco == 50.0

    usuario_repo.listar_todos.assert_called_once()
    notificacao_uc.executar.assert_not_called()

@pytest.mark.asyncio
async def test_atualizar_churrasco_sucesso_notificacao_excecao(mock_evento, mock_usuarios):
    evento_repo = AsyncMock()
    evento_repo.buscar_por_id.return_value = mock_evento

    usuario_repo = AsyncMock()
    usuario_repo.listar_todos.return_value = mock_usuarios

    notificacao_uc = AsyncMock()
    notificacao_uc.executar.side_effect = Exception("Push falhou")

    use_case = AtualizarChurrascoUseCase(evento_repo, usuario_repo, notificacao_uc)

    # Exceção deve ser tratada, não propagada
    resultado = await use_case.executar(1, True, 50.0)

    assert resultado.flag_churrasco is True
    assert resultado.valor_churrasco == 50.0
    notificacao_uc.executar.assert_called_once()

@pytest.mark.asyncio
async def test_atualizar_churrasco_flag_false(mock_evento, mock_usuarios):
    evento_repo = AsyncMock()
    evento_repo.buscar_por_id.return_value = mock_evento

    usuario_repo = AsyncMock()
    notificacao_uc = AsyncMock()

    use_case = AtualizarChurrascoUseCase(evento_repo, usuario_repo, notificacao_uc)
    resultado = await use_case.executar(1, False, 0.0)

    assert resultado.flag_churrasco is False
    assert resultado.valor_churrasco == 0.0

    evento_repo.salvar.assert_called_once_with(mock_evento)
    usuario_repo.listar_todos.assert_not_called()
    notificacao_uc.executar.assert_not_called()

@pytest.mark.asyncio
async def test_atualizar_churrasco_sem_use_case_notificacao(mock_evento, mock_usuarios):
    evento_repo = AsyncMock()
    evento_repo.buscar_por_id.return_value = mock_evento

    usuario_repo = AsyncMock()

    use_case = AtualizarChurrascoUseCase(evento_repo, usuario_repo)
    resultado = await use_case.executar(1, True, 50.0)

    assert resultado.flag_churrasco is True
    assert resultado.valor_churrasco == 50.0

    evento_repo.salvar.assert_called_once_with(mock_evento)
    usuario_repo.listar_todos.assert_not_called()
