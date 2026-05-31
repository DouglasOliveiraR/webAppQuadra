from domain.usuarios.repositories import UsuarioRepository
from domain.presencas.repositories import PresencaRepository
from domain.financeiro.repositories import FinanceiroRepository
from domain.eventos.repositories import EventoRepository
from domain.usuarios.enums import StatusUsuario
from domain.eventos.enums import StatusEvento
from domain.financeiro.enums import StatusPagamento
import time

class DeletarUsuarioUseCase:
    def __init__(
        self,
        usuario_repo: UsuarioRepository,
        presenca_repo: PresencaRepository,
        financeiro_repo: FinanceiroRepository,
        evento_repo: EventoRepository
    ):
        self.usuario_repo = usuario_repo
        self.presenca_repo = presenca_repo
        self.financeiro_repo = financeiro_repo
        self.evento_repo = evento_repo

    async def executar(self, usuario_id: int) -> bool:
        usuario = await self.usuario_repo.buscar_por_id(usuario_id)
        if not usuario:
            return False

        usuario.status = StatusUsuario.INATIVO
        usuario.telefone = f"{usuario.telefone}_del_{int(time.time())}"

        await self.usuario_repo.salvar(usuario)

        # Limpar presenças em eventos não concluídos (ABERTO ou VOTACAO)
        eventos = await self.evento_repo.listar_todos()
        eventos_nao_concluidos_ids = [e.id for e in eventos if e.status_evento in [StatusEvento.PRESENCA_ABERTA, StatusEvento.VOTACAO_ABERTA]]

        if eventos_nao_concluidos_ids:
            await self.presenca_repo.deletar_por_usuario_em_eventos(usuario_id, eventos_nao_concluidos_ids)

        # Limpar financeiro pendente do usuário
        await self.financeiro_repo.deletar_pendentes_por_usuario(usuario_id)

        return True
