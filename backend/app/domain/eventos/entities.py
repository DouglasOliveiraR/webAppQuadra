from dataclasses import dataclass
from typing import Optional
from datetime import date, time
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
