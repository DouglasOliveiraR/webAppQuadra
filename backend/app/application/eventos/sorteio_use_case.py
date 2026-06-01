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
        times = [{"id": i, "nome": f"Time {chr(65+i)}", "jogadores": [], "soma_notas": 0.0, "target_linhas": 0, "target_total": 0} for i in range(num_times)]

        linhas_restantes = len(linhas)
        for i in range(num_times):
            if linhas_restantes >= 5:
                times[i]["target_linhas"] = 5
                linhas_restantes -= 5
            else:
                times[i]["target_linhas"] = linhas_restantes
                linhas_restantes = 0

        # Distribuir goleiros (um por vez em cada time)
        for i, gol in enumerate(goleiros):
            time_alvo = times[i % num_times]
            time_alvo["jogadores"].append(gol)
            time_alvo["soma_notas"] += gol["nota"]

        # Calcula a capacidade total de cada time para a métrica de balanceamento
        for t in times:
            num_gol = sum(1 for p in t["jogadores"] if p["posicao"] == "GOL")
            t["target_total"] = t["target_linhas"] + num_gol

        # Distribuir linhas balanceando a média projetada final
        for j in linhas:
            # Encontrar os times que ainda não atingiram sua cota exata de linhas
            times_disponiveis = [t for t in times if sum(1 for p in t["jogadores"] if p["posicao"] != "GOL") < t["target_linhas"]]
            if not times_disponiveis:
                # Fallback de segurança
                times_disponiveis = times
            
            # Escolhe o time com a MENOR média projetada
            time_alvo = min(times_disponiveis, key=lambda t: t["soma_notas"] / max(1, t["target_total"]))
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

        # --- NOVA LÓGICA: SUGESTÕES DE BANCO ---
        sugestoes_banco = []
        target_gol = 1 if goleiros else 0
        target_linha = 5
        max_total = target_gol + target_linha

        if max_total > 0 and confirmados:
            media_geral = sum(p.nota_admin if criterio == "NOTA_ADMIN" else (p.nota_galera_media or p.nota_admin) for p in usuarios) / len(usuarios) if usuarios else 0
            # Como filtramos e pegamos direto de 'linhas' e 'goleiros':
            media_geral = sum(p["nota"] for p in (goleiros + linhas)) / len(goleiros + linhas) if (goleiros + linhas) else 0

            for t_inc in times:
                qtd_gol = sum(1 for p in t_inc["jogadores"] if p["posicao"] == "GOL")
                qtd_linha = sum(1 for p in t_inc["jogadores"] if p["posicao"] != "GOL")
                
                vagas_gol = max(0, target_gol - qtd_gol)
                vagas_linha = max(0, target_linha - qtd_linha)
                
                if vagas_gol == 0 and vagas_linha == 0:
                    continue # Time já está completo
                
                target_soma_total = media_geral * max_total
                soma_atual = t_inc["soma_notas"]
                falta_soma = target_soma_total - soma_atual
                
                opcoes = []
                for t_comp in times:
                    if t_comp["id"] == t_inc["id"]:
                        continue
                        
                    gols_comp = [p for p in t_comp["jogadores"] if p["posicao"] == "GOL"]
                    linhas_comp = [p for p in t_comp["jogadores"] if p["posicao"] != "GOL"]
                    
                    # O time de origem precisa ter os jogadores suficientes para emprestar
                    if len(gols_comp) < vagas_gol or len(linhas_comp) < vagas_linha:
                        continue
                        
                    import itertools
                    combo_gol = []
                    soma_gol = 0
                    if vagas_gol > 0:
                        combo_gol = [gols_comp[0]] # Geralmente pega o único goleiro
                        soma_gol = combo_gol[0]["nota"]
                        
                    target_soma_linha = falta_soma - soma_gol
                    
                    combo_linha = []
                    if vagas_linha > 0:
                        best_combo = None
                        best_diff = float('inf')
                        # Testa todas as combinações de linhas do time completo
                        for combo in itertools.combinations(linhas_comp, vagas_linha):
                            soma_combo = sum(p["nota"] for p in combo)
                            diff = abs(soma_combo - target_soma_linha)
                            if diff < best_diff:
                                best_diff = diff
                                best_combo = combo
                        combo_linha = list(best_combo) if best_combo else []
                        
                    sugestao_jogadores = combo_gol + combo_linha
                    media_simulada = (soma_atual + sum(p["nota"] for p in sugestao_jogadores)) / max_total
                    
                    opcoes.append({
                        "origem": t_comp["nome"],
                        "jogadores": sugestao_jogadores,
                        "media_simulada": media_simulada
                    })
                    
                if opcoes:
                    sugestoes_banco.append({
                        "time_incompleto": t_inc["nome"],
                        "vagas": vagas_gol + vagas_linha,
                        "opcoes": opcoes
                    })

        return {
            "times": times_response,
            "sugestoes_banco": sugestoes_banco
        }
