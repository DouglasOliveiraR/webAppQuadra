from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from api.schemas.ranking_schemas import RankingResponse
from application.ranking.use_cases import ListarRankingUseCase
from api.v1.deps import get_listar_ranking_use_case

router = APIRouter(prefix="/api/ranking", tags=["Ranking"])

@router.get("", response_model=List[RankingResponse])
async def get_ranking(use_case: ListarRankingUseCase = Depends(get_listar_ranking_use_case)):
    return await use_case.executar()
