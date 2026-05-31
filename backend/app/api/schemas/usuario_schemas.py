from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from domain.usuarios.enums import PerfilUsuario, StatusUsuario

class NotaAdminRequest(BaseModel):
    nota: int

class UsuarioCreateRequest(BaseModel):
    nome: str = Field(..., max_length=100)
    telefone: str = Field(..., max_length=100)  # Allowed up to 100 for AVULSO fallback logic
    perfil: PerfilUsuario = PerfilUsuario.AVULSO
    nota_admin: int = Field(5, ge=0, le=10)
    senha: Optional[str] = Field(None, max_length=128)

class UsuarioUpdateRequest(BaseModel):
    nome: str = Field(..., max_length=100)
    telefone: str = Field(..., max_length=100)
    perfil: PerfilUsuario
    status: StatusUsuario
    nota_admin: int = Field(..., ge=0, le=10)

class AlterarSenhaRequest(BaseModel):
    senha_atual: str = Field(..., max_length=128)
    nova_senha: str = Field(..., max_length=128)

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
