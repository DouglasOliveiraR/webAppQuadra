from fastapi import APIRouter, Depends, Query
from typing import List
from api.schemas.ranking_schemas import RankingResponse
from application.ranking.use_cases import ListarRankingUseCase
from application.eventos.obter_ultimo_resultado_use_case import ObterUltimoResultadoUseCase
from api.v1.deps import get_listar_ranking_use_case, get_obter_ultimo_resultado_use_case

router = APIRouter(prefix="/api/ranking", tags=["Ranking"])

@router.get("", response_model=List[RankingResponse])
async def get_ranking(
    limit: int = Query(50, ge=1, description="Número máximo de jogadores no ranking"),
    use_case: ListarRankingUseCase = Depends(get_listar_ranking_use_case)
):
    return await use_case.executar(limit=limit)

@router.get("/ultimo-resultado")
async def get_ultimo_resultado(use_case: ObterUltimoResultadoUseCase = Depends(get_obter_ultimo_resultado_use_case)):
    resultado = await use_case.executar()
    if not resultado:
        return {"detail": "Nenhum jogo encerrado encontrado"}
    return resultado
