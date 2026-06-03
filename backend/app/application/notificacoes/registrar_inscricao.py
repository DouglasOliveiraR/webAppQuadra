import json
from domain.notificacoes.entities import PushSubscription
from domain.notificacoes.repositories import PushSubscriptionRepository

class RegistrarInscricaoUseCase:
    def __init__(self, push_repo: PushSubscriptionRepository):
        self.push_repo = push_repo

    async def executar(self, usuario_id: int, subscription_data: dict) -> bool:
        endpoint = subscription_data.get("endpoint")
        if not endpoint:
            raise ValueError("Payload inválido: sem endpoint")

        # [Security Fix] Previne que um usuário forje o endpoint para sobrescrever ou roubar a inscrição de outro
        inscricao_existente = await self.push_repo.buscar_por_endpoint(endpoint)
        if inscricao_existente and inscricao_existente.usuario_id != usuario_id:
            raise ValueError("Endpoint já registrado por outro usuário")

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
