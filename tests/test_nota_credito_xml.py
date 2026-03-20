import tempfile
import unittest
from pathlib import Path

from lxml import etree

from fe_ec.utils.manejador_xml import ManejadorXML
from tests.test_nota_credito_builder import _build_request


class NotaCreditoXMLTests(unittest.TestCase):
    def _build_payload(self) -> dict:
        request = _build_request()
        return request.to_payload(
            clave_acceso="1903202604010352390800110010010000001231234567819",
            ambiente="1",
        )

    def test_serializa_raiz_y_version_oficiales(self):
        manejador = ManejadorXML(document_type="nota_credito")

        xml_bytes = manejador.dict_a_xml_string(self._build_payload(), as_bytes=True)
        root = etree.fromstring(xml_bytes)

        self.assertEqual(root.tag, "notaCredito")
        self.assertEqual(root.get("id"), "comprobante")
        self.assertEqual(root.get("version"), "1.1.0")
        self.assertEqual(root.findtext("./infoNotaCredito/motivo"), "DEVOLUCION PARCIAL")

    def test_serializa_detalles_adicionales_como_atributos(self):
        manejador = ManejadorXML(document_type="nota_credito")

        xml_bytes = manejador.dict_a_xml_string(self._build_payload(), as_bytes=True)
        root = etree.fromstring(xml_bytes)
        detalle_adicional = root.find(
            "./detalles/detalle/detallesAdicionales/detAdicional"
        )

        self.assertIsNotNone(detalle_adicional)
        self.assertEqual(detalle_adicional.get("nombre"), "lote")
        self.assertEqual(detalle_adicional.get("valor"), "ABC123")
        self.assertEqual(len(detalle_adicional), 0)

    def test_valida_con_xsd_oficial_empaquetado(self):
        manejador = ManejadorXML(document_type="nota_credito")
        xml_str = manejador.dict_a_xml_string(self._build_payload())

        with tempfile.TemporaryDirectory() as tmpdir:
            xml_path = Path(tmpdir) / "nota_credito.xml"
            xml_path.write_text(xml_str, encoding="utf-8")
            self.assertTrue(manejador.validar_estructura_xml(str(xml_path)))


if __name__ == "__main__":
    unittest.main()
