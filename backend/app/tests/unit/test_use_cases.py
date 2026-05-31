import pytest
from datetime import date, time
from unittest.mock import AsyncMock
from domain.usuarios.entities import Usuario
from domain.usuarios.enums import PerfilUsuario, StatusUsuario
from domain.eventos.entities import Evento
from domain.eventos.enums import StatusEvento
from domain.votos.enums import CategoriaVoto
from core.exceptions import RegraDeNegocioError
from application.votos.use_cases import RegistrarVotoUseCase, EncerrarVotacaoUseCase
from domain.votos.entities import Voto

@pytest.mark.asyncio
async def test_registrar_voto_sucesso():
    # Setup mocks
    voto_repo = AsyncMock()
    evento_repo = AsyncMock()
    usuario_repo = AsyncMock()

    # Mocks de dados
    evento = Evento(
        id=1,
        data_jogo=date(2026, 6, 1),
        hora_inicio=time(19, 0),
        hora_fim=time(21, 0),
        status_evento=StatusEvento.VOTACAO_ABERTA,
        flag_churrasco=False,
        valor_churrasco=0.0
    )
    
    eleitor = Usuario(
        id=1,
        nome="Eleitor",
        telefone="11999999999",
        senha_hash="",
        perfil=PerfilUsuario.MENSALISTA,
        status=StatusUsuario.ATIVO,
        nota_admin=8,
        nota_galera_media=8.0,
        pontos_ranking=0
    )
    
    candidato = Usuario(
        id=2,
        nome="Candidato",
        telefone="11888888888",
        senha_hash="",
        perfil=PerfilUsuario.MENSALISTA,
        status=StatusUsuario.ATIVO,
        nota_admin=8,
        nota_galera_media=8.0,
        pontos_ranking=0
    )

    evento_repo.buscar_por_id.return_value = evento
    usuario_repo.buscar_por_id.side_effect = lambda uid: eleitor if uid == 1 else candidato
    voto_repo.buscar_voto_eleitor.return_value = None
    voto_repo.salvar.side_effect = lambda v: v

    use_case = RegistrarVotoUseCase(voto_repo, evento_repo, usuario_repo)
    voto = await use_case.executar(
        evento_id=1,
        eleitor_id=1,
        candidato_id=2,
        categoria=CategoriaVoto.BOLA_CHEIA
    )

    assert voto.eleitor_id == 1
    assert voto.candidato_id == 2
    assert voto.categoria == CategoriaVoto.BOLA_CHEIA
    voto_repo.salvar.assert_called_once()

@pytest.mark.asyncio
async def test_registrar_voto_si_mesmo_erro():
    voto_repo = AsyncMock()
    evento_repo = AsyncMock()
    usuario_repo = AsyncMock()

    evento = Evento(
        id=1,
        data_jogo=date(2026, 6, 1),
        hora_inicio=time(19, 0),
        hora_fim=time(21, 0),
        status_evento=StatusEvento.VOTACAO_ABERTA,
        flag_churrasco=False,
        valor_churrasco=0.0
    )
    evento_repo.buscar_por_id.return_value = evento

    use_case = RegistrarVotoUseCase(voto_repo, evento_repo, usuario_repo)
    
    with pytest.raises(RegraDeNegocioError, match="Você não pode votar em si mesmo"):
        await use_case.executar(
            evento_id=1,
            eleitor_id=1,
            candidato_id=1,
            categoria=CategoriaVoto.BOLA_CHEIA
        )

@pytest.mark.asyncio
async def test_registrar_voto_eleitor_avulso_erro():
    voto_repo = AsyncMock()
    evento_repo = AsyncMock()
    usuario_repo = AsyncMock()

    evento = Evento(
        id=1,
        data_jogo=date(2026, 6, 1),
        hora_inicio=time(19, 0),
        hora_fim=time(21, 0),
        status_evento=StatusEvento.VOTACAO_ABERTA,
        flag_churrasco=False,
        valor_churrasco=0.0
    )
    
    eleitor = Usuario(
        id=1,
        nome="Avulso Eleitor",
        telefone="AVULSO_123",
        senha_hash="",
        perfil=PerfilUsuario.AVULSO,
        status=StatusUsuario.ATIVO,
        nota_admin=8,
        nota_galera_media=8.0,
        pontos_ranking=0
    )
    
    candidato = Usuario(
        id=2,
        nome="Candidato",
        telefone="11888888888",
        senha_hash="",
        perfil=PerfilUsuario.MENSALISTA,
        status=StatusUsuario.ATIVO,
        nota_admin=8,
        nota_galera_media=8.0,
        pontos_ranking=0
    )

    evento_repo.buscar_por_id.return_value = evento
    usuario_repo.buscar_por_id.side_effect = lambda uid: eleitor if uid == 1 else candidato

    use_case = RegistrarVotoUseCase(voto_repo, evento_repo, usuario_repo)
    
    with pytest.raises(RegraDeNegocioError, match="Jogadores avulsos não podem votar"):
        await use_case.executar(
            evento_id=1,
            eleitor_id=1,
            candidato_id=2,
            categoria=CategoriaVoto.BOLA_CHEIA
        )

