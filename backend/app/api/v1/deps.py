from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt

from api.db.database import get_db
from core.config import settings, SERVER_SESSION_ID
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
from application.financeiro.listar_todos_financeiro_use_case import ListarTodosFinanceiroUseCase
from application.eventos.use_cases import ObterEventoUseCase, CriarEventoUseCase, ListarEventosUseCase
from application.eventos.iniciar_votacao_use_case import IniciarVotacaoUseCase
from application.eventos.cancelar_votacao_use_case import CancelarVotacaoUseCase
from application.eventos.sorteio_use_case import SorteioUseCase
from application.eventos.atualizar_churrasco_use_case import AtualizarChurrascoUseCase
from application.eventos.atualizar_chave_pix_use_case import AtualizarChavePixUseCase
from application.eventos.atualizar_mensalidade_use_case import AtualizarMensalidadeUseCase
from application.eventos.atualizar_custo_quadra_use_case import AtualizarCustoQuadraUseCase
from application.eventos.cancelar_evento_use_case import CancelarEventoUseCase
from application.eventos.obter_ultimo_resultado_use_case import ObterUltimoResultadoUseCase
from application.usuarios.atualizar_nota_admin_use_case import AtualizarNotaAdminUseCase
from application.usuarios.listar_usuarios_use_case import ListarUsuariosUseCase
from application.usuarios.criar_usuario_use_case import CriarUsuarioUseCase
from application.usuarios.atualizar_usuario_use_case import AtualizarUsuarioUseCase
from application.usuarios.alterar_senha_use_case import AlterarSenhaUseCase
from application.usuarios.atualizar_foto_perfil_use_case import AtualizarFotoPerfilUseCase
from application.usuarios.deletar_usuario_use_case import DeletarUsuarioUseCase
from domain.usuarios.entities import Usuario

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Usuario:
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        usuario_id: str = payload.get("sub")
        token_sid: str = payload.get("sid")
        if usuario_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
        # Rejeita tokens emitidos em sessões anteriores do servidor
        if token_sid != SERVER_SESSION_ID:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessão expirada. Faça login novamente.")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
        
    repo = SQLAlchemyUsuarioRepository(db)
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
    from api.db.repositories.premio_repo import SQLAlchemyPremioRepository
    evento_repo = SQLAlchemyEventoRepository(db)
    voto_repo = SQLAlchemyVotoRepository(db)
    usuario_repo = SQLAlchemyUsuarioRepository(db)
    premio_repo = SQLAlchemyPremioRepository(db)
    return EncerrarVotacaoUseCase(evento_repo, voto_repo, usuario_repo, premio_repo)

def get_registrar_voto_use_case(db: Session = Depends(get_db)):
    voto_repo = SQLAlchemyVotoRepository(db)
    evento_repo = SQLAlchemyEventoRepository(db)
    usuario_repo = SQLAlchemyUsuarioRepository(db)
    return RegistrarVotoUseCase(voto_repo, evento_repo, usuario_repo)

def get_listar_ranking_use_case(db: Session = Depends(get_db)):
    from api.db.repositories.premio_repo import SQLAlchemyPremioRepository
    repo = SQLAlchemyUsuarioRepository(db)
    premio_repo = SQLAlchemyPremioRepository(db)
    return ListarRankingUseCase(repo, premio_repo)

def get_listar_financeiro_use_case(db: Session = Depends(get_db)):
    repo = SQLAlchemyFinanceiroRepository(db)
    usuario_repo = SQLAlchemyUsuarioRepository(db)
    evento_repo = SQLAlchemyEventoRepository(db)
    return ListarFinanceiroUseCase(repo, usuario_repo, evento_repo)

def get_listar_todos_financeiro_use_case(db: Session = Depends(get_db)) -> ListarTodosFinanceiroUseCase:
    financeiro_repo = SQLAlchemyFinanceiroRepository(db)
    usuario_repo = SQLAlchemyUsuarioRepository(db)
    evento_repo = SQLAlchemyEventoRepository(db)
    presenca_repo = SQLAlchemyPresencaRepository(db)
    return ListarTodosFinanceiroUseCase(financeiro_repo, usuario_repo, evento_repo, presenca_repo)

