import unittest
from pathlib import Path

from fe_ec.constants import DEFAULT_XSD_PATH, XSD_PATH, normalizar_ambiente


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
