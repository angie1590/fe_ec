### factura.py ###
from datetime import datetime
from fe_ec.models.factura_modelo import Factura
from fe_ec.utils.generador_clave_acceso import GeneradorClaveAcceso
from fe_ec.utils.manejador_xml import ManejadorXML

class FacturaElectronica:
    """
    Clase principal para gestionar la facturación electrónica.
    """
    def __init__(self, factura: Factura):
        self.factura = factura
        self.clave_acceso = self.generar_clave_acceso()

    def generar_clave_acceso(self) -> str:
        """
        Genera la clave de acceso para la factura según el SRI.
        """
        return GeneradorClaveAcceso.generar(
            tipo_comprobante="01",
            fecha_emision=self.factura.fecha_emision.replace("-", ""),
            ruc=self.factura.empresa.ruc,
            ambiente="1",
            serie=self.factura.numero_factura[:7].replace("-", ""),
            secuencial=self.factura.numero_factura[8:],
            codigo_numerico="12345678",
            tipo_emision="1"
        )

    def generar_xml(self) -> str:
        """
        Genera el XML de la factura electrónica.
        """
        return ManejadorXML.crear_xml(self.factura.model_dump())

    def validar_factura(self) -> bool:
        """
        Valida que la factura contenga todos los datos requeridos antes de enviarla.
        """
        return all([
            self.factura.empresa.ruc,
            self.factura.cliente.identificacion,
            self.factura.items,
            self.factura.total > 0
        ])

    def firmar_factura(self, certificado_path: str, clave_certificado: str) -> str:
        """
        Firma digitalmente la factura electrónica con el certificado SRI.
        """
        from fe_ec.core.firma_digital import FirmadorDigital
        return FirmadorDigital.firmar_xml(self.generar_xml(), certificado_path, clave_certificado)