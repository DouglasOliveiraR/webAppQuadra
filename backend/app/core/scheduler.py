import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from api.db.database import SessionLocal
from application.financeiro.virada_mes_use_case import ViradaMesUseCase
from api.db.repositories.financeiro_repo import SQLAlchemyFinanceiroRepository
from api.db.repositories.usuario_repo import SQLAlchemyUsuarioRepository
from api.db.repositories.evento_repo import SQLAlchemyEventoRepository

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

def start_scheduler():
    # Roda dia 1 de cada mês às 00:01
    scheduler.add_job(
        job_virada_mes,
        CronTrigger(day=1, hour=0, minute=1),
        id="virada_mes_job",
        replace_existing=True
    )
    scheduler.start()
    logger.info("APScheduler iniciado. Jobs agendados: " + str(len(scheduler.get_jobs())))

def stop_scheduler():
    scheduler.shutdown()
    logger.info("APScheduler finalizado.")
