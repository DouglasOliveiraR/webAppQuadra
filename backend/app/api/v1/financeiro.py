from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from api.schemas.financeiro_schemas import FinanceiroResponse
from application.financeiro.use_cases import ListarFinanceiroUseCase, BaixarPagamentoUseCase
from api.v1.deps import get_listar_financeiro_use_case, get_baixar_pagamento_use_case, get_current_user, get_admin_user
from domain.usuarios.entities import Usuario
from core.exceptions import RecursoNaoEncontradoError

router = APIRouter(prefix="/api/financeiro", tags=["Financeiro"])

@router.get("/me", response_model=List[FinanceiroResponse])
async def get_meu_financeiro(
    use_case: ListarFinanceiroUseCase = Depends(get_listar_financeiro_use_case),
    current_user: Usuario = Depends(get_current_user)
):
    return await use_case.executar(current_user.id)

@router.put("/{pagamento_id}/baixar", response_model=FinanceiroResponse)
async def baixar_pagamento(
    pagamento_id: int,
    use_case: BaixarPagamentoUseCase = Depends(get_baixar_pagamento_use_case),
    admin_user: Usuario = Depends(get_admin_user)
):
    try:
        return await use_case.executar(pagamento_id)
    except RecursoNaoEncontradoError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)
