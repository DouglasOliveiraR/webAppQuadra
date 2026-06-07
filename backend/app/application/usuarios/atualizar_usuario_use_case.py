from domain.usuarios.repositories import UsuarioRepository
from domain.usuarios.entities import Usuario
from domain.usuarios.enums import StatusUsuario, PerfilUsuario
from core.exceptions import RegraDeNegocioError

class AtualizarUsuarioUseCase:
    def __init__(self, usuario_repo: UsuarioRepository):
        self.usuario_repo = usuario_repo

    async def executar(self, usuario_id: int, nome: str, telefone: str, perfil: PerfilUsuario, status: StatusUsuario, nota_admin: int) -> Usuario:
        usuario = await self.usuario_repo.buscar_por_id(usuario_id)
        if not usuario:
            raise RegraDeNegocioError("Jogador não encontrado.")

        if usuario.telefone != telefone:
            if telefone and not telefone.startswith("AVULSO_"):
                import re
                telefone = re.sub(r'\D', '', telefone)
            
            existente = await self.usuario_repo.buscar_por_telefone(telefone)
            if existente and existente.id != usuario_id:
                raise RegraDeNegocioError("Outro jogador com este telefone já está cadastrado.")

        usuario.nome = nome
        usuario.telefone = telefone
        usuario.perfil = perfil
        usuario.status = status
        usuario.nota_admin = nota_admin

        return await self.usuario_repo.salvar(usuario)
