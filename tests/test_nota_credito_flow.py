import tempfile
import unittest
from pathlib import Path

from lxml import etree

from fe_ec.utils.generador_clave_acceso import GeneradorClaveAcceso
from fe_ec.utils.manejador_xml import ManejadorXML
from tests.test_nota_credito_builder import _build_request


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
        Path(output_path).write_text(
            Path(xml_path).read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        return output_path


class NotaCreditoFlowTests(unittest.TestCase):
    def test_generador_clave_acceso_soporta_coddoc_04(self):
        clave = GeneradorClaveAcceso.generar(
            fecha_emision="19/03/2026",
            tipo_comprobante="04",
            ruc="0103523908001",
            tipo_ambiente="1",
            serie="001001",
            secuencial="000000123",
            tipo_emision="1",
        )

        self.assertEqual(len(clave), 49)
        self.assertTrue(clave.startswith("1903202604"))

    def test_nota_credito_reutiliza_flujo_de_firma_y_validacion(self):
        request = _build_request()
        payload = request.to_payload(
            clave_acceso="1903202604010352390800110010010000001231234567819",
            ambiente="1",
        )
        firmador = DummyFirmador()
        manejador = ManejadorXML(
            document_type="nota_credito",
            firmador=firmador,
            p12_path="firma.p12",
            p12_password="dummy-password",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "nota_credito_firmada.xml"
            signed_path = manejador.firmar_y_guardar_xml(
                payload,
                output_path=str(output_path),
            )

            self.assertEqual(signed_path, str(output_path))
            self.assertEqual(len(firmador.calls), 1)
            self.assertTrue(output_path.exists())
            self.assertEqual(etree.parse(str(output_path)).getroot().tag, "notaCredito")


if __name__ == "__main__":
    unittest.main()
