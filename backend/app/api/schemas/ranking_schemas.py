from pydantic import BaseModel
from typing import Optional

class RankingResponse(BaseModel):
    id: int
    nome: str
    pontos_ranking: int
    nota_admin: int
    nota_galera_media: float
    foto_url: Optional[str] = None

    class Config:
        from_attributes = True
