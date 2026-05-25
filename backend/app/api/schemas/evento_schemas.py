from pydantic import BaseModel
from typing import Optional
from datetime import date, time, datetime

class EventoRequest(BaseModel):
    data_jogo: date
    hora_inicio: time
    hora_fim: time
    flag_churrasco: bool
    valor_churrasco: Optional[float] = 0.0
    endereco: Optional[str] = None
    chave_pix: Optional[str] = None
    valor_mensalidade: Optional[float] = 60.0
    custo_quadra: Optional[float] = 0.0

class ChurrascoRequest(BaseModel):
    flag_churrasco: bool
    valor_churrasco: Optional[float] = 0.0

class ChavePixRequest(BaseModel):
    chave_pix: Optional[str] = None

class MensalidadeRequest(BaseModel):
    valor_mensalidade: float

class CustoQuadraRequest(BaseModel):
    custo_quadra: float

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
    endereco: Optional[str]
    chave_pix: Optional[str] = None
    valor_mensalidade: Optional[float] = 60.0
    custo_quadra: Optional[float] = 0.0
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None

    class Config:
        from_attributes = True
