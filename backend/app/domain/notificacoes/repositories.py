from abc import ABC, abstractmethod
from typing import List
from domain.notificacoes.entities import PushSubscription

class PushSubscriptionRepository(ABC):
    @abstractmethod
    async def salvar(self, subscription: PushSubscription) -> PushSubscription:
        pass

    @abstractmethod
    async def deletar_por_endpoint(self, endpoint: str) -> bool:
        pass

    @abstractmethod
    async def listar_por_usuario(self, usuario_id: int) -> List[PushSubscription]:
        pass

    @abstractmethod
    async def listar_todos(self) -> List[PushSubscription]:
        pass

    @abstractmethod
    async def listar_por_usuarios(self, usuarios_ids: List[int]) -> List[PushSubscription]:
        pass
