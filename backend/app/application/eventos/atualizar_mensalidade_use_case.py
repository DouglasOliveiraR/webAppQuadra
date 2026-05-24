from domain.eventos.repositories import EventoRepository
from core.exceptions import RegraDeNegocioError
from domain.eventos.entities import Evento

class AtualizarMensalidadeUseCase:
    def __init__(self, evento_repo: EventoRepository):
        self.evento_repo = evento_repo

    async def executar(self, evento_id: int, valor_mensalidade: float) -> Evento:
        evento = await self.evento_repo.buscar_por_id(evento_id)
        if not evento:
            raise RegraDeNegocioError("Evento não encontrado")

        evento.valor_mensalidade = valor_mensalidade

        await self.evento_repo.salvar(evento)
        return evento
