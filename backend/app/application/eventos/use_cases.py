from domain.eventos.repositories import EventoRepository
from domain.eventos.entities import Evento
from domain.presencas.repositories import PresencaRepository
from domain.usuarios.repositories import UsuarioRepository
from domain.votos.repositories import VotoRepository
from core.exceptions import RecursoNaoEncontradoError
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

class ObterEventoUseCase:
    def __init__(
        self,
        evento_repo: EventoRepository,
        presenca_repo: PresencaRepository,
        usuario_repo: UsuarioRepository,
        voto_repo: VotoRepository
    ):
        self.evento_repo = evento_repo
        self.presenca_repo = presenca_repo
        self.usuario_repo = usuario_repo
        self.voto_repo = voto_repo

    async def executar(self, evento_id: int, usuario_logado_id: int) -> dict:
        evento = await self.evento_repo.buscar_por_id(evento_id)
        if not evento:
            raise RecursoNaoEncontradoError("Evento não encontrado")

        presencas = await self.presenca_repo.listar_por_evento(evento_id)
        
        usuario_ids = [p.usuario_id for p in presencas]
        usuarios = {}
        if usuario_ids:
            usuarios_lista = await self.usuario_repo.buscar_por_ids(usuario_ids)
            usuarios = {u.id: u.nome for u in usuarios_lista}

        presencas_detalhadas = []
        for p in presencas:
            presencas_detalhadas.append({
                "usuario_id": p.usuario_id,
                "usuario_nome": usuarios.get(p.usuario_id, "Usuário Desconhecido"),
                "status_jogo": p.status_jogo.value,
                "posicao": p.posicao.value,
                "vai_churrasco": p.vai_churrasco,
                "checkin_validado": p.checkin_validado
            })

        votos = await self.voto_repo.listar_por_evento(evento_id)
        usuario_ja_votou = any(v.eleitor_id == usuario_logado_id for v in votos)

        return {
            "id": evento.id,
            "data_jogo": evento.data_jogo,
            "hora_inicio": evento.hora_inicio,
            "hora_fim": evento.hora_fim,
            "status_evento": evento.status_evento.value,
            "flag_churrasco": evento.flag_churrasco,
            "valor_churrasco": evento.valor_churrasco,
            "usuario_ja_votou": usuario_ja_votou,
            "presencas": presencas_detalhadas
        }

