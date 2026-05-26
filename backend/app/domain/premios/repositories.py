from abc import ABC, abstractmethod
from typing import List, Optional
from domain.premios.entities import Premio

class PremioRepository(ABC):
    @abstractmethod
    async def salvar(self, premio: Premio) -> Premio:
        pass

    @abstractmethod
    async def salvar_lote(self, premios: List[Premio]) -> List[Premio]:
        pass

    @abstractmethod
    async def listar_todos(self) -> List[Premio]:
        pass

    @abstractmethod
    async def listar_por_usuario(self, usuario_id: int) -> List[Premio]:
        pass
