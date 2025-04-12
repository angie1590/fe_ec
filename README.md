# 🇪🇨 Librería de Facturación Electrónica Ecuador (SRI)

Esta es una librería en Python diseñada para generar, firmar y enviar comprobantes electrónicos (como facturas) al Servicio de Rentas Internas (SRI) de Ecuador bajo el esquema offline.

---

## 🚀 Características

- ✅ Generación automática de la **clave de acceso**
- ✅ Construcción del XML a partir de un `dict` Python
- ✅ Validación del XML contra el XSD del SRI
- ✅ Firma digital del XML con archivo `.p12`
- ✅ Envío al Web Service de **Recepción** del SRI
- ✅ Consulta automática al Web Service de **Autorización**
- ✅ Compatible con ambiente de **pruebas** y **producción**
- ✅ Soporte para ejecución **asíncrona** con espera entre recepción y autorización

---

## 📦 Instalación

1. Clona el repositorio:

```bash
git clone https://github.com/tu_usuario/facturacion-ec.git
cd facturacion-ec
```

2. Instala las dependencias con Poetry:

```bash
poetry install
```

---

## ⚙️ Requisitos

- Python 3.10+
- Certificado digital `.p12` válido emitido por entidad autorizada
- Conexión a internet
- Archivo XSD del SRI (por ejemplo, `factura_V2.xsd`)

---

## 🧪 Ejemplo de uso simple

```python
from src.fe_ec.utils.generador_clave_acceso import GeneradorClaveAcceso
from src.fe_ec.utils.manejador_xml import ManejadorXML
from src.fe_ec.utils.sri import SRIService

clave = GeneradorClaveAcceso.generar(
    fecha_emision="02/04/2025",
    tipo_comprobante="01",
    ruc="0104815956001",
    tipo_ambiente="1",
    serie="001050",
    secuencial="000000001",
    tipo_emision="1"
)

# Estructura básica de la factura
datos_factura = {
    "infoTributaria": {
        "ambiente": "1",
        "tipoEmision": "1",
        "razonSocial": "Mi Empresa S.A.",
        "nombreComercial": "MiComercio",
        "ruc": "0104815956001",
        "claveAcceso": clave,
        "codDoc": "01",
        "estab": "001",
        "ptoEmi": "050",
        "secuencial": "000000001",
        "dirMatriz": "Av. Principal 123"
    },
    "infoFactura": {
        "fechaEmision": "02/04/2025",
        "dirEstablecimiento": "Av. Secundaria 456",
        "obligadoContabilidad": "NO",
        "tipoIdentificacionComprador": "05",
        "razonSocialComprador": "Cliente S.A.",
        "identificacionComprador": "1104567890",
        "totalSinImpuestos": "200.00",
        "totalDescuento": "10.00",
        "totalConImpuestos": {
            "totalImpuesto": [
                {
                    "codigo": "2",
                    "codigoPorcentaje": "3",
                    "baseImponible": "190.00",
                    "valor": "19.00"
                }
            ]
        },
        "propina": "0.00",
        "importeTotal": "219.00",
        "moneda": "USD"
    },
    "detalles": {
        "detalle": [
            {
                "codigoPrincipal": "A001",
                "codigoAuxiliar": "B001",
                "descripcion": "Producto A",
                "unidadMedida": "Unidad",
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
                            "valor": "19.00"
                        }
                    ]
                }
            }
        ]
    }
}

# Firmar el XML
manejador = ManejadorXML()
firmado_path = manejador.firmar_y_guardar_xml(json_data=datos_factura)

# Enviar y consultar
with open(firmado_path, "rb") as f:
    xml_firmado = f.read()

sri = SRIService(ambiente="pruebas")
respuesta_recepcion = sri.enviar_recepcion(xml_firmado)

if respuesta_recepcion.estado == "RECIBIDA":
    respuesta_autorizacion = sri.consultar_autorizacion(clave)
    print("✅ XML autorizado:", respuesta_autorizacion)
else:
    print("❌ XML rechazado:", respuesta_recepcion)
```

---

## 🔐 Configuración por defecto

Puedes configurar rutas y parámetros por defecto en:

```
src/fe_ec/utils/constants.py
```

Incluye:

- `DEFAULT_XSD_PATH`
- `DEFAULT_P12_PATH`
- `DEFAULT_P12_PASSWORD`
- `SRI_ENDPOINTS`
- `DEFAULT_AMBIENTE`
- `DEFAULT_TIEMPO_ESPERA`

---

## 🛠 Publicación con Poetry

1. Verifica tu archivo `pyproject.toml`
2. Construye el paquete:

```bash
poetry build
```

3. Publica en PyPI:

```bash
poetry publish --username __token__ --password <TOKEN_AQUI>
```

Requiere que tengas una cuenta en [https://pypi.org](https://pypi.org).

---

## 📞 Contacto

**OpenLatina**
📱 0984228883
📱 0995767370
