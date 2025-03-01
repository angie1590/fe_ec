from pydantic import BaseModel, Field
from typing import Optional

class Cliente(BaseModel):
    identificacion: str = Field(..., min_length=10, max_length=13, description="Cédula o RUC del cliente")
    nombre: str = Field(..., description="Nombre o razón social del cliente")
    direccion: Optional[str] = Field(None, description="Dirección del cliente")
