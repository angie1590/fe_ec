import tempfile
import unittest
from pathlib import Path

from lxml import etree

from fe_ec.utils.nota_credito import (
    ComprobanteModificado,
    CompradorNotaCredito,
    DetalleAdicionalNotaCredito,
    DetalleNotaCredito,
    EmisorNotaCredito,
    ImpuestoDetalleNotaCredito,
    NotaCreditoRequest,
    TotalImpuestoNotaCredito,
)
from fe_ec.utils.manejador_xml import ManejadorXML


def _build_emisor() -> EmisorNotaCredito:
    return EmisorNotaCredito(
        ruc="0103523908001",
        razon_social="PRUEBAS SERVICIO DE RENTAS INTERNA",
        nombre_comercial="MiComercio",
        estab="001",
        pto_emi="001",
        dir_matriz="Av. Principal 123",
        dir_establecimiento="Av. Secundaria 456",
        obligado_contabilidad="NO",
    )


def _build_comprador() -> CompradorNotaCredito:
    return CompradorNotaCredito(
        tipo_identificacion="04",
        razon_social="CLIENTE DE PRUEBA S.A.",
        identificacion="0195125988001",
    )


def _build_request() -> NotaCreditoRequest:
    return NotaCreditoRequest(
        secuencial="000000123",
        fecha_emision="19/03/2026",
        tipo_emision="1",
        emisor=_build_emisor(),
        comprador=_build_comprador(),
        comprobante_modificado=ComprobanteModificado(
            cod_doc_modificado="01",
            num_doc_modificado="001-001-000000321",
            fecha_emision_doc_sustento="18/03/2026",
        ),
        total_sin_impuestos="100.00",
        valor_modificacion="115.00",
        total_con_impuestos=[
            TotalImpuestoNotaCredito(
                codigo="2",
                codigo_porcentaje="4",
                base_imponible="100.00",
                valor="15.00",
            )
        ],
        detalles=[
            DetalleNotaCredito(
                codigo_interno="P001",
                codigo_adicional="P001-A",
                descripcion="Producto ajustado",
                cantidad="1.00",
                precio_unitario="100.00",
                descuento="0.00",
                precio_total_sin_impuesto="100.00",
                detalles_adicionales=[
                    DetalleAdicionalNotaCredito(nombre="lote", valor="ABC123")
                ],
                impuestos=[
                    ImpuestoDetalleNotaCredito(
                        codigo="2",
                        codigo_porcentaje="4",
                        tarifa="15.00",
                        base_imponible="100.00",
                        valor="15.00",
                    )
                ],
            )
        ],
        motivo="DEVOLUCION PARCIAL",
        info_adicional=[{"nombre": "email", "valor": "cliente@ejemplo.com"}],
    )


class NotaCreditoBuilderTests(unittest.TestCase):
    def test_construye_payload_valido_para_xsd_oficial(self):
        request = _build_request()
        payload = request.to_payload(
            clave_acceso="1903202604010352390800110010010000001231234567819",
            ambiente="1",
        )
        manejador = ManejadorXML(document_type="nota_credito")

        xml_bytes = manejador.dict_a_xml_string(payload, as_bytes=True)
        root = etree.fromstring(xml_bytes)

        self.assertEqual(root.tag, "notaCredito")
        self.assertEqual(root.get("id"), "comprobante")
        self.assertEqual(root.get("version"), "1.1.0")
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
            xml_path = Path(tmpdir) / "nota_credito.xml"
            xml_path.write_bytes(xml_bytes)
            self.assertTrue(manejador.validar_estructura_xml(str(xml_path)))

    def test_rechaza_numero_documento_modificado_invalido(self):
        request = _build_request()
        request = NotaCreditoRequest(
            secuencial=request.secuencial,
            fecha_emision=request.fecha_emision,
            tipo_emision=request.tipo_emision,
            emisor=request.emisor,
            comprador=request.comprador,
            comprobante_modificado=ComprobanteModificado(
                cod_doc_modificado="01",
                num_doc_modificado="001001000000321",
                fecha_emision_doc_sustento="18/03/2026",
            ),
            total_sin_impuestos=request.total_sin_impuestos,
            valor_modificacion=request.valor_modificacion,
            total_con_impuestos=request.total_con_impuestos,
            detalles=request.detalles,
            motivo=request.motivo,
        )

        with self.assertRaisesRegex(ValueError, "num_doc_modificado"):
            request.to_payload(
                clave_acceso="1903202604010352390800110010010000001231234567819",
                ambiente="1",
            )


if __name__ == "__main__":
    unittest.main()
