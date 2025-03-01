import pytest
from fe_ec.utils.generador_clave_acceso import GeneradorClaveAcceso
from fe_ec.utils.manejador_xml import ManejadorXML

# Prueba para GeneradorClaveAcceso
def test_generar_clave_acceso():
    clave = GeneradorClaveAcceso.generar(
        tipo_comprobante="01",
        fecha_emision="20250301",
        ruc="1234567890123",
        ambiente="1",
        serie="001001",
        secuencial="000000001",
        codigo_numerico="12345678",
        tipo_emision="1"
    )
    assert len(clave) == 49
    assert clave.isdigit()  # La clave de acceso debe ser numérica

# Prueba para el cálculo del dígito verificador
def test_calculo_digito_verificador():
    clave_base = "202503010112345678901231001001000000001123456781"
    digito = GeneradorClaveAcceso._calcular_digito_verificador(clave_base)
    assert digito.isdigit()
    assert len(digito) == 1

# Prueba para la generación de XML con datos de productos con IVA, sin IVA y con ICE
def test_crear_xml():
    datos_factura = {
        "infoTributaria": {
            "razonSocial": "Mi Empresa S.A.",
            "ruc": "1234567890123",
            "claveAcceso": "12345678901234567890123456789012345678901234567"
        },
        "detalles": [
            {"descripcion": "Producto A", "cantidad": "1", "precioUnitario": "100.00", "subtotal": "100.00",
             "impuestos": [{"codigo": "2", "tarifa": "15", "valor": "15.00"}]},
            {"descripcion": "Producto B", "cantidad": "2", "precioUnitario": "50.00", "subtotal": "100.00",
             "impuestos": [{"codigo": "2", "tarifa": "0", "valor": "0.00"}]},
            {"descripcion": "Producto C", "cantidad": "3", "precioUnitario": "30.00", "subtotal": "90.00",
             "impuestos": [{"codigo": "3", "tarifa": "10", "valor": "9.00"}]},
            {"descripcion": "Producto D", "cantidad": "1", "precioUnitario": "200.00", "subtotal": "200.00",
             "impuestos": [{"codigo": "2", "tarifa": "15", "valor": "30.00"}, {"codigo": "3", "tarifa": "10", "valor": "20.00"}]}
        ]
    }
    xml_generado = ManejadorXML.crear_xml(datos_factura)
    assert xml_generado is not None
    assert "<factura>" in xml_generado
    assert "<infoTributaria>" in xml_generado
    assert "<detalles>" in xml_generado
    assert "<impuestos>" in xml_generado
    assert "<codigo>2</codigo>" in xml_generado  # IVA
    assert "<codigo>3</codigo>" in xml_generado  # ICE