from pydantic import BaseModel, Field
from typing import List, Optional

class Empresa(BaseModel):
    ruc: str = Field(..., min_length=13, max_length=13, description="RUC de la empresa")
    razon_social: str = Field(..., description="Razón social de la empresa")
    direccion: str = Field(..., description="Dirección de la empresa")
    es_matriz: bool = Field(..., description="Indica si la empresa es matriz o sucursal")
    sucursales: Optional[List[str]] = Field(None, description="Lista de sucursales si la empresa tiene")
