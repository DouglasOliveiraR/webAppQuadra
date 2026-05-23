import asyncio
from api.db.database import SessionLocal
from api.db.repositories.usuario_repo import SQLAlchemyUsuarioRepository
from application.auth.use_cases import LoginUseCase
from core.exceptions import CredenciaisInvalidasError

async def test_login():
    db = SessionLocal()
    repo = SQLAlchemyUsuarioRepository(db)
    use_case = LoginUseCase(repo)
    
    try:
        token = await use_case.executar("11999999999", "admin123")
        print("LOGIN SUCESSO! Token:", token)
    except Exception as e:
        print("ERRO:", type(e), str(e))
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_login())
