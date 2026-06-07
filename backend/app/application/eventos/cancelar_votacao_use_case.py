from domain.eventos.repositories import EventoRepository
from domain.votos.repositories import VotoRepository
from domain.eventos.enums import StatusEvento
from core.exceptions import RegraDeNegocioError

class CancelarVotacaoUseCase:
    def __init__(self, evento_repo: EventoRepository, voto_repo: VotoRepository):
        self.evento_repo = evento_repo
        self.voto_repo = voto_repo

    async def executar(self, evento_id: int):
        evento = await self.evento_repo.buscar_por_id(evento_id)
        if not evento:
            raise RegraDeNegocioError("Evento não encontrado")
            
        if evento.status_evento != StatusEvento.VOTACAO_ABERTA:
            raise RegraDeNegocioError("O evento não está em fase de votação para ser cancelado.")
            
        # Retorna para a fase de presenças
        evento.status_evento = StatusEvento.PRESENCA_ABERTA
        
        # Apaga eventuais votos que já foram feitos para não ficarem "fantasmas"
        await self.voto_repo.deletar_por_evento(evento_id)
            
        return await self.evento_repo.salvar(evento)
