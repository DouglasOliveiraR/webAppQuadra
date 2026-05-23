from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Pelada FC Manager"
    DATABASE_URL: str = "sqlite:///./pelada.db"
    SECRET_KEY: str = "super_secret_key_mock_for_mvp"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000", "http://localhost:8000"]

settings = Settings()
