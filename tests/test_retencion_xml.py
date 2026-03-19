import tempfile
import unittest
from pathlib import Path

from lxml import etree

from fe_ec.utils.manejador_xml import ManejadorXML
from tests.fixtures_retencion import build_retencion_payload


class RetencionXMLTests(unittest.TestCase):
    def _build_payload(self, **kwargs) -> dict:
        clave_acceso = "1303202607179001234500110010010000001231234567810"
        return build_retencion_payload(clave_acceso, **kwargs)

    def test_serializa_raiz_oficial_de_retencion(self):
        manejador = ManejadorXML(document_type="retencion")

        xml_bytes = manejador.dict_a_xml_string(self._build_payload(), as_bytes=True)
        root = etree.fromstring(xml_bytes)

        self.assertEqual(root.tag, "comprobanteRetencion")
        self.assertEqual(root.get("id"), "comprobante")
        self.assertEqual(root.get("version"), "2.0.0")
        self.assertEqual(len(root.findall("./docsSustento/docSustento")), 1)
        self.assertEqual(
            len(root.findall("./docsSustento/docSustento/retenciones/retencion")),
            2,
        )
        self.assertEqual(
            root.findtext("./docsSustento/docSustento/pagos/pago/formaPago"),
            "01",
        )

    def test_valida_con_xsd_oficial_empaquetado(self):
        manejador = ManejadorXML(document_type="retencion")
        xml_str = manejador.dict_a_xml_string(self._build_payload())

        with tempfile.TemporaryDirectory() as tmpdir:
            xml_path = Path(tmpdir) / "retencion.xml"
            xml_path.write_text(xml_str, encoding="utf-8")

            self.assertTrue(manejador.validar_estructura_xml(str(xml_path)))

    def test_normaliza_aliases_de_tags_a_forma_oficial(self):
        manejador = ManejadorXML(document_type="retencion")
        payload = self._build_payload(
            use_legacy_pago_aliases=True,
            include_reembolso=True,
            include_dividendos=True,
        )

        xml_bytes = manejador.dict_a_xml_string(payload, as_bytes=True)
        root = etree.fromstring(xml_bytes)

        self.assertEqual(
            root.findtext(
                "./docsSustento/docSustento/reembolsos/reembolsoDetalle/numeroAutorizacionDocReemb"
            ),
            "1303202601017901234500120010010000003211234567810",
        )
        self.assertEqual(
            root.findtext("./docsSustento/docSustento/pagos/pago/formaPago"),
            "01",
        )
        self.assertIsNotNone(
            root.find(
                "./docsSustento/docSustento/retenciones/retencion/dividendos/fechaPagoDiv"
            )
        )

    def test_rechaza_payload_sin_bloques_obligatorios(self):
        manejador = ManejadorXML(document_type="retencion")
        payload = self._build_payload()
        payload.pop("docsSustento")

        with self.assertRaisesRegex(ValueError, "Faltan bloques obligatorios"):
            manejador.dict_a_xml_string(payload)
