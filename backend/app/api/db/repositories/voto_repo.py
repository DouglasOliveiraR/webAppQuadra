from typing import List, Optional
from sqlalchemy.orm import Session
from domain.votos.entities import Voto
from domain.votos.repositories import VotoRepository
from api.db.models import VotoModel

class SQLAlchemyVotoRepository(VotoRepository):
    def __init__(self, session: Session):
        self.session = session

    def _to_entity(self, model: VotoModel) -> Voto:
        if not model:
            return None
        return Voto(
            id=model.id,
            evento_id=model.evento_id,
            eleitor_id=model.eleitor_id,
            candidato_id=model.candidato_id,
            categoria=model.categoria,
            criado_em=model.criado_em,
            atualizado_em=model.atualizado_em
        )

    def _to_model(self, entity: Voto) -> VotoModel:
        model = VotoModel(
            id=entity.id,
            evento_id=entity.evento_id,
            eleitor_id=entity.eleitor_id,
            candidato_id=entity.candidato_id,
            categoria=entity.categoria
        )
        if entity.criado_em:
            model.criado_em = entity.criado_em
        if entity.atualizado_em:
            model.atualizado_em = entity.atualizado_em
        return model

    async def buscar_por_id(self, voto_id: int) -> Optional[Voto]:
        model = self.session.query(VotoModel).filter(VotoModel.id == voto_id).first()
        return self._to_entity(model)

    async def listar_por_evento(self, evento_id: int) -> List[Voto]:
        models = self.session.query(VotoModel).filter(VotoModel.evento_id == evento_id).all()
        return [self._to_entity(m) for m in models]

    async def buscar_voto_eleitor(self, evento_id: int, eleitor_id: int, categoria: str) -> Optional[Voto]:
        model = self.session.query(VotoModel).filter(
            VotoModel.evento_id == evento_id,
            VotoModel.eleitor_id == eleitor_id,
            VotoModel.categoria == categoria
        ).first()
        return self._to_entity(model)

    async def salvar(self, voto: Voto) -> Voto:
        model = self._to_model(voto)
        if model.id:
            model = self.session.merge(model)
        else:
            self.session.add(model)
        
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    async def deletar(self, voto_id: int) -> bool:
        model = self.session.query(VotoModel).filter(VotoModel.id == voto_id).first()
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False
