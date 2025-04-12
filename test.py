from src.fe_ec.utils.sri import SRIService
from src.fe_ec.utils.manejador_xml import ManejadorXML
from src.fe_ec.utils.generador_clave_acceso import GeneradorClaveAcceso


def main():
    xsd_path = "sri_docs/factura_sin_firma.xsd"
    p12_path = "firma.p12"
    p12_password = "Angie1590"

    clave_generada = GeneradorClaveAcceso.generar(
        fecha_emision="12/04/2025",
        tipo_comprobante="01",
        ruc="0104815956001",
        tipo_ambiente="1",
        serie="001050",
        secuencial="000000012",
        tipo_emision="1"
    )
    print(clave_generada)
    datos_factura = {
    "infoTributaria": {
        "ambiente": "1",
        "tipoEmision": "1",
        "razonSocial": "Mi Empresa S.A.",
        "nombreComercial": "MiComercio",
        "ruc": "0104815956001",
        "claveAcceso": clave_generada,
        "codDoc": "01",
        "estab": "001",
        "ptoEmi": "050",
        "secuencial": "000000010",
        "dirMatriz": "Av. Principal 123"
    },
    "infoFactura": {
        "fechaEmision": "12/04/2025",
        "dirEstablecimiento": "Av. Secundaria 456",
        "obligadoContabilidad": "NO",
        "tipoIdentificacionComprador": "07",
        "razonSocialComprador": "Consumidor Final",
        "identificacionComprador": "9999999999999",
        "totalSinImpuestos": "250.00",
        "totalDescuento": "12.00",
        "totalConImpuestos": {
            "totalImpuesto": [
                {
                    "codigo": "2",
                    "codigoPorcentaje": "3",
                    "baseImponible": "238.00",
                    "valor": "35.70"
                }
            ]
        },
        "propina": "0.00",
        "importeTotal": "273.70",
        "moneda": "USD"
    },
    "detalles": {
    "detalle": [
        {
            "codigoPrincipal": "A001",
            "codigoAuxiliar": "B001",
            "descripcion": "Producto A",
            "cantidad": "2.00",
            "precioUnitario": "100.00",
            "descuento": "10.00",
            "precioTotalSinImpuesto": "190.00",
            "impuestos": {
                "impuesto": [
                    {
                        "codigo": "2",
                        "codigoPorcentaje": "3",
                        "tarifa": "15.00",
                        "baseImponible": "190.00",
                        "valor": "28.50"
                    }
                ]
            }
        },
        {
            "codigoPrincipal": "A002",
            "codigoAuxiliar": "B002",
            "descripcion": "Producto B",
            "cantidad": "5.00",
            "precioUnitario": "10.00",
            "descuento": "2.00",
            "precioTotalSinImpuesto": "48.00",
            "impuestos": {
                "impuesto": [
                    {
                        "codigo": "2",
                        "codigoPorcentaje": "3",
                        "tarifa": "15.00",
                        "baseImponible": "48.00",
                        "valor": "7.20"
                    }
                ]
            }
        }
    ]
}

}

    try:
        manejador = ManejadorXML(xsd_path)
        firmado_path = manejador.firmar_y_guardar_xml(
            json_data=datos_factura,
            p12_path=p12_path,
            p12_password=p12_password,
            output_path="fact_firmado.xml"
        )
        print(f"✅ XML firmado generado en: {firmado_path}")
        sri = SRIService(ambiente="pruebas", espera_autorizacion=7)

        # 1. Enviar XML firmado a recepción
        with open("fact_firmado.xml", "rb") as f:
            xml_bytes = f.read()

        respuesta_recepcion = sri.enviar_recepcion(xml_bytes)
        print("Respuesta recepción:", respuesta_recepcion)

        # 2. Si es 'RECIBIDA', consulta autorización automáticamente
        if hasattr(respuesta_recepcion, "estado") and respuesta_recepcion.estado == "RECIBIDA":
            respuesta_autorizacion = sri.consultar_autorizacion(clave_generada)
            print("✅ Respuesta de autorización del SRI:")
            print("Número:", respuesta_autorizacion["numero_autorizacion"])
            print("Fecha :", respuesta_autorizacion["fecha_autorizacion"])
            print("XML   :", respuesta_autorizacion["xml_autorizado"])

    except Exception as e:
        print(f"❌ Error durante la generación o firma del XML: {e}")

if __name__ == "__main__":
    main()
