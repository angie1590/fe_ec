# fe_ec_lib 📎

Librería en Python para generar, firmar digitalmente y enviar comprobantes electrónicos al SRI (Ecuador), incluyendo la consulta y validación de autorizaciones. Esta librería está basada en los esquemas XSD oficiales del SRI y firmada bajo el estándar XAdES-BES.

## ⚡ Características

- Generación de clave de acceso según estructura oficial.
- Construcción y validación de XML contra esquema XSD.
- Firma digital XAdES-BES usando certificados .p12.
- Envió a los servicios web del SRI (recepción y autorización).
- Adaptado para funcionar como librería externa y reutilizable.

---

## 📂 Instalación

```bash
pip install fe-ec-lib
```

Si estás trabajando con el repositorio directamente:
```bash
poetry install
```

---

## 🔧 Uso básico

```python
import os

os.environ["FEEC_P12_PATH"] = "firma.p12"
os.environ["FEEC_P12_PASSWORD"] = "123456"
os.environ["FEEC_AMBIENTE"] = "1"

from fe_ec.utils.manejador_xml import ManejadorXML

manejador = ManejadorXML()
manejador.firmar_y_guardar_xml(
    datos_factura,
    output_path=".artifacts/xml/fact_firmado.xml",
)
```

Si prefieres no construir el payload de factura a mano, puedes usar un contrato
YAML:

```bash
poetry run python test2.py --contract contracts/factura.example.yaml
```

Para comprobantes de retencion ATS (`codDoc = 07`):

```python
from fe_ec.utils.manejador_xml import ManejadorXML

manejador = ManejadorXML(document_type="retencion")
manejador.firmar_y_guardar_xml(
    datos_retencion,
    output_path=".artifacts/xml/retencion_firmada.xml",
)
```

Si prefieres no pasar decenas de variables de entorno para una retencion, puedes
usar un contrato YAML y dejar las `FEEC_*` solo para runtime y secretos:

```bash
poetry run python test_retencion.py --contract contracts/retencion.example.yaml
```

El contrato de ejemplo vive en [contracts/retencion.example.yaml](/Users/andrea/Documents/Proyectos/fe_ec/contracts/retencion.example.yaml).
Por defecto, los scripts de prueba dejan sus XML firmados en `.artifacts/xml/`,
que está ignorado por git.


---

## 📁 Estructura del Proyecto

```
fe_ec_lib/
├── src/
│   └── fe_ec/
│       ├── constants.py
│       └── utils/
│           ├── firmador_xml.py
│           ├── sri.py
│           ├── manejador_xml.py
│           ├── generador_clave_acceso.py
│           └── FirmaElectronica/
├── tests/
│   └── test_*.py
├── README.md
├── pyproject.toml
```

> Los archivos de prueba (`test.py`, `firma.p12`, etc.) **no se incluyen** en el empaquetado.


---

## 🔐 Configuración

La librería toma su configuración de runtime desde variables de entorno:

- `FEEC_P12_PATH`: Ruta al archivo `.p12`.
- `FEEC_P12_PASSWORD`: Contraseña del archivo.
- `FEEC_XSD_PATH`: Opcional. Ruta al esquema XML del SRI si quieres sobrescribir el XSD empaquetado.
- `FEEC_FACTURA_XSD_PATH`: Opcional. Sobrescribe el XSD empaquetado de factura.
- `FEEC_RETENCION_XSD_PATH`: Opcional. Sobrescribe el XSD empaquetado de retención ATS 2.0.0.
- `FEEC_AMBIENTE`: `pruebas`, `produccion`, `1` o `2`.
- `FEEC_JAVA_BIN`: Opcional, binario de Java a usar si no quieres depender de `PATH`.

Los datos tributarios del comprobante, especialmente para retenciones, se
recomienda pasarlos como objetos Python o como contrato YAML, no como secretos
ni como configuración global del proceso.


---

## ✅ Validaciones compatibles

- Facturas electrónicas (codDoc = 01)
- Comprobantes de retención ATS (codDoc = 07)
- Firma digital según XAdES-BES
- Validación por XSD oficial del SRI empaquetado en la librería


---

## 🧱 Requisitos

- Python 3.10 - 3.11
- Java 8 recomendado. Con Java 9+ la librería aplica flags de compatibilidad automáticamente.
- Dependencias gestionadas con Poetry


---

## 📤 Compilación de la librería

```bash
poetry build
```

Esto generará el archivo `.whl` que podrá ser usado en otros proyectos.

---

## 📣 Contribuciones

Pull requests, mejoras y correcciones son bienvenidas. Por favor asegúrate de pasar los tests:
```bash
pytest
```

Además, los cambios de comportamiento del paquete deben respetar la constitución
del proyecto en `.specify/memory/constitution.md`: validación SRI explícita,
pruebas automáticas para cambios de cumplimiento, portabilidad de runtime,
manejo seguro de certificados y contraseñas, y prohibición de modificar la
arquitectura del proyecto sin una enmienda previa de la constitución.


---

## 📞 Contacto

**OpenLatina**
📞 0984228883
📞 0995767370
