from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Nota:
    id: Optional[int]
    avaliado_id: int
    avaliador_id: Optional[int]
    evento_id: Optional[int]
    nota: int
    tipo: str # ADMIN or GALERA
    criado_em: Optional[datetime] = None
