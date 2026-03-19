import tempfile
import unittest
from pathlib import Path

from lxml import etree

from fe_ec.utils.manejador_xml import ManejadorXML
from fe_ec.utils.retencion import (
    DocumentoSustentoRetencion,
    EmisorRetencion,
    ImpuestoDocSustento,
    PagoRetencion,
    RetencionLinea,
    SujetoRetenido,
    construir_payload_retencion,
    decimal_formateado,
    extraer_metadata_clave_acceso,
    fecha_desde_clave_acceso,
    numero_documento_desde_clave_acceso,
    periodo_fiscal_desde_fecha,
)


def _build_emisor() -> EmisorRetencion:
    return EmisorRetencion(
        ruc="0103523908001",
        razon_social="PRUEBAS SERVICIO DE RENTAS INTERNA",
        nombre_comercial="MiComercio",
        estab="001",
        pto_emi="001",
        dir_matriz="Av. Principal 123",
        dir_establecimiento="Av. Secundaria 456",
        obligado_contabilidad="NO",
        agente_retencion="001",
    )


def _build_sujeto() -> SujetoRetenido:
    return SujetoRetenido(
        tipo_identificacion="04",
        identificacion="0195125988001",
        razon_social="PROVEEDOR DEMO S.A.",
        parte_rel="NO",
        tipo_sujeto_retenido="01",
    )


def _build_documento() -> DocumentoSustentoRetencion:
    return DocumentoSustentoRetencion(
        cod_sustento="01",
        cod_doc_sustento="01",
        num_doc_sustento="001001000000123",
        fecha_emision_doc_sustento="13/03/2026",
        num_aut_doc_sustento="1303202601019512598800110010010000001231234567814",
        pago_loc_ext="01",
        total_sin_impuestos="100.00",
        importe_total="115.00",
        impuestos_doc_sustento=[
            ImpuestoDocSustento(
                cod_impuesto_doc_sustento="2",
                codigo_porcentaje="4",
                base_imponible="100.00",
                tarifa="15.00",
                valor_impuesto="15.00",
            )
        ],
        retenciones=[
            RetencionLinea(
                codigo="1",
                codigo_retencion="332",
                base_imponible="100.00",
                porcentaje_retener="1.00",
                valor_retenido="1.00",
            ),
            RetencionLinea(
                codigo="2",
                codigo_retencion="1",
                base_imponible="15.00",
                porcentaje_retener="30.00",
                valor_retenido="4.50",
            ),
        ],
        pagos=[PagoRetencion(forma_pago="01", total="115.00")],
    )


class RetencionBuilderTests(unittest.TestCase):
    def test_extrae_metadata_desde_clave_acceso(self):
        clave = "1403202601010422809300120010020000047251106242116"

        self.assertEqual(
            extraer_metadata_clave_acceso(clave),
            {
                "fecha": "14032026",
                "cod_doc": "01",
                "ruc": "0104228093001",
                "ambiente": "2",
                "serie": "001002",
                "secuencial": "000004725",
            },
        )
        self.assertEqual(fecha_desde_clave_acceso(clave), "14/03/2026")
        self.assertEqual(numero_documento_desde_clave_acceso(clave), "001002000004725")

    def test_periodo_fiscal_se_deriva_desde_la_fecha_de_emision(self):
        self.assertEqual(periodo_fiscal_desde_fecha("13/03/2026"), "03/2026")

    def test_formatea_decimales_con_dos_decimales(self):
        self.assertEqual(decimal_formateado("4.613", "valor"), "4.61")

    def test_construye_payload_valido_para_xsd_oficial(self):
        payload = construir_payload_retencion(
            clave_acceso="1303202607010352390800110010010000001231234567810",
            ambiente="1",
            tipo_emision="1",
            secuencial="000000123",
            fecha_emision="13/03/2026",
            emisor=_build_emisor(),
            sujeto_retenido=_build_sujeto(),
            documentos_sustento=[_build_documento()],
            info_adicional=[("email", "contabilidad@ejemplo.com")],
        )
        manejador = ManejadorXML(document_type="retencion")

        xml_bytes = manejador.dict_a_xml_string(payload, as_bytes=True)
        root = etree.fromstring(xml_bytes)

        self.assertEqual(root.tag, "comprobanteRetencion")
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
                "agenteRetencion",
            ],
        )
        self.assertEqual(
            [child.tag for child in root.find("./infoCompRetencion")],
            [
                "fechaEmision",
                "dirEstablecimiento",
                "obligadoContabilidad",
                "tipoIdentificacionSujetoRetenido",
                "tipoSujetoRetenido",
                "parteRel",
                "razonSocialSujetoRetenido",
                "identificacionSujetoRetenido",
                "periodoFiscal",
            ],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            xml_path = Path(tmpdir) / "retencion.xml"
            xml_path.write_bytes(xml_bytes)
            self.assertTrue(manejador.validar_estructura_xml(str(xml_path)))

    def test_rechaza_documento_sustento_autorreferenciado(self):
        clave = "1303202607010352390800110010010000001231234567810"

        with self.assertRaisesRegex(ValueError, "misma clave de acceso"):
            construir_payload_retencion(
                clave_acceso=clave,
                ambiente="1",
                tipo_emision="1",
                secuencial="000000123",
                fecha_emision="13/03/2026",
                emisor=_build_emisor(),
                sujeto_retenido=_build_sujeto(),
                documentos_sustento=[
                    DocumentoSustentoRetencion(
                        cod_sustento="01",
                        cod_doc_sustento="01",
                        num_doc_sustento="001001000000123",
                        fecha_emision_doc_sustento="13/03/2026",
                        num_aut_doc_sustento=clave,
                        pago_loc_ext="01",
                        total_sin_impuestos="100.00",
                        importe_total="115.00",
                        impuestos_doc_sustento=[
                            ImpuestoDocSustento(
                                cod_impuesto_doc_sustento="2",
                                codigo_porcentaje="4",
                                base_imponible="100.00",
                                tarifa="15.00",
                                valor_impuesto="15.00",
                            )
                        ],
                        retenciones=[
                            RetencionLinea(
                                codigo="1",
                                codigo_retencion="332",
                                base_imponible="100.00",
                                porcentaje_retener="1.00",
                                valor_retenido="1.00",
                            )
                        ],
                        pagos=[PagoRetencion(forma_pago="01", total="115.00")],
                    )
                ],
            )
