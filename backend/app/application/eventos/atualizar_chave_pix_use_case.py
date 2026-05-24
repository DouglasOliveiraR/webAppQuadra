from domain.eventos.repositories import EventoRepository
from core.exceptions import RegraDeNegocioError
from domain.eventos.entities import Evento

class AtualizarChavePixUseCase:
    def __init__(self, evento_repo: EventoRepository):
        self.evento_repo = evento_repo

    async def executar(self, evento_id: int, chave_pix: str) -> Evento:
        evento = await self.evento_repo.buscar_por_id(evento_id)
        if not evento:
            raise RegraDeNegocioError("Evento não encontrado")

        evento.chave_pix = chave_pix

        await self.evento_repo.salvar(evento)
        return evento
