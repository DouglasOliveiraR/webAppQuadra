from enum import Enum

class PerfilUsuario(str, Enum):
    ADMIN = "ADMIN"
    MENSALISTA = "MENSALISTA"
    AVULSO = "AVULSO"

class StatusUsuario(str, Enum):
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"
