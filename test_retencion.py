import argparse
import os
import re
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from fe_ec.constants import normalizar_ambiente
from fe_ec.utils.generador_clave_acceso import GeneradorClaveAcceso
from fe_ec.utils.manejador_xml import ManejadorXML
from fe_ec.utils.retencion import (
    DocumentoSustentoRetencion,
    EmisorRetencion,
    ImpuestoDocSustento,
    PagoRetencion,
    RetencionLinea,
    SujetoRetenido,
    decimal_formateado,
    extraer_metadata_clave_acceso,
    fecha_desde_clave_acceso,
    numero_documento_desde_clave_acceso,
)
from fe_ec.utils.retencion_contract import (
    RetencionRequest,
    load_retencion_request_from_yaml,
)
from fe_ec.utils.sri import SRIService


RUC = os.getenv("FEEC_RUC", "0103523908001")
ESTAB = os.getenv("FEEC_ESTAB", "001")
PTO_EMI = os.getenv("FEEC_PTO_EMI", "001")
SECUENCIAL = os.getenv("FEEC_SECUENCIAL", datetime.now().strftime("%H%M%S%f")[-9:])
FECHA_EMISION = os.getenv(
    "FEEC_FECHA_EMISION",
    (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y"),
)
TIPO_EMISION = os.getenv("FEEC_TIPO_EMISION", "1")
OUTPUT_XML = os.getenv("FEEC_OUTPUT_RETENCION_XML", "retencion_firmada.xml")
AMBIENTE_NORMALIZADO = normalizar_ambiente(os.getenv("FEEC_AMBIENTE", "pruebas"))
TIPO_AMBIENTE = {"pruebas": "1", "produccion": "2"}[AMBIENTE_NORMALIZADO]
SERIE = f"{ESTAB}{PTO_EMI}"

# Perfil del emisor en pruebas.
RAZON_SOCIAL_EMISOR = os.getenv(
    "FEEC_RAZON_SOCIAL",
    "PINEDA ALVAREZ DANIEL FERNANDO",
)
NOMBRE_COMERCIAL = os.getenv("FEEC_NOMBRE_COMERCIAL", RAZON_SOCIAL_EMISOR)
DIR_MATRIZ = os.getenv("FEEC_DIR_MATRIZ", "Av. Principal 123")
DIR_ESTABLECIMIENTO = os.getenv("FEEC_DIR_ESTABLECIMIENTO", "Av. Secundaria 456")
OBLIGADO_CONTABILIDAD = os.getenv("FEEC_OBLIGADO_CONTABILIDAD", "NO")
AGENTE_RETENCION = os.getenv("FEEC_AGENTE_RETENCION", "").strip()
CONTRIBUYENTE_ESPECIAL = os.getenv("FEEC_CONTRIBUYENTE_ESPECIAL", "").strip()
CONTRIBUYENTE_RIMPE = os.getenv("FEEC_CONTRIBUYENTE_RIMPE", "").strip()

# Datos del proveedor retenido.
TIPO_ID_SUJETO_RETENIDO = os.getenv("FEEC_SUJETO_RETENIDO_TIPO_ID", "04")
TIPO_SUJETO_RETENIDO = os.getenv("FEEC_TIPO_SUJETO_RETENIDO", "")
PARTE_REL = os.getenv("FEEC_PARTE_REL", "NO")
SUJETO_RETENIDO_RAZON_SOCIAL = os.getenv(
    "FEEC_SUJETO_RETENIDO_RAZON_SOCIAL",
    "PRUEBAS SERVICIO DE RENTAS INTERNA",
).strip()
SUJETO_RETENIDO_IDENTIFICACION = os.getenv(
    "FEEC_SUJETO_RETENIDO_IDENTIFICACION",
    "0195125988001",
).strip()

# Los datos transaccionales del documento sustento no deben vivir en constants.py.
# En la libreria deben pasarse como parametros; aqui solo se exponen para el script.
COD_SUSTENTO = os.getenv("FEEC_COD_SUSTENTO", "01")
COD_DOC_SUSTENTO = os.getenv("FEEC_DOC_SUSTENTO_COD_DOC", "01")
DOC_SUSTENTO_NUMERO = os.getenv("FEEC_DOC_SUSTENTO_NUMERO", "").strip()
DOC_SUSTENTO_AUTORIZACION = os.getenv("FEEC_DOC_SUSTENTO_AUTORIZACION", "").strip()
DOC_SUSTENTO_FECHA = os.getenv("FEEC_DOC_SUSTENTO_FECHA", FECHA_EMISION)
DOC_SUSTENTO_FECHA_REGISTRO_CONTABLE = os.getenv(
    "FEEC_DOC_SUSTENTO_FECHA_REGISTRO_CONTABLE",
    DOC_SUSTENTO_FECHA,
)
PAGO_LOC_EXT = os.getenv("FEEC_PAGO_LOC_EXT", "01")
DOC_SUSTENTO_TOTAL_SIN_IMPUESTOS = os.getenv(
    "FEEC_DOC_SUSTENTO_TOTAL_SIN_IMPUESTOS",
    "",
)
DOC_SUSTENTO_IMPORTE_TOTAL = os.getenv("FEEC_DOC_SUSTENTO_IMPORTE_TOTAL", "")
FORMA_PAGO_DOC_SUSTENTO = os.getenv("FEEC_FORMA_PAGO_DOC_SUSTENTO", "")
DOC_SUSTENTO_CODIGO_PORCENTAJE = os.getenv("FEEC_DOC_SUSTENTO_CODIGO_PORCENTAJE", "")
DOC_SUSTENTO_BASE_IVA = os.getenv(
    "FEEC_DOC_SUSTENTO_BASE_IVA",
    "",
)
DOC_SUSTENTO_TARIFA_IVA = os.getenv("FEEC_DOC_SUSTENTO_TARIFA_IVA", "")
DOC_SUSTENTO_VALOR_IVA = os.getenv("FEEC_DOC_SUSTENTO_VALOR_IVA", "")

RETENCION_RENTA_CODIGO = os.getenv("FEEC_RETENCION_RENTA_CODIGO", "1")
RETENCION_RENTA_CODIGO_RETENCION = os.getenv("FEEC_RETENCION_RENTA_CODIGO_RETENCION", "")
RETENCION_RENTA_BASE = os.getenv(
    "FEEC_RETENCION_RENTA_BASE",
    "",
)
RETENCION_RENTA_PORCENTAJE = os.getenv("FEEC_RETENCION_RENTA_PORCENTAJE", "")
RETENCION_RENTA_VALOR = os.getenv("FEEC_RETENCION_RENTA_VALOR", "").strip()

RETENCION_IVA_CODIGO = os.getenv("FEEC_RETENCION_IVA_CODIGO", "2")
RETENCION_IVA_CODIGO_RETENCION = os.getenv("FEEC_RETENCION_IVA_CODIGO_RETENCION", "")
RETENCION_IVA_BASE = os.getenv("FEEC_RETENCION_IVA_BASE", "")
RETENCION_IVA_PORCENTAJE = os.getenv("FEEC_RETENCION_IVA_PORCENTAJE", "")
RETENCION_IVA_VALOR = os.getenv("FEEC_RETENCION_IVA_VALOR", "").strip()

DEFAULT_INFO_ADICIONAL = (
    {"nombre": "email", "valor": "cliente@ejemplo.com"},
    {"nombre": "referencia", "valor": f"RET-{SECUENCIAL}"},
)


def _parse_decimal(value: str, field_name: str) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field_name} debe ser un numero decimal valido.") from exc


