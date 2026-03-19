import tempfile
import unittest
from pathlib import Path

from lxml import etree

from fe_ec.utils.generador_clave_acceso import GeneradorClaveAcceso
from fe_ec.utils.manejador_xml import ManejadorXML
from tests.fixtures_retencion import build_retencion_payload


class DummyFirmador:
    def __init__(self):
        self.calls = []

    def firmar_xml(self, xml_path: str, output_path: str, p12_path: str, p12_password: str):
        self.calls.append(
            {
                "xml_path": xml_path,
                "output_path": output_path,
                "p12_path": p12_path,
                "p12_password": p12_password,
            }
        )
        Path(output_path).write_text(Path(xml_path).read_text(encoding="utf-8"), encoding="utf-8")
        return output_path


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
    }


class RetencionFlowTests(unittest.TestCase):
    def test_generador_clave_acceso_soporta_coddoc_07(self):
        clave = GeneradorClaveAcceso.generar(
            fecha_emision="13/03/2026",
            tipo_comprobante="07",
            ruc="1790012345001",
            tipo_ambiente="1",
            serie="001001",
            secuencial="000000123",
            tipo_emision="1",
        )

        self.assertEqual(len(clave), 49)
        self.assertTrue(clave.startswith("1303202607"))

    def test_retencion_reutiliza_flujo_de_firma_y_validacion(self):
        clave = GeneradorClaveAcceso.generar(
            fecha_emision="13/03/2026",
            tipo_comprobante="07",
            ruc="1790012345001",
            tipo_ambiente="1",
            serie="001001",
            secuencial="000000123",
            tipo_emision="1",
        )
        payload = build_retencion_payload(clave)
        firmador = DummyFirmador()
        manejador = ManejadorXML(
            document_type="retencion",
            firmador=firmador,
            p12_path="firma.p12",
            p12_password="dummy-password",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "retencion_firmada.xml"
            signed_path = manejador.firmar_y_guardar_xml(payload, output_path=str(output_path))

            self.assertEqual(signed_path, str(output_path))
            self.assertEqual(len(firmador.calls), 1)
            self.assertTrue(output_path.exists())
            self.assertEqual(etree.parse(str(output_path)).getroot().tag, "comprobanteRetencion")

    def test_factura_permanece_como_default_compatible(self):
        manejador = ManejadorXML()
        xml_bytes = manejador.dict_a_xml_string(_build_factura_payload(), as_bytes=True)
        root = etree.fromstring(xml_bytes)

        self.assertEqual(root.tag, "factura")
        self.assertEqual(root.get("version"), "2.0.0")

    def test_rechaza_coddoc_inconsistente_con_document_type(self):
        payload = _build_factura_payload()
        manejador = ManejadorXML(document_type="retencion")

        with self.assertRaisesRegex(ValueError, "se esperaba codDoc 07"):
            manejador.dict_a_xml_string(payload)
