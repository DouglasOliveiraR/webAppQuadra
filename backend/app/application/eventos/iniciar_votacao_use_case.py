from domain.eventos.repositories import EventoRepository
from domain.eventos.enums import StatusEvento
from core.exceptions import RegraDeNegocioError

class IniciarVotacaoUseCase:
    def __init__(self, evento_repo: EventoRepository):
        self.evento_repo = evento_repo

    async def executar(self, evento_id: int):
        evento = await self.evento_repo.buscar_por_id(evento_id)
        if not evento:
            raise RegraDeNegocioError("Evento não encontrado")
            
        if evento.status_evento != StatusEvento.PRESENCA_ABERTA:
            raise RegraDeNegocioError("O evento não está em fase de presença para iniciar a votação")
            
        evento.status_evento = StatusEvento.VOTACAO_ABERTA
        return await self.evento_repo.salvar(evento)
