from dataclasses import dataclass
from typing import Optional
from domain.votos.enums import CategoriaVoto

@dataclass
class Voto:
    id: Optional[int]
    evento_id: int
    eleitor_id: int
    candidato_id: int
    categoria: CategoriaVoto
