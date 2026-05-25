from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
from api.schemas.financeiro_schemas import FinanceiroResponse, FinanceiroAdminResponse, TransparenciaResponse
from application.financeiro.use_cases import ListarFinanceiroUseCase, BaixarPagamentoUseCase
from application.financeiro.listar_todos_financeiro_use_case import ListarTodosFinanceiroUseCase
from application.financeiro.obter_transparencia_use_case import ObterTransparenciaUseCase
from application.usuarios.listar_usuarios_use_case import ListarUsuariosUseCase
from api.v1.deps import (
    get_listar_financeiro_use_case, 
    get_listar_todos_financeiro_use_case,
    get_listar_usuarios_use_case,
    get_baixar_pagamento_use_case, 
    get_obter_transparencia_use_case,
    get_current_user, 
    get_admin_user
)
from domain.usuarios.entities import Usuario
from core.exceptions import RecursoNaoEncontradoError

router = APIRouter(prefix="/api/financeiro", tags=["Financeiro"])

@router.get("/me", response_model=List[FinanceiroResponse])
async def get_meu_financeiro(
    mes: Optional[str] = None,
    use_case: ListarFinanceiroUseCase = Depends(get_listar_financeiro_use_case),
    current_user: Usuario = Depends(get_current_user)
):
    filtro_mes = mes or datetime.now().strftime("%Y-%m")
    return await use_case.executar(current_user.id, filtro_mes)

@router.get("/admin", response_model=List[FinanceiroAdminResponse])
async def get_financeiro_admin(
    mes: Optional[str] = None,
    use_case: ListarTodosFinanceiroUseCase = Depends(get_listar_todos_financeiro_use_case),
    usuarios_use_case: ListarUsuariosUseCase = Depends(get_listar_usuarios_use_case),
    admin_user: Usuario = Depends(get_admin_user)
):
    filtro_mes = mes or datetime.now().strftime("%Y-%m")
    registros = await use_case.executar(filtro_mes)
    usuarios = await usuarios_use_case.executar()
    
    # Criar mapeamento de usuario_id -> (nome, telefone)
    usuarios_map = {u.id: (u.nome, u.telefone) for u in usuarios}
    
    resposta = []
    for reg in registros:
        nome, tel = usuarios_map.get(reg.usuario_id, (None, None))
        resposta.append(
            FinanceiroAdminResponse(
                id=reg.id,
                usuario_id=reg.usuario_id,
                tipo=reg.tipo,
                valor=reg.valor,
                status_pagamento=reg.status_pagamento,
                mes_referencia=reg.mes_referencia,
                usuario_nome=nome,
                usuario_telefone=tel
            )
        )
    return resposta

@router.get("/transparencia", response_model=TransparenciaResponse)
async def get_transparencia(
    mes: Optional[str] = None,
    use_case: ObterTransparenciaUseCase = Depends(get_obter_transparencia_use_case),
    current_user: Usuario = Depends(get_current_user)
):
    filtro_mes = mes or datetime.now().strftime("%Y-%m")
    return await use_case.executar(filtro_mes)

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
