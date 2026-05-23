from pydantic import BaseModel
from typing import Optional
from datetime import date, time

class EventoRequest(BaseModel):
    data_jogo: date
    hora_inicio: time
    hora_fim: time
    flag_churrasco: bool
    valor_churrasco: Optional[float] = 0.0

class ChurrascoRequest(BaseModel):
    flag_churrasco: bool
    valor_churrasco: Optional[float] = 0.0

class SorteioRequest(BaseModel):
    criterio: str

class EventoResponse(BaseModel):
    id: int
    data_jogo: date
    hora_inicio: time
    hora_fim: time
    status_evento: str
    flag_churrasco: bool
    valor_churrasco: Optional[float]

    class Config:
        from_attributes = True
