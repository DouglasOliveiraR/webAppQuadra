import asyncio
from api.db.database import SessionLocal
from api.db.repositories.evento_repo import SQLAlchemyEventoRepository
from api.db.repositories.presenca_repo import SQLAlchemyPresencaRepository
from api.db.repositories.usuario_repo import SQLAlchemyUsuarioRepository
from application.eventos.sorteio_use_case import SorteioUseCase

async def run():
    db = SessionLocal()
    e_repo = SQLAlchemyEventoRepository(db)
    p_repo = SQLAlchemyPresencaRepository(db)
    u_repo = SQLAlchemyUsuarioRepository(db)
    uc = SorteioUseCase(e_repo, p_repo, u_repo)
    try:
        res = await uc.executar(2, 'NOTA_ADMIN')
        print(res)
    except Exception as e:
        print(f"Exception Type: {type(e)}")
        print(f"Exception Message: {e}")
    finally:
        db.close()

asyncio.run(run())
