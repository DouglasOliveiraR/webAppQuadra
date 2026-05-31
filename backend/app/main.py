import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.db.database import engine
from api.db.models import Base
from core.config import settings

from api.v1 import auth, eventos, ranking, financeiro, usuarios, notas

# Cria as tabelas do banco (Apenas para MVP SQLite, em prod usar Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para o Pelada FC Manager",
    version="1.0.0"
)

from fastapi.staticfiles import StaticFiles
import os

static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(os.path.join(static_dir, "fotos"), exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra os Routers
app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(eventos.router)
app.include_router(ranking.router)
app.include_router(financeiro.router)
app.include_router(notas.router)

from fastapi.responses import FileResponse, JSONResponse
from fastapi import Request

logger = logging.getLogger(__name__)

# Handler global para Exceptions não tratadas (Prevenção de vazamento de stack traces HTTP 500)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erro interno não tratado na rota {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno no servidor"}
    )

# Servir o Frontend React compilado em produção/túnel
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))

if os.path.exists(frontend_dist):
    # Serve os arquivos da pasta assets de forma estática
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    # Handler customizado para erro 404 (Not Found)
    @app.exception_handler(404)
    async def custom_404_handler(request: Request, exc: Exception):
        path = request.url.path
        
        # Se for uma rota de API real que não existe, retorna 404 JSON padrão
        if path.startswith(("/api", "/static", "/docs", "/redoc", "/openapi.json")):
            return JSONResponse(
                status_code=404,
                content={"detail": "Not Found"}
            )
            
        # Remove a barra inicial para bater com o caminho do arquivo no dist
        relative_path = path.lstrip("/")
        file_path = os.path.abspath(os.path.join(frontend_dist, relative_path))
        
        # Verifica se o arquivo resolvido está dentro de frontend_dist para evitar Path Traversal
        if os.path.commonpath([frontend_dist, file_path]) != frontend_dist:
            return JSONResponse(
                status_code=404,
                content={"detail": "Not Found"}
            )

        # Se for um arquivo estático existente no dist (ex: manifest.json, favicon.svg), serve ele
        if relative_path and os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
            
        # Caso contrário (subrotas do React Router como /login, /ranking), serve o index.html
        index_path = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
            
        return JSONResponse(
            status_code=404,
            content={"detail": "Not Found"}
        )
else:
    @app.get("/")
    def read_root():
        return {"message": f"Bem-vindo ao {settings.PROJECT_NAME} (Frontend não compilado)"}
