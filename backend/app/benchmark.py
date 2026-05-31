import asyncio
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.db.models import Base, FinanceiroModel, UsuarioModel, EventoModel, PresencaModel
from api.db.repositories.financeiro_repo import SQLAlchemyFinanceiroRepository
from api.db.repositories.usuario_repo import SQLAlchemyUsuarioRepository
from api.db.repositories.evento_repo import SQLAlchemyEventoRepository
from api.db.repositories.presenca_repo import SQLAlchemyPresencaRepository
from application.financeiro.listar_todos_financeiro_use_case import ListarTodosFinanceiroUseCase

engine = create_engine('sqlite:///:memory:')
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def run_benchmark():
    session = SessionLocal()

    # Add users to avoid unique constraints problems with financeiro items
    for i in range(1, 1001):
        u = UsuarioModel(nome=f"Teste{i}", telefone=f"123456{i}", senha_hash="123", perfil="MENSALISTA", status="ATIVO", pontos_ranking=0)
        session.add(u)

    session.commit()

    # Insert 10000 dummy records for different months
    for i in range(1, 1001):
        for m in range(1, 13):
            mes = f"2023-{m:02d}"
            f = FinanceiroModel(
                usuario_id=i,
                tipo="MENSALIDADE",
                valor=60.0,
                status_pagamento="PAGO",
                mes_referencia=mes
            )
            session.add(f)
    session.commit()

    financeiro_repo = SQLAlchemyFinanceiroRepository(session)
    usuario_repo = SQLAlchemyUsuarioRepository(session)
    evento_repo = SQLAlchemyEventoRepository(session)
    presenca_repo = SQLAlchemyPresencaRepository(session)

    uc = ListarTodosFinanceiroUseCase(financeiro_repo, usuario_repo, evento_repo, presenca_repo)

    start = time.perf_counter()
    res = await uc.executar("2023-01")
    end = time.perf_counter()

    print(f"Time taken: {end - start:.4f} seconds")
    print(f"Records found: {len(res)}")

asyncio.run(run_benchmark())
