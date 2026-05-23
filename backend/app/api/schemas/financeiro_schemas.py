from pydantic import BaseModel
from typing import Optional
from domain.financeiro.enums import StatusPagamento

class FinanceiroResponse(BaseModel):
    id: int
    tipo: str
    valor: float
    status_pagamento: StatusPagamento

    class Config:
        from_attributes = True
