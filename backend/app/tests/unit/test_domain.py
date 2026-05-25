from datetime import date, time
from domain.usuarios.entities import Usuario
from domain.usuarios.enums import PerfilUsuario, StatusUsuario
from domain.eventos.entities import Evento
from domain.eventos.enums import StatusEvento
from domain.presencas.entities import Presenca
from domain.presencas.enums import StatusJogo, Posicao
from domain.votos.entities import Voto
from domain.votos.enums import CategoriaVoto
from domain.financeiro.entities import Financeiro
from domain.financeiro.enums import StatusPagamento

def test_usuario_entity_creation():
    usuario = Usuario(
        id=1,
        nome="Douglas",
        telefone="11999999999",
        senha_hash="hash123",
        perfil=PerfilUsuario.ADMIN,
        status=StatusUsuario.ATIVO,
        nota_admin=10.0,
        nota_galera_media=9.5,
        pontos_ranking=100
    )
    assert usuario.nome == "Douglas"
    assert usuario.perfil == PerfilUsuario.ADMIN

def test_evento_entity_creation():
    evento = Evento(
        id=1,
        data_jogo=date(2026, 6, 1),
        hora_inicio=time(19, 0),
        hora_fim=time(21, 0),
        status_evento=StatusEvento.AGENDADO,
        flag_churrasco=True,
        valor_churrasco=50.0
    )
    assert evento.flag_churrasco is True
    assert evento.status_evento == StatusEvento.AGENDADO

def test_presenca_entity_creation():
    presenca = Presenca(
        id=1,
        usuario_id=1,
        evento_id=1,
        status_jogo=StatusJogo.VOU,
        posicao=Posicao.LINHA,
        vai_churrasco=True,
        checkin_validado=False,
        falta_penalizada=False
    )
    assert presenca.status_jogo == StatusJogo.VOU
    assert presenca.posicao == Posicao.LINHA

def test_voto_entity_creation():
    voto = Voto(
        id=1,
        evento_id=1,
        eleitor_id=1,
        candidato_id=2,
        categoria=CategoriaVoto.BOLA_CHEIA
    )
    assert voto.categoria == CategoriaVoto.BOLA_CHEIA

def test_financeiro_entity_creation():
    financeiro = Financeiro(
        id=1,
        usuario_id=1,
        tipo="MENSALIDADE",
        valor=100.0,
        status_pagamento=StatusPagamento.PENDENTE,
        mes_referencia="2026-05"
    )
    assert financeiro.status_pagamento == StatusPagamento.PENDENTE
    assert financeiro.valor == 100.0
