import json
from src.fe_ec.utils.sri import SRIService
from src.fe_ec.utils.manejador_xml import ManejadorXML
from src.fe_ec.utils.generador_clave_acceso import GeneradorClaveAcceso


def main():
    xsd_path = "sri_docs/factura_V1_1.xsd"
    p12_path = "firma.p12"
    p12_password = "Angie1590"

    clave_generada = GeneradorClaveAcceso.generar(
        fecha_emision="14/04/2025",
        tipo_comprobante="01",
        ruc="0104815956001",
        tipo_ambiente="1",
        serie="001001",
        secuencial="000000019",
        tipo_emision="1"
    )
    print(clave_generada)
    datos_factura = {
        "infoTributaria": {
            "ambiente": "1",
            "tipoEmision": "1",
            "razonSocial": "PRUEBAS SERVICIO DE RENTAS INTERNA",
            #"nombreComercial": "MiComercio",
            "ruc": "0104815956001",
            "claveAcceso": clave_generada,
            "codDoc": "01",
            "estab": "001",
            "ptoEmi": "001",
            "secuencial": "000000019",
            "dirMatriz": "Av. Principal 123"
        },
        "infoFactura": {
            "fechaEmision": "14/04/2025",
            "dirEstablecimiento": "Av. Secundaria 456",
            "obligadoContabilidad": "NO",
            "tipoIdentificacionComprador": "04",
            "razonSocialComprador": "PRUEBAS SERVICIO DE RENTAS INTERNA",
            "identificacionComprador": "0195125988001",
            #"direccionComprador": "Guapondelig",
            "totalSinImpuestos": "100.00",
            "totalDescuento": "0.00",
            "totalConImpuestos": {
                "totalImpuesto": [
                    {
                        "codigo": "2",
                        "codigoPorcentaje": "4",  # IVA 15%
                        "baseImponible": "100.00",
                        "valor": "15.00"
                    }
                ]
            },
            "propina": "0.00",
            "importeTotal": "115.00",
            "moneda": "DOLAR",
            "pagos": [
                {
                    "formaPago": "01",
                    "total": "115.00",
                    "plazo": "0",
                    "unidadTiempo": "DIAS"
                }
            ]
        },
        "detalles": [
            {
                "codigoPrincipal": "P001",
                "descripcion": "Producto de prueba",
                "cantidad": "1.00",
                "precioUnitario": "100.00",
                "descuento": "0.00",
                "precioTotalSinImpuesto": "100.00",
                "impuestos": [
                    {
                        "codigo": "2",
                        "codigoPorcentaje": "4",
                        "tarifa": "15.00",
                        "baseImponible": "100.00",
                        "valor": "15.00"
                    }
                ]
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
        manejador = ManejadorXML(xsd_path)
        # 1. Generar XML sin firmar
        #with open("factura_temp.xml", "wb") as f:
        #    f.write(manejador.dict_a_xml_string(datos_factura, as_bytes=True))
        if manejador.firmar_y_guardar_xml(datos_factura) != None:
            print("Estructura válida, listo para firmar y enviar.")
            sri = SRIService(ambiente="pruebas", espera_autorizacion=7)

            # 1. Enviar XML firmado a recepción
            with open("fact_firmado.xml", "rb") as f:
                xml_bytes = f.read()

            respuesta_recepcion = sri.enviar_recepcion(xml_bytes)
            print("Respuesta recepción:", respuesta_recepcion)

            # 2. Si es 'RECIBIDA', consulta autorización automáticamente
            if respuesta_recepcion.estado == "RECIBIDA":
                print("✅ Comprobante recibido. Consultando autorización...")

                respuesta_autorizacion = sri.consultar_autorizacion(clave_generada)
                print("📄 Respuesta de autorización del SRI:")
                print(json.dumps(respuesta_autorizacion, indent=2))

                numero = respuesta_autorizacion.get("numero_autorizacion")
                fecha = respuesta_autorizacion.get("fecha_autorizacion")
                xml_aut = respuesta_autorizacion.get("xml_autorizado")

                print("Número:", numero or "—")
                print("Fecha :", fecha or "—")

                if xml_aut:
                    with open("autorizado.xml", "w", encoding="utf-8") as f:
                        f.write(xml_aut)
                    print("✅ XML autorizado guardado como autorizado.xml")
                else:
                    print("⚠️ El SRI no devolvió el XML autorizado. Puede que el comprobante aún no esté autorizado.")
        else:
            print("Hay errores en la estructura del XML. No se puede firmar")

    except Exception as e:
        print(f"❌ Error durante la generación o firma del XML: {e}")

if __name__ == "__main__":
    main()
