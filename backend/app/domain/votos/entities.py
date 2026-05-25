from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from domain.votos.enums import CategoriaVoto

@dataclass
class Voto:
    id: Optional[int]
    evento_id: int
    eleitor_id: int
    candidato_id: int
    categoria: CategoriaVoto
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None
