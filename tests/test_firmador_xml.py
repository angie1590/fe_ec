import tempfile
import unittest
from pathlib import Path

from fe_ec.utils.firmador_xml import FirmadorXML


class FirmadorXMLTests(unittest.TestCase):
    def test_parse_java_8(self):
        self.assertEqual(
            FirmadorXML.parse_java_major_version('java version "1.8.0_111"'),
            8,
        )

    def test_parse_java_17(self):
        self.assertEqual(
            FirmadorXML.parse_java_major_version('openjdk version "17.0.7" 2023-04-18'),
            17,
        )

    def test_agrega_flags_de_compatibilidad_desde_java_9(self):
        flags = FirmadorXML.compat_jvm_args(17)

        self.assertIn(
            "--add-exports=java.xml/com.sun.org.apache.xerces.internal.jaxp=ALL-UNNAMED",
            flags,
        )
        self.assertIn(
            "--add-exports=java.xml/com.sun.org.apache.xerces.internal.dom=ALL-UNNAMED",
            flags,
        )
        self.assertEqual(FirmadorXML.compat_jvm_args(8), [])

    def test_requiere_contrasena_del_p12(self):
        firmador = FirmadorXML()

        with tempfile.TemporaryDirectory() as tmpdir:
            xml_path = Path(tmpdir) / "temp.xml"
            xml_path.write_text("<factura />", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "FEEC_P12_PASSWORD"):
                firmador._build_command(str(xml_path), "out.xml", "firma.p12", "")
