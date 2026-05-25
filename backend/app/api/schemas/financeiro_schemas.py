from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from domain.financeiro.enums import StatusPagamento

class FinanceiroResponse(BaseModel):
    id: int
    tipo: str
    valor: float
    status_pagamento: StatusPagamento
    mes_referencia: str
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None

    class Config:
        from_attributes = True

class FinanceiroAdminResponse(BaseModel):
    id: int
    usuario_id: Optional[int]
    tipo: str
    valor: float
    status_pagamento: StatusPagamento
    mes_referencia: str
    usuario_nome: Optional[str] = None
    usuario_telefone: Optional[str] = None
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None

    class Config:
        from_attributes = True
