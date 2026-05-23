import pytest
from unittest.mock import AsyncMock
from application.presencas.use_cases import CheckinUseCase
from application.votos.use_cases import EncerrarVotacaoUseCase
from core.exceptions import RegraDeNegocioError
from domain.usuarios.entities import Usuario
from domain.presencas.entities import Presenca
from domain.eventos.entities import Evento
from domain.votos.entities import Voto
from domain.usuarios.enums import PerfilUsuario, StatusUsuario
from domain.presencas.enums import StatusJogo, Posicao
from domain.eventos.enums import StatusEvento
from domain.votos.enums import CategoriaVoto
from datetime import date, time

@pytest.fixture
def mock_repos():
    return {
        "presenca_repo": AsyncMock(),
        "usuario_repo": AsyncMock(),
        "evento_repo": AsyncMock(),
        "voto_repo": AsyncMock()
    }

@pytest.fixture
def base_user():
    return Usuario(
        id=1, nome="Teste", telefone="1199", senha_hash="",
        perfil=PerfilUsuario.MENSALISTA, status=StatusUsuario.ATIVO,
        nota_admin=0.0, nota_galera_media=0.0, pontos_ranking=10
    )

@pytest.mark.asyncio
async def test_checkin_chegou_ganha_ponto(mock_repos, base_user):
    # Setup
    use_case = CheckinUseCase(mock_repos["presenca_repo"], mock_repos["usuario_repo"])
    presenca = Presenca(id=1, usuario_id=1, evento_id=1, status_jogo=StatusJogo.VOU, posicao=Posicao.LINHA, vai_churrasco=False, checkin_validado=False, falta_penalizada=False)
    
    mock_repos["presenca_repo"].buscar_por_usuario_evento.return_value = presenca
    mock_repos["usuario_repo"].buscar_por_id.return_value = base_user
    
    # Act
    await use_case.executar(evento_id=1, usuario_id=1, chegou=True, falta_justificada=False)
    
    # Assert
    assert base_user.pontos_ranking == 11
    assert presenca.checkin_validado is True
    assert presenca.falta_penalizada is False
    mock_repos["usuario_repo"].salvar.assert_called_once_with(base_user)

@pytest.mark.asyncio
async def test_checkin_faltou_sem_avisar_perde_ponto(mock_repos, base_user):
    use_case = CheckinUseCase(mock_repos["presenca_repo"], mock_repos["usuario_repo"])
    presenca = Presenca(id=1, usuario_id=1, evento_id=1, status_jogo=StatusJogo.VOU, posicao=Posicao.LINHA, vai_churrasco=False, checkin_validado=False, falta_penalizada=False)
    
    mock_repos["presenca_repo"].buscar_por_usuario_evento.return_value = presenca
    mock_repos["usuario_repo"].buscar_por_id.return_value = base_user
    
    await use_case.executar(evento_id=1, usuario_id=1, chegou=False, falta_justificada=False)
    
    # Regra nova: Falta sem avisar = -1 ponto
    assert base_user.pontos_ranking == 9
    assert presenca.falta_penalizada is True

@pytest.mark.asyncio
async def test_checkin_faltou_justificado_neutro(mock_repos, base_user):
    use_case = CheckinUseCase(mock_repos["presenca_repo"], mock_repos["usuario_repo"])
    presenca = Presenca(id=1, usuario_id=1, evento_id=1, status_jogo=StatusJogo.VOU, posicao=Posicao.LINHA, vai_churrasco=False, checkin_validado=False, falta_penalizada=False)
    
    mock_repos["presenca_repo"].buscar_por_usuario_evento.return_value = presenca
    mock_repos["usuario_repo"].buscar_por_id.return_value = base_user
    
    await use_case.executar(evento_id=1, usuario_id=1, chegou=False, falta_justificada=True)
    
    assert base_user.pontos_ranking == 10
    assert presenca.falta_penalizada is False

