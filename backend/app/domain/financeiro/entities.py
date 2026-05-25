from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from domain.financeiro.enums import StatusPagamento

@dataclass
class Financeiro:
    id: Optional[int]
    usuario_id: Optional[int]
    tipo: str
    valor: float
    status_pagamento: StatusPagamento
    mes_referencia: str
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None
