from dataclasses import dataclass
from typing import Optional
from domain.usuarios.enums import PerfilUsuario, StatusUsuario

@dataclass
class Usuario:
    id: Optional[int]
    nome: str
    telefone: str
    senha_hash: str
    perfil: PerfilUsuario
    status: StatusUsuario
    nota_admin: float
    nota_galera_media: float
    pontos_ranking: int
