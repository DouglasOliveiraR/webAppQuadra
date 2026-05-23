from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt

from api.db.database import get_db
from core.config import settings
from api.db.repositories.usuario_repo import SQLAlchemyUsuarioRepository
from api.db.repositories.evento_repo import SQLAlchemyEventoRepository
from api.db.repositories.presenca_repo import SQLAlchemyPresencaRepository
from api.db.repositories.voto_repo import SQLAlchemyVotoRepository
from api.db.repositories.financeiro_repo import SQLAlchemyFinanceiroRepository

from application.auth.use_cases import LoginUseCase
from application.presencas.use_cases import AtualizarPresencaUseCase, CheckinUseCase
from application.votos.use_cases import RegistrarVotoUseCase, EncerrarVotacaoUseCase
from application.ranking.use_cases import ListarRankingUseCase
from application.financeiro.use_cases import ListarFinanceiroUseCase, BaixarPagamentoUseCase
from domain.usuarios.entities import Usuario

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Usuario:
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        usuario_id: str = payload.get("sub")
        if usuario_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
        
    repo = SQLAlchemyUsuarioRepository(db)
    # Impacto: remove o uso de asyncio.run que bloqueava o event loop do FastAPI, melhorando a performance
    usuario = await repo.buscar_por_id(int(usuario_id))
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado")
    return usuario

async def get_admin_user(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    if current_user.perfil.value != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Privilégios insuficientes")
    return current_user

# --- DI para Repositórios ---
def get_usuario_repo(db: Session = Depends(get_db)) -> SQLAlchemyUsuarioRepository:
    return SQLAlchemyUsuarioRepository(db)

def get_evento_repo(db: Session = Depends(get_db)) -> SQLAlchemyEventoRepository:
    return SQLAlchemyEventoRepository(db)

def get_presenca_repo(db: Session = Depends(get_db)) -> SQLAlchemyPresencaRepository:
    return SQLAlchemyPresencaRepository(db)

def get_voto_repo(db: Session = Depends(get_db)) -> SQLAlchemyVotoRepository:
    return SQLAlchemyVotoRepository(db)

# --- DI para Use Cases ---
def get_login_use_case(repo: SQLAlchemyUsuarioRepository = Depends(get_usuario_repo)) -> LoginUseCase:
    return LoginUseCase(repo)

def get_atualizar_presenca_use_case(
    presenca_repo: SQLAlchemyPresencaRepository = Depends(get_presenca_repo),
    evento_repo: SQLAlchemyEventoRepository = Depends(get_evento_repo)
) -> AtualizarPresencaUseCase:
    return AtualizarPresencaUseCase(presenca_repo, evento_repo)

def get_checkin_use_case(
    repo: SQLAlchemyPresencaRepository = Depends(get_presenca_repo),
    usuario_repo: SQLAlchemyUsuarioRepository = Depends(get_usuario_repo)
) -> CheckinUseCase:
    return CheckinUseCase(repo, usuario_repo)

def get_encerrar_votacao_use_case(db: Session = Depends(get_db)):
    evento_repo = SQLAlchemyEventoRepository(db)
    voto_repo = SQLAlchemyVotoRepository(db)
    usuario_repo = SQLAlchemyUsuarioRepository(db)
    return EncerrarVotacaoUseCase(evento_repo, voto_repo, usuario_repo)

def get_registrar_voto_use_case(db: Session = Depends(get_db)):
    voto_repo = SQLAlchemyVotoRepository(db)
    evento_repo = SQLAlchemyEventoRepository(db)
    return RegistrarVotoUseCase(voto_repo, evento_repo)

def get_listar_ranking_use_case(db: Session = Depends(get_db)):
    repo = SQLAlchemyUsuarioRepository(db)
    return ListarRankingUseCase(repo)

def get_listar_financeiro_use_case(db: Session = Depends(get_db)):
    repo = SQLAlchemyFinanceiroRepository(db)
    return ListarFinanceiroUseCase(repo)

def get_baixar_pagamento_use_case(db: Session = Depends(get_db)):
    repo = SQLAlchemyFinanceiroRepository(db)
    return BaixarPagamentoUseCase(repo)
