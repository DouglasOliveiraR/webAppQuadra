from pydantic import BaseModel

class LoginRequest(BaseModel):
    telefone: str
    senha: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
