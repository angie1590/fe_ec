import json
from src.fe_ec.utils.sri import SRIService
from src.fe_ec.utils.manejador_xml import ManejadorXML
from src.fe_ec.utils.generador_clave_acceso import GeneradorClaveAcceso


def main():
    clave_generada = GeneradorClaveAcceso.generar(
        fecha_emision="14/04/2025",
        tipo_comprobante="01",
        ruc="0104815956001",
        tipo_ambiente="1",
        serie="001001",
        secuencial="000000027",
        tipo_emision="1"
    )
    print(clave_generada)
    datos_factura = {
    "infoTributaria": {
        "ambiente": "1",
        "tipoEmision": "1",
        "razonSocial": "PRUEBAS SERVICIO DE RENTAS INTERNA",
        "nombreComercial": "MiComercio",
        "ruc": "0104815956001",
        "claveAcceso": clave_generada,
        "codDoc": "01",
        "estab": "001",
        "ptoEmi": "001",
        "secuencial": "000000027",
        "dirMatriz": "Av. Principal 123"
    },
    "infoFactura": {
        "fechaEmision": "14/04/2025",
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
                    "valor": "147.06"
                },
                {
                    "codigo": "2",
                    "codigoPorcentaje": "7",
                    "baseImponible": "100.00",
                    "valor": "0.00"
                },
                {
                    "codigo": "2",
                    "codigoPorcentaje": "6",
                    "baseImponible": "50.00",
                    "valor": "0.00"
                },
                {
                    "codigo": "3",
                    "codigoPorcentaje": "3043",
                    "baseImponible": "861.91",
                    "valor": "18.52"
                }
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
                "unidadTiempo": "DIAS"
            }
        ]
    },
    "detalles": [
        {
            "codigoPrincipal": "P001",
            "descripcion": "Producto de prueba",
            "cantidad": 1,
            "precioUnitario": 100.00,
            "descuento": 0.00,
            "precioTotalSinImpuesto": 100.00,
            "impuestos": {
                "impuesto": [
                    {
                        "codigo": "2",
                        "codigoPorcentaje": "4",
                        "tarifa": 15.00,
                        "baseImponible": 100.00,
                        "valor": 15.00
                    }
                ]
            }
        },
        {
            "codigoPrincipal": "P002",
            "descripcion": "Producto de prueba 2 (exento)",
            "cantidad": 1,
            "precioUnitario": 100.00,
            "descuento": 0.00,
            "precioTotalSinImpuesto": 100.00,
            "impuestos": {
                "impuesto": [
                    {
                        "codigo": "2",
                        "codigoPorcentaje": "7",
                        "tarifa": 0.00,
                        "baseImponible": 100.00,
                        "valor": 0.00
                    }
                ]
            }
        },
        {
            "codigoPrincipal": "P003",
            "descripcion": "Producto de prueba 3 (no grava IVA)",
            "cantidad": 1,
            "precioUnitario": 50.00,
            "descuento": 0.00,
            "precioTotalSinImpuesto": 50.00,
            "impuestos": {
                "impuesto": [
                    {
                        "codigo": "2",
                        "codigoPorcentaje": "6",
                        "tarifa": 0.00,
                        "baseImponible": 50.00,
                        "valor": 0.00
                    }
                ]
            }
        },
        {
            "codigoPrincipal": "C001",
            "descripcion": "Cerveza artesanal 4L",
            "cantidad": "225.00",
            "precioUnitario": "3.83",
            "descuento": 0.00,
            "precioTotalSinImpuesto": "861.91",
            "impuestos": {
                "impuesto": [
                    {
                        "codigo": "2",
                        "codigoPorcentaje": "4",
                        "tarifa": "15.00",
                        "baseImponible": "880.43",
                        "valor": "132.06"
                    },
                    {
                        "codigo": "3",
                        "codigoPorcentaje": "3043",
                        "tarifa": "0",
                        "baseImponible": "861.91",
                        "valor": "18.52"
                    }
                ]
            }
        }
    ],
    "infoAdicional": {
        "campoAdicional": [
            {"nombre": "email", "valor": "cliente@ejemplo.com"},
            {"nombre": "teléfono", "valor": "0999999999"}
        ]
    }
}


    try:
        manejador = ManejadorXML()
        if manejador.firmar_y_guardar_xml(datos_factura) != None:
            print("Estructura válida, listo para firmar y enviar.")
            sri = SRIService()

            # 1. Enviar XML firmado a recepción
            with open("fact_firmado.xml", "rb") as f:
                xml_bytes = f.read()

            respuesta_recepcion = sri.enviar_recepcion(xml_bytes)
            print("Respuesta recepción:", respuesta_recepcion)

            # 2. Si es 'RECIBIDA', consulta autorización automáticamente
            if respuesta_recepcion.estado == "RECIBIDA":
                print("✅ Comprobante recibido. Consultando autorización...")

                respuesta = sri.consultar_autorizacion(clave_generada)

                # Puedes inspeccionar directamente la respuesta
                print("📦 Respuesta bruta del SRI:", respuesta)

                # Acceso directo a campos:
                if hasattr(respuesta, "autorizaciones") and respuesta.autorizaciones and respuesta.autorizaciones.autorizacion:
                    autorizacion = respuesta.autorizaciones.autorizacion[0]
                    print("✅ Número de autorización:", autorizacion.numeroAutorizacion)
                    print("🕒 Fecha:", autorizacion.fechaAutorizacion)
                else:
                    print("❌ No autorizado.")
                    print(respuesta.autorizaciones.autorizacion[0].mensajes)
        else:
            print("Hay errores en la estructura del XML. No se puede firmar")

    except Exception as e:
        print(f"❌ Error durante la generación o firma del XML: {e}")

if __name__ == "__main__":
    main()
