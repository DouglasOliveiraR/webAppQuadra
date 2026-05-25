from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from domain.usuarios.enums import PerfilUsuario, StatusUsuario

class NotaAdminRequest(BaseModel):
    nota: int

class UsuarioCreateRequest(BaseModel):
    nome: str
    telefone: str
    perfil: PerfilUsuario = PerfilUsuario.AVULSO
    nota_admin: int = 5

class UsuarioUpdateRequest(BaseModel):
    nome: str
    telefone: str
    perfil: PerfilUsuario
    status: StatusUsuario
    nota_admin: int

class AlterarSenhaRequest(BaseModel):
    senha_atual: str
    nova_senha: str

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
