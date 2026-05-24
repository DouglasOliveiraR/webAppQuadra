from typing import List, Optional
from sqlalchemy.orm import Session
from domain.eventos.entities import Evento
from domain.eventos.repositories import EventoRepository
from api.db.models import EventoModel

class SQLAlchemyEventoRepository(EventoRepository):
    def __init__(self, session: Session):
        self.session = session

    def _to_entity(self, model: EventoModel) -> Evento:
        if not model:
            return None
        return Evento(
            id=model.id,
            data_jogo=model.data_jogo,
            hora_inicio=model.hora_inicio,
            hora_fim=model.hora_fim,
            status_evento=model.status_evento,
            flag_churrasco=model.flag_churrasco,
            valor_churrasco=model.valor_churrasco,
            endereco=model.endereco,
            chave_pix=model.chave_pix,
            valor_mensalidade=model.valor_mensalidade
        )

    def _to_model(self, entity: Evento) -> EventoModel:
        return EventoModel(
            id=entity.id,
            data_jogo=entity.data_jogo,
            hora_inicio=entity.hora_inicio,
            hora_fim=entity.hora_fim,
            status_evento=entity.status_evento,
            flag_churrasco=entity.flag_churrasco,
            valor_churrasco=entity.valor_churrasco,
            endereco=entity.endereco,
            chave_pix=entity.chave_pix,
            valor_mensalidade=entity.valor_mensalidade
        )

    async def buscar_por_id(self, evento_id: int) -> Optional[Evento]:
        model = self.session.query(EventoModel).filter(EventoModel.id == evento_id).first()
        return self._to_entity(model)

    async def listar_todos(self) -> List[Evento]:
        models = self.session.query(EventoModel).all()
        return [self._to_entity(m) for m in models]

    async def salvar(self, evento: Evento) -> Evento:
        model = self._to_model(evento)
        if model.id:
            model = self.session.merge(model)
        else:
            self.session.add(model)
        
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    async def deletar(self, evento_id: int) -> bool:
        model = self.session.query(EventoModel).filter(EventoModel.id == evento_id).first()
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False
