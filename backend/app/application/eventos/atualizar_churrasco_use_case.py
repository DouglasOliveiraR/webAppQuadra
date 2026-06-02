from domain.eventos.repositories import EventoRepository
from domain.usuarios.repositories import UsuarioRepository
from domain.usuarios.enums import PerfilUsuario
from core.exceptions import RegraDeNegocioError
from domain.eventos.entities import Evento
from application.notificacoes.disparar_notificacao import DispararNotificacaoUseCase

class AtualizarChurrascoUseCase:
    def __init__(self, evento_repo: EventoRepository, usuario_repo: UsuarioRepository, disparar_notificacao_uc: DispararNotificacaoUseCase = None):
        self.evento_repo = evento_repo
        self.usuario_repo = usuario_repo
        self.disparar_notificacao_uc = disparar_notificacao_uc

    async def executar(self, evento_id: int, flag_churrasco: bool, valor_churrasco: float) -> Evento:
        evento = await self.evento_repo.buscar_por_id(evento_id)
        if not evento:
            raise RegraDeNegocioError("Evento não encontrado")

        churrasco_foi_ativado = flag_churrasco

        evento.flag_churrasco = flag_churrasco
        evento.valor_churrasco = valor_churrasco

        await self.evento_repo.salvar(evento)

        if churrasco_foi_ativado and self.disparar_notificacao_uc:
            try:
                todos_usuarios = await self.usuario_repo.listar_todos()
                ids_alvos = [u.id for u in todos_usuarios if u.perfil in (PerfilUsuario.MENSALISTA, PerfilUsuario.ADMIN)]
                
                if ids_alvos:
                    await self.disparar_notificacao_uc.executar(
                        titulo="Vai ter Churras! 🍖🍻",
                        corpo=f"O admin ativou o churrasco da pelada no valor de R${valor_churrasco:.2f}. Acesse o app para confirmar se vai!",
                        url="/",
                        usuarios_ids=ids_alvos
                    )
            except Exception:
                pass  # Ignore notification errors

        return evento
