from dataclasses import dataclass
from typing import Optional
from domain.presencas.enums import StatusJogo, Posicao

@dataclass
class Presenca:
    id: Optional[int]
    usuario_id: int
    evento_id: int
    status_jogo: StatusJogo
    posicao: Posicao
    vai_churrasco: bool
    checkin_validado: bool
    falta_penalizada: bool
