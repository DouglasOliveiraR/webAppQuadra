from abc import ABC, abstractmethod
from typing import List, Optional
from domain.financeiro.entities import Financeiro

class FinanceiroRepository(ABC):
    @abstractmethod
    async def buscar_por_id(self, financeiro_id: int) -> Optional[Financeiro]:
        pass

    @abstractmethod
    async def listar_por_usuario(self, usuario_id: int) -> List[Financeiro]:
        pass

    @abstractmethod
    async def listar_todos(self) -> List[Financeiro]:
        pass

    @abstractmethod
    async def listar_por_mes(self, mes: str) -> List[Financeiro]:
        pass

    @abstractmethod
    async def salvar(self, financeiro: Financeiro) -> Financeiro:
        pass

    @abstractmethod
    async def deletar(self, financeiro_id: int) -> bool:
        pass

    @abstractmethod
    async def deletar_pendentes_por_usuario(self, usuario_id: int) -> bool:
        pass
