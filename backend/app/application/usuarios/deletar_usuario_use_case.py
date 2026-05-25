from domain.usuarios.repositories import UsuarioRepository

class DeletarUsuarioUseCase:
    def __init__(self, usuario_repo: UsuarioRepository):
        self.usuario_repo = usuario_repo

    async def executar(self, usuario_id: int) -> bool:
        usuario = await self.usuario_repo.buscar_por_id(usuario_id)
        if not usuario:
            return False
            
        return await self.usuario_repo.deletar(usuario_id)
