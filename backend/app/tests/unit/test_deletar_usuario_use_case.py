import pytest
from unittest.mock import AsyncMock
from application.usuarios.deletar_usuario_use_case import DeletarUsuarioUseCase
from domain.usuarios.entities import Usuario
from domain.usuarios.enums import StatusUsuario, PerfilUsuario
from domain.eventos.entities import Evento
from domain.eventos.enums import StatusEvento
from domain.presencas.entities import Presenca
from domain.presencas.enums import StatusJogo, Posicao
from domain.financeiro.entities import Financeiro
from domain.financeiro.enums import StatusPagamento
from datetime import date, time

@pytest.mark.asyncio
async def test_deletar_usuario_use_case_performance():
    usuario_repo = AsyncMock()
    presenca_repo = AsyncMock()
    financeiro_repo = AsyncMock()
    evento_repo = AsyncMock()

    # Mocks de dados
    usuario = Usuario(
        id=1,
        nome="Usuario Teste",
        telefone="11999999999",
        senha_hash="",
        perfil=PerfilUsuario.MENSALISTA,
        status=StatusUsuario.ATIVO,
        nota_admin=8,
        nota_galera_media=8.0,
        pontos_ranking=0
    )
    usuario_repo.buscar_por_id.return_value = usuario

    # Create many events
    eventos = []
    for i in range(1, 101):
        eventos.append(Evento(
            id=i,
            data_jogo=date(2026, 6, 1),
            hora_inicio=time(19, 0),
            hora_fim=time(21, 0),
            status_evento=StatusEvento.PRESENCA_ABERTA,
            flag_churrasco=False,
            valor_churrasco=0.0
        ))
    evento_repo.listar_todos.return_value = eventos

    # Create many presences for each event
    def mock_listar_por_evento(evento_id):
        return [
            Presenca(id=evento_id*1000 + 1, usuario_id=1, evento_id=evento_id, status_jogo=StatusJogo.VOU, posicao=Posicao.LINHA, vai_churrasco=False, checkin_validado=False, falta_penalizada=False),
            Presenca(id=evento_id*1000 + 2, usuario_id=2, evento_id=evento_id, status_jogo=StatusJogo.VOU, posicao=Posicao.LINHA, vai_churrasco=False, checkin_validado=False, falta_penalizada=False),
            Presenca(id=evento_id*1000 + 3, usuario_id=3, evento_id=evento_id, status_jogo=StatusJogo.VOU, posicao=Posicao.LINHA, vai_churrasco=False, checkin_validado=False, falta_penalizada=False)
        ]
    presenca_repo.listar_por_evento.side_effect = mock_listar_por_evento

    financeiro_repo.listar_todos.return_value = []

    use_case = DeletarUsuarioUseCase(usuario_repo, presenca_repo, financeiro_repo, evento_repo)

    import time as time_module
    start = time_module.time()
    await use_case.executar(1)
    end = time_module.time()

    print(f"Time taken: {end - start:.4f} seconds")
    print(f"Call count listar_por_evento: {presenca_repo.listar_por_evento.call_count}")
    print(f"Call count deletar: {presenca_repo.deletar.call_count}")
