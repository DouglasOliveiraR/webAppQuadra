from domain.eventos.repositories import EventoRepository
from domain.eventos.entities import Evento
from typing import List

class CriarEventoUseCase:
    def __init__(self, evento_repo: EventoRepository):
        self.evento_repo = evento_repo
        
    async def executar(self, evento: Evento) -> Evento:
        return await self.evento_repo.salvar(evento)

class ListarEventosUseCase:
    def __init__(self, evento_repo: EventoRepository):
        self.evento_repo = evento_repo
        
    async def executar(self) -> List[Evento]:
        return await self.evento_repo.listar_todos()
