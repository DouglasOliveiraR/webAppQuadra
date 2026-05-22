from enum import Enum

class StatusJogo(str, Enum):
    PENDENTE = "PENDENTE"
    VOU = "VOU"
    NAO_VOU = "NAO_VOU"

class Posicao(str, Enum):
    LINHA = "LINHA"
    GOL = "GOL"
