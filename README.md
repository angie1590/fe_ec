# Facturación Electrónica Ecuador (SRI) - Librería Python

Este proyecto proporciona una librería en Python para la **generación, firma electrónica y envío** de comprobantes electrónicos (facturas) al **Servicio de Rentas Internas del Ecuador (SRI)**.

Incluye:
- Generación de la estructura XML basada en la ficha técnica 2.2.6
- Firma electrónica usando un JAR externo
- Envio del comprobante al **Web Service de Recepción**
- Consulta posterior al **Web Service de Autorización**

## 📊 Requisitos

### Python
- Python 3.8 - 3.10 recomendado
- Librerías:
  - `lxml`
  - `xmlschema`
  - `zeep`
  - `cryptography <= 40`
  - `poetry` para la gestión del entorno y dependencias

### Java
- Java 8 obligatorio
- `FirmaElectronica.jar` debe estar ubicado en `utils/`
- Instalar Java 8 y asegurarse de que `java -version` muestra `1.8.*`

### Dependencias adicionales
Instala Poetry si no lo tienes:
```bash
pipx install poetry
```

Instala las dependencias:
```bash
poetry install
```

Activa el entorno:
```bash
poetry shell
```

## 📝 Estructura del Proyecto

```
.
├── src/
│   ├── fe_ec/
│       ├── utils/
│       │   ├── manejador_xml.py
│       │   ├── firmador_xml.py
│       │   ├── sri.py
│       │   ├── config.py
│       │   ├── constants.py
│       │   └── FirmaElectronica.jar
│       └── __init__.py
└── test.py
```

## ✅ Uso Rápido

```bash
poetry run python test.py
```

El archivo `test.py` incluye la generación de una factura con 4 productos distintos (gravado, exento, no IVA, ICE + IVA), la firma del XML y el envío al SRI.

## 🔐 Firma Electrónica
La firma se realiza ejecutando el archivo `FirmaElectronica.jar`. Asegúrese de que Java 8 esté instalado y accesible desde el entorno. La clave del archivo `.p12` se configura en `config.py`.

## 🌐 Web Services SRI
- Recepción: `https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl`
- Autorización: `https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl`

Se usan los servicios del **ambiente de pruebas**, puede cambiarse a producción modificando la variable `AMBIENTE`.

## 🔹 Parametrización
Todos los valores sensibles (ruta del .p12, clave, ambiente, URLs de WS) pueden configurarse en `config.py` o desde un `YAML` externo.

## 🔧 Validación con XSD
Antes de firmar se realiza validación del XML contra el esquema `factura_V2.xsd` del SRI. Si el XML no cumple, se aborta la firma.

## ☑️ Consideraciones
- Todas las fechas deben estar en formato `dd/mm/yyyy`
- Las cantidades y precios deben tener precisión hasta 2 decimales
- Se deben incluir los códigos de impuestos correctos para IVA, ICE, etc.

## 🚀 Futuras mejoras
- Empaquetado como PyPI package
- Validación contra XSD de notas de crédito, retenciones, etc.
- Frontend web para ingreso y emisión de comprobantes

## 📱 Contacto

**OpenLatina**
📞 0984228883
📞 0995767370

