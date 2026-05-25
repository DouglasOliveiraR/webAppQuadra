from dataclasses import dataclass
from typing import Optional
from datetime import date, time, datetime
from domain.eventos.enums import StatusEvento

@dataclass
class Evento:
    id: Optional[int]
    data_jogo: date
    hora_inicio: time
    hora_fim: time
    status_evento: StatusEvento
    flag_churrasco: bool
    valor_churrasco: float
    endereco: Optional[str] = None
    chave_pix: Optional[str] = None
    valor_mensalidade: Optional[float] = 60.0
    custo_quadra: Optional[float] = 0.0
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None
