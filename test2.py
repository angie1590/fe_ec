import argparse
import os
from datetime import datetime, timedelta

from fe_ec.constants import normalizar_ambiente
from fe_ec.utils.emisor import EmisorProfile
from fe_ec.utils.factura import (
    CompradorFactura,
    DetalleFactura,
    FacturaRequest,
    ImpuestoDetalleFactura,
    PagoFactura,
    TotalImpuestoFactura,
)
from fe_ec.utils.factura_contract import load_factura_request_from_yaml
from fe_ec.utils.generador_clave_acceso import GeneradorClaveAcceso
from fe_ec.utils.manejador_xml import ManejadorXML
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
DEFAULT_OUTPUT_XML = ".artifacts/xml/fact_firmado.xml"
OUTPUT_XML = os.getenv(
    "FEEC_OUTPUT_FACTURA_XML",
    os.getenv("FEEC_OUTPUT_XML", DEFAULT_OUTPUT_XML),
)
AMBIENTE_NORMALIZADO = normalizar_ambiente(os.getenv("FEEC_AMBIENTE", "1"))
TIPO_AMBIENTE = {"pruebas": "1", "produccion": "2"}[AMBIENTE_NORMALIZADO]

DEFAULT_INFO_ADICIONAL = (
    {"nombre": "email", "valor": "cliente@ejemplo.com"},
    {"nombre": "telefono", "valor": "0999999999"},
)


def build_emisor() -> EmisorProfile:
    return EmisorProfile(
        ruc=RUC,
        razon_social=os.getenv("FEEC_RAZON_SOCIAL", "PRUEBAS SERVICIO DE RENTAS INTERNA"),
        nombre_comercial=os.getenv("FEEC_NOMBRE_COMERCIAL", "MiComercio"),
        estab=ESTAB,
        pto_emi=PTO_EMI,
        dir_matriz=os.getenv("FEEC_DIR_MATRIZ", "Av. Principal 123"),
        dir_establecimiento=os.getenv("FEEC_DIR_ESTABLECIMIENTO", "Av. Secundaria 456"),
        obligado_contabilidad=os.getenv("FEEC_OBLIGADO_CONTABILIDAD", "NO"),
    )


def build_comprador() -> CompradorFactura:
    return CompradorFactura(
        tipo_identificacion=os.getenv("FEEC_COMPRADOR_TIPO_ID", "04"),
        razon_social=os.getenv(
            "FEEC_COMPRADOR_RAZON_SOCIAL",
            "PRUEBAS SERVICIO DE RENTAS INTERNA",
        ),
        identificacion=os.getenv("FEEC_COMPRADOR_IDENTIFICACION", "0195125988001"),
        direccion=os.getenv("FEEC_COMPRADOR_DIRECCION", "Guapondelig"),
    )


def build_total_con_impuestos() -> list[TotalImpuestoFactura]:
    return [
        TotalImpuestoFactura(
            codigo="2",
            codigo_porcentaje="4",
            base_imponible="980.43",
            valor="147.06",
        ),
        TotalImpuestoFactura(
            codigo="2",
            codigo_porcentaje="7",
            base_imponible="100.00",
            valor="0.00",
        ),
        TotalImpuestoFactura(
            codigo="2",
            codigo_porcentaje="6",
            base_imponible="50.00",
            valor="0.00",
        ),
        TotalImpuestoFactura(
            codigo="3",
            codigo_porcentaje="3043",
            base_imponible="861.91",
            valor="18.52",
        ),
    ]


def build_pagos() -> list[PagoFactura]:
    return [
        PagoFactura(
            forma_pago="01",
            total="1277.49",
            plazo="0",
            unidad_tiempo="DIAS",
        )
    ]


def build_detalles() -> list[DetalleFactura]:
    return [
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
        ),
        DetalleFactura(
            codigo_principal="P002",
            descripcion="Producto de prueba 2 (exento)",
            cantidad="1.00",
            precio_unitario="100.00",
            descuento="0.00",
            precio_total_sin_impuesto="100.00",
            impuestos=[
                ImpuestoDetalleFactura(
                    codigo="2",
                    codigo_porcentaje="7",
                    tarifa="0.00",
                    base_imponible="100.00",
                    valor="0.00",
                )
            ],
        ),
        DetalleFactura(
            codigo_principal="P003",
            descripcion="Producto de prueba 3 (no grava IVA)",
            cantidad="1.00",
            precio_unitario="50.00",
            descuento="0.00",
            precio_total_sin_impuesto="50.00",
            impuestos=[
                ImpuestoDetalleFactura(
                    codigo="2",
                    codigo_porcentaje="6",
                    tarifa="0.00",
                    base_imponible="50.00",
                    valor="0.00",
                )
            ],
        ),
        DetalleFactura(
            codigo_principal="C001",
            descripcion="Cerveza artesanal 4L",
            cantidad="225.00",
            precio_unitario="3.83",
            descuento="0.00",
            precio_total_sin_impuesto="861.91",
            impuestos=[
                ImpuestoDetalleFactura(
                    codigo="2",
                    codigo_porcentaje="4",
                    tarifa="15.00",
                    base_imponible="880.43",
                    valor="132.06",
                ),
                ImpuestoDetalleFactura(
                    codigo="3",
                    codigo_porcentaje="3043",
                    tarifa="0",
                    base_imponible="861.91",
                    valor="18.52",
                ),
            ],
        ),
    ]


def build_factura_request_from_env() -> FacturaRequest:
    return FacturaRequest(
        secuencial=SECUENCIAL,
        fecha_emision=FECHA_EMISION,
        tipo_emision=TIPO_EMISION,
        output_xml=OUTPUT_XML,
        emisor=build_emisor(),
        comprador=build_comprador(),
        total_sin_impuestos="1111.91",
        total_descuento="0.00",
        total_con_impuestos=build_total_con_impuestos(),
        propina="0.00",
        importe_total="1277.49",
        moneda="DOLAR",
        pagos=build_pagos(),
        detalles=build_detalles(),
        info_adicional=list(DEFAULT_INFO_ADICIONAL),
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Genera, firma y envia una factura electronica.",
    )
    parser.add_argument(
        "--contract",
        help="Ruta a un contrato YAML de factura. Si se omite, usa el ejemplo por FEEC_*.",
    )
    return parser.parse_args()


def resolve_factura_request(contract_path: str | None) -> FacturaRequest:
    if not contract_path:
        return build_factura_request_from_env()

    return load_factura_request_from_yaml(
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
    request = resolve_factura_request(args.contract)

    clave_generada = GeneradorClaveAcceso.generar(
        fecha_emision=request.fecha_emision,
        tipo_comprobante="01",
        ruc=request.emisor.ruc,
        tipo_ambiente=TIPO_AMBIENTE,
        serie=f"{request.emisor.estab}{request.emisor.pto_emi}",
        secuencial=request.secuencial,
        tipo_emision=request.tipo_emision,
    )
    datos_factura = request.to_payload(
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
        manejador = ManejadorXML(document_type="factura")
        xml_firmado = manejador.firmar_y_guardar_xml(
            datos_factura,
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