@pytest.mark.asyncio
async def test_encerrar_votacao_empates_e_pontos(mock_repos):
    use_case = EncerrarVotacaoUseCase(mock_repos["evento_repo"], mock_repos["voto_repo"], mock_repos["usuario_repo"])
    
    # Evento válido
    evento = Evento(id=1, data_jogo=date.today(), hora_inicio=time(20,0), hora_fim=time(22,0), status_evento=StatusEvento.VOTACAO_ABERTA, flag_churrasco=False, valor_churrasco=0)
    mock_repos["evento_repo"].buscar_por_id.return_value = evento
    
    # Votos: 
    # Bola Cheia: Usuário 2 e 3 recebem 2 votos cada (empate) -> ambos ganham +3
    # Lafon: Usuário 4 recebe 1 voto -> ganha -1
    votos = [
        Voto(id=1, evento_id=1, eleitor_id=1, candidato_id=2, categoria=CategoriaVoto.BOLA_CHEIA),
        Voto(id=2, evento_id=1, eleitor_id=4, candidato_id=2, categoria=CategoriaVoto.BOLA_CHEIA),
        Voto(id=3, evento_id=1, eleitor_id=1, candidato_id=3, categoria=CategoriaVoto.BOLA_CHEIA),
        Voto(id=4, evento_id=1, eleitor_id=5, candidato_id=3, categoria=CategoriaVoto.BOLA_CHEIA),
        Voto(id=5, evento_id=1, eleitor_id=2, candidato_id=4, categoria=CategoriaVoto.LAFON),
    ]
    mock_repos["voto_repo"].listar_por_evento.return_value = votos
    
    # Usuários (2, 3, 4)
    u2 = Usuario(id=2, nome="U2", telefone="2", senha_hash="", perfil=PerfilUsuario.MENSALISTA, status=StatusUsuario.ATIVO, nota_admin=0.0, nota_galera_media=0.0, pontos_ranking=10)
    u3 = Usuario(id=3, nome="U3", telefone="3", senha_hash="", perfil=PerfilUsuario.MENSALISTA, status=StatusUsuario.ATIVO, nota_admin=0.0, nota_galera_media=0.0, pontos_ranking=10)
    u4 = Usuario(id=4, nome="U4", telefone="4", senha_hash="", perfil=PerfilUsuario.MENSALISTA, status=StatusUsuario.ATIVO, nota_admin=0.0, nota_galera_media=0.0, pontos_ranking=10)
    
    async def mock_buscar_usuario(uid):
        if uid == 2: return u2
        if uid == 3: return u3
        if uid == 4: return u4
        return None
        
    async def mock_buscar_usuarios(uids):
        res = []
        for uid in uids:
            if uid == 2: res.append(u2)
            if uid == 3: res.append(u3)
            if uid == 4: res.append(u4)
        return res

    mock_repos["usuario_repo"].buscar_por_id.side_effect = mock_buscar_usuario
    mock_repos["usuario_repo"].buscar_por_ids.side_effect = mock_buscar_usuarios
    
    resultado = await use_case.executar(1)
    
    # Assert do evento encerrado
    assert evento.status_evento == StatusEvento.ENCERRADO
    
    # U2 e U3 deveriam estar com 13 pontos (10 + 3)
    assert u2.pontos_ranking == 13
    assert u3.pontos_ranking == 13
    
    # U4 deveria estar com 9 pontos (10 - 1) porque Lafon agora é -1
    assert u4.pontos_ranking == 9
    
    assert resultado["BOLA_CHEIA"][2] == 2
    assert resultado["BOLA_CHEIA"][3] == 2

@pytest.mark.asyncio
async def test_encerrar_votacao_evento_nao_encontrado(mock_repos):
    use_case = EncerrarVotacaoUseCase(mock_repos["evento_repo"], mock_repos["voto_repo"], mock_repos["usuario_repo"])
    mock_repos["evento_repo"].buscar_por_id.return_value = None

    with pytest.raises(RegraDeNegocioError, match="Evento não encontrado"):
        await use_case.executar(1)

@pytest.mark.asyncio
async def test_encerrar_votacao_evento_ja_encerrado(mock_repos):
    use_case = EncerrarVotacaoUseCase(mock_repos["evento_repo"], mock_repos["voto_repo"], mock_repos["usuario_repo"])

    evento = Evento(id=1, data_jogo=date.today(), hora_inicio=time(20,0), hora_fim=time(22,0), status_evento=StatusEvento.ENCERRADO, flag_churrasco=False, valor_churrasco=0)
    mock_repos["evento_repo"].buscar_por_id.return_value = evento

    with pytest.raises(RegraDeNegocioError, match="Votação já foi encerrada"):
        await use_case.executar(1)

@pytest.mark.asyncio
async def test_encerrar_votacao_sem_votos(mock_repos):
    use_case = EncerrarVotacaoUseCase(mock_repos["evento_repo"], mock_repos["voto_repo"], mock_repos["usuario_repo"])

    evento = Evento(id=1, data_jogo=date.today(), hora_inicio=time(20,0), hora_fim=time(22,0), status_evento=StatusEvento.VOTACAO_ABERTA, flag_churrasco=False, valor_churrasco=0)
    mock_repos["evento_repo"].buscar_por_id.return_value = evento
    mock_repos["voto_repo"].listar_por_evento.return_value = []

    resultado = await use_case.executar(1)

    assert evento.status_evento == StatusEvento.ENCERRADO
    mock_repos["evento_repo"].salvar.assert_called_once_with(evento)
    mock_repos["usuario_repo"].salvar.assert_not_called()
    assert resultado == {}

