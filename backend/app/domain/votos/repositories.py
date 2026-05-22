from abc import ABC, abstractmethod
from typing import List, Optional
from domain.votos.entities import Voto

class VotoRepository(ABC):
    @abstractmethod
    async def buscar_por_id(self, voto_id: int) -> Optional[Voto]:
        pass

    @abstractmethod
    async def listar_por_evento(self, evento_id: int) -> List[Voto]:
        pass

    @abstractmethod
    async def buscar_voto_eleitor(self, evento_id: int, eleitor_id: int, categoria: str) -> Optional[Voto]:
        pass

    @abstractmethod
    async def salvar(self, voto: Voto) -> Voto:
        pass

    @abstractmethod
    async def deletar(self, voto_id: int) -> bool:
        pass
