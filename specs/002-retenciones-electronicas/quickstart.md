# Quickstart: Implementacion de Retenciones ATS

## 1. Preparar assets oficiales y entorno

Colocar el XSD oficial de retención ATS del SRI dentro de
`src/fe_ec/schemas/` y definir, cuando aplique:

```bash
export FEEC_RETENCION_XSD_PATH=src/fe_ec/schemas/retencion_ats_v2_0_0.xsd
export FEEC_P12_PATH=firma.p12
export FEEC_P12_PASSWORD='***'
export FEEC_AMBIENTE=1
```

Compatibilidad requerida:

- `FEEC_XSD_PATH` se conserva para el flujo legacy de factura
- la ruta oficial nueva para retención debe vivir en `constants.py`

## 2. Extender el contrato de configuración oficial

Objetivo técnico:

- resolver metadata por documento en `src/fe_ec/constants.py`
- mantener defaults oficiales para factura y retención
- no usar `constants_copy.py` para runtime

## 3. Parametrizar el generador XML existente

Objetivo técnico:

- permitir `document_type="retencion"` sin romper el default actual de factura
- generar la raíz `comprobanteRetencion`
- aplicar la versión `2.0.0`
- usar el XSD oficial de retención
- serializar correctamente:
  - `docsSustento/docSustento`
  - `impuestosDocSustento/impuestoDocSustento`
  - `retenciones/retencion`
  - `reembolsos/reembolsoDetalle`
  - `detalleImpuestos/detalleImpuesto`
  - `Pagos/Pago`

## 4. Validar con un payload mínimo completo

Después de implementar, el flujo esperado debe permitir algo equivalente a:

```python
from fe_ec.utils.generador_clave_acceso import GeneradorClaveAcceso
from fe_ec.utils.manejador_xml import ManejadorXML

clave = GeneradorClaveAcceso.generar(
    fecha_emision="13/03/2026",
    tipo_comprobante="07",
    ruc="1792146739001",
    tipo_ambiente="1",
    serie="001001",
    secuencial="000000001",
    tipo_emision="1",
)

manejador = ManejadorXML(document_type="retencion")
signed_path = manejador.firmar_y_guardar_xml(payload_retencion, "retencion_firmada.xml")
```

## 5. Verificar regresión y cobertura

```bash
poetry run python -m unittest discover -q
```

La validación debe cubrir:

- factura sigue funcionando igual
- retención genera XML con tags correctos
- retención valida contra XSD oficial
- fallos por datos incompletos se detectan antes de firmar

## 6. Validar flujo operacional reutilizado

Una vez generado y firmado el XML de retención, el documento debe poder entrar
al mismo flujo de recepción/autorización del SRI ya usado por factura, sin crear
clientes ni servicios paralelos.
