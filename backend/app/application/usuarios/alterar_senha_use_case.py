from domain.usuarios.repositories import UsuarioRepository
from core.exceptions import RegraDeNegocioError
from core.security import verify_password, get_password_hash

class AlterarSenhaUseCase:
    def __init__(self, usuario_repo: UsuarioRepository):
        self.usuario_repo = usuario_repo

    async def executar(self, usuario_id: int, senha_atual: str, nova_senha: str) -> bool:
        usuario = await self.usuario_repo.buscar_por_id(usuario_id)
        if not usuario:
            raise RegraDeNegocioError("Jogador não encontrado.")

        if not verify_password(senha_atual, usuario.senha_hash):
            raise RegraDeNegocioError("Senha atual incorreta.")

        usuario.senha_hash = get_password_hash(nova_senha)
        await self.usuario_repo.salvar(usuario)
        return True
