import pytest
from src.fe_ec.models.empresa_modelo import Empresa
from src.fe_ec.models.cliente_modelo import Cliente
from src.fe_ec.models.factura_modelo import Factura, ItemFactura, Impuesto

# Prueba para el modelo Empresa
def test_empresa_modelo():
    empresa = Empresa(
        ruc="1234567890123",
        razon_social="Mi Empresa S.A.",
        direccion="Av. Principal 123",
        es_matriz=True,
        sucursales=["Sucursal 1", "Sucursal 2"]
    )
    assert empresa.ruc == "1234567890123"
    assert empresa.es_matriz is True
    assert len(empresa.sucursales) == 2

# Prueba para el modelo Cliente
def test_cliente_modelo():
    cliente = Cliente(
        identificacion="1104567890",
        nombre="Juan Pérez",
        direccion="Calle Secundaria 456"
    )
    assert cliente.identificacion == "1104567890"
    assert cliente.nombre == "Juan Pérez"

# Prueba para el modelo Factura con productos con IVA, sin IVA y con ICE
def test_factura_modelo():
    empresa = Empresa(
        ruc="1234567890123",
        razon_social="Mi Empresa S.A.",
        direccion="Av. Principal 123",
        es_matriz=True
    )
    cliente = Cliente(
        identificacion="1104567890",
        nombre="Juan Pérez",
        direccion="Calle Secundaria 456"
    )
    items = [
        ItemFactura(
            descripcion="Producto A",
            cantidad=1,
            precio_unitario=100.00,
            subtotal=100.00,
            impuestos=[Impuesto(codigo="2", tarifa=15, valor=15.00)]
        ),
        ItemFactura(
            descripcion="Producto B",
            cantidad=2,
            precio_unitario=50.00,
            subtotal=100.00,
            impuestos=[Impuesto(codigo="2", tarifa=0, valor=0.00)]
        ),
        ItemFactura(
            descripcion="Producto C",
            cantidad=3,
            precio_unitario=30.00,
            subtotal=90.00,
            impuestos=[Impuesto(codigo="3", tarifa=10, valor=9.00)]
        ),
        ItemFactura(
            descripcion="Producto D",
            cantidad=1,
            precio_unitario=200.00,
            subtotal=200.00,
            impuestos=[
                Impuesto(codigo="2", tarifa=15, valor=30.00),
                Impuesto(codigo="3", tarifa=10, valor=20.00)
            ]
        )
    ]
    factura = Factura(
        empresa=empresa,
        cliente=cliente,
        fecha_emision="2025-03-01",
        numero_factura="001-001-000000001",
        items=items,
        total=415.00
    )
    assert factura.empresa.ruc == "1234567890123"
    assert factura.cliente.nombre == "Juan Pérez"
    assert len(factura.items) == 4
    assert factura.total == 415.00