from zeep import Client
import zeep
from zeep.helpers import serialize_object
from lxml import etree
from .config import SRI_ENDPOINTS
import time
from src.fe_ec.constants import SRI_ENDPOINTS, AMBIENTE, DEFAULT_TIEMPO_ESPERA

class SRIService:
    def __init__(self, ambiente=AMBIENTE, espera_autorizacion=DEFAULT_TIEMPO_ESPERA, endpoints=None):
        self.ambiente = ambiente
        self.endpoints = endpoints if endpoints else SRI_ENDPOINTS[ambiente]
        self.tiempo_espera = espera_autorizacion

    def enviar_recepcion(self, xml_bytes):
        try:
            client = Client(wsdl=self.endpoints["recepcion"])
            response = client.service.validarComprobante(xml_bytes)
            return response
        except Exception as e:
            raise RuntimeError(f"Error en recepción del comprobante: {e}")

    def consultar_autorizacion(self, clave_acceso: str) -> dict:
        try:
            wsdl = self.endpoints["autorizacion"]
            client = zeep.Client(wsdl=wsdl)
            response = client.service.autorizacionComprobante(clave_acceso)

            if hasattr(response, "autorizaciones") and response.autorizaciones and len(response.autorizaciones.autorizacion) > 0:
                autorizacion = response.autorizaciones.autorizacion[0]
                fecha = autorizacion.fechaAutorizacion.isoformat() if hasattr(autorizacion, "fechaAutorizacion") else None

                # Convertir OrderedDict a XML usando lxml Element
                serialized_dict = serialize_object(autorizacion)
                xml_root = etree.Element("autorizacion")
                for key, value in serialized_dict.items():
                    if isinstance(value, str):
                        child = etree.SubElement(xml_root, key)
                        child.text = value

                return {
                    "numero_autorizacion": autorizacion.numeroAutorizacion,
                    "fecha_autorizacion": fecha,
                    "xml_autorizado": etree.tostring(xml_root, pretty_print=True, encoding="unicode")
                }

            return {
                "numero_autorizacion": None,
                "fecha_autorizacion": None,
                "xml_autorizado": None
            }

        except Exception as e:
            raise ValueError(f"Error al consultar autorización del SRI: {e}")

