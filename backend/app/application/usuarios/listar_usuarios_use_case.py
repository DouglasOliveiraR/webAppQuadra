from typing import List
from domain.usuarios.entities import Usuario
from domain.usuarios.repositories import UsuarioRepository

class ListarUsuariosUseCase:
    def __init__(self, usuario_repo: UsuarioRepository):
        self.usuario_repo = usuario_repo

    async def executar(self) -> List[Usuario]:
        return await self.usuario_repo.listar_todos()
