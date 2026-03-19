import unittest
from pathlib import Path

from fe_ec.constants import (
    DEFAULT_FACTURA_XSD_PATH,
    DEFAULT_RETENCION_XSD_PATH,
    DEFAULT_XSD_PATH,
    FACTURA_XSD_PATH,
    RETENCION_XSD_PATH,
    XSD_PATH,
    get_document_config,
    infer_document_type,
    normalizar_ambiente,
)


class NormalizarAmbienteTests(unittest.TestCase):
    def test_acepta_alias_numericos(self):
        self.assertEqual(normalizar_ambiente("1"), "pruebas")
        self.assertEqual(normalizar_ambiente("2"), "produccion")

    def test_acepta_alias_textuales(self):
        self.assertEqual(normalizar_ambiente("pruebas"), "pruebas")
        self.assertEqual(normalizar_ambiente("produccion"), "produccion")

    def test_rechaza_valores_invalidos(self):
        with self.assertRaises(ValueError):
            normalizar_ambiente("sandbox")

    def test_xsd_por_defecto_existe(self):
        self.assertTrue(Path(DEFAULT_XSD_PATH).exists())
        self.assertTrue(str(XSD_PATH))
        self.assertTrue(Path(DEFAULT_FACTURA_XSD_PATH).exists())
        self.assertTrue(Path(DEFAULT_RETENCION_XSD_PATH).exists())
        self.assertTrue(str(FACTURA_XSD_PATH))
        self.assertTrue(str(RETENCION_XSD_PATH))

    def test_infiere_retencion_desde_coddoc(self):
        self.assertEqual(infer_document_type("01"), "factura")
        self.assertEqual(infer_document_type("07"), "retencion")
        self.assertIsNone(infer_document_type("99"))

    def test_resuelve_metadata_por_tipo_documento(self):
        factura = get_document_config("factura")
        retencion = get_document_config("retencion")

        self.assertEqual(factura["cod_doc"], "01")
        self.assertEqual(factura["root_tag"], "factura")
        self.assertEqual(retencion["cod_doc"], "07")
        self.assertEqual(retencion["root_tag"], "comprobanteRetencion")
        self.assertIn("docsSustento", retencion["required_blocks"])