def _format_decimal(value: Decimal, digits: str = "0.01") -> str:
    return str(value.quantize(Decimal(digits), rounding=ROUND_HALF_UP))


def _resolve_retencion_valor(raw_value: str, base: str, porcentaje: str, field_name: str) -> str:
    if raw_value:
        return _format_decimal(_parse_decimal(raw_value, field_name))

    base_decimal = _parse_decimal(base, f"{field_name}.base")
    porcentaje_decimal = _parse_decimal(porcentaje, f"{field_name}.porcentaje")
    valor = (base_decimal * porcentaje_decimal) / Decimal("100")
    return _format_decimal(valor)


def build_emisor() -> EmisorRetencion:
    return EmisorRetencion(
        ruc=RUC,
        razon_social=RAZON_SOCIAL_EMISOR,
        nombre_comercial=NOMBRE_COMERCIAL,
        estab=ESTAB,
        pto_emi=PTO_EMI,
        dir_matriz=DIR_MATRIZ,
        dir_establecimiento=DIR_ESTABLECIMIENTO,
        obligado_contabilidad=OBLIGADO_CONTABILIDAD,
        agente_retencion=AGENTE_RETENCION or None,
        contribuyente_especial=CONTRIBUYENTE_ESPECIAL or None,
        contribuyente_rimpe=CONTRIBUYENTE_RIMPE or None,
    )


