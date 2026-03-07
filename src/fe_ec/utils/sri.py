from zeep import Client
from fe_ec.constants import SRI_ENDPOINTS, AMBIENTE

class SRIService:
    def __init__(self):
        self.ambiente = AMBIENTE
        self.endpoints = SRI_ENDPOINTS[AMBIENTE]

    def enviar_recepcion(self, xml_bytes):
        try:
            client = Client(wsdl=self.endpoints["recepcion"])
            response = client.service.validarComprobante(xml_bytes)
            return response
        except Exception as e:
            raise RuntimeError(f"Error en recepción del comprobante: {e}")

    def consultar_autorizacion(self, clave_acceso: str):
        try:
            client = Client(wsdl=self.endpoints["autorizacion"])
            return client.service.autorizacionComprobante(clave_acceso)
        except Exception as e:
            raise ValueError(f"❌ Error al consultar autorización del SRI: {e}")