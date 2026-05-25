from domain.usuarios.repositories import UsuarioRepository
from core.exceptions import RegraDeNegocioError
from domain.usuarios.entities import Usuario

class AtualizarFotoPerfilUseCase:
    def __init__(self, usuario_repo: UsuarioRepository):
        self.usuario_repo = usuario_repo

    async def executar(self, usuario_id: int, foto_url: str) -> Usuario:
        usuario = await self.usuario_repo.buscar_por_id(usuario_id)
        if not usuario:
            raise RegraDeNegocioError("Usuário não encontrado.")

        usuario.foto_url = foto_url
        await self.usuario_repo.salvar(usuario)
        return usuario
