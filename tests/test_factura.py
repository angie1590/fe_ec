import pytest
from fe_ec.core.factura import FacturaElectronica
from fe_ec.models.factura_modelo import Factura, ItemFactura, Impuesto
from fe_ec.models.empresa_modelo import Empresa
from fe_ec.models.cliente_modelo import Cliente

# Datos de prueba
empresa_data = Empresa(
    ruc="1234567890123",
    razon_social="Mi Empresa S.A.",
    direccion="Av. Principal 123",
    es_matriz=True
)

cliente_data = Cliente(
    identificacion="1104567890",
    nombre="Juan Pérez",
    direccion="Calle Secundaria 456"
)

items_data = [
    ItemFactura(
        descripcion="Producto A",
        cantidad=1,
        precio_unitario=100.00,
        subtotal=100.00,
        impuestos=[Impuesto(codigo="2", tarifa=15, valor=15.00)]
    )
]

factura_data = Factura(
    empresa=empresa_data,
    cliente=cliente_data,
    fecha_emision="2025-03-01",
    numero_factura="001-001-000000001",
    items=items_data,
    total=115.00
)


# Pruebas para FacturaElectronica
def test_generar_clave_acceso():
    factura = FacturaElectronica(factura_data)
    clave = factura.generar_clave_acceso()
    assert len(clave) == 49  # Longitud esperada de la clave de acceso

def test_generar_xml():
    factura = FacturaElectronica(factura_data)
    xml = factura.generar_xml()
    assert "<factura>" in xml  # Verifica que se genera XML correctamente

def test_validar_factura():
    factura = FacturaElectronica(factura_data)
    assert factura.validar_factura() is True