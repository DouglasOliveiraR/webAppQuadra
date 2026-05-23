from domain.usuarios.repositories import UsuarioRepository
from core.exceptions import RegraDeNegocioError
from domain.usuarios.entities import Usuario

class AtualizarNotaAdminUseCase:
    def __init__(self, usuario_repo: UsuarioRepository):
        self.usuario_repo = usuario_repo

    async def executar(self, usuario_id: int, nota: float) -> Usuario:
        if nota < 0 or nota > 10:
            raise RegraDeNegocioError("Nota deve estar entre 0 e 10.")
            
        usuario = await self.usuario_repo.buscar_por_id(usuario_id)
        if not usuario:
            raise RegraDeNegocioError("Usuário não encontrado.")

        usuario.nota_admin = nota
        await self.usuario_repo.salvar(usuario)
        return usuario
