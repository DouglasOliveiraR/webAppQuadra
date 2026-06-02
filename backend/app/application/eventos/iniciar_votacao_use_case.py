from domain.eventos.repositories import EventoRepository
from domain.eventos.enums import StatusEvento
from core.exceptions import RegraDeNegocioError

class IniciarVotacaoUseCase:
    def __init__(self, evento_repo: EventoRepository, disparar_notificacao_uc=None):
        self.evento_repo = evento_repo
        self.disparar_notificacao_uc = disparar_notificacao_uc

    async def executar(self, evento_id: int):
        evento = await self.evento_repo.buscar_por_id(evento_id)
        if not evento:
            raise RegraDeNegocioError("Evento não encontrado")
            
        if evento.status_evento != StatusEvento.PRESENCA_ABERTA:
            raise RegraDeNegocioError("O evento não está em fase de presença para iniciar a votação")
            
        evento.status_evento = StatusEvento.VOTACAO_ABERTA
        salvo = await self.evento_repo.salvar(evento)
        
        if self.disparar_notificacao_uc:
            import asyncio
            asyncio.create_task(
                self.disparar_notificacao_uc.executar(
                    titulo="O Paredão tá ON! 🔥",
                    corpo="A votação dos prêmios já começou. Entre no app e vote nos melhores (e piores) de hoje!",
                    url="/votos"
                )
            )
            
        return salvo
