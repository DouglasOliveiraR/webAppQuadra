from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from api.schemas.usuario_schemas import NotaAdminRequest, UsuarioCreateRequest, UsuarioUpdateRequest, UsuarioResponse, AlterarSenhaRequest
from application.usuarios.atualizar_nota_admin_use_case import AtualizarNotaAdminUseCase
from application.usuarios.listar_usuarios_use_case import ListarUsuariosUseCase
from application.usuarios.criar_usuario_use_case import CriarUsuarioUseCase
from application.usuarios.atualizar_usuario_use_case import AtualizarUsuarioUseCase
from application.usuarios.alterar_senha_use_case import AlterarSenhaUseCase
from api.v1.deps import (
    get_admin_user, 
    get_atualizar_nota_admin_use_case,
    get_listar_usuarios_use_case,
    get_criar_usuario_use_case,
    get_atualizar_usuario_use_case,
    get_current_user,
    get_alterar_senha_use_case
)
from domain.usuarios.entities import Usuario
from core.exceptions import RegraDeNegocioError

router = APIRouter(prefix="/api/usuarios", tags=["Usuários"])

@router.get("/", response_model=List[UsuarioResponse])
async def listar_usuarios(
    admin_user: Usuario = Depends(get_admin_user),
    use_case: ListarUsuariosUseCase = Depends(get_listar_usuarios_use_case)
):
    try:
        return await use_case.executar()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/", response_model=UsuarioResponse)
async def criar_usuario(
    payload: UsuarioCreateRequest,
    admin_user: Usuario = Depends(get_admin_user),
    use_case: CriarUsuarioUseCase = Depends(get_criar_usuario_use_case)
):
    try:
        return await use_case.executar(
            nome=payload.nome,
            telefone=payload.telefone,
            perfil=payload.perfil,
            nota_admin=payload.nota_admin
        )
    except RegraDeNegocioError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.detail)

@router.put("/{usuario_id}", response_model=UsuarioResponse)
async def atualizar_usuario(
    usuario_id: int,
    payload: UsuarioUpdateRequest,
    admin_user: Usuario = Depends(get_admin_user),
    use_case: AtualizarUsuarioUseCase = Depends(get_atualizar_usuario_use_case)
):
    try:
        return await use_case.executar(
            usuario_id=usuario_id,
            nome=payload.nome,
            telefone=payload.telefone,
            perfil=payload.perfil,
            status=payload.status,
            nota_admin=payload.nota_admin
        )
    except RegraDeNegocioError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.detail)

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

@router.put("/me/senha")
async def alterar_senha(
    payload: AlterarSenhaRequest,
    current_user: Usuario = Depends(get_current_user),
    use_case: AlterarSenhaUseCase = Depends(get_alterar_senha_use_case)
):
    try:
        await use_case.executar(
            usuario_id=current_user.id,
            senha_atual=payload.senha_atual,
            nova_senha=payload.nova_senha
        )
        return {"detail": "Senha alterada com sucesso!"}
    except RegraDeNegocioError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.detail)
