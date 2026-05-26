from abc import ABC, abstractmethod
from typing import List, Optional
from domain.usuarios.entities import Usuario

class UsuarioRepository(ABC):
    @abstractmethod
    async def buscar_por_id(self, usuario_id: int) -> Optional[Usuario]:
        pass

    @abstractmethod
    async def buscar_por_telefone(self, telefone: str) -> Optional[Usuario]:
        pass

    @abstractmethod
    async def buscar_por_ids(self, usuario_ids: List[int]) -> List[Usuario]:
        pass

    @abstractmethod
    async def listar_todos(self) -> List[Usuario]:
        pass

    @abstractmethod
    async def salvar(self, usuario: Usuario) -> Usuario:
        pass

    @abstractmethod
    async def salvar_lote(self, usuarios: List[Usuario]) -> List[Usuario]:
        pass

    @abstractmethod
    async def deletar(self, usuario_id: int) -> bool:
        pass

    @abstractmethod
    async def deletar_lote(self, usuario_ids: List[int]) -> bool:
        pass
