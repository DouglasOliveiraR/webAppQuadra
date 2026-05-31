from collections import defaultdict
from typing import Optional, Dict, Any
from domain.eventos.repositories import EventoRepository
from domain.eventos.enums import StatusEvento
from domain.votos.repositories import VotoRepository
from domain.usuarios.repositories import UsuarioRepository

class ObterUltimoResultadoUseCase:
    def __init__(
        self,
        evento_repo: EventoRepository,
        voto_repo: VotoRepository,
        usuario_repo: UsuarioRepository
    ):
        self.evento_repo = evento_repo
        self.voto_repo = voto_repo
        self.usuario_repo = usuario_repo

    async def executar(self) -> Optional[Dict[str, Any]]:
        # 1. Busca todos os eventos e filtra pelos encerrados
        eventos = await self.evento_repo.listar_todos()
        eventos_encerrados = [e for e in eventos if e.status_evento == StatusEvento.ENCERRADO]
        
        if not eventos_encerrados:
            return None
            
        # 2. Ordena para obter o último evento encerrado
        ultimo_evento = sorted(eventos_encerrados, key=lambda e: (e.data_jogo, e.id), reverse=True)[0]
        
        # 3. Busca todos os votos do evento
        votos = await self.voto_repo.listar_por_evento(ultimo_evento.id)
        
        # 4. Agrupa e conta os votos por categoria e por candidato
        contagem_votos = defaultdict(lambda: defaultdict(int))
        for v in votos:
            contagem_votos[v.categoria.value][v.candidato_id] += 1
            
        categorias = ["BOLA_CHEIA", "GOL_BONITO", "BOLA_MURCHA", "LAFON"]
        vencedores = {}
        
        # 5. Descobre os vencedores de cada categoria
        todos_candidatos = set()
        candidatos_por_cat = {}
        max_votos_por_cat = {}

        for cat in categorias:
            contagem_cat = contagem_votos[cat]
            if not contagem_cat:
                candidatos_por_cat[cat] = []
                max_votos_por_cat[cat] = 0
                continue
                
            max_votos = max(contagem_cat.values())
            candidatos_vencedores = [cand_id for cand_id, qtd in contagem_cat.items() if qtd == max_votos]
            candidatos_por_cat[cat] = candidatos_vencedores
            max_votos_por_cat[cat] = max_votos
            todos_candidatos.update(candidatos_vencedores)

        # 6. Realiza a busca em lote de todos os usuários
        usuarios_dit = {}
        if todos_candidatos:
            usuarios = await self.usuario_repo.buscar_por_ids(list(todos_candidatos))
            usuarios_dit = {u.id: u for u in usuarios}
            
        # 7. Monta os dados detalhados
        for cat in categorias:
            candidatos = candidatos_por_cat[cat]
            max_votos = max_votos_por_cat[cat]
            usuarios_detalhes = []
            for cand_id in candidatos:
                u = usuarios_dit.get(cand_id)
                if u:
                    usuarios_detalhes.append({
                        "id": u.id,
                        "nome": u.nome,
                        "foto_url": u.foto_url,
                        "votos": max_votos
                    })
            vencedores[cat] = usuarios_detalhes
            
        return {
            "evento_id": ultimo_evento.id,
            "data_jogo": ultimo_evento.data_jogo,
            "endereco": ultimo_evento.endereco,
            "vencedores": vencedores
        }
