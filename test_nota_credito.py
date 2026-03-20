import argparse
import os
from datetime import datetime

from fe_ec.constants import normalizar_ambiente
from fe_ec.utils.generador_clave_acceso import GeneradorClaveAcceso
from fe_ec.utils.manejador_xml import ManejadorXML
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
from fe_ec.utils.nota_credito_contract import load_nota_credito_request_from_yaml
from fe_ec.utils.sri import SRIService


RUC = os.getenv("FEEC_RUC", "0103523908001")
ESTAB = os.getenv("FEEC_ESTAB", "001")
PTO_EMI = os.getenv("FEEC_PTO_EMI", "001")
SECUENCIAL = os.getenv("FEEC_SECUENCIAL", datetime.now().strftime("%H%M%S%f")[-9:])
FECHA_EMISION = os.getenv(
    "FEEC_FECHA_EMISION",
    datetime.now().strftime("%d/%m/%Y"),
)
TIPO_EMISION = os.getenv("FEEC_TIPO_EMISION", "1")
DEFAULT_OUTPUT_XML = ".artifacts/xml/nota_credito_firmada.xml"
OUTPUT_XML = os.getenv(
    "FEEC_OUTPUT_NOTA_CREDITO_XML",
    os.getenv("FEEC_OUTPUT_XML", DEFAULT_OUTPUT_XML),
)
AMBIENTE_NORMALIZADO = normalizar_ambiente(os.getenv("FEEC_AMBIENTE", "1"))
TIPO_AMBIENTE = {"pruebas": "1", "produccion": "2"}[AMBIENTE_NORMALIZADO]

DEFAULT_INFO_ADICIONAL = (
    {"nombre": "email", "valor": "cliente@ejemplo.com"},
)


def build_emisor() -> EmisorNotaCredito:
    razon_social = os.getenv(
        "FEEC_RAZON_SOCIAL",
        "PINEDA ALVAREZ DANIEL FERNANDO",
    )
    return EmisorNotaCredito(
        ruc=RUC,
        razon_social=razon_social,
        nombre_comercial=os.getenv("FEEC_NOMBRE_COMERCIAL", razon_social),
        estab=ESTAB,
        pto_emi=PTO_EMI,
        dir_matriz=os.getenv("FEEC_DIR_MATRIZ", "Av. Principal 123"),
        dir_establecimiento=os.getenv("FEEC_DIR_ESTABLECIMIENTO", "Av. Secundaria 456"),
        obligado_contabilidad=os.getenv("FEEC_OBLIGADO_CONTABILIDAD", "NO"),
        contribuyente_especial=os.getenv("FEEC_CONTRIBUYENTE_ESPECIAL", "").strip() or None,
        contribuyente_rimpe=os.getenv("FEEC_CONTRIBUYENTE_RIMPE", "").strip() or None,
        rise=os.getenv("FEEC_RISE", "").strip() or None,
    )


def build_comprador() -> CompradorNotaCredito:
    return CompradorNotaCredito(
        tipo_identificacion=os.getenv("FEEC_COMPRADOR_TIPO_ID", "04"),
        razon_social=os.getenv("FEEC_COMPRADOR_RAZON_SOCIAL", "CLIENTE DE PRUEBA S.A."),
        identificacion=os.getenv("FEEC_COMPRADOR_IDENTIFICACION", "0195125988001"),
    )


def build_comprobante_modificado() -> ComprobanteModificado:
    return ComprobanteModificado(
        cod_doc_modificado=os.getenv("FEEC_DOC_MODIFICADO_COD_DOC", "01"),
        num_doc_modificado=os.getenv(
            "FEEC_DOC_MODIFICADO_NUMERO",
            "001-001-000000321",
        ),
        fecha_emision_doc_sustento=os.getenv(
            "FEEC_DOC_MODIFICADO_FECHA_EMISION",
            FECHA_EMISION,
        ),
    )