def build_sujeto_retenido() -> SujetoRetenido:
    return SujetoRetenido(
        tipo_identificacion=TIPO_ID_SUJETO_RETENIDO,
        identificacion=SUJETO_RETENIDO_IDENTIFICACION,
        razon_social=SUJETO_RETENIDO_RAZON_SOCIAL,
        parte_rel=PARTE_REL,
        tipo_sujeto_retenido=TIPO_SUJETO_RETENIDO or None,
    )


def build_impuestos_doc_sustento() -> list[ImpuestoDocSustento]:
    return [
        ImpuestoDocSustento(
            cod_impuesto_doc_sustento="2",
            codigo_porcentaje=DOC_SUSTENTO_CODIGO_PORCENTAJE,
            base_imponible=DOC_SUSTENTO_BASE_IVA,
            tarifa=DOC_SUSTENTO_TARIFA_IVA,
            valor_impuesto=_format_decimal(
                _parse_decimal(
                    DOC_SUSTENTO_VALOR_IVA,
                    "FEEC_DOC_SUSTENTO_VALOR_IVA",
                )
            ),
        )
    ]


def build_retenciones() -> list[RetencionLinea]:
    return [
        RetencionLinea(
            codigo=RETENCION_RENTA_CODIGO,
            codigo_retencion=RETENCION_RENTA_CODIGO_RETENCION,
            base_imponible=RETENCION_RENTA_BASE,
            porcentaje_retener=RETENCION_RENTA_PORCENTAJE,
            valor_retenido=_resolve_retencion_valor(
                RETENCION_RENTA_VALOR,
                RETENCION_RENTA_BASE,
                RETENCION_RENTA_PORCENTAJE,
                "FEEC_RETENCION_RENTA_VALOR",
            ),
        ),
        RetencionLinea(
            codigo=RETENCION_IVA_CODIGO,
            codigo_retencion=RETENCION_IVA_CODIGO_RETENCION,
            base_imponible=RETENCION_IVA_BASE,
            porcentaje_retener=RETENCION_IVA_PORCENTAJE,
            valor_retenido=_resolve_retencion_valor(
                RETENCION_IVA_VALOR,
                RETENCION_IVA_BASE,
                RETENCION_IVA_PORCENTAJE,
                "FEEC_RETENCION_IVA_VALOR",
            ),
        ),
    ]


def build_pagos() -> list[PagoRetencion]:
    return [
        PagoRetencion(
            forma_pago=FORMA_PAGO_DOC_SUSTENTO,
            total=DOC_SUSTENTO_IMPORTE_TOTAL,
        )
    ]


def build_documento_sustento() -> DocumentoSustentoRetencion:
    return DocumentoSustentoRetencion(
        cod_sustento=COD_SUSTENTO,
        cod_doc_sustento=COD_DOC_SUSTENTO,
        num_doc_sustento=DOC_SUSTENTO_NUMERO,
        fecha_emision_doc_sustento=DOC_SUSTENTO_FECHA,
        fecha_registro_contable=DOC_SUSTENTO_FECHA_REGISTRO_CONTABLE,
        num_aut_doc_sustento=DOC_SUSTENTO_AUTORIZACION,
        pago_loc_ext=PAGO_LOC_EXT,
        total_sin_impuestos=DOC_SUSTENTO_TOTAL_SIN_IMPUESTOS,
        importe_total=DOC_SUSTENTO_IMPORTE_TOTAL,
        impuestos_doc_sustento=build_impuestos_doc_sustento(),
        retenciones=build_retenciones(),
        pagos=build_pagos(),
    )


