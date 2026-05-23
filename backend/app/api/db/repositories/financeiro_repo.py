from typing import List, Optional
from sqlalchemy.orm import Session
from domain.financeiro.entities import Financeiro
from domain.financeiro.repositories import FinanceiroRepository
from api.db.models import FinanceiroModel

class SQLAlchemyFinanceiroRepository(FinanceiroRepository):
    def __init__(self, session: Session):
        self.session = session

    def _to_entity(self, model: FinanceiroModel) -> Financeiro:
        if not model:
            return None
        return Financeiro(
            id=model.id,
            usuario_id=model.usuario_id,
            tipo=model.tipo,
            valor=model.valor,
            status_pagamento=model.status_pagamento
        )

    def _to_model(self, entity: Financeiro) -> FinanceiroModel:
        return FinanceiroModel(
            id=entity.id,
            usuario_id=entity.usuario_id,
            tipo=entity.tipo,
            valor=entity.valor,
            status_pagamento=entity.status_pagamento
        )

    async def buscar_por_id(self, financeiro_id: int) -> Optional[Financeiro]:
        model = self.session.query(FinanceiroModel).filter(FinanceiroModel.id == financeiro_id).first()
        return self._to_entity(model)

    async def listar_por_usuario(self, usuario_id: int) -> List[Financeiro]:
        models = self.session.query(FinanceiroModel).filter(FinanceiroModel.usuario_id == usuario_id).all()
        return [self._to_entity(m) for m in models]

    async def salvar(self, financeiro: Financeiro) -> Financeiro:
        model = self._to_model(financeiro)
        if model.id:
            model = self.session.merge(model)
        else:
            self.session.add(model)
        
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    async def deletar(self, financeiro_id: int) -> bool:
        model = self.session.query(FinanceiroModel).filter(FinanceiroModel.id == financeiro_id).first()
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False
