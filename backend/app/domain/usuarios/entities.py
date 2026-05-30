from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from domain.usuarios.enums import PerfilUsuario, StatusUsuario

@dataclass
class UsuarioRanking:
    id: int
    nome: str
    pontos_ranking: int
    nota_admin: int
    nota_galera_media: float
    foto_url: Optional[str]
    premios: list

@dataclass
class Usuario:
    id: Optional[int]
    nome: str
    telefone: str
    senha_hash: str
    perfil: PerfilUsuario
    status: StatusUsuario
    nota_admin: int
    nota_galera_media: float
    pontos_ranking: int
    foto_url: Optional[str] = None
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None
