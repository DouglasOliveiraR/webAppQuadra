from domain.eventos.repositories import EventoRepository
from core.exceptions import RegraDeNegocioError
from domain.eventos.entities import Evento

class AtualizarChurrascoUseCase:
    def __init__(self, evento_repo: EventoRepository):
        self.evento_repo = evento_repo

    async def executar(self, evento_id: int, flag_churrasco: bool, valor_churrasco: float) -> Evento:
        evento = await self.evento_repo.buscar_por_id(evento_id)
        if not evento:
            raise RegraDeNegocioError("Evento não encontrado")

        evento.flag_churrasco = flag_churrasco
        evento.valor_churrasco = valor_churrasco

        await self.evento_repo.salvar(evento)
        return evento
