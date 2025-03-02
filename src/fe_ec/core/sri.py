import requests

class SriServicio:
    """
    Servicio para la comunicación con el SRI y envío de documentos electrónicos.
    """

    URL_PRUEBAS = "https://cel.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantes"
    URL_PRODUCCION = "https://cel.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesProduccion"

    def __init__(self, ambiente="1"):
        """
        Inicializa el servicio SRI con el ambiente especificado.

        1: Pruebas
        2: Producción
        """
        self.ambiente = ambiente
        self.url_sri = self.URL_PRODUCCION if ambiente == "2" else self.URL_PRUEBAS

    def enviar_factura(self, xml_firmado: str) -> bool:
        """
        Envía la factura firmada al SRI mediante su servicio web.
        """
        headers = {"Content-Type": "application/xml"}
        response = requests.post(self.url_sri, data=xml_firmado.encode("utf-8"), headers=headers)
        return response.status_code == 200
