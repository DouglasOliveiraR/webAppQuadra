from pydantic import BaseModel
from typing import Optional, List

class PremioCount(BaseModel):
    categoria: str
    quantidade: int

class RankingResponse(BaseModel):
    id: int
    nome: str
    pontos_ranking: int
    nota_admin: int
    nota_galera_media: float
    foto_url: Optional[str] = None
    premios: List[PremioCount] = []
    gols_total: int = 0

    class Config:
        from_attributes = True