@pytest.mark.asyncio
async def test_encerrar_votacao_mesmo_usuario_ganha_varias_categorias(mock_repos):
    use_case = EncerrarVotacaoUseCase(mock_repos["evento_repo"], mock_repos["voto_repo"], mock_repos["usuario_repo"])

    evento = Evento(id=1, data_jogo=date.today(), hora_inicio=time(20,0), hora_fim=time(22,0), status_evento=StatusEvento.VOTACAO_ABERTA, flag_churrasco=False, valor_churrasco=0)
    mock_repos["evento_repo"].buscar_por_id.return_value = evento

    # Usuário 2 ganha Bola Cheia (+3) e Gol Bonito (+2)
    # Total de pontos a receber: +5
    votos = [
        Voto(id=1, evento_id=1, eleitor_id=1, candidato_id=2, categoria=CategoriaVoto.BOLA_CHEIA),
        Voto(id=2, evento_id=1, eleitor_id=3, candidato_id=2, categoria=CategoriaVoto.BOLA_CHEIA),
        Voto(id=3, evento_id=1, eleitor_id=1, candidato_id=2, categoria=CategoriaVoto.GOL_BONITO),
    ]
    mock_repos["voto_repo"].listar_por_evento.return_value = votos

    u2 = Usuario(id=2, nome="U2", telefone="2", senha_hash="", perfil=PerfilUsuario.MENSALISTA, status=StatusUsuario.ATIVO, nota_admin=0.0, nota_galera_media=0.0, pontos_ranking=10)

    async def mock_buscar_usuario(uid):
        if uid == 2: return u2
        return None

    async def mock_buscar_usuarios(uids):
        if 2 in uids: return [u2]
        return []

    mock_repos["usuario_repo"].buscar_por_id.side_effect = mock_buscar_usuario
    mock_repos["usuario_repo"].buscar_por_ids.side_effect = mock_buscar_usuarios

    resultado = await use_case.executar(1)

    assert evento.status_evento == StatusEvento.ENCERRADO
    assert u2.pontos_ranking == 15
    assert resultado["BOLA_CHEIA"][2] == 2
    assert resultado["GOL_BONITO"][2] == 1

@pytest.mark.asyncio
async def test_encerrar_votacao_vencedor_nao_encontrado(mock_repos):
    use_case = EncerrarVotacaoUseCase(mock_repos["evento_repo"], mock_repos["voto_repo"], mock_repos["usuario_repo"])

    evento = Evento(id=1, data_jogo=date.today(), hora_inicio=time(20,0), hora_fim=time(22,0), status_evento=StatusEvento.VOTACAO_ABERTA, flag_churrasco=False, valor_churrasco=0)
    mock_repos["evento_repo"].buscar_por_id.return_value = evento

    # Usuário 999 (inexistente) ganha Bola Cheia (+3)
    # Usuário 2 ganha Gol Bonito (+2)
    votos = [
        Voto(id=1, evento_id=1, eleitor_id=1, candidato_id=999, categoria=CategoriaVoto.BOLA_CHEIA),
        Voto(id=2, evento_id=1, eleitor_id=1, candidato_id=2, categoria=CategoriaVoto.GOL_BONITO),
    ]
    mock_repos["voto_repo"].listar_por_evento.return_value = votos

    u2 = Usuario(id=2, nome="U2", telefone="2", senha_hash="", perfil=PerfilUsuario.MENSALISTA, status=StatusUsuario.ATIVO, nota_admin=0.0, nota_galera_media=0.0, pontos_ranking=10)

    async def mock_buscar_usuario(uid):
        if uid == 2: return u2
        return None

    async def mock_buscar_usuarios(uids):
        res = []
        if 2 in uids: res.append(u2)
        # 999 não é retornado
        return res

    mock_repos["usuario_repo"].buscar_por_id.side_effect = mock_buscar_usuario
    mock_repos["usuario_repo"].buscar_por_ids.side_effect = mock_buscar_usuarios

    resultado = await use_case.executar(1)

    assert evento.status_evento == StatusEvento.ENCERRADO

    # U2 ganha +2
    assert u2.pontos_ranking == 12
    # Nenhuma exceção para o usuário não encontrado, mas a votação dele está na apuração
    assert resultado["BOLA_CHEIA"][999] == 1
    assert resultado["GOL_BONITO"][2] == 1
