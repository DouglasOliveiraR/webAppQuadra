from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from domain.usuarios.enums import PerfilUsuario, StatusUsuario

class NotaAdminRequest(BaseModel):
    nota: int

class UsuarioCreateRequest(BaseModel):
    nome: str = Field(..., max_length=100)
    # [Security Fix] Added min_length and pattern validation to prevent injection or invalid formats.
    telefone: str = Field(..., min_length=8, max_length=100, pattern=r"^([\d\s\-\(\)\+]+|AVULSO_.*)$")  # Allowed up to 100 for AVULSO fallback logic
    perfil: PerfilUsuario = PerfilUsuario.AVULSO
    nota_admin: int = Field(5, ge=0, le=10)
    senha: Optional[str] = Field(None, min_length=6, max_length=128)

class UsuarioUpdateRequest(BaseModel):
    nome: str = Field(..., max_length=100)
    # [Security Fix] Added min_length and pattern validation.
    telefone: str = Field(..., min_length=8, max_length=100, pattern=r"^([\d\s\-\(\)\+]+|AVULSO_.*)$")
    perfil: PerfilUsuario
    status: StatusUsuario
    nota_admin: int = Field(..., ge=0, le=10)

class AlterarSenhaRequest(BaseModel):
    # [Security Fix] Enforce minimum password length.
    senha_atual: str = Field(..., min_length=6, max_length=128)
    nova_senha: str = Field(..., min_length=6, max_length=128)

class UsuarioResponse(BaseModel):
    id: int
    nome: str
    telefone: str
    perfil: PerfilUsuario
    status: StatusUsuario
    nota_admin: int
    nota_galera_media: float
    pontos_ranking: int
    foto_url: Optional[str] = None
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None

    class Config:
        from_attributes = True

class AdminEditUsuarioRequest(BaseModel):
    pontos_ranking: Optional[int] = None
    resetar_senha: Optional[bool] = False
