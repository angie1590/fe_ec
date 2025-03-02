import pytest

from fe_ec.core.firma_digital import FirmadorDigital

def test_firmar_xml():
    xml = "<factura>Factura de prueba</factura>"
    certificado_path = "/Users/andrea/Documents/Proyectos/fe_ec/firma.p12"
    clave_certificado = "Angie1590"

    # Simulación de firma
    firmado = FirmadorDigital.firmar_xml(xml, certificado_path, clave_certificado)
    assert "Firma:" in firmado