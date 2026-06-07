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
    original_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db_e2e

    Base.metadata.create_all(bind=engine_e2e)
    db = TestingSessionLocalE2E()

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
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine_e2e)
    if original_override:
        app.dependency_overrides[get_db] = original_override
    else:
        app.dependency_overrides.pop(get_db, None)

@pytest.fixture
def test_client():
    return TestClient(app)

def test_upload_foto_perfil_valida(test_client):
    # Setup login
    login_response = test_client.post("/api/auth/login", json={
        "telefone": "11999999999",
        "senha": "senha123"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Send valid file
    content = b"\x89PNG\r\n\x1a\n" + b"rest_of_the_image"
    files = {"file": ("test.png", content, "image/png")}

    response = test_client.post("/api/usuarios/me/foto", headers=headers, files=files)
    assert response.status_code == 200
    assert response.json()["foto_url"] is not None

def test_upload_foto_perfil_invalida_magic_number(test_client):
    login_response = test_client.post("/api/auth/login", json={
        "telefone": "11999999999",
        "senha": "senha123"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    content = b"<!DOCTYPE html><html><body><script>alert(1)</script></body></html>"
    files = {"file": ("malicious.png", content, "image/png")}

    response = test_client.post("/api/usuarios/me/foto", headers=headers, files=files)
    assert response.status_code == 400
    assert "Apenas imagens válidas" in response.json()["detail"]
