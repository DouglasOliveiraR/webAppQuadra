import uuid
import socket
from pydantic_settings import BaseSettings, SettingsConfigDict

def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

class Settings(BaseSettings):
    PROJECT_NAME: str = "Pelada FC Manager"
    DATABASE_URL: str = "sqlite:///./pelada.db"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    # [Security Fix] Reduzido para 24h para minimizar a janela de exposição de tokens roubados.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    @property
    def cors_origins(self) -> list[str]:
        origins = list(self.BACKEND_CORS_ORIGINS)
        local_ip = get_local_ip()
        if local_ip and local_ip != "127.0.0.1":
            origins.append(f"http://{local_ip}:5173")
            # Adiciona também a própria origem com IP para maior flexibilidade
            origins.append(f"http://{local_ip}:8000")
        return origins

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# ID único gerado a cada inicialização do servidor.
# Tokens JWT emitidos em sessões anteriores são invalidados automaticamente
# pois carregam um session_id diferente do atual.
SERVER_SESSION_ID: str = str(uuid.uuid4())