def get_baixar_pagamento_use_case(db: Session = Depends(get_db)):
    repo = SQLAlchemyFinanceiroRepository(db)
    return BaixarPagamentoUseCase(repo)

def get_obter_evento_use_case(db: Session = Depends(get_db)) -> ObterEventoUseCase:
    from api.db.repositories.nota_repo import SQLAlchemyNotaRepository
    evento_repo = SQLAlchemyEventoRepository(db)
    presenca_repo = SQLAlchemyPresencaRepository(db)
    usuario_repo = SQLAlchemyUsuarioRepository(db)
    voto_repo = SQLAlchemyVotoRepository(db)
    nota_repo = SQLAlchemyNotaRepository(db)
    return ObterEventoUseCase(evento_repo, presenca_repo, usuario_repo, voto_repo, nota_repo)

def get_disparar_notificacao_use_case(db: Session = Depends(get_db)):
    from application.notificacoes.disparar_notificacao import DispararNotificacaoUseCase
    from api.db.repositories.push_subscription_repo import SQLAlchemyPushSubscriptionRepository
    repo = SQLAlchemyPushSubscriptionRepository(db)
    return DispararNotificacaoUseCase(repo)

def get_criar_evento_use_case(db: Session = Depends(get_db), disparar_uc=Depends(get_disparar_notificacao_use_case)) -> CriarEventoUseCase:
    evento_repo = SQLAlchemyEventoRepository(db)
    financeiro_repo = SQLAlchemyFinanceiroRepository(db)
    return CriarEventoUseCase(evento_repo, financeiro_repo, disparar_notificacao_uc=disparar_uc)

def get_listar_eventos_use_case(db: Session = Depends(get_db)) -> ListarEventosUseCase:
    evento_repo = SQLAlchemyEventoRepository(db)
    return ListarEventosUseCase(evento_repo)

def get_iniciar_votacao_use_case(db: Session = Depends(get_db), disparar_uc=Depends(get_disparar_notificacao_use_case)) -> IniciarVotacaoUseCase:
    evento_repo = SQLAlchemyEventoRepository(db)
    return IniciarVotacaoUseCase(evento_repo, disparar_notificacao_uc=disparar_uc)

def get_cancelar_votacao_use_case(db: Session = Depends(get_db)) -> CancelarVotacaoUseCase:
    evento_repo = SQLAlchemyEventoRepository(db)
    voto_repo = SQLAlchemyVotoRepository(db)
    return CancelarVotacaoUseCase(evento_repo, voto_repo)

def get_sorteio_use_case(db: Session = Depends(get_db)) -> SorteioUseCase:
    evento_repo = SQLAlchemyEventoRepository(db)
    presenca_repo = SQLAlchemyPresencaRepository(db)
    usuario_repo = SQLAlchemyUsuarioRepository(db)
    return SorteioUseCase(evento_repo, presenca_repo, usuario_repo)

def get_atualizar_churrasco_use_case(db: Session = Depends(get_db), disparar_uc=Depends(get_disparar_notificacao_use_case)) -> AtualizarChurrascoUseCase:
    evento_repo = SQLAlchemyEventoRepository(db)
    usuario_repo = SQLAlchemyUsuarioRepository(db)
    return AtualizarChurrascoUseCase(evento_repo, usuario_repo, disparar_notificacao_uc=disparar_uc)

def get_atualizar_chave_pix_use_case(db: Session = Depends(get_db)) -> AtualizarChavePixUseCase:
    evento_repo = SQLAlchemyEventoRepository(db)
    return AtualizarChavePixUseCase(evento_repo)

def get_atualizar_mensalidade_use_case(db: Session = Depends(get_db)) -> AtualizarMensalidadeUseCase:
    evento_repo = SQLAlchemyEventoRepository(db)
    financeiro_repo = SQLAlchemyFinanceiroRepository(db)
    return AtualizarMensalidadeUseCase(evento_repo, financeiro_repo)

