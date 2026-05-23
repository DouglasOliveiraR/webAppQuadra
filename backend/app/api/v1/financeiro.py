from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from api.schemas.financeiro_schemas import FinanceiroResponse
from application.financeiro.use_cases import ListarFinanceiroUseCase, BaixarPagamentoUseCase
from api.v1.deps import get_listar_financeiro_use_case, get_baixar_pagamento_use_case, get_current_user
from core.exceptions import RecursoNaoEncontradoError

router = APIRouter(prefix="/api/financeiro", tags=["Financeiro"])

@router.get("/me", response_model=List[FinanceiroResponse])
async def get_meu_financeiro(
    use_case: ListarFinanceiroUseCase = Depends(get_listar_financeiro_use_case),
    current_user: dict = Depends(get_current_user)
):
    # Simulando a extração do ID do usuário logado via token
    usuario_id = int(current_user["sub"])
    return await use_case.executar(usuario_id)

@router.put("/{pagamento_id}/baixar", response_model=FinanceiroResponse)
async def baixar_pagamento(
    pagamento_id: int,
    use_case: BaixarPagamentoUseCase = Depends(get_baixar_pagamento_use_case),
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("perfil") != "ADMIN":
        raise HTTPException(status_code=403, detail="Acesso negado")
        
    try:
        return await use_case.executar(pagamento_id)
    except RecursoNaoEncontradoError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)
