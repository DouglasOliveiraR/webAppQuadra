from pydantic import BaseModel

class RankingResponse(BaseModel):
    id: int
    nome: str
    pontos_ranking: int
    nota_admin: float
    nota_galera_media: float

    class Config:
        from_attributes = True
