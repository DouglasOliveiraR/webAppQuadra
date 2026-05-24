from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.db.database import engine
from api.db.models import Base
from core.config import settings

from api.v1.auth import router as auth_router
from api.v1.eventos import router as eventos_router
from api.v1.usuarios import router as usuarios_router
from api.v1 import auth, eventos, ranking, financeiro, usuarios

# Cria as tabelas do banco (Apenas para MVP SQLite, em prod usar Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para o Pelada FC Manager",
    version="1.0.0"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra os Routers
app.include_router(auth_router)
app.include_router(eventos_router)
app.include_router(usuarios_router)
app.include_router(ranking.router)
app.include_router(financeiro.router)

@app.get("/")
def read_root():
    return {"message": f"Bem-vindo ao {settings.PROJECT_NAME}"}
