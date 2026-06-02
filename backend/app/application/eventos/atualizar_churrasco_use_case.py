from domain.eventos.repositories import EventoRepository
from core.exceptions import RegraDeNegocioError
from domain.eventos.entities import Evento
from application.notificacoes.disparar_notificacao import DispararNotificacaoUseCase

class AtualizarChurrascoUseCase:
    def __init__(self, evento_repo: EventoRepository, disparar_notificacao_uc: DispararNotificacaoUseCase = None):
        self.evento_repo = evento_repo
        self.disparar_notificacao_uc = disparar_notificacao_uc

    async def executar(self, evento_id: int, flag_churrasco: bool, valor_churrasco: float) -> Evento:
        evento = await self.evento_repo.buscar_por_id(evento_id)
        if not evento:
            raise RegraDeNegocioError("Evento não encontrado")

        churrasco_foi_ativado = (not evento.flag_churrasco) and flag_churrasco

        evento.flag_churrasco = flag_churrasco
        evento.valor_churrasco = valor_churrasco

        await self.evento_repo.salvar(evento)

        if churrasco_foi_ativado and self.disparar_notificacao_uc:
            try:
                await self.disparar_notificacao_uc.executar(
                    titulo="Vai ter Churras! 🍖🍻",
                    corpo=f"O admin ativou o churrasco da pelada no valor de R${valor_churrasco:.2f}. Acesse o app para confirmar se vai!",
                    url="/"
                )
            except Exception:
                pass  # Ignore notification errors

        return evento
