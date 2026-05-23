from domain.votos.repositories import VotoRepository
from domain.eventos.repositories import EventoRepository
from domain.votos.entities import Voto
from domain.votos.enums import CategoriaVoto
from domain.eventos.enums import StatusEvento
from domain.usuarios.repositories import UsuarioRepository
from core.exceptions import RegraDeNegocioError
from collections import defaultdict

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

class EncerrarVotacaoUseCase:
    def __init__(self, evento_repo: EventoRepository, voto_repo: VotoRepository, usuario_repo: UsuarioRepository):
        self.evento_repo = evento_repo
        self.voto_repo = voto_repo
        self.usuario_repo = usuario_repo

    async def executar(self, evento_id: int):
        evento = await self.evento_repo.buscar_por_id(evento_id)
        if not evento:
            raise RegraDeNegocioError("Evento não encontrado")
            
        if evento.status_evento == StatusEvento.ENCERRADO:
            raise RegraDeNegocioError("Votação já foi encerrada")
            
        votos = await self.voto_repo.listar_por_evento(evento_id)
        
        apuracao = defaultdict(lambda: defaultdict(int))
        for v in votos:
            apuracao[v.categoria.value][v.candidato_id] += 1
            
        pontos_map = {
            "BOLA_CHEIA": 3,
            "GOL_BONITO": 2,
            "BOLA_MURCHA": -1,
            "LAFON": -1
        }
        
        todos_vencedores = set()
        vencedores_por_categoria = {}
        
        for cat_nome, contagem in apuracao.items():
            if not contagem:
                continue
            max_votos = max(contagem.values())
            vencedores = [cand_id for cand_id, qtd in contagem.items() if qtd == max_votos]
            vencedores_por_categoria[cat_nome] = vencedores
            todos_vencedores.update(vencedores)
            
        usuarios_atualizados = {}
        if todos_vencedores:
            usuarios_models = await self.usuario_repo.buscar_por_ids(list(todos_vencedores))
            for u in usuarios_models:
                usuarios_atualizados[u.id] = u

        for cat_nome, vencedores in vencedores_por_categoria.items():
            pontos = pontos_map.get(cat_nome, 0)
            for v_id in vencedores:
                if v_id in usuarios_atualizados:
                    usuarios_atualizados[v_id].pontos_ranking += pontos
                    
        for u in usuarios_atualizados.values():
            await self.usuario_repo.salvar(u)
            
        evento.status_evento = StatusEvento.ENCERRADO
        await self.evento_repo.salvar(evento)
        
        # Converte para dict simples para retornar
        return {k: dict(v) for k, v in apuracao.items()}
