from typing import List, Dict
from domain.usuarios.repositories import UsuarioRepository
from domain.premios.repositories import PremioRepository
import dataclasses

class ListarRankingUseCase:
    def __init__(self, usuario_repo: UsuarioRepository, premio_repo: PremioRepository):
        self.usuario_repo = usuario_repo
        self.premio_repo = premio_repo

    async def executar(self, limit: int = 50) -> List[Dict]:
        ranking = await self.usuario_repo.obter_ranking_agrupado(limit)
        return [dataclasses.asdict(u) for u in ranking]
