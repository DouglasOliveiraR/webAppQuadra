from typing import List
from domain.financeiro.repositories import FinanceiroRepository
from domain.financeiro.enums import StatusPagamento
from domain.financeiro.entities import Financeiro
from domain.usuarios.repositories import UsuarioRepository
from domain.usuarios.enums import PerfilUsuario, StatusUsuario
from domain.eventos.repositories import EventoRepository
from core.exceptions import RecursoNaoEncontradoError

class ListarFinanceiroUseCase:
    def __init__(
        self, 
        financeiro_repo: FinanceiroRepository,
        usuario_repo: UsuarioRepository,
        evento_repo: EventoRepository
    ):
        self.financeiro_repo = financeiro_repo
        self.usuario_repo = usuario_repo
        self.evento_repo = evento_repo

    async def executar(self, usuario_id: int, mes: str) -> List[Financeiro]:
        # 1. Garantir que o usuário mensalista ativo (ou admin ativo) tenha mensalidade gerada para o mês selecionado
        usuario = await self.usuario_repo.buscar_por_id(usuario_id)
        if usuario and usuario.perfil in [PerfilUsuario.MENSALISTA, PerfilUsuario.ADMIN] and usuario.status == StatusUsuario.ATIVO:
            meus_registros = await self.financeiro_repo.listar_por_usuario(usuario_id)
            tem_mensalidade = any(r.tipo == "MENSALIDADE" and r.mes_referencia == mes for r in meus_registros)
            
            if not tem_mensalidade:
                valor_padrao = 60.0
                try:
                    eventos = await self.evento_repo.listar_todos()
                    if eventos:
                        # Filtrar eventos do mês específico primeiro para obter a mensalidade correta
                        eventos_do_mes = [e for e in eventos if e.data_jogo.strftime("%Y-%m") == mes]
                        if eventos_do_mes:
                            eventos_ordenados = sorted(eventos_do_mes, key=lambda e: e.id, reverse=True)
                        else:
                            eventos_ordenados = sorted(eventos, key=lambda e: e.id, reverse=True)
                        ultimo_evento = eventos_ordenados[0]
                        if ultimo_evento.valor_mensalidade is not None and ultimo_evento.valor_mensalidade > 0:
                            valor_padrao = ultimo_evento.valor_mensalidade
                except Exception:
                    pass
                
                nova_mensalidade = Financeiro(
                    id=None,
                    usuario_id=usuario_id,
                    tipo="MENSALIDADE",
                    valor=valor_padrao,
                    status_pagamento=StatusPagamento.PENDENTE,
                    mes_referencia=mes
                )
                await self.financeiro_repo.salvar(nova_mensalidade)

        return await self.financeiro_repo.listar_por_usuario(usuario_id)

class BaixarPagamentoUseCase:
    def __init__(self, financeiro_repo: FinanceiroRepository):
        self.financeiro_repo = financeiro_repo

    async def executar(self, pagamento_id: int) -> Financeiro:
        resultado = await self.financeiro_repo.alternar_status_pagamento(pagamento_id)
        if not resultado:
            raise RecursoNaoEncontradoError("Pagamento não encontrado")
        return resultado
