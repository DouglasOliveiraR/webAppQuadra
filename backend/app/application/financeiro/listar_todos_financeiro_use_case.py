from typing import List
from domain.financeiro.repositories import FinanceiroRepository
from domain.financeiro.enums import StatusPagamento
from domain.financeiro.entities import Financeiro
from domain.usuarios.repositories import UsuarioRepository
from domain.usuarios.enums import PerfilUsuario, StatusUsuario
from domain.eventos.repositories import EventoRepository
from domain.presencas.repositories import PresencaRepository

class ListarTodosFinanceiroUseCase:
    def __init__(
        self,
        financeiro_repo: FinanceiroRepository,
        usuario_repo: UsuarioRepository,
        evento_repo: EventoRepository,
        presenca_repo: PresencaRepository
    ):
        self.financeiro_repo = financeiro_repo
        self.usuario_repo = usuario_repo
        self.evento_repo = evento_repo
        self.presenca_repo = presenca_repo

    async def executar(self, mes: str) -> List[Financeiro]:
        # 1. Buscar todos os registros financeiros
        registros_financeiros = await self.financeiro_repo.listar_todos()
        
        # Filtra os registros que já existem para o mês especificado
        registros_do_mes = [r for r in registros_financeiros if r.mes_referencia == mes]

        # 2. Garantir que todos os mensalistas e admins ativos tenham um registro de MENSALIDADE para o mês selecionado
        todos_usuarios = await self.usuario_repo.listar_todos()
        usuarios_ativos = [
            u for u in todos_usuarios 
            if u.perfil in [PerfilUsuario.MENSALISTA, PerfilUsuario.ADMIN] and u.status == StatusUsuario.ATIVO
        ]

        usuarios_com_mensalidade = {
            reg.usuario_id for reg in registros_do_mes 
            if reg.tipo == "MENSALIDADE" and reg.usuario_id is not None
        }

        # Determinar valor padrão da mensalidade e listar eventos do mês
        valor_padrao = 60.0
        eventos_do_mes = []
        try:
            eventos = await self.evento_repo.listar_todos()
            if eventos:
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

        precisa_recarregar = False
        for usuario in usuarios_ativos:
            if usuario.id not in usuarios_com_mensalidade:
                nova_mensalidade = Financeiro(
                    id=None,
                    usuario_id=usuario.id,
                    tipo="MENSALIDADE",
                    valor=valor_padrao,
                    status_pagamento=StatusPagamento.PENDENTE,
                    mes_referencia=mes
                )
                await self.financeiro_repo.salvar(nova_mensalidade)
                precisa_recarregar = True

        # 3. Garantir que confirmados para churrasco tenham registro financeiro
        if eventos_do_mes:
            for evento in eventos_do_mes:
                if evento.flag_churrasco:
                    presencas = await self.presenca_repo.listar_por_evento(evento.id)
                    confirmados = [p.usuario_id for p in presencas if p.vai_churrasco]
                    tipo_churrasco = f"CHURRASCO_{evento.id}"
                    
                    usuarios_com_churrasco = {
                        reg.usuario_id for reg in registros_financeiros 
                        if reg.tipo == tipo_churrasco and reg.usuario_id is not None
                    }
                    
                    for uid in confirmados:
                        if uid not in usuarios_com_churrasco:
                            novo_churrasco = Financeiro(
                                id=None,
                                usuario_id=uid,
                                tipo=tipo_churrasco,
                                valor=evento.valor_churrasco or 40.0,
                                status_pagamento=StatusPagamento.PENDENTE,
                                mes_referencia=mes
                            )
                            await self.financeiro_repo.salvar(novo_churrasco)
                            precisa_recarregar = True

        if precisa_recarregar:
            registros_financeiros = await self.financeiro_repo.listar_todos()
            registros_do_mes = [r for r in registros_financeiros if r.mes_referencia == mes]

        # Filtra os registros para retornar apenas os de usuários ATIVOS
        ids_usuarios_ativos = {u.id for u in todos_usuarios if u.status == StatusUsuario.ATIVO}
        registros_ativos = [r for r in registros_do_mes if r.usuario_id in ids_usuarios_ativos]

        return registros_ativos
