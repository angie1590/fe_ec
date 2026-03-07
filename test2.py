import os
from datetime import datetime, timedelta

from fe_ec.constants import normalizar_ambiente
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
OUTPUT_XML = os.getenv("FEEC_OUTPUT_XML", "fact_firmado.xml")
AMBIENTE_NORMALIZADO = normalizar_ambiente(os.getenv("FEEC_AMBIENTE", "1"))
TIPO_AMBIENTE = {"pruebas": "1", "produccion": "2"}[AMBIENTE_NORMALIZADO]
SERIE = f"{ESTAB}{PTO_EMI}"


def build_factura_payload(clave_acceso: str) -> dict:
    return {
        "infoTributaria": {
            "ambiente": TIPO_AMBIENTE,
            "tipoEmision": TIPO_EMISION,
            "razonSocial": "PRUEBAS SERVICIO DE RENTAS INTERNA",
            "nombreComercial": "MiComercio",
            "ruc": RUC,
            "claveAcceso": clave_acceso,
            "codDoc": "01",
            "estab": ESTAB,
            "ptoEmi": PTO_EMI,
            "secuencial": SECUENCIAL,
            "dirMatriz": "Av. Principal 123",
        },
        "infoFactura": {
            "fechaEmision": FECHA_EMISION,
            "dirEstablecimiento": "Av. Secundaria 456",
            "obligadoContabilidad": "NO",
            "tipoIdentificacionComprador": "04",
            "razonSocialComprador": "PRUEBAS SERVICIO DE RENTAS INTERNA",
            "identificacionComprador": "0195125988001",
            "direccionComprador": "Guapondelig",
            "totalSinImpuestos": "1111.91",
            "totalDescuento": "0.00",
            "totalConImpuestos": {
                "totalImpuesto": [
                    {
                        "codigo": "2",
                        "codigoPorcentaje": "4",
                        "baseImponible": "980.43",
                        "valor": "147.06",
                    },
                    {
                        "codigo": "2",
                        "codigoPorcentaje": "7",
                        "baseImponible": "100.00",
                        "valor": "0.00",
                    },
                    {
                        "codigo": "2",
                        "codigoPorcentaje": "6",
                        "baseImponible": "50.00",
                        "valor": "0.00",
                    },
                    {
                        "codigo": "3",
                        "codigoPorcentaje": "3043",
                        "baseImponible": "861.91",
                        "valor": "18.52",
                    },
                ]
            },
            "propina": "0.00",
            "importeTotal": "1277.49",
            "moneda": "DOLAR",
            "pagos": [
                {
                    "formaPago": "01",
                    "total": "1277.49",
                    "plazo": "0",
                    "unidadTiempo": "DIAS",
                }
            ],
        },
        "detalles": [
            {
                "codigoPrincipal": "P001",
                "descripcion": "Producto de prueba",
                "cantidad": "1.00",
                "precioUnitario": "100.00",
                "descuento": "0.00",
                "precioTotalSinImpuesto": "100.00",
                "impuestos": {
                    "impuesto": [
                        {
                            "codigo": "2",
                            "codigoPorcentaje": "4",
                            "tarifa": "15.00",
                            "baseImponible": "100.00",
                            "valor": "15.00",
                        }
                    ]
                },
            },
            {
                "codigoPrincipal": "P002",
                "descripcion": "Producto de prueba 2 (exento)",
                "cantidad": "1.00",
                "precioUnitario": "100.00",
                "descuento": "0.00",
                "precioTotalSinImpuesto": "100.00",
                "impuestos": {
                    "impuesto": [
                        {
                            "codigo": "2",
                            "codigoPorcentaje": "7",
                            "tarifa": "0.00",
                            "baseImponible": "100.00",
                            "valor": "0.00",
                        }
                    ]
                },
            },
            {
                "codigoPrincipal": "P003",
                "descripcion": "Producto de prueba 3 (no grava IVA)",
                "cantidad": "1.00",
                "precioUnitario": "50.00",
                "descuento": "0.00",
                "precioTotalSinImpuesto": "50.00",
                "impuestos": {
                    "impuesto": [
                        {
                            "codigo": "2",
                            "codigoPorcentaje": "6",
                            "tarifa": "0.00",
                            "baseImponible": "50.00",
                            "valor": "0.00",
                        }
                    ]
                },
            },
            {
                "codigoPrincipal": "C001",
                "descripcion": "Cerveza artesanal 4L",
                "cantidad": "225.00",
                "precioUnitario": "3.83",
                "descuento": "0.00",
                "precioTotalSinImpuesto": "861.91",
                "impuestos": {
                    "impuesto": [
                        {
                            "codigo": "2",
                            "codigoPorcentaje": "4",
                            "tarifa": "15.00",
                            "baseImponible": "880.43",
                            "valor": "132.06",
                        },
                        {
                            "codigo": "3",
                            "codigoPorcentaje": "3043",
                            "tarifa": "0",
                            "baseImponible": "861.91",
                            "valor": "18.52",
                        },
                    ]
                },
            },
        ],
        "infoAdicional": {
            "campoAdicional": [
                {"nombre": "email", "valor": "cliente@ejemplo.com"},
                {"nombre": "teléfono", "valor": "0999999999"},
            ]
        },
    }


def print_sri_messages(mensajes) -> None:
    for mensaje in mensajes or []:
        print(f"- [{mensaje.identificador}] {mensaje.mensaje}")
        if mensaje.informacionAdicional:
            print(f"  {mensaje.informacionAdicional}")


def main():
    clave_generada = GeneradorClaveAcceso.generar(
        fecha_emision=FECHA_EMISION,
        tipo_comprobante="01",
        ruc=RUC,
        tipo_ambiente=TIPO_AMBIENTE,
        serie=SERIE,
        secuencial=SECUENCIAL,
        tipo_emision=TIPO_EMISION,
    )
    datos_factura = build_factura_payload(clave_generada)

    print(f"Clave acceso: {clave_generada}")
    print(
        "Configuracion:"
        f" ambiente={TIPO_AMBIENTE}"
        f" estab={ESTAB}"
        f" ptoEmi={PTO_EMI}"
        f" secuencial={SECUENCIAL}"
        f" fecha={FECHA_EMISION}"
    )

    try:
        manejador = ManejadorXML()
        xml_firmado = manejador.firmar_y_guardar_xml(datos_factura, output_path=OUTPUT_XML)
        if xml_firmado is None:
            print("Hay errores en la estructura del XML. No se puede firmar")
            return

        print(f"Estructura valida, listo para firmar y enviar: {xml_firmado}")
        sri = SRIService()

        with open(OUTPUT_XML, "rb") as xml_file:
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
    except Exception as e:
        print(f"Error durante la generación o firma del XML: {e}")


if __name__ == "__main__":
    main()
