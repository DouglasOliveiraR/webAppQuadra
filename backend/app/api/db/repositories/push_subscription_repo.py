from typing import List
from sqlalchemy.orm import Session
from domain.notificacoes.entities import PushSubscription
from domain.notificacoes.repositories import PushSubscriptionRepository
from api.db.models import PushSubscriptionModel

class SQLAlchemyPushSubscriptionRepository(PushSubscriptionRepository):
    def __init__(self, session: Session):
        self.session = session

    def _to_entity(self, model: PushSubscriptionModel) -> PushSubscription:
        if not model:
            return None
        return PushSubscription(
            id=model.id,
            usuario_id=model.usuario_id,
            subscription_json=model.subscription_json,
            criado_em=model.criado_em
        )

    def _to_model(self, entity: PushSubscription) -> PushSubscriptionModel:
        model = PushSubscriptionModel(
            id=entity.id,
            usuario_id=entity.usuario_id,
            subscription_json=entity.subscription_json
        )
        if entity.criado_em:
            model.criado_em = entity.criado_em
        return model

    async def salvar(self, subscription: PushSubscription) -> PushSubscription:
        model = self._to_model(subscription)
        
        # Avoid duplicate exact subscriptions
        existing = self.session.query(PushSubscriptionModel).filter(
            PushSubscriptionModel.usuario_id == model.usuario_id,
            PushSubscriptionModel.subscription_json == model.subscription_json
        ).first()
        
        if existing:
            return self._to_entity(existing)
            
        if model.id:
            self.session.merge(model)
        else:
            self.session.add(model)
        
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    async def deletar_por_endpoint(self, endpoint: str) -> bool:
        # Note: In SQLite we might need to use LIKE to match the endpoint inside the JSON string
        models = self.session.query(PushSubscriptionModel).filter(
            PushSubscriptionModel.subscription_json.like(f"%{endpoint}%")
        ).all()
        
        if models:
            for m in models:
                self.session.delete(m)
            self.session.commit()
            return True
        return False

    async def listar_por_usuario(self, usuario_id: int) -> List[PushSubscription]:
        models = self.session.query(PushSubscriptionModel).filter(
            PushSubscriptionModel.usuario_id == usuario_id
        ).all()
        return [self._to_entity(m) for m in models]

    async def listar_todos(self) -> List[PushSubscription]:
        models = self.session.query(PushSubscriptionModel).all()
        return [self._to_entity(m) for m in models]
