import asyncio
import time
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from api.db.models import Base
from api.db.repositories.nota_repo import SQLAlchemyNotaRepository
from application.notas.salvar_notas_galera_use_case import SalvarNotasGaleraUseCase

from domain.eventos.entities import Evento
from domain.eventos.enums import StatusEvento
from datetime import date, time as dtime

class MockEventoRepo:
    async def buscar_por_id(self, id):
        return Evento(
            id=1,
            data_jogo=date(2026, 6, 1),
            hora_inicio=dtime(19, 0),
            hora_fim=dtime(21, 0),
            status_evento=StatusEvento.VOTACAO_ABERTA,
            flag_churrasco=False,
            valor_churrasco=0.0
        )

async def run_benchmark():
    engine = create_engine('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    nota_repo = SQLAlchemyNotaRepository(session)

    use_case = SalvarNotasGaleraUseCase(nota_repo, None, MockEventoRepo())

    num_notas = 1000
    notas_dict = {i: 8 for i in range(2, num_notas+2)}

    start_time = time.time()
    await use_case.executar(avaliador_id=1, evento_id=1, notas=notas_dict)
    end_time = time.time()

    print(f"Time to save {num_notas} notas: {end_time - start_time:.4f} seconds")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
