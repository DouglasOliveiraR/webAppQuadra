import pytest
from datetime import date, time
from unittest.mock import AsyncMock
from domain.usuarios.entities import Usuario
from domain.usuarios.enums import PerfilUsuario, StatusUsuario
from domain.eventos.entities import Evento
from domain.eventos.enums import StatusEvento
from domain.votos.enums import CategoriaVoto
from core.exceptions import RegraDeNegocioError
from application.votos.use_cases import RegistrarVotoUseCase

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

from application.votos.use_cases import EncerrarVotacaoUseCase
from domain.votos.entities import Voto

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

    votos = [
        Voto(id=1, evento_id=1, eleitor_id=1, candidato_id=2, categoria=CategoriaVoto.BOLA_CHEIA),
        Voto(id=2, evento_id=1, eleitor_id=3, candidato_id=2, categoria=CategoriaVoto.BOLA_CHEIA),
        Voto(id=3, evento_id=1, eleitor_id=2, candidato_id=3, categoria=CategoriaVoto.BOLA_MURCHA),
    ]
    voto_repo.listar_por_evento.return_value = votos

    usuarios = [
        Usuario(id=2, nome="Cand1", telefone="11999999991", senha_hash="", perfil=PerfilUsuario.MENSALISTA, status=StatusUsuario.ATIVO, nota_admin=8, nota_galera_media=8.0, pontos_ranking=0),
        Usuario(id=3, nome="Cand2", telefone="11999999992", senha_hash="", perfil=PerfilUsuario.MENSALISTA, status=StatusUsuario.ATIVO, nota_admin=8, nota_galera_media=8.0, pontos_ranking=0)
    ]
    usuario_repo.buscar_por_ids.return_value = usuarios

    use_case = EncerrarVotacaoUseCase(evento_repo, voto_repo, usuario_repo, premio_repo)
    result = await use_case.executar(evento_id=1)

    assert result == {
        CategoriaVoto.BOLA_CHEIA.value: {2: 2},
        CategoriaVoto.BOLA_MURCHA.value: {3: 1}
    }

    assert evento.status_evento == StatusEvento.ENCERRADO
    evento_repo.salvar.assert_any_call(evento)

    # Should schedule next event
    assert evento_repo.salvar.call_count == 2

    usuario_repo.salvar_lote.assert_called_once()
    usuarios_salvos = usuario_repo.salvar_lote.call_args[0][0]
    assert len(usuarios_salvos) == 2
    # Bola cheia gets 3 points
    assert any(u.id == 2 and u.pontos_ranking == 3 for u in usuarios_salvos)
    # Bola murcha gets -1 points
    assert any(u.id == 3 and u.pontos_ranking == -1 for u in usuarios_salvos)

    premio_repo.salvar_lote.assert_called_once()
    premios = premio_repo.salvar_lote.call_args[0][0]
    assert len(premios) == 2

@pytest.mark.asyncio
async def test_encerrar_votacao_evento_nao_encontrado():
    evento_repo = AsyncMock()
    voto_repo = AsyncMock()
    usuario_repo = AsyncMock()
    premio_repo = AsyncMock()

    evento_repo.buscar_por_id.return_value = None

    use_case = EncerrarVotacaoUseCase(evento_repo, voto_repo, usuario_repo, premio_repo)
    with pytest.raises(RegraDeNegocioError, match="Evento não encontrado"):
        await use_case.executar(evento_id=1)

@pytest.mark.asyncio
async def test_encerrar_votacao_ja_encerrada():
    evento_repo = AsyncMock()
    voto_repo = AsyncMock()
    usuario_repo = AsyncMock()
    premio_repo = AsyncMock()

    evento = Evento(
        id=1,
        data_jogo=date(2026, 6, 1),
        hora_inicio=time(19, 0),
        hora_fim=time(21, 0),
        status_evento=StatusEvento.ENCERRADO,
        flag_churrasco=False,
        valor_churrasco=0.0
    )
    evento_repo.buscar_por_id.return_value = evento

    use_case = EncerrarVotacaoUseCase(evento_repo, voto_repo, usuario_repo, premio_repo)
    with pytest.raises(RegraDeNegocioError, match="Votação já foi encerrada"):
        await use_case.executar(evento_id=1)

@pytest.mark.asyncio
async def test_encerrar_votacao_empate():
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

    # Empate entre 2 e 3 na Bola Cheia (2 votos cada)
    votos = [
        Voto(id=1, evento_id=1, eleitor_id=1, candidato_id=2, categoria=CategoriaVoto.BOLA_CHEIA),
        Voto(id=2, evento_id=1, eleitor_id=4, candidato_id=2, categoria=CategoriaVoto.BOLA_CHEIA),
        Voto(id=3, evento_id=1, eleitor_id=5, candidato_id=3, categoria=CategoriaVoto.BOLA_CHEIA),
        Voto(id=4, evento_id=1, eleitor_id=6, candidato_id=3, categoria=CategoriaVoto.BOLA_CHEIA),
    ]
    voto_repo.listar_por_evento.return_value = votos

    usuarios = [
        Usuario(id=2, nome="Cand1", telefone="11999999991", senha_hash="", perfil=PerfilUsuario.MENSALISTA, status=StatusUsuario.ATIVO, nota_admin=8, nota_galera_media=8.0, pontos_ranking=0),
        Usuario(id=3, nome="Cand2", telefone="11999999992", senha_hash="", perfil=PerfilUsuario.MENSALISTA, status=StatusUsuario.ATIVO, nota_admin=8, nota_galera_media=8.0, pontos_ranking=0)
    ]
    usuario_repo.buscar_por_ids.return_value = usuarios

    use_case = EncerrarVotacaoUseCase(evento_repo, voto_repo, usuario_repo, premio_repo)
    result = await use_case.executar(evento_id=1)

    assert result == {
        CategoriaVoto.BOLA_CHEIA.value: {2: 2, 3: 2}
    }

    usuario_repo.salvar_lote.assert_called_once()
    usuarios_salvos = usuario_repo.salvar_lote.call_args[0][0]
    assert len(usuarios_salvos) == 2
    # Ambos recebem 3 pontos
    assert any(u.id == 2 and u.pontos_ranking == 3 for u in usuarios_salvos)
    assert any(u.id == 3 and u.pontos_ranking == 3 for u in usuarios_salvos)

    premio_repo.salvar_lote.assert_called_once()
    premios = premio_repo.salvar_lote.call_args[0][0]
    assert len(premios) == 2

@pytest.mark.asyncio
async def test_encerrar_votacao_sem_votos():
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
    voto_repo.listar_por_evento.return_value = []

    use_case = EncerrarVotacaoUseCase(evento_repo, voto_repo, usuario_repo, premio_repo)
    result = await use_case.executar(evento_id=1)

    assert result == {}

    assert evento.status_evento == StatusEvento.ENCERRADO
    evento_repo.salvar.assert_any_call(evento)

    usuario_repo.salvar_lote.assert_not_called()
    premio_repo.salvar_lote.assert_not_called()
