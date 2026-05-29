from domain.eventos.repositories import EventoRepository
from domain.eventos.entities import Evento
from domain.presencas.repositories import PresencaRepository
from domain.usuarios.repositories import UsuarioRepository
from domain.votos.repositories import VotoRepository
from domain.financeiro.repositories import FinanceiroRepository
from domain.financeiro.enums import StatusPagamento
from domain.notas.repositories import NotaRepository
from core.exceptions import RecursoNaoEncontradoError
from typing import List

class CriarEventoUseCase:
    def __init__(self, evento_repo: EventoRepository, financeiro_repo: FinanceiroRepository):
        self.evento_repo = evento_repo
        self.financeiro_repo = financeiro_repo
        
    async def executar(self, evento: Evento) -> Evento:
        evento_salvo = await self.evento_repo.salvar(evento)
        
        # Propaga a alteração de mensalidade do novo evento para registros pendentes do mês de referência
        if evento_salvo.valor_mensalidade is not None and evento_salvo.valor_mensalidade > 0:
            mes_ref = evento_salvo.data_jogo.strftime("%Y-%m")
            registros = await self.financeiro_repo.listar_todos()
            registros_atualizados = []
            for r in registros:
                if r.tipo == "MENSALIDADE" and r.mes_referencia == mes_ref and r.status_pagamento == StatusPagamento.PENDENTE:
                    r.valor = evento_salvo.valor_mensalidade
                    registros_atualizados.append(r)
            if registros_atualizados:
                await self.financeiro_repo.salvar_lote(registros_atualizados)
                    
        return evento_salvo

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
        voto_repo: VotoRepository,
        nota_repo: NotaRepository
    ):
        self.evento_repo = evento_repo
        self.presenca_repo = presenca_repo
        self.usuario_repo = usuario_repo
        self.voto_repo = voto_repo
        self.nota_repo = nota_repo

    async def executar(self, evento_id: int, usuario_logado_id: int) -> dict:
        evento = await self.evento_repo.buscar_por_id(evento_id)
        if not evento:
            raise RecursoNaoEncontradoError("Evento não encontrado")

        presencas = await self.presenca_repo.listar_por_evento(evento_id)
        
        usuario_ids = [p.usuario_id for p in presencas]
        usuarios = {}
        if usuario_ids:
            usuarios_lista = await self.usuario_repo.buscar_por_ids(usuario_ids)
            usuarios = {u.id: {"nome": u.nome, "foto_url": u.foto_url, "perfil": u.perfil.value} for u in usuarios_lista}

        presencas_detalhadas = []
        for p in presencas:
            u_info = usuarios.get(p.usuario_id, {"nome": "Usuário Desconhecido", "foto_url": None, "perfil": "AVULSO"})
            presencas_detalhadas.append({
                "usuario_id": p.usuario_id,
                "usuario_nome": u_info["nome"],
                "usuario_foto_url": u_info["foto_url"],
                "usuario_perfil": u_info["perfil"],
                "status_jogo": p.status_jogo.value,
                "posicao": p.posicao.value,
                "vai_churrasco": p.vai_churrasco,
                "checkin_validado": p.checkin_validado
            })

        votos = await self.voto_repo.listar_por_evento(evento_id)
        usuario_ja_votou = any(v.eleitor_id == usuario_logado_id for v in votos)
        
        notas_enviadas = await self.nota_repo.listar_por_avaliador_e_evento(usuario_logado_id, evento_id)
        usuario_ja_avaliou = len(notas_enviadas) > 0

        return {
            "id": evento.id,
            "data_jogo": evento.data_jogo,
            "hora_inicio": evento.hora_inicio,
            "hora_fim": evento.hora_fim,
            "status_evento": evento.status_evento.value,
            "flag_churrasco": evento.flag_churrasco,
            "valor_churrasco": evento.valor_churrasco,
            "endereco": evento.endereco,
            "chave_pix": evento.chave_pix,
            "valor_mensalidade": evento.valor_mensalidade,
            "custo_quadra": evento.custo_quadra,
            "usuario_ja_votou": usuario_ja_votou,
            "usuario_ja_avaliou": usuario_ja_avaliou,
            "presencas": presencas_detalhadas
        }

