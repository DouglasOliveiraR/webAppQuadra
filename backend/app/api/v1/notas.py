from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict
from domain.usuarios.entities import Usuario
from api.v1.deps import get_current_user, get_db
from sqlalchemy.orm import Session
from application.notas.salvar_notas_galera_use_case import SalvarNotasGaleraUseCase

router = APIRouter(prefix="/api/notas", tags=["Notas"])

class NotasGaleraRequest(BaseModel):
    evento_id: int
    notas: Dict[int, int] # dicionario de usuario_id para nota

def get_salvar_notas_galera_use_case(db: Session = Depends(get_db)):
    from api.db.repositories.nota_repo import SQLAlchemyNotaRepository
    from api.db.repositories.usuario_repo import SQLAlchemyUsuarioRepository
    from api.db.repositories.evento_repo import SQLAlchemyEventoRepository
    nota_repo = SQLAlchemyNotaRepository(db)
    usuario_repo = SQLAlchemyUsuarioRepository(db)
    evento_repo = SQLAlchemyEventoRepository(db)
    return SalvarNotasGaleraUseCase(nota_repo, usuario_repo, evento_repo)

@router.post("/galera")
async def salvar_notas_galera(
    payload: NotasGaleraRequest,
    current_user: Usuario = Depends(get_current_user),
    use_case: SalvarNotasGaleraUseCase = Depends(get_salvar_notas_galera_use_case)
):
    try:
        await use_case.executar(
            avaliador_id=current_user.id,
            evento_id=payload.evento_id,
            notas=payload.notas
        )
        return {"detail": "Notas salvas com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
