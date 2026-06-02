import json
from domain.notificacoes.entities import PushSubscription
from domain.notificacoes.repositories import PushSubscriptionRepository

class RegistrarInscricaoUseCase:
    def __init__(self, push_repo: PushSubscriptionRepository):
        self.push_repo = push_repo

    async def executar(self, usuario_id: int, subscription_data: dict) -> bool:
        # Convert the dictionary back to JSON string for storage
        sub_json = json.dumps(subscription_data)
        
        subscription = PushSubscription(
            id=None,
            usuario_id=usuario_id,
            subscription_json=sub_json
        )
        
        await self.push_repo.salvar(subscription)
        return True

class DesregistrarInscricaoUseCase:
    def __init__(self, push_repo: PushSubscriptionRepository):
        self.push_repo = push_repo

    async def executar(self, endpoint: str) -> bool:
        return await self.push_repo.deletar_por_endpoint(endpoint)
