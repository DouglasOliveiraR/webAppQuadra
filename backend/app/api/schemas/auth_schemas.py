from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    # Security: Telefone validation limits length and only accepts digits or formatting
    telefone: str = Field(..., max_length=20, pattern=r"^[\d\s\-\(\)\+]+$")
    # Security: Max length to prevent ReDoS or large payload attacks on bcrypt
    senha: str = Field(..., max_length=128)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
