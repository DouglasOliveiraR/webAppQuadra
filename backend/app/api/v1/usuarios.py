from fastapi import APIRouter, Depends, HTTPException, status
from api.schemas.usuario_schemas import NotaAdminRequest
from application.usuarios.atualizar_nota_admin_use_case import AtualizarNotaAdminUseCase
from api.v1.deps import get_admin_user, get_atualizar_nota_admin_use_case
from domain.usuarios.entities import Usuario
from core.exceptions import RegraDeNegocioError

router = APIRouter(prefix="/api/usuarios", tags=["Usuários"])

@router.put("/{usuario_id}/nota-admin")
async def atualizar_nota_admin(
    usuario_id: int,
    payload: NotaAdminRequest,
    admin_user: Usuario = Depends(get_admin_user),
    use_case: AtualizarNotaAdminUseCase = Depends(get_atualizar_nota_admin_use_case)
):
    try:
        usuario = await use_case.executar(usuario_id, payload.nota)
        return {"id": usuario.id, "nota_admin": usuario.nota_admin}
    except RegraDeNegocioError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.detail)
