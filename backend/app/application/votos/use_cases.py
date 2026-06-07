from datetime import timedelta
from collections import defaultdict

from domain.votos.repositories import VotoRepository
from domain.eventos.repositories import EventoRepository
from domain.votos.entities import Voto
from domain.votos.enums import CategoriaVoto
from domain.eventos.enums import StatusEvento
from domain.eventos.entities import Evento
from domain.usuarios.repositories import UsuarioRepository
from domain.usuarios.enums import PerfilUsuario
from domain.premios.entities import Premio
from core.exceptions import RegraDeNegocioError


class RegistrarVotoUseCase:
    def __init__(self, voto_repo: VotoRepository, evento_repo: EventoRepository, usuario_repo: UsuarioRepository):
        self.voto_repo = voto_repo
        self.evento_repo = evento_repo
        self.usuario_repo = usuario_repo

    async def executar(self, evento_id: int, eleitor_id: int, candidato_id: int, categoria: CategoriaVoto):
        evento = await self.evento_repo.buscar_por_id(evento_id)
        if not evento:
            raise RegraDeNegocioError("Evento não encontrado")
            
        if evento.status_evento != StatusEvento.VOTACAO_ABERTA:
            raise RegraDeNegocioError("A votação para este evento não está aberta")
            
        if eleitor_id == candidato_id:
            raise RegraDeNegocioError("Você não pode votar em si mesmo")
            
        # Validar se eleitor ou candidato são avulsos
        eleitor = await self.usuario_repo.buscar_por_id(eleitor_id)
        if not eleitor:
            raise RegraDeNegocioError("Eleitor não encontrado")
        if eleitor.perfil == PerfilUsuario.AVULSO:
            raise RegraDeNegocioError("Jogadores avulsos não podem votar")
            
        candidato = await self.usuario_repo.buscar_por_id(candidato_id)
        if not candidato:
            raise RegraDeNegocioError("Candidato não encontrado")
        if candidato.perfil == PerfilUsuario.AVULSO:
            raise RegraDeNegocioError("Jogadores avulsos não podem ser votados")
            
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
    def __init__(self, evento_repo: EventoRepository, voto_repo: VotoRepository, usuario_repo: UsuarioRepository, premio_repo):
        self.evento_repo = evento_repo
        self.voto_repo = voto_repo
        self.usuario_repo = usuario_repo
        self.premio_repo = premio_repo

    async def executar(self, evento_id: int):
        evento = await self.evento_repo.buscar_por_id(evento_id)
        if not evento:
            raise RegraDeNegocioError("Evento não encontrado")
            
        if evento.status_evento == StatusEvento.ENCERRADO:
            raise RegraDeNegocioError("Votação já foi encerrada")
            
        votos = await self.voto_repo.listar_por_evento(evento_id)
        
        apuracao = self._apurar_votos(votos)
        vencedores_por_categoria, todos_vencedores = self._determinar_vencedores(apuracao)

        mes_ref = evento.data_jogo.strftime("%Y-%m")
        await self._processar_premiacoes_e_ranking(
            evento_id, mes_ref, vencedores_por_categoria, todos_vencedores
        )

        evento.status_evento = StatusEvento.ENCERRADO
        await self.evento_repo.salvar(evento)

        await self._deletar_usuarios_avulsos()
        await self._agendar_proximo_evento(evento)

        return {k: dict(v) for k, v in apuracao.items()}

    def _apurar_votos(self, votos):
        apuracao = defaultdict(lambda: defaultdict(int))
        for v in votos:
            apuracao[v.categoria.value][v.candidato_id] += 1
        return apuracao

    def _determinar_vencedores(self, apuracao):
        todos_vencedores = set()
        vencedores_por_categoria = {}
        for cat_nome, contagem in apuracao.items():
            if not contagem:
                continue
            max_votos = max(contagem.values())
            vencedores = [cand_id for cand_id, qtd in contagem.items() if qtd == max_votos]
            vencedores_por_categoria[cat_nome] = vencedores
            todos_vencedores.update(vencedores)
        return vencedores_por_categoria, todos_vencedores

    async def _processar_premiacoes_e_ranking(self, evento_id, mes_ref, vencedores_por_categoria, todos_vencedores):
        usuarios_atualizados = {}
        if todos_vencedores:
            usuarios_models = await self.usuario_repo.buscar_por_ids(list(todos_vencedores))
            for u in usuarios_models:
                usuarios_atualizados[u.id] = u

        pontos_map = {
            "BOLA_CHEIA": 3,
            "GOL_BONITO": 2,
            "BOLA_MURCHA": -1,
            "LAFON": -1
        }

        self._atualizar_pontos_ranking(usuarios_atualizados, vencedores_por_categoria, pontos_map)
        novos_premios = self._gerar_premios(evento_id, mes_ref, vencedores_por_categoria)

        if novos_premios:
            await self.premio_repo.salvar_lote(novos_premios)

        if usuarios_atualizados:
            await self.usuario_repo.salvar_lote(list(usuarios_atualizados.values()))

    def _atualizar_pontos_ranking(self, usuarios_atualizados, vencedores_por_categoria, pontos_map):
        for cat_nome, vencedores in vencedores_por_categoria.items():
            pontos = pontos_map.get(cat_nome, 0)
            for v_id in vencedores:
                if v_id in usuarios_atualizados:
                    usuarios_atualizados[v_id].pontos_ranking += pontos

    def _gerar_premios(self, evento_id, mes_ref, vencedores_por_categoria):
        novos_premios = []
        for cat_nome, vencedores in vencedores_por_categoria.items():
            for v_id in vencedores:
                novo_premio = Premio(
                    id=None,
                    usuario_id=v_id,
                    evento_id=evento_id,
                    categoria=CategoriaVoto(cat_nome),
                    mes_referencia=mes_ref
                )
                novos_premios.append(novo_premio)
        return novos_premios

    async def _deletar_usuarios_avulsos(self):
        try:
            await self.usuario_repo.deletar_por_perfil(PerfilUsuario.AVULSO)
        except Exception as e:
            print(f"Erro ao deletar usuários avulsos no encerramento: {e}")

    async def _agendar_proximo_evento(self, evento):
        nova_data = evento.data_jogo + timedelta(days=7)
        proximo_evento = Evento(
            id=None,
            data_jogo=nova_data,
            hora_inicio=evento.hora_inicio,
            hora_fim=evento.hora_fim,
            status_evento=StatusEvento.AGENDADO,
            flag_churrasco=evento.flag_churrasco,
            valor_churrasco=evento.valor_churrasco,
            endereco=evento.endereco,
            chave_pix=evento.chave_pix,
            valor_mensalidade=evento.valor_mensalidade,
            custo_quadra=evento.custo_quadra
        )
        await self.evento_repo.salvar(proximo_evento)
