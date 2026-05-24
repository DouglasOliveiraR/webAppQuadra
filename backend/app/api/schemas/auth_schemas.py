from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    telefone: str = Field(..., min_length=10, max_length=15, pattern=r'^\d+$', description="Apenas números")
    senha: str = Field(..., min_length=6, max_length=50, description="Senha do usuário")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
