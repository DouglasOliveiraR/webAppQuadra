from enum import Enum

class StatusPagamento(str, Enum):
    PENDENTE = "PENDENTE"
    PAGO = "PAGO"
