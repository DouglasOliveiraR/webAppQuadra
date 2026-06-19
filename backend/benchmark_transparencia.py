import asyncio
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.api.db.models import Base, FinanceiroModel, EventoModel, UsuarioModel
from app.api.db.repositories.financeiro_repo import SQLAlchemyFinanceiroRepository
from app.api.db.repositories.evento_repo import SQLAlchemyEventoRepository
from app.application.financeiro.obter_transparencia_use_case import ObterTransparenciaUseCase
from app.domain.financeiro.enums import StatusPagamento

engine = create_engine('sqlite:///:memory:')
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

async def main():
    session = SessionLocal()
    # Populate dummy data
    for i in range(10000):
        mes = "2023-10" if i % 10 == 0 else "2023-09"
        f = FinanceiroModel(
            usuario_id=i,
            tipo="MENSALIDADE",
            valor=50.0,
            status_pagamento=StatusPagamento.PAGO,
            mes_referencia=mes
        )
        session.add(f)
    session.commit()

    financeiro_repo = SQLAlchemyFinanceiroRepository(session)
    evento_repo = SQLAlchemyEventoRepository(session)
    use_case = ObterTransparenciaUseCase(financeiro_repo, evento_repo)

    start = time.perf_counter()
    for _ in range(100):
        await use_case.executar("2023-10")
    end = time.perf_counter()

    print(f"Time taken: {end - start:.4f}s")
    session.close()

if __name__ == "__main__":
    asyncio.run(main())
