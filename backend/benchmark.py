import asyncio
import time
from datetime import date, time as dtime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.api.db.models import Base, UsuarioModel, EventoModel, VotoModel
from app.api.db.repositories.usuario_repo import SQLAlchemyUsuarioRepository
from app.api.db.repositories.evento_repo import SQLAlchemyEventoRepository
from app.api.db.repositories.voto_repo import SQLAlchemyVotoRepository
from app.domain.usuarios.enums import PerfilUsuario, StatusUsuario
from app.domain.eventos.enums import StatusEvento
from app.domain.votos.enums import CategoriaVoto
from app.application.votos.use_cases import EncerrarVotacaoUseCase

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def run_benchmark():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Setup many users and votes
    users = []
    for i in range(1, 1001):
        users.append(UsuarioModel(
            id=i,
            nome=f"Jogador {i}",
            telefone=f"119{i:08d}",
            senha_hash="hash",
            perfil=PerfilUsuario.MENSALISTA,
            status=StatusUsuario.ATIVO,
            nota_admin=8.0,
            nota_galera_media=8.0,
            pontos_ranking=0
        ))
    db.add_all(users)

    evento = EventoModel(
        id=1,
        data_jogo=date(2026, 6, 1),
        hora_inicio=dtime(19, 0),
        hora_fim=dtime(21, 0),
        status_evento=StatusEvento.VOTACAO_ABERTA,
        flag_churrasco=False,
        valor_churrasco=0.0
    )
    db.add(evento)

    # Simulate tie for all users so all get points
    # If we have 1000 users, and we want many winners, we can make 1000 users all receive exactly 1 vote in BOLA_CHEIA
    votes = []
    for i in range(1, 1001):
        votes.append(VotoModel(
            evento_id=1,
            eleitor_id=i,
            candidato_id=i,
            categoria=CategoriaVoto.BOLA_CHEIA
        ))
    db.add_all(votes)
    db.commit()

    usuario_repo = SQLAlchemyUsuarioRepository(db)
    evento_repo = SQLAlchemyEventoRepository(db)
    voto_repo = SQLAlchemyVotoRepository(db)

    use_case = EncerrarVotacaoUseCase(
        evento_repo=evento_repo,
        voto_repo=voto_repo,
        usuario_repo=usuario_repo
    )

    start_time = time.time()
    await use_case.executar(1)
    end_time = time.time()

    print(f"Time taken to execute EncerrarVotacaoUseCase with 1000 updated users: {end_time - start_time:.4f} seconds")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