def build_total_con_impuestos() -> list[TotalImpuestoNotaCredito]:
    return [
        TotalImpuestoNotaCredito(
            codigo=os.getenv("FEEC_NOTA_CREDITO_IMPUESTO_CODIGO", "2"),
            codigo_porcentaje=os.getenv(
                "FEEC_NOTA_CREDITO_IMPUESTO_CODIGO_PORCENTAJE",
                "4",
            ),
            base_imponible=os.getenv(
                "FEEC_NOTA_CREDITO_IMPUESTO_BASE_IMPONIBLE",
                "100.00",
            ),
            valor=os.getenv("FEEC_NOTA_CREDITO_IMPUESTO_VALOR", "15.00"),
        )
    ]


def build_detalles() -> list[DetalleNotaCredito]:
    detalle_adicional = DetalleAdicionalNotaCredito(
        nombre=os.getenv("FEEC_NOTA_CREDITO_DETALLE_ADICIONAL_NOMBRE", "lote"),
        valor=os.getenv("FEEC_NOTA_CREDITO_DETALLE_ADICIONAL_VALOR", "ABC123"),
    )
    impuesto = ImpuestoDetalleNotaCredito(
        codigo=os.getenv("FEEC_NOTA_CREDITO_DETALLE_IMPUESTO_CODIGO", "2"),
        codigo_porcentaje=os.getenv(
            "FEEC_NOTA_CREDITO_DETALLE_IMPUESTO_CODIGO_PORCENTAJE",
            "4",
        ),
        tarifa=os.getenv("FEEC_NOTA_CREDITO_DETALLE_IMPUESTO_TARIFA", "15.00"),
        base_imponible=os.getenv(
            "FEEC_NOTA_CREDITO_DETALLE_IMPUESTO_BASE_IMPONIBLE",
            "100.00",
        ),
        valor=os.getenv("FEEC_NOTA_CREDITO_DETALLE_IMPUESTO_VALOR", "15.00"),
    )
    return [
        DetalleNotaCredito(
            codigo_interno=os.getenv("FEEC_NOTA_CREDITO_DETALLE_CODIGO_INTERNO", "P001"),
            codigo_adicional=os.getenv("FEEC_NOTA_CREDITO_DETALLE_CODIGO_ADICIONAL", "P001-A"),
            descripcion=os.getenv("FEEC_NOTA_CREDITO_DETALLE_DESCRIPCION", "Producto ajustado"),
            cantidad=os.getenv("FEEC_NOTA_CREDITO_DETALLE_CANTIDAD", "1.00"),
            precio_unitario=os.getenv("FEEC_NOTA_CREDITO_DETALLE_PRECIO_UNITARIO", "100.00"),
            descuento=os.getenv("FEEC_NOTA_CREDITO_DETALLE_DESCUENTO", "0.00"),
            precio_total_sin_impuesto=os.getenv(
                "FEEC_NOTA_CREDITO_DETALLE_PRECIO_TOTAL_SIN_IMPUESTO",
                "100.00",
            ),
            detalles_adicionales=[detalle_adicional],
            impuestos=[impuesto],
        )
    ]


def build_nota_credito_request_from_env() -> NotaCreditoRequest:
    return NotaCreditoRequest(
        secuencial=SECUENCIAL,
        fecha_emision=FECHA_EMISION,
        tipo_emision=TIPO_EMISION,
        output_xml=OUTPUT_XML,
        emisor=build_emisor(),
        comprador=build_comprador(),
        comprobante_modificado=build_comprobante_modificado(),
        total_sin_impuestos=os.getenv("FEEC_NOTA_CREDITO_TOTAL_SIN_IMPUESTOS", "100.00"),
        valor_modificacion=os.getenv("FEEC_NOTA_CREDITO_VALOR_MODIFICACION", "115.00"),
        total_con_impuestos=build_total_con_impuestos(),
        detalles=build_detalles(),
        motivo=os.getenv("FEEC_NOTA_CREDITO_MOTIVO", "DEVOLUCION PARCIAL"),
        moneda=os.getenv("FEEC_NOTA_CREDITO_MONEDA", "DOLAR"),
        info_adicional=list(DEFAULT_INFO_ADICIONAL),
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Genera, firma y envia una nota de credito electronica.",
    )
    parser.add_argument(
        "--contract",
        help="Ruta a un contrato YAML de nota de credito. Si se omite, usa FEEC_*.",
    )
    return parser.parse_args()


