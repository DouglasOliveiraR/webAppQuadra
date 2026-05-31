import asyncio
import time
import os
import sys
from datetime import date, timedelta

# Setup environment to run tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))
os.environ["SECRET_KEY"] = "test_key"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.db.models import Base, FinanceiroModel
from api.db.repositories.financeiro_repo import SQLAlchemyFinanceiroRepository
from domain.financeiro.entities import Financeiro
from domain.financeiro.enums import StatusPagamento

class SQLAlchemyFinanceiroRepositoryOptimized(SQLAlchemyFinanceiroRepository):
    async def salvar_lote(self, lista_financeiro: list[Financeiro]) -> list[Financeiro]:
        if not lista_financeiro:
            return []
        model_list = []
        for item in lista_financeiro:
            model = self._to_model(item)
            if model.id:
                model = self.session.merge(model)
            else:
                self.session.add(model)
            model_list.append(model)

        self.session.flush()
        result = [self._to_entity(m) for m in model_list]
        self.session.commit()
        return result


async def run_benchmark():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    repo = SQLAlchemyFinanceiroRepository(session)
    repo_opt = SQLAlchemyFinanceiroRepositoryOptimized(session)

    base_date = date(2020, 1, 1)

    # Original
    items1 = []
    for i in range(1000):
        items1.append(Financeiro(
            id=None,
            usuario_id=i + 1,
            tipo="MENSALIDADE",
            valor=50.0,
            status_pagamento=StatusPagamento.PENDENTE,
            mes_referencia=base_date
        ))

    start = time.time()
    await repo.salvar_lote(items1)
    end = time.time()
    print(f"Time taken to salvar_lote insert 1000 items with N+1 queries: {end - start:.4f} seconds")

    session.close()

    engine2 = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine2)
    Session2 = sessionmaker(bind=engine2)
    session2 = Session2()
    repo_opt2 = SQLAlchemyFinanceiroRepositoryOptimized(session2)

    # Optimized
    items2 = []
    for i in range(1000):
        items2.append(Financeiro(
            id=None,
            usuario_id=i + 1,
            tipo="MENSALIDADE",
            valor=50.0,
            status_pagamento=StatusPagamento.PENDENTE,
            mes_referencia=base_date
        ))

    start = time.time()
    res = await repo_opt2.salvar_lote(items2)
    end = time.time()
    print(f"Time taken to salvar_lote insert 1000 items with flush+commit: {end - start:.4f} seconds")
    print(f"First ID from optimized: {res[0].id}")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
