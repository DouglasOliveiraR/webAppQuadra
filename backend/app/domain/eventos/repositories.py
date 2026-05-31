from abc import ABC, abstractmethod
from typing import List, Optional
from domain.eventos.entities import Evento

class EventoRepository(ABC):
    @abstractmethod
    async def buscar_por_id(self, evento_id: int) -> Optional[Evento]:
        pass

    @abstractmethod
    async def listar_todos(self) -> List[Evento]:
        pass

    @abstractmethod
    async def obter_ultimo_evento_encerrado(self) -> Optional[Evento]:
        pass

    @abstractmethod
    async def salvar(self, evento: Evento) -> Evento:
        pass

    @abstractmethod
    async def deletar(self, evento_id: int) -> bool:
        pass
