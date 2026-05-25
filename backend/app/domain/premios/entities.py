from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from domain.votos.enums import CategoriaVoto

@dataclass
class Premio:
    id: Optional[int]
    usuario_id: int
    evento_id: int
    categoria: CategoriaVoto
    mes_referencia: str
    criado_em: Optional[datetime] = None
