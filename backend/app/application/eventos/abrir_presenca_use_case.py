from datetime import date, datetime, timedelta
from typing import List

from domain.eventos.repositories import EventoRepository
from domain.eventos.enums import StatusEvento
from domain.eventos.entities import Evento
from core.exceptions import RegraDeNegocioError


class AbrirPresencaUseCase:
    def __init__(self, evento_repo: EventoRepository, disparar_notificacao_uc=None):
        self.evento_repo = evento_repo
        self.disparar_notificacao_uc = disparar_notificacao_uc

    async def executar_automatico(self) -> int:
        """
        Busca todos os eventos AGENDADO. Se a data do jogo for em <= 4 dias,
        altera para PRESENCA_ABERTA e dispara push.
        Retorna a quantidade de eventos alterados.
        """
        eventos = await self.evento_repo.listar_todos()
        hoje = date.today()
        limite_abertura = hoje + timedelta(days=4)
        
        eventos_alterados = 0
        
        for evento in eventos:
            if evento.status_evento == StatusEvento.AGENDADO and evento.data_jogo <= limite_abertura:
                evento.status_evento = StatusEvento.PRESENCA_ABERTA
                await self.evento_repo.salvar(evento)
                eventos_alterados += 1
                
                if self.disparar_notificacao_uc:
                    data_formatada = evento.data_jogo.strftime("%d/%m")
                    hora_str = evento.hora_inicio.strftime("%H:%M")
                    import asyncio
                    asyncio.create_task(
                        self.disparar_notificacao_uc.executar(
                            titulo="Lista de Presença Liberada! ⚽",
                            corpo=f"A pelada do dia {data_formatada} às {hora_str} já está com a lista aberta. Confirme sua vaga!"
                        )
                    )
                    
        return eventos_alterados

    async def executar_manual(self, evento_id: int) -> Evento:
        """
        Força a abertura da lista de presença de um evento específico.
        """
        evento = await self.evento_repo.buscar_por_id(evento_id)
        if not evento:
            raise RegraDeNegocioError("Evento não encontrado")
            
        if evento.status_evento != StatusEvento.AGENDADO:
            raise RegraDeNegocioError("A lista de presença só pode ser aberta para eventos com status AGENDADO.")
            
        evento.status_evento = StatusEvento.PRESENCA_ABERTA
        evento_salvo = await self.evento_repo.salvar(evento)
        
        if self.disparar_notificacao_uc:
            data_formatada = evento.data_jogo.strftime("%d/%m")
            hora_str = evento.hora_inicio.strftime("%H:%M")
            import asyncio
            asyncio.create_task(
                self.disparar_notificacao_uc.executar(
                    titulo="Lista de Presença Liberada! ⚽",
                    corpo=f"A pelada do dia {data_formatada} às {hora_str} já está com a lista aberta. Confirme sua vaga!"
                )
            )
            
        return evento_salvo
