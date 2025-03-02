from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend

class FirmadorDigital:
    """
    Clase para la firma digital de documentos electrónicos sin usar pyOpenSSL.
    Utiliza cryptography para manejar certificados y claves privadas.
    """

    @staticmethod
    def cargar_certificado_y_llave(certificado_path: str, clave_certificado: str):
        """
        Carga el certificado y la clave privada desde un archivo .p12 (PKCS#12).
        """
        with open(certificado_path, "rb") as cert_file:
            p12_data = cert_file.read()

        # Cargar el archivo PKCS#12
        from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates

        private_key, certificate, additional_certs = load_key_and_certificates(
            p12_data, clave_certificado.encode(), backend=default_backend()
        )

        return private_key, certificate

    @staticmethod
    def firmar_xml(xml: str, certificado_path: str, clave_certificado: str) -> str:
        """
        Firma el XML con el certificado digital.
        """
        private_key, _ = FirmadorDigital.cargar_certificado_y_llave(certificado_path, clave_certificado)

        # Crear la firma digital con SHA256
        firma = private_key.sign(
            xml.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )

        return xml + f"<!-- Firma: {firma.hex()} -->"
