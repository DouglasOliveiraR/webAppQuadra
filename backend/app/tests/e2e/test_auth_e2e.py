import pytest
from fastapi.testclient import TestClient

from main import app
from api.db.database import get_db
from api.db.models import Base, UsuarioModel
from domain.usuarios.enums import PerfilUsuario, StatusUsuario
from core.security import get_password_hash
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

# E2E Tests for Authentication Flow
# This covers the scenarios handled by the frontend useAuth hook

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine_e2e = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocalE2E = sessionmaker(autocommit=False, autoflush=False, bind=engine_e2e)

def override_get_db_e2e():
    try:
        db = TestingSessionLocalE2E()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module", autouse=True)
def setup_db_auth_e2e():
    # Salva o override original, se existir
    original_override = app.dependency_overrides.get(get_db)

    app.dependency_overrides[get_db] = override_get_db_e2e

    Base.metadata.create_all(bind=engine_e2e)
    db = TestingSessionLocalE2E()

    # Inserir Usuário (Ativo)
    usuario_ativo = UsuarioModel(
        nome="Usuario Ativo",
        telefone="11999999999",
        senha_hash=get_password_hash("senha123"),
        perfil=PerfilUsuario.MENSALISTA,
        status=StatusUsuario.ATIVO,
        nota_admin=10.0,
        pontos_ranking=50
    )
    db.add(usuario_ativo)

    # Inserir Usuário (Inativo)
    usuario_inativo = UsuarioModel(
        nome="Usuario Inativo",
        telefone="11988888888",
        senha_hash=get_password_hash("senha123"),
        perfil=PerfilUsuario.MENSALISTA,
        status=StatusUsuario.INATIVO,
        nota_admin=10.0,
        pontos_ranking=50
    )
    db.add(usuario_inativo)

    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine_e2e)
    # Restaura o override original ou limpa
    if original_override:
        app.dependency_overrides[get_db] = original_override
    else:
        app.dependency_overrides.pop(get_db, None)

@pytest.fixture
def test_client():
    # Provide a clean test client
    return TestClient(app)

# --- Testes E2E de Login (Simulando useAuth.js) ---

def test_login_sucesso(test_client):
    """Simula o 'happy path' do useAuth.js (login com sucesso)"""
    response = test_client.post("/api/auth/login", json={
        "telefone": "11999999999",
        "senha": "senha123"
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_falha_senha_incorreta(test_client):
    """Simula o erro de credenciais inválidas no useAuth.js"""
    response = test_client.post("/api/auth/login", json={
        "telefone": "11999999999",
        "senha": "senha_errada"
    })

    assert response.status_code == 401
    assert response.json()["detail"] == "Telefone ou senha incorretos"


def test_login_falha_telefone_nao_cadastrado(test_client):
    """Simula o erro de usuário não encontrado no useAuth.js"""
    response = test_client.post("/api/auth/login", json={
        "telefone": "11000000000",
        "senha": "senha123"
    })

    assert response.status_code == 401
    assert response.json()["detail"] == "Telefone ou senha incorretos"


def test_login_falha_usuario_inativo(test_client):
    """Simula o erro de usuário inativo no useAuth.js"""
    response = test_client.post("/api/auth/login", json={
        "telefone": "11988888888",
        "senha": "senha123"
    })

    assert response.status_code == 401
    assert response.json()["detail"] == "Usuário inativo"


def test_login_payload_invalido(test_client):
    """Simula o erro de validação (ex: campos ausentes) no useAuth.js"""
    response = test_client.post("/api/auth/login", json={
        "telefone": "11999999999"
        # Sem senha
    })

    assert response.status_code == 422 # Unprocessable Entity
