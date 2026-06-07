from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from api.v1.deps import get_current_user, get_admin_user, get_db
from sqlalchemy.orm import Session
from domain.usuarios.entities import Usuario
from api.db.repositories.push_subscription_repo import SQLAlchemyPushSubscriptionRepository
from application.notificacoes.registrar_inscricao import RegistrarInscricaoUseCase, DesregistrarInscricaoUseCase
from application.notificacoes.disparar_notificacao import DispararNotificacaoUseCase
from core.config import settings

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
        await use_case.executar(payload.endpoint, current_user.id)
        return {"detail": "Inscrição removida com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/debug")
async def debug_push(
    admin_user: Usuario = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Endpoint de diagnóstico para Push Notifications (somente admin)"""
    repo = SQLAlchemyPushSubscriptionRepository(db)
    todas = await repo.listar_todos()
    
    return {
        "vapid_private_key_configurada": bool(settings.VAPID_PRIVATE_KEY),
        "vapid_public_key_configurada": bool(settings.VAPID_PUBLIC_KEY),
        "vapid_claims_email": settings.VAPID_CLAIMS_EMAIL,
        "total_inscricoes": len(todas),
        "inscricoes": [
            {
                "id": s.id,
                "usuario_id": s.usuario_id,
                "criado_em": str(s.criado_em) if s.criado_em else None
            }
            for s in todas
        ]
    }

@router.post("/test")
async def test_push(
    admin_user: Usuario = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Dispara uma notificação de teste para o admin logado"""
    repo = SQLAlchemyPushSubscriptionRepository(db)
    use_case = DispararNotificacaoUseCase(repo)
    
    try:
        await use_case.executar(
            titulo="Teste de Notificação 🔔",
            corpo="Se você está vendo isso, as notificações estão funcionando!",
            url="/",
            usuarios_ids=[admin_user.id]
        )
        return {"detail": "Notificação de teste disparada com sucesso"}
    except Exception as e:
        return {"detail": f"Erro ao disparar: {str(e)}"}

