import os
import tempfile
import unittest
from pathlib import Path

from lxml import etree

from fe_ec.utils.manejador_xml import ManejadorXML


def _build_factura_payload() -> dict:
    clave_generada = "1404202501010481595600110010010000000241234567817"
    return {
        "infoTributaria": {
            "ambiente": "1",
            "tipoEmision": "1",
            "razonSocial": "PRUEBAS SERVICIO DE RENTAS INTERNA",
            "nombreComercial": "MiComercio",
            "ruc": "0104815956001",
            "claveAcceso": clave_generada,
            "codDoc": "01",
            "estab": "001",
            "ptoEmi": "001",
            "secuencial": "000000024",
            "dirMatriz": "Av. Principal 123",
        },
        "infoFactura": {
            "fechaEmision": "14/04/2025",
            "dirEstablecimiento": "Av. Secundaria 456",
            "obligadoContabilidad": "NO",
            "tipoIdentificacionComprador": "04",
            "razonSocialComprador": "PRUEBAS SERVICIO DE RENTAS INTERNA",
            "identificacionComprador": "0195125988001",
            "direccionComprador": "Guapondelig",
            "totalSinImpuestos": "100.00",
            "totalDescuento": "0.00",
            "totalConImpuestos": {
                "totalImpuesto": [
                    {
                        "codigo": "2",
                        "codigoPorcentaje": "4",
                        "baseImponible": "100.00",
                        "valor": "15.00",
                    }
                ]
            },
            "propina": "0.00",
            "importeTotal": "115.00",
            "moneda": "DOLAR",
            "pagos": [
                {
                    "formaPago": "01",
                    "total": "115.00",
                    "plazo": "0",
                    "unidadTiempo": "DIAS",
                }
            ],
        },
        "detalles": [
            {
                "codigoPrincipal": "P001",
                "descripcion": "Producto de prueba",
                "cantidad": "1.00",
                "precioUnitario": "100.00",
                "descuento": "0.00",
                "precioTotalSinImpuesto": "100.00",
                "impuestos": [
                    {
                        "codigo": "2",
                        "codigoPorcentaje": "4",
                        "tarifa": "15.00",
                        "baseImponible": "100.00",
                        "valor": "15.00",
                    }
                ],
            }
        ],
        "infoAdicional": {
            "campoAdicional": [
                {"nombre": "email", "valor": "cliente@ejemplo.com"},
                {"nombre": "telefono", "valor": "0999999999"},
            ]
        },
    }


def _smoke_test_requirements() -> tuple[bool, str, str]:
    p12_path = os.getenv("FEEC_P12_PATH", "firma.p12")
    p12_password = os.getenv("FEEC_P12_PASSWORD", "")
    can_run = bool(p12_password) and Path(p12_path).exists()
    return can_run, p12_path, p12_password


@unittest.skipUnless(
    _smoke_test_requirements()[0],
    "Define FEEC_P12_PASSWORD y asegura FEEC_P12_PATH/firma.p12 para ejecutar el smoke test.",
)
class FirmaElectronicaSmokeTests(unittest.TestCase):
    def test_firma_end_to_end_genera_signature(self):
        _, p12_path, p12_password = _smoke_test_requirements()
        payload = _build_factura_payload()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "fact_firmado.xml"
            manejador = ManejadorXML(p12_path=p12_path, p12_password=p12_password)

            signed_path = manejador.firmar_y_guardar_xml(payload, output_path=str(output_path))

            self.assertEqual(signed_path, str(output_path))
            self.assertTrue(output_path.exists())

            tree = etree.parse(str(output_path))
            ns = {"ds": "http://www.w3.org/2000/09/xmldsig#"}
            signature = tree.find(".//ds:Signature", namespaces=ns)
            self.assertIsNotNone(signature)
