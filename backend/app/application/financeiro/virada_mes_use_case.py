from typing import List
from datetime import datetime
from domain.financeiro.repositories import FinanceiroRepository
from domain.financeiro.enums import StatusPagamento
from domain.financeiro.entities import Financeiro
from domain.usuarios.repositories import UsuarioRepository
from domain.usuarios.enums import PerfilUsuario, StatusUsuario
from domain.eventos.repositories import EventoRepository

class ViradaMesUseCase:
    def __init__(
        self, 
        financeiro_repo: FinanceiroRepository,
        usuario_repo: UsuarioRepository,
        evento_repo: EventoRepository
    ):
        self.financeiro_repo = financeiro_repo
        self.usuario_repo = usuario_repo
        self.evento_repo = evento_repo

    async def executar(self) -> int:
        """
        Gera pendências de mensalidade para todos os usuários ativos
        (Mensalistas e Admins) no início de um novo mês.
        Retorna a quantidade de novas mensalidades geradas.
        """
        hoje = datetime.now()
        mes_atual = hoje.strftime("%Y-%m")
        
        # 1. Obter todos os usuários
        todos_usuarios = await self.usuario_repo.listar_todos()
        
        # Filtrar apenas ativos (MENSALISTA ou ADMIN)
        usuarios_alvo = [
            u for u in todos_usuarios 
            if u.perfil in [PerfilUsuario.MENSALISTA, PerfilUsuario.ADMIN] 
            and u.status == StatusUsuario.ATIVO
        ]
        
        if not usuarios_alvo:
            return 0
            
        # 2. Descobrir o valor padrão da mensalidade baseado no último evento do mês atual
        valor_padrao = 60.0
        try:
            eventos = await self.evento_repo.listar_todos()
            if eventos:
                eventos_do_mes = [e for e in eventos if e.data_jogo.strftime("%Y-%m") == mes_atual]
                if eventos_do_mes:
                    eventos_ordenados = sorted(eventos_do_mes, key=lambda e: e.id, reverse=True)
                else:
                    eventos_ordenados = sorted(eventos, key=lambda e: e.id, reverse=True)
                
                ultimo_evento = eventos_ordenados[0]
                if ultimo_evento.valor_mensalidade is not None and ultimo_evento.valor_mensalidade > 0:
                    valor_padrao = ultimo_evento.valor_mensalidade
        except Exception:
            pass
            
        novas_mensalidades = []
        
        # 3. Verificar para cada usuário se já existe a mensalidade
        # ⚡ Bolt: Fetch all relevant records in a single query to avoid N+1 queries.
        # Impacto: Reduz o bloqueio do event loop e o tempo de transação no banco.
        usuarios_ids = [u.id for u in usuarios_alvo]
        registros_existentes = await self.financeiro_repo.listar_por_usuarios_e_mes(usuarios_ids, mes_atual)

        # Cria um set de IDs de usuários que já possuem mensalidade neste mês
        usuarios_com_mensalidade = {
            r.usuario_id for r in registros_existentes if r.tipo == "MENSALIDADE"
        }

        for usuario in usuarios_alvo:
            if usuario.id not in usuarios_com_mensalidade:
                nova_mensalidade = Financeiro(
                    id=None,
                    usuario_id=usuario.id,
                    tipo="MENSALIDADE",
                    valor=valor_padrao,
                    status_pagamento=StatusPagamento.PENDENTE,
                    mes_referencia=mes_atual
                )
                novas_mensalidades.append(nova_mensalidade)
                
        # 4. Salvar todas as novas mensalidades em lote
        if novas_mensalidades:
            await self.financeiro_repo.salvar_lote(novas_mensalidades)
            
        return len(novas_mensalidades)
