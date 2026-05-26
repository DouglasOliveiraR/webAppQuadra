import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from datetime import date, time

from main import app
from api.db.database import get_db
from api.db.models import Base, UsuarioModel, EventoModel
from domain.usuarios.enums import PerfilUsuario, StatusUsuario
from domain.eventos.enums import StatusEvento
from core.security import get_password_hash

# --- Configuração do Banco de Dados de Teste (Em Memória) ---
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


# --- Fixtures e Configuração Inicial ---
@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Inserir Usuário (Admin)
    admin = UsuarioModel(
        nome="Admin Douglas",
        telefone="11999999999",
        senha_hash=get_password_hash("senha123"),
        perfil=PerfilUsuario.ADMIN,
        status=StatusUsuario.ATIVO,
        nota_admin=10.0,
        pontos_ranking=50
    )
    # Inserir Usuário (Comum)
    jogador = UsuarioModel(
        nome="Jogador Teste",
        telefone="11988888888",
        senha_hash=get_password_hash("senha123"),
        perfil=PerfilUsuario.MENSALISTA,
        status=StatusUsuario.ATIVO,
        nota_admin=8.0,
        pontos_ranking=20
    )
    # Inserir Evento com Presença e Votação Abertas (para facilitar o teste unificado)
    # Na vida real a votação só abre pós jogo, mas vamos deixar PRESENCA_ABERTA 
    # e mudar o status durante o teste de votação.
    evento = EventoModel(
        data_jogo=date(2026, 6, 1),
        hora_inicio=time(19, 0),
        hora_fim=time(21, 0),
        status_evento=StatusEvento.PRESENCA_ABERTA,
        flag_churrasco=True,
        valor_churrasco=50.0
    )
    
    db.add_all([admin, jogador, evento])
    db.commit()
    db.close()
    
    yield
    
    Base.metadata.drop_all(bind=engine)


# --- Testes de Integração ---

