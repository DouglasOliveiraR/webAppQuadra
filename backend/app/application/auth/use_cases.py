from datetime import timedelta
import logging
from domain.usuarios.repositories import UsuarioRepository
from domain.usuarios.enums import StatusUsuario
from core.security import verify_password, create_access_token
from core.config import settings
from core.exceptions import CredenciaisInvalidasError

logger = logging.getLogger(__name__)

class LoginUseCase:
    def __init__(self, usuario_repo: UsuarioRepository):
        self.usuario_repo = usuario_repo

    async def executar(self, telefone: str, senha_plain: str) -> str:
        usuario = await self.usuario_repo.buscar_por_telefone(telefone)
        if not usuario:
            logger.warning(f"Tentativa de login falha: Usuário não encontrado para o telefone {telefone}")
            raise CredenciaisInvalidasError("Telefone ou senha incorretos")
        
        if not verify_password(senha_plain, usuario.senha_hash):
            logger.warning(f"Tentativa de login falha: Senha incorreta para o telefone {telefone}")
            raise CredenciaisInvalidasError("Telefone ou senha incorretos")
            
        if usuario.status != StatusUsuario.ATIVO:
            logger.warning(f"Tentativa de login falha: Usuário inativo para o telefone {telefone}")
            raise CredenciaisInvalidasError("Usuário inativo")
            
        token_data = {"sub": str(usuario.id), "perfil": usuario.perfil.value, "nome": usuario.nome}
        expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return create_access_token(token_data, expires_delta=expires)
