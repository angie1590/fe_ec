from pydantic import BaseModel, Field
from typing import List
from .empresa_modelo import Empresa
from .cliente_modelo import Cliente

class Impuesto(BaseModel):
    codigo: str = Field(..., description="Código del impuesto (IVA, ICE, etc.)")
    tarifa: float = Field(..., description="Tarifa del impuesto en porcentaje")
    valor: float = Field(..., description="Valor del impuesto calculado")

class ItemFactura(BaseModel):
    descripcion: str = Field(..., description="Descripción del producto o servicio")
    cantidad: int = Field(..., gt=0, description="Cantidad del producto")
    precio_unitario: float = Field(..., gt=0, description="Precio unitario del producto")
    subtotal: float = Field(..., gt=0, description="Subtotal sin impuestos")
    impuestos: List[Impuesto] = Field(..., description="Lista de impuestos aplicados al producto")

class Factura(BaseModel):
    empresa: Empresa = Field(..., description="Datos de la empresa emisora de la factura")
    cliente: Cliente = Field(..., description="Datos del cliente que recibe la factura")
    fecha_emision: str = Field(..., description="Fecha de emisión de la factura en formato YYYY-MM-DD")
    numero_factura: str = Field(..., description="Número de la factura")
    items: List[ItemFactura] = Field(..., description="Lista de productos o servicios")
    total: float = Field(..., gt=0, description="Total de la factura con impuestos")
