import json
import logging
from pywebpush import webpush, WebPushException
from core.config import settings
from domain.notificacoes.repositories import PushSubscriptionRepository

logger = logging.getLogger(__name__)

class DispararNotificacaoUseCase:
    def __init__(self, push_repo: PushSubscriptionRepository):
        self.push_repo = push_repo

    async def executar(self, titulo: str, corpo: str, url: str = "/", usuarios_ids: list[int] = None):
        """
        Dispara notificacao push.
        Se usuarios_ids for None, manda para todo mundo.
        """
        if not settings.VAPID_PRIVATE_KEY:
            logger.warning("VAPID_PRIVATE_KEY nao configurada. Push Notifications desativadas.")
            return

        # Busca inscricoes
        if usuarios_ids:
            todas_inscricoes = []
            for uid in usuarios_ids:
                inscricoes = await self.push_repo.listar_por_usuario(uid)
                todas_inscricoes.extend(inscricoes)
        else:
            todas_inscricoes = await self.push_repo.listar_todos()

        payload = json.dumps({
            "title": titulo,
            "body": corpo,
            "url": url,
            "icon": "/icons.svg"
        })

        for sub in todas_inscricoes:
            try:
                sub_info = json.loads(sub.subscription_json)
                webpush(
                    subscription_info=sub_info,
                    data=payload,
                    vapid_private_key=settings.VAPID_PRIVATE_KEY,
                    vapid_claims={"sub": settings.VAPID_CLAIMS_EMAIL}
                )
            except WebPushException as ex:
                logger.error(f"Erro ao enviar push notification: {ex}")
                # 410 Gone = Inscricao expirou ou usuario removeu permissao
                if ex.response and ex.response.status_code == 410:
                    await self.push_repo.deletar_por_endpoint(sub_info.get("endpoint"))
            except Exception as e:
                logger.error(f"Erro inesperado no webpush: {e}")
