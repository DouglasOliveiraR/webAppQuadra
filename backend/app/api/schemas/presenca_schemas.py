from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from domain.presencas.enums import StatusJogo, Posicao

class PresencaUpdateRequest(BaseModel):
    status: StatusJogo
    posicao: Posicao
    churrasco: bool

class PresencaResponse(BaseModel):
    id: int
    usuario_id: int
    evento_id: int
    status_jogo: StatusJogo
    posicao: Posicao
    vai_churrasco: bool
    checkin_validado: bool
    falta_penalizada: bool
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class CheckinRequest(BaseModel):
    chegou: bool
    falta_justificada: bool
