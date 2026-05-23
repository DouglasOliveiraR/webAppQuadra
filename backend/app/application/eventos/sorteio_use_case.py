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
        
        # Pega confirmados (idealmente quem tem check-in, mas se ngm tiver, pega todos os VOU)
        confirmados = [p for p in presencas if p.status_jogo.value == "VOU" and p.checkin_validado]
        if not confirmados:
            confirmados = [p for p in presencas if p.status_jogo.value == "VOU"]

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

        time_a = []
        time_b = []
        soma_a = 0
        soma_b = 0

        # Distribuir goleiros
        if len(goleiros) >= 1:
            time_a.append(goleiros[0])
            soma_a += goleiros[0]["nota"]
        if len(goleiros) >= 2:
            time_b.append(goleiros[1])
            soma_b += goleiros[1]["nota"]

        # Distribuir linhas balanceando as notas
        for j in linhas:
            if soma_a <= soma_b:
                if len(time_a) < 6:
                    time_a.append(j)
                    soma_a += j["nota"]
                elif len(time_b) < 6:
                    time_b.append(j)
                    soma_b += j["nota"]
            else:
                if len(time_b) < 6:
                    time_b.append(j)
                    soma_b += j["nota"]
                elif len(time_a) < 6:
                    time_a.append(j)
                    soma_a += j["nota"]

        return {
            "time_a": time_a,
            "time_b": time_b,
            "media_a": soma_a / len(time_a) if time_a else 0,
            "media_b": soma_b / len(time_b) if time_b else 0
        }
