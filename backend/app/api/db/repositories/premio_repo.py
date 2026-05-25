from typing import List, Optional
from sqlalchemy.orm import Session
from domain.premios.entities import Premio
from domain.premios.repositories import PremioRepository
from api.db.models import PremioModel
from domain.votos.enums import CategoriaVoto

class SQLAlchemyPremioRepository(PremioRepository):
    def __init__(self, session: Session):
        self.session = session

    def _to_entity(self, model: PremioModel) -> Premio:
        if not model:
            return None
        return Premio(
            id=model.id,
            usuario_id=model.usuario_id,
            evento_id=model.evento_id,
            categoria=CategoriaVoto(model.categoria),
            mes_referencia=model.mes_referencia,
            criado_em=model.criado_em
        )

    def _to_model(self, entity: Premio) -> PremioModel:
        model = PremioModel(
            id=entity.id,
            usuario_id=entity.usuario_id,
            evento_id=entity.evento_id,
            categoria=entity.categoria,
            mes_referencia=entity.mes_referencia
        )
        if entity.criado_em:
            model.criado_em = entity.criado_em
        return model

    async def salvar(self, premio: Premio) -> Premio:
        model = self._to_model(premio)
        if model.id:
            model = self.session.merge(model)
        else:
            self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    async def listar_todos(self) -> List[Premio]:
        models = self.session.query(PremioModel).all()
        return [self._to_entity(m) for m in models]

    async def listar_por_usuario(self, usuario_id: int) -> List[Premio]:
        models = self.session.query(PremioModel).filter(PremioModel.usuario_id == usuario_id).all()
        return [self._to_entity(m) for m in models]