def test_login_sucesso():
    response = client.post("/api/auth/login", json={
        "telefone": "11999999999",
        "senha": "senha123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # Guardamos o token no teste para usar depois, embora no Pytest é melhor fixture
    pytest.admin_token = data["access_token"]


def test_login_falha():
    response = client.post("/api/auth/login", json={
        "telefone": "11999999999",
        "senha": "errada"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Telefone ou senha incorretos"


def test_atualizar_presenca_sucesso():
    # Precisamos do token do jogador comum
    res_login = client.post("/api/auth/login", json={"telefone": "11988888888", "senha": "senha123"})
    token = res_login.json()["access_token"]
    
    response = client.put("/api/eventos/1/presencas/me", 
        json={
            "status": "VOU",
            "posicao": "LINHA",
            "churrasco": True
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status_jogo"] == "VOU"
    assert data["posicao"] == "LINHA"
    assert data["vai_churrasco"] is True
    assert data["usuario_id"] == 2


def test_registrar_checkin_admin_sucesso():
    response = client.post("/api/eventos/1/checkin/2", 
        json={
            "chegou": True,
            "falta_justificada": False
        },
        headers={"Authorization": f"Bearer {pytest.admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["checkin_validado"] is True


def test_registrar_checkin_admin_falha_privilegio():
    res_login = client.post("/api/auth/login", json={"telefone": "11988888888", "senha": "senha123"})
    jogador_token = res_login.json()["access_token"]
    
    response = client.post("/api/eventos/1/checkin/2", 
        json={
            "chegou": True,
            "falta_justificada": False
        },
        headers={"Authorization": f"Bearer {jogador_token}"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Privilégios insuficientes"


def test_registrar_voto_falha_status_evento():
    # O status do evento é PRESENCA_ABERTA, a votação vai falhar
    res_login = client.post("/api/auth/login", json={"telefone": "11988888888", "senha": "senha123"})
    jogador_token = res_login.json()["access_token"]
    
    response = client.post("/api/eventos/1/votos", 
        json={
            "categoria": "BOLA_CHEIA",
            "candidato_id": 1
        },
        headers={"Authorization": f"Bearer {jogador_token}"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "A votação para este evento não está aberta"


def test_registrar_voto_sucesso():
    # Primeiro mudamos o status do evento no DB para VOTACAO_ABERTA
    db = TestingSessionLocal()
    evento = db.query(EventoModel).first()
    evento.status_evento = StatusEvento.VOTACAO_ABERTA
    db.commit()
    db.close()
    
    res_login = client.post("/api/auth/login", json={"telefone": "11988888888", "senha": "senha123"})
    jogador_token = res_login.json()["access_token"]
    
    response = client.post("/api/eventos/1/votos", 
        json={
            "categoria": "BOLA_CHEIA",
            "candidato_id": 1
        },
        headers={"Authorization": f"Bearer {jogador_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["categoria"] == "BOLA_CHEIA"
    assert data["candidato_id"] == 1


def test_registrar_voto_falha_voto_duplicado():
    # Primeiro assegura que o evento está como VOTACAO_ABERTA (se executado isolado)
    db = TestingSessionLocal()
    evento = db.query(EventoModel).first()
    if evento.status_evento != StatusEvento.VOTACAO_ABERTA:
        evento.status_evento = StatusEvento.VOTACAO_ABERTA
        db.commit()
    db.close()

    res_login = client.post("/api/auth/login", json={"telefone": "11988888888", "senha": "senha123"})
    jogador_token = res_login.json()["access_token"]
    
    # Fazemos um voto garantido antes, caso esse teste rode primeiro
    client.post("/api/eventos/1/votos",
        json={
            "categoria": "BOLA_CHEIA",
            "candidato_id": 1
        },
        headers={"Authorization": f"Bearer {jogador_token}"}
    )

    # O jogador 2 já votou no 1 na categoria BOLA_CHEIA no teste anterior
    response = client.post("/api/eventos/1/votos", 
        json={
            "categoria": "BOLA_CHEIA",
            "candidato_id": 1
        },
        headers={"Authorization": f"Bearer {jogador_token}"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Você já votou para a categoria BOLA_CHEIA neste evento"


def test_registrar_checkin_multiplos_idempotente():
    db = TestingSessionLocal()
    # Pega pontos iniciais do usuário 2
    usr2 = db.query(UsuarioModel).filter(UsuarioModel.id == 2).first()
    pontos_iniciais = usr2.pontos_ranking
    
    # 1. Primeiro check-in: Chegou = True
    response = client.post("/api/eventos/1/checkin/2", 
        json={"chegou": True, "falta_justificada": False},
        headers={"Authorization": f"Bearer {pytest.admin_token}"}
    )
    assert response.status_code == 200
    db.refresh(usr2)
    pontos_apos_checkin = usr2.pontos_ranking
    
    # Se ele já estava com checkin antes, os pontos mantêm, se não, sobe 1
    # Vamos verificar que fazer de novo o mesmo check-in não altera os pontos
    response = client.post("/api/eventos/1/checkin/2", 
        json={"chegou": True, "falta_justificada": False},
        headers={"Authorization": f"Bearer {pytest.admin_token}"}
    )
    assert response.status_code == 200
    db.refresh(usr2)
    assert usr2.pontos_ranking == pontos_apos_checkin  # Não deve somar repetido!
    
    # 2. Check-in: Marcar falta sem justificativa
    response = client.post("/api/eventos/1/checkin/2", 
        json={"chegou": False, "falta_justificada": False},
        headers={"Authorization": f"Bearer {pytest.admin_token}"}
    )
    assert response.status_code == 200
    db.refresh(usr2)
    pontos_apos_falta = usr2.pontos_ranking
    
    # De Chegou=True para Chegou=False com falta injustificada: perde presença (-1) e ganha penalidade (-1), totalizando -2
    assert pontos_apos_falta == pontos_apos_checkin - 2
    
    # Refazer a mesma marcação de falta não deve subtrair novamente
    response = client.post("/api/eventos/1/checkin/2", 
        json={"chegou": False, "falta_justificada": False},
        headers={"Authorization": f"Bearer {pytest.admin_token}"}
    )
    assert response.status_code == 200
    db.refresh(usr2)
    assert usr2.pontos_ranking == pontos_apos_falta  # Mantém
    db.close()
