from domain.financeiro.enums import StatusPagamento
from typing import List, Optional
from sqlalchemy.orm import Session
from domain.financeiro.entities import Financeiro
from domain.financeiro.repositories import FinanceiroRepository
from api.db.models import FinanceiroModel

class SQLAlchemyFinanceiroRepository(FinanceiroRepository):
    def __init__(self, session: Session):
        self.session = session

    def _to_entity(self, model: FinanceiroModel) -> Financeiro:
        if not model:
            return None
        return Financeiro(
            id=model.id,
            usuario_id=model.usuario_id,
            tipo=model.tipo,
            valor=model.valor,
            status_pagamento=model.status_pagamento,
            mes_referencia=model.mes_referencia,
            criado_em=model.criado_em,
            atualizado_em=model.atualizado_em
        )

    def _to_model(self, entity: Financeiro) -> FinanceiroModel:
        model = FinanceiroModel(
            id=entity.id,
            usuario_id=entity.usuario_id,
            tipo=entity.tipo,
            valor=entity.valor,
            status_pagamento=entity.status_pagamento,
            mes_referencia=entity.mes_referencia
        )
        if entity.criado_em:
            model.criado_em = entity.criado_em
        if entity.atualizado_em:
            model.atualizado_em = entity.atualizado_em
        return model

    async def buscar_por_id(self, financeiro_id: int) -> Optional[Financeiro]:
        model = self.session.query(FinanceiroModel).filter(FinanceiroModel.id == financeiro_id).first()
        return self._to_entity(model)

    async def listar_por_usuario(self, usuario_id: int) -> List[Financeiro]:
        models = self.session.query(FinanceiroModel).filter(FinanceiroModel.usuario_id == usuario_id).all()
        return [self._to_entity(m) for m in models]

    async def listar_todos(self) -> List[Financeiro]:
        models = self.session.query(FinanceiroModel).all()
        return [self._to_entity(m) for m in models]

    async def listar_por_usuarios_e_mes(self, usuario_ids: List[int], mes_referencia: str) -> List[Financeiro]:
        if not usuario_ids:
            return []
        models = self.session.query(FinanceiroModel).filter(
            FinanceiroModel.usuario_id.in_(usuario_ids),
            FinanceiroModel.mes_referencia == mes_referencia
        ).all()
        return [self._to_entity(m) for m in models]

    async def salvar(self, financeiro: Financeiro) -> Financeiro:
        if financeiro.id:
            # Expurgar qualquer instância em cache na sessão para evitar conflito de identity map
            existing = self.session.get(FinanceiroModel, financeiro.id)
            if existing:
                existing.usuario_id = financeiro.usuario_id
                existing.tipo = financeiro.tipo
                existing.valor = financeiro.valor
                existing.status_pagamento = financeiro.status_pagamento
                existing.mes_referencia = financeiro.mes_referencia
                self.session.flush()
                self.session.commit()
                self.session.refresh(existing)
                return self._to_entity(existing)
        
        # Novo registro
        model = self._to_model(financeiro)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    async def alternar_status_pagamento(self, pagamento_id: int) -> Optional[Financeiro]:
        """Toggle atômico do status de pagamento, evitando conflito de identity map."""
        model = self.session.get(FinanceiroModel, pagamento_id)
        if not model:
            return None
        
        if model.status_pagamento == StatusPagamento.PAGO:
            model.status_pagamento = StatusPagamento.PENDENTE
        else:
            model.status_pagamento = StatusPagamento.PAGO
        
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    # Impacto: A utilização de salvar_lote melhora drasticamente a performance ao persistir
    # registros no banco em lote. Ao invés de executar um commit por iteração num loop,
    # realizamos apenas um commit no final, reduzindo a latência, overhead do ORM e acessos em disco.
    async def salvar_lote(self, lista_financeiro: List[Financeiro]) -> List[Financeiro]:
        if not lista_financeiro:
            return []
        model_list = []
        for item in lista_financeiro:
            model = self._to_model(item)
            if model.id:
                model = self.session.merge(model)
            else:
                self.session.add(model)
            model_list.append(model)
        self.session.commit()
        for m in model_list:
            self.session.refresh(m)
        return [self._to_entity(m) for m in model_list]

    async def deletar(self, financeiro_id: int) -> bool:
        model = self.session.query(FinanceiroModel).filter(FinanceiroModel.id == financeiro_id).first()
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False

    async def deletar_pendentes_por_usuario(self, usuario_id: int) -> bool:
        self.session.query(FinanceiroModel).filter(FinanceiroModel.usuario_id == usuario_id, FinanceiroModel.status_pagamento == StatusPagamento.PENDENTE).delete(synchronize_session=False)
        self.session.commit()
        return True
