from domain.usuarios.repositories import UsuarioRepository
from core.security import verify_password, create_access_token
from core.exceptions import CredenciaisInvalidasError

class LoginUseCase:
    def __init__(self, usuario_repo: UsuarioRepository):
        self.usuario_repo = usuario_repo

    async def executar(self, telefone: str, senha_plain: str) -> str:
        usuario = await self.usuario_repo.buscar_por_telefone(telefone)
        if not usuario:
            raise CredenciaisInvalidasError("Telefone ou senha incorretos")
        
        if not verify_password(senha_plain, usuario.senha_hash):
            raise CredenciaisInvalidasError("Telefone ou senha incorretos")
            
        if usuario.status != "ATIVO":
            raise CredenciaisInvalidasError("Usuário inativo")
            
        token_data = {"sub": str(usuario.id), "perfil": usuario.perfil.value}
        return create_access_token(token_data)
