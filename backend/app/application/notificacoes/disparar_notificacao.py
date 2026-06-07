import json
import logging
import asyncio
from pywebpush import webpush, WebPushException
from core.config import settings
from domain.notificacoes.repositories import PushSubscriptionRepository

logger = logging.getLogger(__name__)

class DispararNotificacaoUseCase:
    def __init__(self, push_repo: PushSubscriptionRepository):
        self.push_repo = push_repo

    async def _enviar_notificacao(self, sub_info: dict, payload: str):
        try:
            # ⚡ Bolt: webpush é uma biblioteca síncrona que faz chamadas HTTP.
            # Encapsular em to_thread previne o bloqueio do Event Loop do FastAPI.
            await asyncio.to_thread(
                webpush,
                subscription_info=sub_info,
                data=payload,
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={"sub": settings.VAPID_CLAIMS_EMAIL}
            )
        except WebPushException as ex:
            logger.error(f"Erro ao enviar push notification: {ex}")
            if ex.response and ex.response.status_code == 410:
                await self.push_repo.deletar_por_endpoint(sub_info.get("endpoint"))
        except Exception as e:
            logger.error(f"Erro inesperado no webpush: {e}")

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
            todas_inscricoes = await self.push_repo.listar_por_usuarios(usuarios_ids)
        else:
            todas_inscricoes = await self.push_repo.listar_todos()

        payload = json.dumps({
            "title": titulo,
            "body": corpo,
            "url": url,
            "icon": "/icons.svg"
        })

        # ⚡ Bolt: Executa de forma concorrente em vez de loop sequencial.
        # Impacto esperado: Evitar timeout de resposta na API em endpoints
        # (ex: marcar presenca, que avisa admin) com muitos usuarios cadastrados.
        tasks = []
        for sub in todas_inscricoes:
            try:
                sub_info = json.loads(sub.subscription_json)
                tasks.append(self._enviar_notificacao(sub_info, payload))
            except Exception as e:
                logger.error(f"Erro ao decodificar subscription: {e}")

        if tasks:
            await asyncio.gather(*tasks)
