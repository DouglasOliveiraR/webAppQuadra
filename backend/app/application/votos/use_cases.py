from domain.votos.repositories import VotoRepository
from domain.eventos.repositories import EventoRepository
from domain.votos.entities import Voto
from domain.votos.enums import CategoriaVoto
from domain.eventos.enums import StatusEvento
from core.exceptions import RegraDeNegocioError

class RegistrarVotoUseCase:
    def __init__(self, voto_repo: VotoRepository, evento_repo: EventoRepository):
        self.voto_repo = voto_repo
        self.evento_repo = evento_repo

    async def executar(self, evento_id: int, eleitor_id: int, candidato_id: int, categoria: CategoriaVoto):
        evento = await self.evento_repo.buscar_por_id(evento_id)
        if not evento:
            raise RegraDeNegocioError("Evento não encontrado")
            
        if evento.status_evento != StatusEvento.VOTACAO_ABERTA:
            raise RegraDeNegocioError("A votação para este evento não está aberta")
            
        if eleitor_id == candidato_id:
            raise RegraDeNegocioError("Você não pode votar em si mesmo")
            
        voto_existente = await self.voto_repo.buscar_voto_eleitor(evento_id, eleitor_id, categoria)
        if voto_existente:
            raise RegraDeNegocioError(f"Você já votou para a categoria {categoria.value} neste evento")
            
        voto = Voto(
            id=None,
            evento_id=evento_id,
            eleitor_id=eleitor_id,
            candidato_id=candidato_id,
            categoria=categoria
        )
        return await self.voto_repo.salvar(voto)
