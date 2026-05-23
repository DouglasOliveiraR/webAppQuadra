from pydantic import BaseModel

class NotaAdminRequest(BaseModel):
    nota: float
