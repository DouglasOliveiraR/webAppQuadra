import asyncio
import logging
from api.db.database import SessionLocal
from api.db.repositories.usuario_repo import SQLAlchemyUsuarioRepository
from application.auth.use_cases import LoginUseCase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_login():
    db = SessionLocal()
    repo = SQLAlchemyUsuarioRepository(db)
    use_case = LoginUseCase(repo)
    
    try:
        token = await use_case.executar("11999999999", "admin123")
        logger.info("LOGIN SUCESSO! Token: %s", token)
    except Exception as e:
        logger.error("ERRO: %s - %s", type(e), str(e))
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_login())
