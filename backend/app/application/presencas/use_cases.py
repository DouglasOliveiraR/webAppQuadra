from domain.presencas.repositories import PresencaRepository
from domain.eventos.repositories import EventoRepository
from domain.presencas.entities import Presenca
from domain.presencas.enums import StatusJogo, Posicao
from domain.eventos.enums import StatusEvento
from domain.usuarios.repositories import UsuarioRepository
from core.exceptions import RegraDeNegocioError

class AtualizarPresencaUseCase:
    def __init__(self, presenca_repo: PresencaRepository, evento_repo: EventoRepository):
        self.presenca_repo = presenca_repo
        self.evento_repo = evento_repo

    async def executar(self, usuario_id: int, evento_id: int, status: StatusJogo, posicao: Posicao, churrasco: bool):
        evento = await self.evento_repo.buscar_por_id(evento_id)
        if not evento:
            raise RegraDeNegocioError("Evento não encontrado")
            
        if evento.status_evento != StatusEvento.PRESENCA_ABERTA:
            raise RegraDeNegocioError("Lista de presença não está aberta")
            
        presenca = await self.presenca_repo.buscar_por_usuario_evento(usuario_id, evento_id)
        if not presenca:
            presenca = Presenca(
                id=None,
                usuario_id=usuario_id,
                evento_id=evento_id,
                status_jogo=status,
                posicao=posicao,
                vai_churrasco=churrasco,
                checkin_validado=False,
                falta_penalizada=False
            )
        else:
            presenca.status_jogo = status
            presenca.posicao = posicao
            presenca.vai_churrasco = churrasco
            
        return await self.presenca_repo.salvar(presenca)

class CheckinUseCase:
    def __init__(self, presenca_repo: PresencaRepository, usuario_repo: UsuarioRepository):
        self.presenca_repo = presenca_repo
        self.usuario_repo = usuario_repo

    async def executar(self, evento_id: int, usuario_id: int, chegou: bool, falta_justificada: bool):
        presenca = await self.presenca_repo.buscar_por_usuario_evento(usuario_id, evento_id)
        if not presenca:
            raise RegraDeNegocioError("Jogador não está na lista deste evento")
            
        usuario = await self.usuario_repo.buscar_por_id(usuario_id)
        if not usuario:
            raise RegraDeNegocioError("Usuário não encontrado")
            
        presenca.checkin_validado = chegou
        
        if chegou:
            usuario.pontos_ranking += 1
            presenca.falta_penalizada = False
        else:
            if not falta_justificada:
                usuario.pontos_ranking -= 1
                presenca.falta_penalizada = True
            else:
                presenca.falta_penalizada = False
                
        await self.usuario_repo.salvar(usuario)
        return await self.presenca_repo.salvar(presenca)
