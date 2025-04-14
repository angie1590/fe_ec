import subprocess
import os


class FirmadorXML:
    def __init__(self):
        # Ruta absoluta del directorio donde se encuentra este archivo
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.jar_path = os.path.join(self.base_dir, "FirmaElectronica", "FirmaElectronica.jar")

    def firmar_xml(self, xml_path: str, output_path: str, p12_path: str, p12_password: str) -> str:
        """
        Firma un archivo XML utilizando el ejecutable Java basado en XAdES-BES.
        :param xml_path: Ruta del archivo XML sin firmar.
        :param output_path: Ruta donde se guardará el XML firmado.
        :param p12_path: Ruta del certificado digital (.p12).
        :param p12_password: Contraseña del archivo .p12.
        :return: Ruta del archivo XML firmado.
        """
        try:
            # ⚠️ Orden correcto de parámetros exigido por el .jar:
            # java -jar FirmaElectronica.jar <input.xml> <firma.p12> <clave> <output.xml>
            cmd = [
                "java",
                "-jar",
                self.jar_path,
                xml_path,
                p12_path,
                p12_password,
                output_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                raise RuntimeError(f"❌ Error ejecutando FirmaElectronica.jar:\n{result.stderr.strip()}")

            print(f"✅ XML firmado correctamente: {output_path}")
            return output_path

        except Exception as e:
            raise RuntimeError(f"❌ Error durante la generación o firma del XML: {e}")