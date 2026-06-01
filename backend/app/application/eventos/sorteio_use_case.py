from domain.eventos.repositories import EventoRepository
from domain.presencas.repositories import PresencaRepository
from domain.usuarios.repositories import UsuarioRepository
from core.exceptions import RegraDeNegocioError
from typing import List, Dict

class SorteioUseCase:
    def __init__(self, evento_repo: EventoRepository, presenca_repo: PresencaRepository, usuario_repo: UsuarioRepository):
        self.evento_repo = evento_repo
        self.presenca_repo = presenca_repo
        self.usuario_repo = usuario_repo

    async def executar(self, evento_id: int, criterio: str) -> Dict[str, List[dict]]:
        evento = await self.evento_repo.buscar_por_id(evento_id)
        if not evento:
            raise RegraDeNegocioError("Evento não encontrado")

        presencas = await self.presenca_repo.listar_por_evento(evento_id)
        
        # Sorteio considera todo mundo que confirmou presença (VOU) OU que recebeu check-in manual do admin (mesmo que não tenha marcado VOU)
        confirmados = [p for p in presencas if p.status_jogo.value == "VOU" or p.checkin_validado]

        if not confirmados:
            raise RegraDeNegocioError("Nenhum jogador confirmado para o sorteio.")

        usuarios = await self.usuario_repo.buscar_por_ids([p.usuario_id for p in confirmados])
        usuario_dict = {u.id: u for u in usuarios}

        goleiros = []
        linhas = []
        for p in confirmados:
            u = usuario_dict.get(p.usuario_id)
            if not u:
                continue
            nota = u.nota_admin if criterio == "NOTA_ADMIN" else (u.nota_galera_media or u.nota_admin)
            jogador_info = {"id": u.id, "nome": u.nome, "nota": nota, "posicao": p.posicao.value}
            
            if p.posicao.value == "GOL":
                goleiros.append(jogador_info)
            else:
                linhas.append(jogador_info)

        goleiros.sort(key=lambda x: x["nota"], reverse=True)
        linhas.sort(key=lambda x: x["nota"], reverse=True)

        import math
        num_times = max(2, math.ceil(len(confirmados) / 6.0))
        times = [{"id": i, "nome": f"Time {chr(65+i)}", "jogadores": [], "soma_notas": 0.0} for i in range(num_times)]

        # Distribuir goleiros (um por vez em cada time)
        for i, gol in enumerate(goleiros):
            time_alvo = times[i % num_times]
            time_alvo["jogadores"].append(gol)
            time_alvo["soma_notas"] += gol["nota"]

        # Distribuir linhas balanceando as notas
        for j in linhas:
            # Encontrar o time com a menor soma de notas DENTRE OS QUE TÊM MENOS DE 6 JOGADORES
            times_disponiveis = [t for t in times if len(t["jogadores"]) < 6]
            if not times_disponiveis:
                # Se por algum motivo todos já tiverem 6, adiciona no de menor soma
                times_disponiveis = times
            
            time_alvo = min(times_disponiveis, key=lambda t: t["soma_notas"])
            time_alvo["jogadores"].append(j)
            time_alvo["soma_notas"] += j["nota"]

        # Formatar a resposta
        times_response = []
        for t in times:
            media = t["soma_notas"] / len(t["jogadores"]) if t["jogadores"] else 0
            times_response.append({
                "nome": t["nome"],
                "jogadores": t["jogadores"],
                "media": media
            })

        return {"times": times_response}
