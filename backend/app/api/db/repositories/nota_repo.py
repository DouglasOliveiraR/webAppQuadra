from typing import List, Optional
from sqlalchemy.orm import Session
from domain.notas.entities import Nota
from domain.notas.repositories import NotaRepository
from api.db.models import NotaModel, TipoNota

class SQLAlchemyNotaRepository(NotaRepository):
    def __init__(self, session: Session):
        self.session = session

    def _to_entity(self, model: NotaModel) -> Nota:
        if not model:
            return None
        return Nota(
            id=model.id,
            avaliado_id=model.avaliado_id,
            avaliador_id=model.avaliador_id,
            evento_id=model.evento_id,
            nota=model.nota,
            tipo=model.tipo.value,
            criado_em=model.criado_em
        )

    def _to_model(self, entity: Nota) -> NotaModel:
        model = NotaModel(
            id=entity.id,
            avaliado_id=entity.avaliado_id,
            avaliador_id=entity.avaliador_id,
            evento_id=entity.evento_id,
            nota=entity.nota,
            tipo=TipoNota(entity.tipo)
        )
        if entity.criado_em:
            model.criado_em = entity.criado_em
        return model

    async def salvar(self, nota: Nota) -> Nota:
        model = self._to_model(nota)
        if model.id:
            model = self.session.merge(model)
        else:
            self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    async def salvar_lote(self, notas: List[Nota]) -> None:
        for nota in notas:
            model = self._to_model(nota)
            if model.id:
                self.session.merge(model)
            else:
                self.session.add(model)
        self.session.commit()

    async def listar_por_avaliado(self, avaliado_id: int) -> List[Nota]:
        models = self.session.query(NotaModel).filter(NotaModel.avaliado_id == avaliado_id).all()
        return [self._to_entity(m) for m in models]

    async def listar_por_avaliador_e_evento(self, avaliador_id: int, evento_id: int) -> List[Nota]:
        models = self.session.query(NotaModel).filter(
            NotaModel.avaliador_id == avaliador_id,
            NotaModel.evento_id == evento_id,
            NotaModel.tipo == TipoNota.GALERA
        ).all()
        return [self._to_entity(m) for m in models]