def build_retencion_request_from_env() -> RetencionRequest:
    return RetencionRequest(
        secuencial=SECUENCIAL,
        fecha_emision=FECHA_EMISION,
        tipo_emision=TIPO_EMISION,
        output_xml=OUTPUT_XML,
        emisor=build_emisor(),
        sujeto_retenido=build_sujeto_retenido(),
        documentos_sustento=[build_documento_sustento()],
        info_adicional=list(DEFAULT_INFO_ADICIONAL),
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Genera, firma y envia un comprobante de retencion ATS.",
    )
    parser.add_argument(
        "--contract",
        help="Ruta a un contrato YAML de retencion. Si se omite, usa FEEC_*.",
    )
    return parser.parse_args()


def resolve_retencion_request(contract_path: str | None) -> RetencionRequest:
    if not contract_path:
        return build_retencion_request_from_env()

    return load_retencion_request_from_yaml(
        contract_path,
        default_secuencial=SECUENCIAL,
        default_fecha_emision=FECHA_EMISION,
        default_tipo_emision=TIPO_EMISION,
        default_output_xml=OUTPUT_XML,
    )


def validar_configuracion_negocio(request: RetencionRequest, clave_retencion: str) -> None:
    if request.sujeto_retenido.identificacion == request.emisor.ruc:
        raise ValueError(
            "El sujeto retenido no puede coincidir con el emisor en este flujo de compras."
        )

    if not request.documentos_sustento:
        raise ValueError("La retencion debe contener al menos un documento sustento.")

    for index, documento in enumerate(request.documentos_sustento, start=1):
        prefix = f"documentos_sustento[{index}]"
        if not documento.num_doc_sustento:
            raise ValueError(f"{prefix}.num_doc_sustento es obligatorio.")
        if not documento.num_aut_doc_sustento:
            raise ValueError(f"{prefix}.num_aut_doc_sustento es obligatorio.")
        if not documento.total_sin_impuestos:
            raise ValueError(f"{prefix}.total_sin_impuestos es obligatorio.")
        if not documento.importe_total:
            raise ValueError(f"{prefix}.importe_total es obligatorio.")
        if not documento.impuestos_doc_sustento:
            raise ValueError(f"{prefix}.impuestos_doc_sustento debe tener al menos un item.")
        if not documento.retenciones:
            raise ValueError(f"{prefix}.retenciones debe tener al menos un item.")
        if not documento.pagos:
            raise ValueError(f"{prefix}.pagos debe tener al menos un item.")

        if not re.fullmatch(r"\d{15}", documento.num_doc_sustento):
            raise ValueError(
                f"{prefix}.num_doc_sustento debe tener 15 digitos sin guiones."
            )

        if documento.num_aut_doc_sustento == clave_retencion:
            raise ValueError(
                f"{prefix}.num_aut_doc_sustento debe ser la clave/autorizacion "
                "del documento sustento, no la clave de la retencion."
            )

        metadata_doc_sustento = extraer_metadata_clave_acceso(documento.num_aut_doc_sustento)
        if metadata_doc_sustento is not None:
            if metadata_doc_sustento["cod_doc"] != documento.cod_doc_sustento:
                raise ValueError(
                    f"{prefix}.num_aut_doc_sustento no coincide con {prefix}.cod_doc_sustento."
                )

            numero_documento = numero_documento_desde_clave_acceso(documento.num_aut_doc_sustento)
            if numero_documento and numero_documento != documento.num_doc_sustento:
                raise ValueError(
                    f"{prefix}.num_doc_sustento no coincide con la clave del documento sustento."
                )

            fecha_documento = fecha_desde_clave_acceso(documento.num_aut_doc_sustento)
            if fecha_documento and fecha_documento != documento.fecha_emision_doc_sustento:
                raise ValueError(
                    f"{prefix}.fecha_emision_doc_sustento no coincide con la fecha embebida "
                    "en la clave del documento sustento."
                )

            if metadata_doc_sustento["ruc"] == request.emisor.ruc:
                raise ValueError(
                    "La clave del documento sustento pertenece al mismo RUC emisor. "
                    "Para una retencion por compras debe corresponder al proveedor."
                )

            if (
                request.sujeto_retenido.tipo_identificacion == "04"
                and metadata_doc_sustento["ruc"] != request.sujeto_retenido.identificacion
            ):
                raise ValueError(
                    "La clave del documento sustento no corresponde al RUC del sujeto retenido."
                )

        impuesto = documento.impuestos_doc_sustento[0]
        total_sin_impuestos = decimal_formateado(
            documento.total_sin_impuestos,
            f"{prefix}.total_sin_impuestos",
        )
        importe_total = decimal_formateado(
            documento.importe_total,
            f"{prefix}.importe_total",
        )
        base_iva = decimal_formateado(
            impuesto.base_imponible,
            f"{prefix}.impuestos_doc_sustento[0].base_imponible",
        )
        valor_iva = decimal_formateado(
            impuesto.valor_impuesto,
            f"{prefix}.impuestos_doc_sustento[0].valor_impuesto",
        )
        total_pago = decimal_formateado(
            documento.pagos[0].total,
            f"{prefix}.pagos[0].total",
        )

        if total_sin_impuestos != base_iva:
            raise ValueError(
                f"{prefix}.impuestos_doc_sustento[0].base_imponible debe coincidir con "
                f"{prefix}.total_sin_impuestos en este flujo simple de un solo impuesto."
            )

        total_calculado = _format_decimal(
            _parse_decimal(total_sin_impuestos, f"{prefix}.total_sin_impuestos")
            + _parse_decimal(valor_iva, f"{prefix}.impuestos_doc_sustento[0].valor_impuesto")
        )
        if total_calculado != importe_total:
            raise ValueError(
                f"{prefix}.importe_total no cuadra con subtotal + IVA del documento sustento."
            )

        if total_pago != importe_total:
            raise ValueError(
                f"{prefix}.pagos[0].total debe coincidir con {prefix}.importe_total."
            )


