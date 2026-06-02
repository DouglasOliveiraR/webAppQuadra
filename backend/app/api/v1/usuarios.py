from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from typing import List
from api.schemas.usuario_schemas import NotaAdminRequest, UsuarioCreateRequest, UsuarioUpdateRequest, UsuarioResponse, AlterarSenhaRequest
from application.usuarios.atualizar_nota_admin_use_case import AtualizarNotaAdminUseCase
from application.usuarios.listar_usuarios_use_case import ListarUsuariosUseCase
from application.usuarios.criar_usuario_use_case import CriarUsuarioUseCase
from application.usuarios.atualizar_usuario_use_case import AtualizarUsuarioUseCase
from application.usuarios.alterar_senha_use_case import AlterarSenhaUseCase
from application.usuarios.atualizar_foto_perfil_use_case import AtualizarFotoPerfilUseCase
from application.usuarios.deletar_usuario_use_case import DeletarUsuarioUseCase
from api.v1.deps import (
    get_admin_user, 
    get_atualizar_nota_admin_use_case,
    get_listar_usuarios_use_case,
    get_criar_usuario_use_case,
    get_atualizar_usuario_use_case,
    get_current_user,
    get_alterar_senha_use_case,
    get_atualizar_foto_perfil_use_case,
    get_deletar_usuario_use_case,
    get_db
)
from core.security import get_password_hash
from api.db.repositories.usuario_repo import SQLAlchemyUsuarioRepository
from sqlalchemy.orm import Session
from api.schemas.usuario_schemas import AdminEditUsuarioRequest
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
            nota_admin=payload.nota_admin,
            senha=payload.senha
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

import os
import shutil

@router.post("/me/foto", response_model=UsuarioResponse)
async def upload_foto_perfil(
    file: UploadFile = File(...),
    current_user: Usuario = Depends(get_current_user),
    use_case: AtualizarFotoPerfilUseCase = Depends(get_atualizar_foto_perfil_use_case)
):
    # Validação da extensão do arquivo
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".png", ".jpg", ".jpeg", ".webp"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Apenas imagens (.png, .jpg, .jpeg, .webp) são permitidas.")
    
    # Caminho para salvar a foto
    # Salva dentro da pasta backend/app/static/fotos
    current_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "static"))
    fotos_dir = os.path.join(static_dir, "fotos")
    os.makedirs(fotos_dir, exist_ok=True)
    
    # O nome do arquivo será fixo baseado no ID do usuário para sobrescrever e não acumular lixo
    filename = f"usuario_{current_user.id}{ext}"
    filepath = os.path.join(fotos_dir, filename)
    
    try:
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Erro ao salvar arquivo: {str(e)}")
        
    # URL relativa para salvar no banco de dados
    foto_url = f"/static/fotos/{filename}"
    
    try:
        return await use_case.executar(current_user.id, foto_url)
    except RegraDeNegocioError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.detail)

@router.delete("/{usuario_id}", status_code=status.HTTP_200_OK)
async def deletar_usuario(
    usuario_id: int,
    admin_user: Usuario = Depends(get_admin_user),
    use_case: DeletarUsuarioUseCase = Depends(get_deletar_usuario_use_case)
):
    try:
        sucesso = await use_case.executar(usuario_id)
        if not sucesso:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
        return {"detail": "Usuário deletado com sucesso!"}
    except RegraDeNegocioError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.detail)

@router.put("/{usuario_id}/admin-edit", response_model=UsuarioResponse)
async def admin_edit_usuario(
    usuario_id: int,
    payload: AdminEditUsuarioRequest,
    admin_user: Usuario = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    repo = SQLAlchemyUsuarioRepository(db)
    usuario = await repo.buscar_por_id(usuario_id)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    
    if payload.pontos_ranking is not None:
        usuario.pontos_ranking = payload.pontos_ranking
    
    if payload.resetar_senha:
        usuario.senha_hash = get_password_hash("123456")
        
    await repo.salvar(usuario)
    return usuario
