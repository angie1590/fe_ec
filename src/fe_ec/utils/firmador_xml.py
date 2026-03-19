import subprocess
import os
import re
from pathlib import Path


class FirmadorXML:
    JAVA_9_COMPAT_FLAGS = (
        "--add-exports=java.xml/com.sun.org.apache.xerces.internal.jaxp=ALL-UNNAMED",
        "--add-exports=java.xml/com.sun.org.apache.xerces.internal.dom=ALL-UNNAMED",
    )

    def __init__(self, java_bin: str | None = None):
        # Determinar la ruta del .jar y el directorio lib dentro del paquete
        self.base_dir = Path(__file__).resolve().parent / "FirmaElectronica"
        self.jar_path = self.base_dir / "FirmaElectronica.jar"
        self.lib_dir = self.base_dir / "lib"
        self.java_bin = java_bin or os.getenv("FEEC_JAVA_BIN", "java")
        self.java_major_version = self._detectar_version_java()

    @staticmethod
    def parse_java_major_version(version_output: str) -> int:
        match = re.search(r'version "(?P<version>[^"]+)"', version_output)
        if not match:
            raise RuntimeError(f"No se pudo detectar la version de Java: {version_output.strip()}")

        version = match.group("version")
        if version.startswith("1."):
            return int(version.split(".")[1])
        return int(version.split(".", 1)[0])

    @classmethod
    def compat_jvm_args(cls, java_major_version: int) -> list[str]:
        if java_major_version >= 9:
            return list(cls.JAVA_9_COMPAT_FLAGS)
        return []

    def _detectar_version_java(self) -> int:
        try:
            result = subprocess.run(
                [self.java_bin, "-version"],
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError as exc:
            raise RuntimeError(
                f"No se encontro Java en PATH. Configure FEEC_JAVA_BIN o instale Java."
            ) from exc

        version_output = "\n".join(
            line for line in (result.stderr.strip(), result.stdout.strip()) if line
        )
        if not version_output:
            raise RuntimeError("No se pudo obtener la version de Java instalada.")

        return self.parse_java_major_version(version_output)

    def _build_command(
        self,
        xml_path: str,
        output_path: str,
        p12_path: str,
        p12_password: str,
    ) -> list[str]:
        if not Path(xml_path).exists():
            raise RuntimeError(f"No se encontro el XML a firmar en {xml_path}")
        if not self.jar_path.exists():
            raise RuntimeError(f"No se encontro el firmador Java en {self.jar_path}")
        if not self.lib_dir.exists():
            raise RuntimeError(f"No se encontro el directorio de librerias en {self.lib_dir}")
        if not Path(p12_path).exists():
            raise RuntimeError(f"No se encontro el certificado .p12 en {p12_path}")
        if not p12_password:
            raise RuntimeError(
                "No se proporciono la contrasena del certificado .p12. "
                "Define FEEC_P12_PASSWORD o pasa p12_password explicitamente."
            )

        classpath = os.pathsep.join([str(self.jar_path), str(self.lib_dir / "*")])
        return [
            self.java_bin,
            *self.compat_jvm_args(self.java_major_version),
            "-cp",
            classpath,
            "firmaelectronica.FirmaElectronica",
            xml_path,
            p12_path,
            p12_password,
            output_path,
        ]

    def firmar_xml(self, xml_path: str, output_path: str, p12_path: str, p12_password: str) -> str:
        """
        Firma un archivo XML utilizando el ejecutable Java basado en XAdES-BES.
        :param xml_path: Ruta del archivo XML sin firmar.
        :param output_path: Ruta donde se guardará el XML firmado.
        :param p12_path: Ruta del certificado digital (.p12).
        :param p12_password: Contraseña del archivo .p12.
        :return: Ruta del archivo XML firmado.
        """
        output_parent = Path(output_path).expanduser().resolve().parent
        output_parent.mkdir(parents=True, exist_ok=True)

        cmd = self._build_command(xml_path, output_path, p12_path, p12_password)

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            output = "\n".join(
                line for line in (result.stderr.strip(), result.stdout.strip()) if line
            )
            if (
                "keystore password was incorrect" in output
                or "UnrecoverableKeyException" in output
            ):
                raise RuntimeError(
                    "La contrasena del certificado .p12 es incorrecta. "
                    "Verifica FEEC_P12_PASSWORD o el valor enviado a p12_password."
                )
            raise RuntimeError(f"Error ejecutando FirmaElectronica.jar:\n{output}")

        print(f"✅ XML firmado correctamente: {output_path}")
        return output_path
