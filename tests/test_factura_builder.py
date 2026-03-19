import tempfile
import unittest
from pathlib import Path

from lxml import etree

from fe_ec.utils.emisor import EmisorProfile
from fe_ec.utils.factura import (
    CompradorFactura,
    DetalleFactura,
    FacturaRequest,
    ImpuestoDetalleFactura,
    PagoFactura,
    TotalImpuestoFactura,
    construir_payload_factura,
)
from fe_ec.utils.manejador_xml import ManejadorXML


def _build_emisor() -> EmisorProfile:
    return EmisorProfile(
        ruc="0103523908001",
        razon_social="PRUEBAS SERVICIO DE RENTAS INTERNA",
        nombre_comercial="MiComercio",
        estab="001",
        pto_emi="001",
        dir_matriz="Av. Principal 123",
        dir_establecimiento="Av. Secundaria 456",
        obligado_contabilidad="NO",
    )


def _build_comprador() -> CompradorFactura:
    return CompradorFactura(
        tipo_identificacion="04",
        razon_social="PRUEBAS SERVICIO DE RENTAS INTERNA",
        identificacion="0195125988001",
        direccion="Guapondelig",
    )


def _build_request() -> FacturaRequest:
    return FacturaRequest(
        secuencial="000000123",
        fecha_emision="17/03/2026",
        tipo_emision="1",
        emisor=_build_emisor(),
        comprador=_build_comprador(),
        total_sin_impuestos="100.00",
        total_descuento="0.00",
        total_con_impuestos=[
            TotalImpuestoFactura(
                codigo="2",
                codigo_porcentaje="4",
                base_imponible="100.00",
                valor="15.00",
            )
        ],
        propina="0.00",
        importe_total="115.00",
        moneda="DOLAR",
        pagos=[
            PagoFactura(
                forma_pago="01",
                total="115.00",
                plazo="0",
                unidad_tiempo="DIAS",
            )
        ],
        detalles=[
            DetalleFactura(
                codigo_principal="P001",
                descripcion="Producto de prueba",
                cantidad="1.00",
                precio_unitario="100.00",
                descuento="0.00",
                precio_total_sin_impuesto="100.00",
                impuestos=[
                    ImpuestoDetalleFactura(
                        codigo="2",
                        codigo_porcentaje="4",
                        tarifa="15.00",
                        base_imponible="100.00",
                        valor="15.00",
                    )
                ],
            )
        ],
        info_adicional=[{"nombre": "email", "valor": "cliente@ejemplo.com"}],
    )


class FacturaBuilderTests(unittest.TestCase):
    def test_construye_payload_valido_para_xsd_oficial(self):
        request = _build_request()
        payload = request.to_payload(
            clave_acceso="1703202601010352390800110010010000001231234567811",
            ambiente="1",
        )
        manejador = ManejadorXML(document_type="factura")

        xml_bytes = manejador.dict_a_xml_string(payload, as_bytes=True)
        root = etree.fromstring(xml_bytes)

        self.assertEqual(root.tag, "factura")
        self.assertEqual(
            [child.tag for child in root.find("./infoTributaria")],
            [
                "ambiente",
                "tipoEmision",
                "razonSocial",
                "nombreComercial",
                "ruc",
                "claveAcceso",
                "codDoc",
                "estab",
                "ptoEmi",
                "secuencial",
                "dirMatriz",
            ],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            xml_path = Path(tmpdir) / "factura.xml"
            xml_path.write_bytes(xml_bytes)
            self.assertTrue(manejador.validar_estructura_xml(str(xml_path)))

    def test_rechaza_factura_sin_detalles(self):
        with self.assertRaisesRegex(ValueError, "detalles debe contener al menos un detalle"):
            construir_payload_factura(
                clave_acceso="1703202601010352390800110010010000001231234567811",
                ambiente="1",
                tipo_emision="1",
                secuencial="000000123",
                fecha_emision="17/03/2026",
                emisor=_build_emisor(),
                comprador=_build_comprador(),
                total_sin_impuestos="100.00",
                total_descuento="0.00",
                total_con_impuestos=[
                    TotalImpuestoFactura(
                        codigo="2",
                        codigo_porcentaje="4",
                        base_imponible="100.00",
                        valor="15.00",
                    )
                ],
                propina="0.00",
                importe_total="115.00",
                moneda="DOLAR",
                pagos=[PagoFactura(forma_pago="01", total="115.00")],
                detalles=[],
            )


if __name__ == "__main__":
    unittest.main()
