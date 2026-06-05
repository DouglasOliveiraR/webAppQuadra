import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from api.db.database import SessionLocal
from application.financeiro.virada_mes_use_case import ViradaMesUseCase
from api.db.repositories.financeiro_repo import SQLAlchemyFinanceiroRepository
from api.db.repositories.usuario_repo import SQLAlchemyUsuarioRepository
from api.db.repositories.evento_repo import SQLAlchemyEventoRepository
from api.db.repositories.presenca_repo import SQLAlchemyPresencaRepository
from api.db.repositories.push_subscription_repo import SQLAlchemyPushSubscriptionRepository
from application.notificacoes.disparar_notificacao import DispararNotificacaoUseCase
from application.notificacoes.lembretes import NotificarMensalidadeAtrasadaUseCase, NotificarPresencaPendenteUseCase
from application.eventos.abrir_presenca_use_case import AbrirPresencaUseCase

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def job_virada_mes():
    """
    Job agendado para rodar na virada do mês.
    Cria uma nova sessão de banco de dados e executa o caso de uso.
    """
    logger.info("Iniciando rotina automática de Virada de Mês...")
    db = SessionLocal()
    try:
        financeiro_repo = SQLAlchemyFinanceiroRepository(db)
        usuario_repo = SQLAlchemyUsuarioRepository(db)
        evento_repo = SQLAlchemyEventoRepository(db)
        
        use_case = ViradaMesUseCase(financeiro_repo, usuario_repo, evento_repo)
        qtd = await use_case.executar()
        db.commit()
        logger.info(f"Rotina de Virada de Mês concluída. {qtd} novas mensalidades geradas.")
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao executar rotina de Virada de Mês: {e}", exc_info=True)
    finally:
        db.close()

async def job_lembrete_mensalidade():
    logger.info("Iniciando rotina de lembrete de mensalidade...")
    db = SessionLocal()
    try:
        financeiro_repo = SQLAlchemyFinanceiroRepository(db)
        push_repo = SQLAlchemyPushSubscriptionRepository(db)
        disparar_uc = DispararNotificacaoUseCase(push_repo)
        
        use_case = NotificarMensalidadeAtrasadaUseCase(financeiro_repo, disparar_uc)
        await use_case.executar()
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao executar rotina de lembrete de mensalidade: {e}")
    finally:
        db.close()

async def job_lembrete_presenca():
    logger.info("Iniciando rotina de lembrete de presenca...")
    db = SessionLocal()
    try:
        evento_repo = SQLAlchemyEventoRepository(db)
        usuario_repo = SQLAlchemyUsuarioRepository(db)
        presenca_repo = SQLAlchemyPresencaRepository(db)
        push_repo = SQLAlchemyPushSubscriptionRepository(db)
        disparar_uc = DispararNotificacaoUseCase(push_repo)
        
        use_case = NotificarPresencaPendenteUseCase(evento_repo, usuario_repo, presenca_repo, disparar_uc)
        await use_case.executar()
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao executar rotina de lembrete de presenca: {e}")
    finally:
        db.close()

async def job_abrir_presenca_automatica():
    logger.info("Iniciando rotina de abertura automática de presenças...")
    db = SessionLocal()
    try:
        evento_repo = SQLAlchemyEventoRepository(db)
        push_repo = SQLAlchemyPushSubscriptionRepository(db)
        disparar_uc = DispararNotificacaoUseCase(push_repo)
        
        use_case = AbrirPresencaUseCase(evento_repo, disparar_uc)
        qtd = await use_case.executar_automatico()
        db.commit()
        if qtd > 0:
            logger.info(f"Rotina concluída: {qtd} evento(s) tiveram a presença aberta.")
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao executar rotina de abertura de presencas: {e}")
    finally:
        db.close()

def start_scheduler():
    # Roda dia 1 de cada mês às 00:01
    scheduler.add_job(
        job_virada_mes,
        CronTrigger(day=1, hour=0, minute=1),
        id="virada_mes_job",
        replace_existing=True
    )
    # Lembrete de Mensalidade: Diário às 12:00
    scheduler.add_job(
        job_lembrete_mensalidade,
        CronTrigger(hour=12, minute=0),
        id="lembrete_mensalidade_job",
        replace_existing=True
    )
    # Lembrete de Presença: Diário às 13:00, 15:00 e 18:00
    scheduler.add_job(
        job_lembrete_presenca,
        CronTrigger(hour='13,15,18', minute=0),
        id="lembrete_presenca_job",
        replace_existing=True
    )
    # Abertura automática de lista: Diário às 10:00
    scheduler.add_job(
        job_abrir_presenca_automatica,
        CronTrigger(hour=10, minute=20),
        id="abrir_presenca_automatica_job",
        replace_existing=True
    )
    scheduler.start()
    logger.info("APScheduler iniciado. Jobs agendados: " + str(len(scheduler.get_jobs())))

def stop_scheduler():
    scheduler.shutdown()
    logger.info("APScheduler finalizado.")
