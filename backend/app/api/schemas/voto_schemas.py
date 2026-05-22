from pydantic import BaseModel, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)
