import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, date, time
from application.financeiro.virada_mes_use_case import ViradaMesUseCase
from domain.usuarios.entities import Usuario
from domain.usuarios.enums import PerfilUsuario, StatusUsuario
from domain.eventos.entities import Evento
from domain.eventos.enums import StatusEvento
from domain.financeiro.entities import Financeiro
from domain.financeiro.enums import StatusPagamento

@pytest.fixture
def mock_financeiro_repo():
    return AsyncMock()

@pytest.fixture
def mock_usuario_repo():
    return AsyncMock()

@pytest.fixture
def mock_evento_repo():
    return AsyncMock()

@pytest.fixture
def use_case(mock_financeiro_repo, mock_usuario_repo, mock_evento_repo):
    return ViradaMesUseCase(mock_financeiro_repo, mock_usuario_repo, mock_evento_repo)

@pytest.mark.asyncio
@patch('application.financeiro.virada_mes_use_case.datetime')
async def test_virada_mes_sem_usuarios_alvo(mock_datetime, use_case, mock_usuario_repo):
    mock_datetime.now.return_value = datetime(2023, 10, 1)

    # Mocking usuarios (none of them target)
    mock_usuario_repo.listar_todos.return_value = [
        Usuario(
            id=1, nome="Avulso", telefone="111", senha_hash="",
            perfil=PerfilUsuario.AVULSO, status=StatusUsuario.ATIVO,
            nota_admin=3, nota_galera_media=3.0, pontos_ranking=0
        ),
        Usuario(
            id=2, nome="Inativo", telefone="222", senha_hash="",
            perfil=PerfilUsuario.MENSALISTA, status=StatusUsuario.INATIVO,
            nota_admin=3, nota_galera_media=3.0, pontos_ranking=0
        )
    ]

    resultado = await use_case.executar()

    assert resultado == 0
    use_case.financeiro_repo.listar_por_usuarios_e_mes.assert_not_called()
    use_case.financeiro_repo.salvar_lote.assert_not_called()

@pytest.mark.asyncio
@patch('application.financeiro.virada_mes_use_case.datetime')
async def test_virada_mes_com_mensalidades_existentes(mock_datetime, use_case, mock_usuario_repo, mock_financeiro_repo):
    mock_datetime.now.return_value = datetime(2023, 10, 1)

    usuario1 = Usuario(
        id=1, nome="Mensalista", telefone="111", senha_hash="",
        perfil=PerfilUsuario.MENSALISTA, status=StatusUsuario.ATIVO,
        nota_admin=3, nota_galera_media=3.0, pontos_ranking=0
    )
    mock_usuario_repo.listar_todos.return_value = [usuario1]

    mock_financeiro_repo.listar_por_usuarios_e_mes.return_value = [
        Financeiro(
            id=1, usuario_id=1, tipo="MENSALIDADE", valor=60.0,
            status_pagamento=StatusPagamento.PENDENTE, mes_referencia="2023-10"
        )
    ]

    resultado = await use_case.executar()

    assert resultado == 0
    mock_financeiro_repo.listar_por_usuarios_e_mes.assert_called_once_with([1], "2023-10")
    mock_financeiro_repo.salvar_lote.assert_not_called()

@pytest.mark.asyncio
@patch('application.financeiro.virada_mes_use_case.datetime')
async def test_virada_mes_gera_novas_mensalidades(mock_datetime, use_case, mock_usuario_repo, mock_evento_repo, mock_financeiro_repo):
    mock_datetime.now.return_value = datetime(2023, 10, 1)

    usuario1 = Usuario(
        id=1, nome="Admin", telefone="111", senha_hash="",
        perfil=PerfilUsuario.ADMIN, status=StatusUsuario.ATIVO,
        nota_admin=3, nota_galera_media=3.0, pontos_ranking=0
    )
    usuario2 = Usuario(
        id=2, nome="Mensalista", telefone="222", senha_hash="",
        perfil=PerfilUsuario.MENSALISTA, status=StatusUsuario.ATIVO,
        nota_admin=3, nota_galera_media=3.0, pontos_ranking=0
    )
    mock_usuario_repo.listar_todos.return_value = [usuario1, usuario2]

    mock_evento_repo.listar_todos.return_value = [
        Evento(
            id=1, data_jogo=date(2023, 10, 5), hora_inicio=time(19, 0), hora_fim=time(21, 0),
            status_evento=StatusEvento.PRESENCA_ABERTA, flag_churrasco=False, valor_churrasco=0.0,
            valor_mensalidade=75.0
        )
    ]

    mock_financeiro_repo.listar_por_usuarios_e_mes.return_value = []

    resultado = await use_case.executar()

    assert resultado == 2
    mock_financeiro_repo.listar_por_usuarios_e_mes.assert_called_once_with([1, 2], "2023-10")
    mock_financeiro_repo.salvar_lote.assert_called_once()

    lote_salvo = mock_financeiro_repo.salvar_lote.call_args[0][0]
    assert len(lote_salvo) == 2
    assert lote_salvo[0].usuario_id == 1
    assert lote_salvo[0].valor == 75.0
    assert lote_salvo[1].usuario_id == 2
    assert lote_salvo[1].valor == 75.0

@pytest.mark.asyncio
@patch('application.financeiro.virada_mes_use_case.datetime')
async def test_virada_mes_com_lotes(mock_datetime, use_case, mock_usuario_repo, mock_evento_repo, mock_financeiro_repo):
    mock_datetime.now.return_value = datetime(2023, 10, 1)

    usuarios = [
        Usuario(
            id=i, nome=f"User {i}", telefone=str(i), senha_hash="",
            perfil=PerfilUsuario.MENSALISTA, status=StatusUsuario.ATIVO,
            nota_admin=3, nota_galera_media=3.0, pontos_ranking=0
        ) for i in range(1, 106)
    ]
    mock_usuario_repo.listar_todos.return_value = usuarios

    mock_evento_repo.listar_todos.return_value = []
    mock_financeiro_repo.listar_por_usuarios_e_mes.return_value = []

    resultado = await use_case.executar()

    assert resultado == 105
    assert mock_financeiro_repo.salvar_lote.call_count == 3

    lote1 = mock_financeiro_repo.salvar_lote.call_args_list[0][0][0]
    lote2 = mock_financeiro_repo.salvar_lote.call_args_list[1][0][0]
    lote3 = mock_financeiro_repo.salvar_lote.call_args_list[2][0][0]

    assert len(lote1) == 50
    assert len(lote2) == 50
    assert len(lote3) == 5
    assert lote1[0].valor == 60.0  # fallback
