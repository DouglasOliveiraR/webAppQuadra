import pytest
from application.eventos.sorteio_use_case import SorteioUseCase
from domain.eventos.entities import Evento
from domain.presencas.entities import Presenca
from domain.usuarios.entities import Usuario
from domain.eventos.enums import StatusEvento
from domain.presencas.enums import StatusJogo, Posicao
from domain.usuarios.enums import PerfilUsuario, StatusUsuario
from core.exceptions import RegraDeNegocioError
from unittest.mock import AsyncMock, Mock

@pytest.fixture
def mock_evento_repo():
    return AsyncMock()

@pytest.fixture
def mock_presenca_repo():
    return AsyncMock()

@pytest.fixture
def mock_usuario_repo():
    return AsyncMock()

@pytest.fixture
def use_case(mock_evento_repo, mock_presenca_repo, mock_usuario_repo):
    return SorteioUseCase(mock_evento_repo, mock_presenca_repo, mock_usuario_repo)

@pytest.mark.asyncio
async def test_sorteio_com_sucesso(use_case, mock_evento_repo, mock_presenca_repo, mock_usuario_repo):
    # Setup mock data
    evento = Evento(id=1, data_jogo=None, hora_inicio=None, hora_fim=None, status_evento=StatusEvento.ENCERRADO, flag_churrasco=False, valor_churrasco=0.0)
    mock_evento_repo.buscar_por_id.return_value = evento

    presencas = [
        Presenca(id=1, evento_id=1, usuario_id=1, status_jogo=StatusJogo.VOU, posicao=Posicao.GOL, vai_churrasco=False, checkin_validado=True, falta_penalizada=False),
        Presenca(id=2, evento_id=1, usuario_id=2, status_jogo=StatusJogo.VOU, posicao=Posicao.LINHA, vai_churrasco=False, checkin_validado=True, falta_penalizada=False),
        Presenca(id=3, evento_id=1, usuario_id=3, status_jogo=StatusJogo.VOU, posicao=Posicao.LINHA, vai_churrasco=False, checkin_validado=True, falta_penalizada=False),
        Presenca(id=4, evento_id=1, usuario_id=4, status_jogo=StatusJogo.VOU, posicao=Posicao.LINHA, vai_churrasco=False, checkin_validado=True, falta_penalizada=False),
        Presenca(id=5, evento_id=1, usuario_id=5, status_jogo=StatusJogo.VOU, posicao=Posicao.LINHA, vai_churrasco=False, checkin_validado=True, falta_penalizada=False),
        Presenca(id=6, evento_id=1, usuario_id=6, status_jogo=StatusJogo.VOU, posicao=Posicao.LINHA, vai_churrasco=False, checkin_validado=True, falta_penalizada=False),
    ]
    mock_presenca_repo.listar_por_evento.return_value = presencas

    usuarios = [
        Usuario(id=1, nome="Gol 1", telefone="1", senha_hash="", perfil=PerfilUsuario.MENSALISTA, status=StatusUsuario.ATIVO, nota_admin=8, nota_galera_media=8.0, pontos_ranking=0),
        Usuario(id=2, nome="Linha 1", telefone="2", senha_hash="", perfil=PerfilUsuario.MENSALISTA, status=StatusUsuario.ATIVO, nota_admin=7, nota_galera_media=7.0, pontos_ranking=0),
        Usuario(id=3, nome="Linha 2", telefone="3", senha_hash="", perfil=PerfilUsuario.MENSALISTA, status=StatusUsuario.ATIVO, nota_admin=6, nota_galera_media=6.0, pontos_ranking=0),
        Usuario(id=4, nome="Linha 3", telefone="4", senha_hash="", perfil=PerfilUsuario.MENSALISTA, status=StatusUsuario.ATIVO, nota_admin=5, nota_galera_media=5.0, pontos_ranking=0),
        Usuario(id=5, nome="Linha 4", telefone="5", senha_hash="", perfil=PerfilUsuario.MENSALISTA, status=StatusUsuario.ATIVO, nota_admin=4, nota_galera_media=4.0, pontos_ranking=0),
        Usuario(id=6, nome="Linha 5", telefone="6", senha_hash="", perfil=PerfilUsuario.MENSALISTA, status=StatusUsuario.ATIVO, nota_admin=3, nota_galera_media=3.0, pontos_ranking=0),
    ]
    mock_usuario_repo.buscar_por_ids.return_value = usuarios

    # Execute
    resultado = await use_case.executar(evento_id=1, criterio="NOTA_ADMIN")

    # Assertions
    assert "times" in resultado
    assert "sugestoes_banco" in resultado
    assert len(resultado["times"]) == 2 # 6 jogadores / 6.0 = 1 -> max(2, 1) = 2
