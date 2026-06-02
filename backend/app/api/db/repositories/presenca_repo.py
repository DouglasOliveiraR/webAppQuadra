from typing import List, Optional
from sqlalchemy.orm import Session
from domain.presencas.entities import Presenca
from domain.presencas.repositories import PresencaRepository
from api.db.models import PresencaModel

class SQLAlchemyPresencaRepository(PresencaRepository):
    def __init__(self, session: Session):
        self.session = session

    def _to_entity(self, model: PresencaModel) -> Presenca:
        if not model:
            return None
        return Presenca(
            id=model.id,
            usuario_id=model.usuario_id,
            evento_id=model.evento_id,
            status_jogo=model.status_jogo,
            posicao=model.posicao,
            vai_churrasco=model.vai_churrasco,
            checkin_validado=model.checkin_validado,
            falta_penalizada=model.falta_penalizada,
            gols=model.gols,
            criado_em=model.criado_em,
            atualizado_em=model.atualizado_em
        )

    def _to_model(self, entity: Presenca) -> PresencaModel:
        model = PresencaModel(
            id=entity.id,
            usuario_id=entity.usuario_id,
            evento_id=entity.evento_id,
            status_jogo=entity.status_jogo,
            posicao=entity.posicao,
            vai_churrasco=entity.vai_churrasco,
            checkin_validado=entity.checkin_validado,
            falta_penalizada=entity.falta_penalizada,
            gols=entity.gols
        )
        if entity.criado_em:
            model.criado_em = entity.criado_em
        if entity.atualizado_em:
            model.atualizado_em = entity.atualizado_em
        return model

    async def buscar_por_id(self, presenca_id: int) -> Optional[Presenca]:
        model = self.session.query(PresencaModel).filter(PresencaModel.id == presenca_id).first()
        return self._to_entity(model)

    async def buscar_por_usuario_evento(self, usuario_id: int, evento_id: int) -> Optional[Presenca]:
        model = self.session.query(PresencaModel).filter(
            PresencaModel.usuario_id == usuario_id,
            PresencaModel.evento_id == evento_id
        ).first()
        return self._to_entity(model)

    async def listar_por_eventos(self, eventos_ids: List[int]) -> List[Presenca]:
        if not eventos_ids:
            return []
        models = self.session.query(PresencaModel).filter(PresencaModel.evento_id.in_(eventos_ids)).all()
        return [self._to_entity(m) for m in models]

    async def listar_por_evento(self, evento_id: int) -> List[Presenca]:
        models = self.session.query(PresencaModel).filter(PresencaModel.evento_id == evento_id).all()
        return [self._to_entity(m) for m in models]

    async def salvar(self, presenca: Presenca) -> Presenca:
        model = self._to_model(presenca)
        if model.id:
            model = self.session.merge(model)
        else:
            self.session.add(model)
        
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    async def deletar(self, presenca_id: int) -> bool:
        model = self.session.query(PresencaModel).filter(PresencaModel.id == presenca_id).first()
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False

    async def deletar_por_usuario_em_eventos(self, usuario_id: int, eventos_ids: List[int]) -> bool:
        if not eventos_ids:
            return True

        self.session.query(PresencaModel).filter(PresencaModel.usuario_id == usuario_id, PresencaModel.evento_id.in_(eventos_ids)).delete(synchronize_session=False)
        self.session.commit()
        return True
