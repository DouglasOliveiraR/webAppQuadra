from typing import List
from domain.usuarios.repositories import UsuarioRepository
from domain.usuarios.entities import Usuario

class ListarRankingUseCase:
    def __init__(self, usuario_repo: UsuarioRepository):
        self.usuario_repo = usuario_repo

    async def executar(self) -> List[Usuario]:
        usuarios = await self.usuario_repo.listar_todos()
        # Ordenar os usuários primariamente por pontos, secundariamente por nota da galera
        usuarios_ordenados = sorted(
            usuarios, 
            key=lambda u: (u.pontos_ranking, u.nota_galera_media), 
            reverse=True
        )
        return usuarios_ordenados
