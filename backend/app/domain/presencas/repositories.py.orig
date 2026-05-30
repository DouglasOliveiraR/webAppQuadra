from abc import ABC, abstractmethod
from typing import List, Optional
from domain.presencas.entities import Presenca

class PresencaRepository(ABC):
    @abstractmethod
    async def buscar_por_id(self, presenca_id: int) -> Optional[Presenca]:
        pass

    @abstractmethod
    async def buscar_por_usuario_evento(self, usuario_id: int, evento_id: int) -> Optional[Presenca]:
        pass

    @abstractmethod
    async def listar_por_evento(self, evento_id: int) -> List[Presenca]:
        pass

    @abstractmethod
    async def salvar(self, presenca: Presenca) -> Presenca:
        pass

    @abstractmethod
    async def deletar(self, presenca_id: int) -> bool:
        pass
