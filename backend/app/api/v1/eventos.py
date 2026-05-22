from fastapi import APIRouter, Depends, HTTPException, status
from api.schemas.presenca_schemas import PresencaUpdateRequest, PresencaResponse, CheckinRequest
from api.schemas.voto_schemas import VotoRequest, VotoResponse
from application.presencas.use_cases import AtualizarPresencaUseCase, CheckinUseCase
from application.votos.use_cases import RegistrarVotoUseCase
from api.v1.deps import (
    get_current_user, get_admin_user, get_atualizar_presenca_use_case,
    get_checkin_use_case, get_registrar_voto_use_case
)
from domain.usuarios.entities import Usuario
from core.exceptions import RegraDeNegocioError

router = APIRouter(prefix="/api/eventos", tags=["Eventos"])

@router.put("/{id}/presencas/me", response_model=PresencaResponse)
async def atualizar_presenca(
    id: int,
    payload: PresencaUpdateRequest,
    current_user: Usuario = Depends(get_current_user),
    use_case: AtualizarPresencaUseCase = Depends(get_atualizar_presenca_use_case)
):
    try:
        presenca = await use_case.executar(
            usuario_id=current_user.id,
            evento_id=id,
            status=payload.status,
            posicao=payload.posicao,
            churrasco=payload.churrasco
        )
        return presenca
    except RegraDeNegocioError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.detail)

@router.post("/{id}/checkin/{usuario_id}", response_model=PresencaResponse)
async def registrar_checkin(
    id: int,
    usuario_id: int,
    payload: CheckinRequest,
    admin_user: Usuario = Depends(get_admin_user),
    use_case: CheckinUseCase = Depends(get_checkin_use_case)
):
    try:
        presenca = await use_case.executar(
            evento_id=id,
            usuario_id=usuario_id,
            chegou=payload.chegou,
            falta_justificada=payload.falta_justificada
        )
        return presenca
    except RegraDeNegocioError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.detail)

@router.post("/{id}/votos", response_model=VotoResponse)
async def registrar_voto(
    id: int,
    payload: VotoRequest,
    current_user: Usuario = Depends(get_current_user),
    use_case: RegistrarVotoUseCase = Depends(get_registrar_voto_use_case)
):
    try:
        voto = await use_case.executar(
            evento_id=id,
            eleitor_id=current_user.id,
            candidato_id=payload.candidato_id,
            categoria=payload.categoria
        )
        return voto
    except RegraDeNegocioError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.detail)
