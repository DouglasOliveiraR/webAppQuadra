from abc import ABC, abstractmethod
from typing import List, Optional
from domain.notas.entities import Nota

class NotaRepository(ABC):
    @abstractmethod
    async def salvar(self, nota: Nota) -> Nota:
        pass

    @abstractmethod
    async def salvar_lote(self, notas: List[Nota]) -> None:
        pass

    @abstractmethod
    async def listar_por_avaliado(self, avaliado_id: int) -> List[Nota]:
        pass

    @abstractmethod
    async def listar_por_avaliador_e_evento(self, avaliador_id: int, evento_id: int) -> List[Nota]:
        pass
