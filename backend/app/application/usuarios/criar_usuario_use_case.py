from domain.usuarios.repositories import UsuarioRepository
from domain.usuarios.entities import Usuario
from domain.usuarios.enums import StatusUsuario, PerfilUsuario
from core.exceptions import RegraDeNegocioError
from core.security import get_password_hash

class CriarUsuarioUseCase:
    def __init__(self, usuario_repo: UsuarioRepository):
        self.usuario_repo = usuario_repo

    async def executar(self, nome: str, telefone: str, perfil: PerfilUsuario, nota_admin: int) -> Usuario:
        existente = await self.usuario_repo.buscar_por_telefone(telefone)
        if existente:
            raise RegraDeNegocioError("Um jogador com este telefone já está cadastrado.")

        senha_padrao = "123456"
        senha_hash = get_password_hash(senha_padrao)

        novo_usuario = Usuario(
            id=None,
            nome=nome,
            telefone=telefone,
            senha_hash=senha_hash,
            perfil=perfil,
            status=StatusUsuario.ATIVO,
            nota_admin=nota_admin,
            nota_galera_media=5.0,
            pontos_ranking=0
        )

        return await self.usuario_repo.salvar(novo_usuario)
