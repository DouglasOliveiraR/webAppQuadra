from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from domain.votos.enums import CategoriaVoto

class VotoRequest(BaseModel):
    categoria: CategoriaVoto
    candidato_id: int

class VotoResponse(BaseModel):
    id: int
    evento_id: int
    eleitor_id: int
    candidato_id: int
    categoria: CategoriaVoto
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