def print_sri_messages(mensajes) -> None:
    for mensaje in mensajes or []:
        identificador = getattr(mensaje, "identificador", "N/A")
        texto = getattr(mensaje, "mensaje", "Sin mensaje")
        info = getattr(mensaje, "informacionAdicional", None)
        print(f"- [{identificador}] {texto}")
        if info:
            print(f"  {info}")


def _normalizar_a_lista(value):
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]


def obtener_mensajes_recepcion(respuesta_recepcion) -> list:
    comprobantes = getattr(respuesta_recepcion, "comprobantes", None)
    mensajes = []

    for comprobante in _normalizar_a_lista(getattr(comprobantes, "comprobante", None)):
        mensajes_respuesta = getattr(getattr(comprobante, "mensajes", None), "mensaje", None)
        mensajes.extend(_normalizar_a_lista(mensajes_respuesta))

    return mensajes


def contiene_clave_en_procesamiento(mensajes) -> bool:
    for mensaje in mensajes or []:
        if str(getattr(mensaje, "identificador", "")).strip() == "70":
            return True
    return False


def obtener_primera_autorizacion(respuesta_autorizacion):
    autorizaciones = getattr(respuesta_autorizacion, "autorizaciones", None)
    items = _normalizar_a_lista(getattr(autorizaciones, "autorizacion", None))
    return items[0] if items else None


def main():
    args = parse_args()
    request = resolve_retencion_request(args.contract)

    clave_generada = GeneradorClaveAcceso.generar(
        fecha_emision=request.fecha_emision,
        tipo_comprobante="07",
        ruc=request.emisor.ruc,
        tipo_ambiente=TIPO_AMBIENTE,
        serie=f"{request.emisor.estab}{request.emisor.pto_emi}",
        secuencial=request.secuencial,
        tipo_emision=request.tipo_emision,
    )
    validar_configuracion_negocio(request, clave_generada)
    datos_retencion = request.to_payload(
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
        manejador = ManejadorXML(document_type="retencion")
        xml_firmado = manejador.firmar_y_guardar_xml(
            datos_retencion,
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

        mensajes_recepcion = []
        if respuesta_recepcion.estado != "RECIBIDA":
            mensajes_recepcion = obtener_mensajes_recepcion(respuesta_recepcion)
            print("El SRI devolvio el comprobante.")
            print_sri_messages(mensajes_recepcion)
            if contiene_clave_en_procesamiento(mensajes_recepcion):
                print(
                    "Clave en procesamiento. La politica de reintentos y polling "
                    "debe manejarla el sistema consumidor."
                )
            return

        print("Comprobante recibido. Consultando autorizacion una sola vez...")
        respuesta = sri.consultar_autorizacion(clave_generada)
        print("Respuesta autorizacion:", respuesta)
        autorizacion = obtener_primera_autorizacion(respuesta)
        if autorizacion is None:
            print("No hubo autorizaciones en la respuesta.")
            return

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
