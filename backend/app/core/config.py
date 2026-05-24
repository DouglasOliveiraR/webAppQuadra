import uuid
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Pelada FC Manager"
    DATABASE_URL: str = "sqlite:///./pelada.db"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

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

