from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from api.v1.deps import get_current_user, get_db
from sqlalchemy.orm import Session
from domain.usuarios.entities import Usuario
from api.db.repositories.push_subscription_repo import SQLAlchemyPushSubscriptionRepository
from application.notificacoes.registrar_inscricao import RegistrarInscricaoUseCase, DesregistrarInscricaoUseCase

router = APIRouter(prefix="/api/notificacoes", tags=["Notificacoes"])

class SubscribeRequest(BaseModel):
    subscription: dict

@router.post("/subscribe")
async def subscribe(
    payload: SubscribeRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = SQLAlchemyPushSubscriptionRepository(db)
    use_case = RegistrarInscricaoUseCase(repo)
    try:
        await use_case.executar(current_user.id, payload.subscription)
        return {"detail": "Inscrição salva com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

class UnsubscribeRequest(BaseModel):
    endpoint: str

@router.post("/unsubscribe")
async def unsubscribe(
    payload: UnsubscribeRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = SQLAlchemyPushSubscriptionRepository(db)
    use_case = DesregistrarInscricaoUseCase(repo)
    try:
        await use_case.executar(payload.endpoint)
        return {"detail": "Inscrição removida com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
