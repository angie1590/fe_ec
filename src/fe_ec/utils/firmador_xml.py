from signxml import XMLSigner, methods
from lxml import etree
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives import hashes

from signxml import XMLSigner, methods

class XMLSignerWithSHA1(XMLSigner):
    def check_deprecated_methods(self):
        # Anula la validación interna de algoritmos inseguros
        pass


def firmar_xml_con_p12(xml_str: str, p12_path: str, p12_password: str):
    """
    Firma un archivo XML utilizando un certificado P12.

    :param xml_str: XML en formato de cadena
    :param p12_path: Ruta al archivo P12
    :param p12_password: Contraseña del archivo P12
    :return: XML firmado (bytes)
    """
    try:
        # Habilitar SHA1 explícitamente
        hashes.SHA1._deprecated_algorithm = False

        # Leer archivo .p12
        with open(p12_path, 'rb') as p12_file:
            p12_data = p12_file.read()

        # Cargar clave y certificado en formato PEM
        key_pem, cert_pem = load_pkcs12(p12_data, p12_password)

        # Crear el objeto XMLSigner con algoritmos SHA256
        signer = XMLSignerWithSHA1(
            method=methods.enveloped,
            signature_algorithm="rsa-sha1",
            digest_algorithm="sha1",
            c14n_algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"
        )

        # Parsear XML de entrada
        xml_root = etree.fromstring(xml_str.encode("utf-8"))

        # Firmar el XML
        signed_xml = signer.sign(xml_root, key=key_pem, cert=cert_pem,reference_uri="#comprobante")

        # Retornar como string con formato
        return etree.tostring(signed_xml, pretty_print=True, encoding="utf-8")

    except Exception as e:
        raise ValueError(f"Error al firmar el XML: {str(e)}")

def load_pkcs12(p12_data, password):
    private_key, certificate, _ = pkcs12.load_key_and_certificates(
        p12_data,
        password.encode(),
        backend=default_backend()
    )

    # Serializar certificado en formato PEM
    cert_pem = certificate.public_bytes(encoding=serialization.Encoding.PEM)

    # Serializar clave privada en formato PEM
    key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    return key_pem, cert_pem
