from domain.eventos.repositories import EventoRepository
from core.exceptions import RegraDeNegocioError
from domain.eventos.entities import Evento

class AtualizarCustoQuadraUseCase:
    def __init__(self, evento_repo: EventoRepository):
        self.evento_repo = evento_repo

    async def executar(self, evento_id: int, custo_quadra: float) -> Evento:
        evento = await self.evento_repo.buscar_por_id(evento_id)
        if not evento:
            raise RegraDeNegocioError("Evento não encontrado")

        evento.custo_quadra = custo_quadra

        await self.evento_repo.salvar(evento)
        return evento