@pytest.mark.asyncio
async def test_encerrar_votacao_sucesso():
    evento_repo = AsyncMock()
    voto_repo = AsyncMock()
    usuario_repo = AsyncMock()
    premio_repo = AsyncMock()

    evento = Evento(
        id=1,
        data_jogo=date(2026, 6, 1),
        hora_inicio=time(19, 0),
        hora_fim=time(21, 0),
        status_evento=StatusEvento.VOTACAO_ABERTA,
        flag_churrasco=False,
        valor_churrasco=0.0
    )

    evento_repo.buscar_por_id.return_value = evento

    voto = Voto(
        id=1,
        evento_id=1,
        eleitor_id=1,
        candidato_id=2,
        categoria=CategoriaVoto.BOLA_CHEIA
    )
    voto_repo.listar_por_evento.return_value = [voto]

    candidato = Usuario(
        id=2,
        nome="Candidato Vencedor",
        telefone="11999999999",
        senha_hash="",
        perfil=PerfilUsuario.MENSALISTA,
        status=StatusUsuario.ATIVO,
        nota_admin=8,
        nota_galera_media=8.0,
        pontos_ranking=0
    )
    usuario_repo.buscar_por_ids.return_value = [candidato]
    usuario_repo.listar_todos.return_value = []

    use_case = EncerrarVotacaoUseCase(evento_repo, voto_repo, usuario_repo, premio_repo)
    resultado = await use_case.executar(evento_id=1)

    assert "BOLA_CHEIA" in resultado
    assert resultado["BOLA_CHEIA"][2] == 1

    # Check if event was saved
    evento_repo.salvar.assert_called()
    assert evento.status_evento == StatusEvento.ENCERRADO

    # Check if new event was created
    assert evento_repo.salvar.call_count == 2

@pytest.mark.asyncio
async def test_registrar_voto_candidato_avulso_erro():
    voto_repo = AsyncMock()
    evento_repo = AsyncMock()
    usuario_repo = AsyncMock()

    evento = Evento(
        id=1,
        data_jogo=date(2026, 6, 1),
        hora_inicio=time(19, 0),
        hora_fim=time(21, 0),
        status_evento=StatusEvento.VOTACAO_ABERTA,
        flag_churrasco=False,
        valor_churrasco=0.0
    )
    
    eleitor = Usuario(
        id=1,
        nome="Eleitor",
        telefone="11999999999",
        senha_hash="",
        perfil=PerfilUsuario.MENSALISTA,
        status=StatusUsuario.ATIVO,
        nota_admin=8,
        nota_galera_media=8.0,
        pontos_ranking=0
    )
    
    candidato = Usuario(
        id=2,
        nome="Avulso Candidato",
        telefone="AVULSO_123",
        senha_hash="",
        perfil=PerfilUsuario.AVULSO,
        status=StatusUsuario.ATIVO,
        nota_admin=8,
        nota_galera_media=8.0,
        pontos_ranking=0
    )

    evento_repo.buscar_por_id.return_value = evento
    usuario_repo.buscar_por_id.side_effect = lambda uid: eleitor if uid == 1 else candidato

    use_case = RegistrarVotoUseCase(voto_repo, evento_repo, usuario_repo)
    
    with pytest.raises(RegraDeNegocioError, match="Jogadores avulsos não podem ser votados"):
        await use_case.executar(
            evento_id=1,
            eleitor_id=1,
            candidato_id=2,
            categoria=CategoriaVoto.BOLA_CHEIA
        )
