import asyncio
import time
from unittest.mock import AsyncMock
from application.votos.use_cases import EncerrarVotacaoUseCase
from domain.eventos.entities import Evento
from domain.votos.entities import Voto
from domain.usuarios.entities import Usuario
from domain.votos.enums import CategoriaVoto
from domain.eventos.enums import StatusEvento
from datetime import date, time as dtime

async def run_benchmark():
    evento_repo = AsyncMock()
    voto_repo = AsyncMock()
    usuario_repo = AsyncMock()

    use_case = EncerrarVotacaoUseCase(evento_repo, voto_repo, usuario_repo)

    evento = Evento(id=1, data_jogo=date.today(), hora_inicio=dtime(20,0), hora_fim=dtime(22,0), status_evento=StatusEvento.VOTACAO_ABERTA, flag_churrasco=False, valor_churrasco=0)
    evento_repo.buscar_por_id.return_value = evento

    # Generate many votes to create many winners (simulate 1000 users)
    votos = []
    for i in range(1, 1001):
        votos.append(Voto(id=i, evento_id=1, eleitor_id=1000+i, candidato_id=i, categoria=CategoriaVoto.BOLA_CHEIA))

    voto_repo.listar_por_evento.return_value = votos

    async def mock_buscar_por_id(uid):
        await asyncio.sleep(0.001)  # Simulate DB latency
        return Usuario(id=uid, nome=f"U{uid}", telefone=str(uid), senha_hash="", perfil="MENSALISTA", status="ATIVO", nota_admin=0.0, nota_galera_media=0.0, pontos_ranking=10)

    async def mock_buscar_por_ids(uids):
        await asyncio.sleep(0.001)  # Simulate DB latency
        return [Usuario(id=uid, nome=f"U{uid}", telefone=str(uid), senha_hash="", perfil="MENSALISTA", status="ATIVO", nota_admin=0.0, nota_galera_media=0.0, pontos_ranking=10) for uid in uids]

    usuario_repo.buscar_por_id.side_effect = mock_buscar_por_id
    usuario_repo.buscar_por_ids.side_effect = mock_buscar_por_ids

    async def mock_salvar(u):
        pass
    usuario_repo.salvar.side_effect = mock_salvar

    start_time = time.time()
    await use_case.executar(1)
    end_time = time.time()

    print(f"Time taken: {end_time - start_time:.4f} seconds")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