def resolve_nota_credito_request(contract_path: str | None) -> NotaCreditoRequest:
    if not contract_path:
        return build_nota_credito_request_from_env()

    return load_nota_credito_request_from_yaml(
        contract_path,
        default_secuencial=SECUENCIAL,
        default_fecha_emision=FECHA_EMISION,
        default_tipo_emision=TIPO_EMISION,
        default_output_xml=OUTPUT_XML,
    )


def print_sri_messages(mensajes) -> None:
    for mensaje in mensajes or []:
        identificador = getattr(mensaje, "identificador", "N/A")
        texto = getattr(mensaje, "mensaje", "Sin mensaje")
        info = getattr(mensaje, "informacionAdicional", None)
        print(f"- [{identificador}] {texto}")
        if info:
            print(f"  {info}")


def main():
    args = parse_args()
    request = resolve_nota_credito_request(args.contract)

    clave_generada = GeneradorClaveAcceso.generar(
        fecha_emision=request.fecha_emision,
        tipo_comprobante="04",
        ruc=request.emisor.ruc,
        tipo_ambiente=TIPO_AMBIENTE,
        serie=f"{request.emisor.estab}{request.emisor.pto_emi}",
        secuencial=request.secuencial,
        tipo_emision=request.tipo_emision,
    )
    datos_nota_credito = request.to_payload(
        clave_acceso=clave_generada,
        ambiente=TIPO_AMBIENTE,
    )

    print(f"Clave acceso: {clave_generada}")
    print(
        "Configuracion:"
        f" ambiente={TIPO_AMBIENTE}"
        f" estab={request.emisor.estab}"
        f" ptoEmi={request.emisor.pto_emi}"
        f" secuencial={request.secuencial}"
        f" fecha={request.fecha_emision}"
    )
    if args.contract:
        print(f"Contrato YAML: {args.contract}")

    try:
        manejador = ManejadorXML(document_type="nota_credito")
        xml_firmado = manejador.firmar_y_guardar_xml(
            datos_nota_credito,
            output_path=request.output_xml,
        )
        if xml_firmado is None:
            print("Hay errores en la estructura del XML. No se puede firmar")
            return

        print(f"Estructura valida, listo para firmar y enviar: {xml_firmado}")
        sri = SRIService()

        with open(request.output_xml, "rb") as xml_file:
            xml_bytes = xml_file.read()

        respuesta_recepcion = sri.enviar_recepcion(xml_bytes)
        print("Respuesta recepcion:", respuesta_recepcion)

        if respuesta_recepcion.estado != "RECIBIDA":
            comprobantes = getattr(respuesta_recepcion, "comprobantes", None)
            comprobante = getattr(comprobantes, "comprobante", None) if comprobantes else None
            mensajes = comprobante[0].mensajes.mensaje if comprobante else []
            print("El SRI devolvio el comprobante.")
            print_sri_messages(mensajes)
            return

        print("Comprobante recibido. Consultando autorizacion...")
        respuesta = sri.consultar_autorizacion(clave_generada)
        print("Respuesta autorizacion:", respuesta)

        if not (
            hasattr(respuesta, "autorizaciones")
            and respuesta.autorizaciones
            and respuesta.autorizaciones.autorizacion
        ):
            print("No hubo autorizaciones en la respuesta.")
            return

        autorizacion = respuesta.autorizaciones.autorizacion[0]
        if autorizacion.estado == "AUTORIZADO":
            print("Autorizado:", autorizacion.numeroAutorizacion)
            print("Fecha autorizacion:", autorizacion.fechaAutorizacion)
            return

        print(f"Estado de autorizacion: {autorizacion.estado}")
        print_sri_messages(getattr(autorizacion.mensajes, "mensaje", []))
    except Exception as exc:
        print(f"Error durante la generacion o firma del XML: {exc}")


if __name__ == "__main__":
    main()
