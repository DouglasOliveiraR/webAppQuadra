from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class PushSubscription:
    id: Optional[int]
    usuario_id: int
    subscription_json: str
    criado_em: Optional[datetime] = None