def get_atualizar_custo_quadra_use_case(db: Session = Depends(get_db)) -> AtualizarCustoQuadraUseCase:
    evento_repo = SQLAlchemyEventoRepository(db)
    return AtualizarCustoQuadraUseCase(evento_repo)

def get_cancelar_evento_use_case(db: Session = Depends(get_db)) -> CancelarEventoUseCase:
    evento_repo = SQLAlchemyEventoRepository(db)
    return CancelarEventoUseCase(evento_repo)

def get_atualizar_nota_admin_use_case(db: Session = Depends(get_db)) -> AtualizarNotaAdminUseCase:
    usuario_repo = SQLAlchemyUsuarioRepository(db)
    return AtualizarNotaAdminUseCase(usuario_repo)

def get_listar_usuarios_use_case(db: Session = Depends(get_db)) -> ListarUsuariosUseCase:
    usuario_repo = SQLAlchemyUsuarioRepository(db)
    return ListarUsuariosUseCase(usuario_repo)

def get_criar_usuario_use_case(db: Session = Depends(get_db)) -> CriarUsuarioUseCase:
    usuario_repo = SQLAlchemyUsuarioRepository(db)
    evento_repo = SQLAlchemyEventoRepository(db)
    presenca_repo = SQLAlchemyPresencaRepository(db)
    return CriarUsuarioUseCase(usuario_repo, evento_repo, presenca_repo)

def get_atualizar_usuario_use_case(db: Session = Depends(get_db)) -> AtualizarUsuarioUseCase:
    usuario_repo = SQLAlchemyUsuarioRepository(db)
    return AtualizarUsuarioUseCase(usuario_repo)

def get_alterar_senha_use_case(db: Session = Depends(get_db)) -> AlterarSenhaUseCase:
    usuario_repo = SQLAlchemyUsuarioRepository(db)
    return AlterarSenhaUseCase(usuario_repo)

def get_atualizar_foto_perfil_use_case(db: Session = Depends(get_db)) -> AtualizarFotoPerfilUseCase:
    usuario_repo = SQLAlchemyUsuarioRepository(db)
    return AtualizarFotoPerfilUseCase(usuario_repo)

def get_obter_ultimo_resultado_use_case(db: Session = Depends(get_db)) -> ObterUltimoResultadoUseCase:
    evento_repo = SQLAlchemyEventoRepository(db)
    voto_repo = SQLAlchemyVotoRepository(db)
    usuario_repo = SQLAlchemyUsuarioRepository(db)
    return ObterUltimoResultadoUseCase(evento_repo, voto_repo, usuario_repo)

def get_deletar_usuario_use_case(db: Session = Depends(get_db)) -> DeletarUsuarioUseCase:
    usuario_repo = SQLAlchemyUsuarioRepository(db)
    financeiro_repo = SQLAlchemyFinanceiroRepository(db)
    presenca_repo = SQLAlchemyPresencaRepository(db)
    evento_repo = SQLAlchemyEventoRepository(db)
    return DeletarUsuarioUseCase(usuario_repo, presenca_repo, financeiro_repo, evento_repo)

def get_obter_transparencia_use_case(db: Session = Depends(get_db)):
    from application.financeiro.obter_transparencia_use_case import ObterTransparenciaUseCase
    financeiro_repo = SQLAlchemyFinanceiroRepository(db)
    evento_repo = SQLAlchemyEventoRepository(db)
    return ObterTransparenciaUseCase(financeiro_repo, evento_repo)

def get_abrir_presenca_use_case(db: Session = Depends(get_db), disparar_uc=Depends(get_disparar_notificacao_use_case)):
    from application.eventos.abrir_presenca_use_case import AbrirPresencaUseCase
    evento_repo = SQLAlchemyEventoRepository(db)
    return AbrirPresencaUseCase(evento_repo, disparar_notificacao_uc=disparar_uc)
