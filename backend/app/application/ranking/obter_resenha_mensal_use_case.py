from collections import defaultdict
from typing import Optional, Dict, Any
from datetime import date
from domain.eventos.repositories import EventoRepository
from domain.votos.repositories import VotoRepository
from domain.usuarios.repositories import UsuarioRepository
from domain.notas.repositories import NotaRepository
from domain.eventos.enums import StatusEvento

class ObterResenhaMensalUseCase:
    def __init__(
        self,
        evento_repo: EventoRepository,
        voto_repo: VotoRepository,
        usuario_repo: UsuarioRepository,
        nota_repo: NotaRepository
    ):
        self.evento_repo = evento_repo
        self.voto_repo = voto_repo
        self.usuario_repo = usuario_repo
        self.nota_repo = nota_repo

    async def executar(self) -> Optional[Dict[str, Any]]:
        hoje = date.today()
        mes_atual = hoje.month
        ano_atual = hoje.year

        todos_eventos = await self.evento_repo.listar_todos()
        eventos_do_mes = [
            e for e in todos_eventos 
            if e.status_evento == StatusEvento.ENCERRADO and 
               e.data_jogo.month == mes_atual and 
               e.data_jogo.year == ano_atual
        ]

        if not eventos_do_mes:
            return None

        eventos_ids = [e.id for e in eventos_do_mes]

        todos_votos = []
        todas_notas = []
        for e_id in eventos_ids:
            votos_evento = await self.voto_repo.listar_por_evento(e_id)
            notas_evento = await self.nota_repo.listar_por_evento(e_id)
            todos_votos.extend(votos_evento)
            todas_notas.extend(notas_evento)

        # Mais Badalado (votos recebidos)
        votos_por_candidato = defaultdict(int)
        for v in todos_votos:
            votos_por_candidato[v.candidato_id] += 1

        mais_votado_id = None
        mais_votado_votos = 0
        if votos_por_candidato:
            mais_votado_id = max(votos_por_candidato, key=votos_por_candidato.get)
            mais_votado_votos = votos_por_candidato[mais_votado_id]

        import math
        minimo_eventos = math.ceil(len(eventos_ids) * 0.6666)
        if minimo_eventos < 1:
            minimo_eventos = 1

        # Médias dadas por cada avaliador (Carrasco / Generoso)
        notas_dadas_por_avaliador = defaultdict(list)
        eventos_por_avaliador = defaultdict(set)
        
        # Notas dadas por cada par (Avaliador -> Avaliado) para Paixão / Inimigo
        notas_por_par = defaultdict(list)
        eventos_por_par = defaultdict(set)

        for n in todas_notas:
            notas_dadas_por_avaliador[n.avaliador_id].append(n.nota)
            if n.evento_id:
                eventos_por_avaliador[n.avaliador_id].add(n.evento_id)
            
            notas_por_par[(n.avaliador_id, n.avaliado_id)].append(n.nota)
            if n.evento_id:
                eventos_por_par[(n.avaliador_id, n.avaliado_id)].add(n.evento_id)

        medias_avaliador = {}
        for av_id, notas_lista in notas_dadas_por_avaliador.items():
            qtd_eventos = len(eventos_por_avaliador[av_id])
            if notas_lista and qtd_eventos >= minimo_eventos:
                medias_avaliador[av_id] = sum(notas_lista) / len(notas_lista)

        carrasco_id = None
        carrasco_media = 0
        generoso_id = None
        generoso_media = 0

        if medias_avaliador:
            carrasco_id = min(medias_avaliador, key=medias_avaliador.get)
            carrasco_media = medias_avaliador[carrasco_id]
            generoso_id = max(medias_avaliador, key=medias_avaliador.get)
            generoso_media = medias_avaliador[generoso_id]

        # Paixão Platônica e Inimigo Pessoal
        medias_pares = {}
        for (avaliador_id, avaliado_id), notas_lista in notas_por_par.items():
            qtd_eventos_par = len(eventos_por_par[(avaliador_id, avaliado_id)])
            if notas_lista and qtd_eventos_par >= minimo_eventos:
                medias_pares[(avaliador_id, avaliado_id)] = sum(notas_lista) / len(notas_lista)

        paixao_platonica = None
        inimigo_pessoal = None

        if medias_pares:
            par_paixao = max(medias_pares, key=medias_pares.get)
            par_inimigo = min(medias_pares, key=medias_pares.get)

            paixao_platonica = {
                "avaliador_id": par_paixao[0],
                "avaliado_id": par_paixao[1],
                "media": round(medias_pares[par_paixao], 2)
            }
            inimigo_pessoal = {
                "avaliador_id": par_inimigo[0],
                "avaliado_id": par_inimigo[1],
                "media": round(medias_pares[par_inimigo], 2)
            }

        # Obter detalhes dos usuários envolvidos
        usuarios_ids_necessarios = set()
        if mais_votado_id: usuarios_ids_necessarios.add(mais_votado_id)
        if carrasco_id: usuarios_ids_necessarios.add(carrasco_id)
        if generoso_id: usuarios_ids_necessarios.add(generoso_id)
        if paixao_platonica:
            usuarios_ids_necessarios.add(paixao_platonica["avaliador_id"])
            usuarios_ids_necessarios.add(paixao_platonica["avaliado_id"])
        if inimigo_pessoal:
            usuarios_ids_necessarios.add(inimigo_pessoal["avaliador_id"])
            usuarios_ids_necessarios.add(inimigo_pessoal["avaliado_id"])

        usuarios_dict = {}
        if usuarios_ids_necessarios:
            usuarios = await self.usuario_repo.buscar_por_ids(list(usuarios_ids_necessarios))
            usuarios_dict = {u.id: u.nome for u in usuarios}

        def get_nome(u_id):
            return usuarios_dict.get(u_id, "Desconhecido")

        resultado = {
            "mes": mes_atual,
            "ano": ano_atual,
            "total_eventos": len(eventos_do_mes),
            "mais_votado": None,
            "carrasco": None,
            "generoso": None,
            "paixao_platonica": None,
            "inimigo_pessoal": None
        }

        if mais_votado_id:
            resultado["mais_votado"] = {
                "id": mais_votado_id,
                "nome": get_nome(mais_votado_id),
                "total_votos": mais_votado_votos
            }

        if carrasco_id:
            resultado["carrasco"] = {
                "id": carrasco_id,
                "nome": get_nome(carrasco_id),
                "media": round(carrasco_media, 2)
            }

        if generoso_id:
            resultado["generoso"] = {
                "id": generoso_id,
                "nome": get_nome(generoso_id),
                "media": round(generoso_media, 2)
            }

        if paixao_platonica:
            resultado["paixao_platonica"] = {
                "avaliador_nome": get_nome(paixao_platonica["avaliador_id"]),
                "avaliado_nome": get_nome(paixao_platonica["avaliado_id"]),
                "media": paixao_platonica["media"]
            }

        if inimigo_pessoal:
            resultado["inimigo_pessoal"] = {
                "avaliador_nome": get_nome(inimigo_pessoal["avaliador_id"]),
                "avaliado_nome": get_nome(inimigo_pessoal["avaliado_id"]),
                "media": inimigo_pessoal["media"]
            }

        return resultado
