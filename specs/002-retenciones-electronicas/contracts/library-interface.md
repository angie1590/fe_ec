# Contract: Library Interface for Electronic Documents

## Goal

Extender la API pública existente de forma compatible para soportar retenciones
ATS y alinear factura/retención bajo el mismo patrón de requests tipados y
contratos YAML opcionales, sin alterar la arquitectura ni romper factura
electrónica.

## Public Runtime Contract

### `fe_ec.constants`

Debe seguir siendo la fuente oficial de configuración y metadata runtime.

**Extensiones esperadas**:

- metadata por tipo de documento
- resolución explícita del XSD de retención
- compatibilidad hacia atrás para factura
- separación entre runtime y datos de negocio por comprobante

**Compatibility rule**:

- el contrato existente usado por factura debe seguir funcionando sin cambios
  obligatorios para integradores actuales

### `fe_ec.utils.emisor.EmisorProfile`

Nuevo perfil común reutilizable para datos estables del emisor.

**Functional contract**:

- encapsula RUC, razón social, establecimiento, punto de emisión y direcciones
- construye `infoTributaria` base por `codDoc`
- expone datos comunes de emisión sin mezclar runtime con datos transaccionales

### `fe_ec.utils.generador_clave_acceso.GeneradorClaveAcceso`

Sin cambio estructural. Debe seguir aceptando `tipo_comprobante` y permitir
`"07"` para retención.

### `fe_ec.utils.manejador_xml.ManejadorXML`

Debe extenderse de forma compatible para aceptar el tipo de documento a emitir.

**Planned compatible surface**:

- comportamiento por defecto conserva factura
- nuevo selector de documento:
  - `document_type="factura"` (default)
  - `document_type="retencion"`

**Functional contract**:

- usa metadata oficial del documento seleccionado
- genera la raíz XML correcta
- valida contra el XSD correcto
- reutiliza firma y flujo posterior sin cambiar el pipeline

### `fe_ec.utils.factura.FacturaRequest`

Nueva superficie compatible para modelar factura como request tipado.

**Functional contract**:

- representa los datos de negocio de una factura concreta
- convierte esos datos a payload SRI mediante `to_payload(...)`
- no reemplaza el pipeline existente; lo alimenta

### `fe_ec.utils.factura_contract`

Adaptador opcional de entrada para factura.

**Functional contract**:

- admite `dict` y contrato YAML versionado
- traduce datos externos a `FacturaRequest`
- mantiene compatibilidad con wrappers que todavía usan `FEEC_*`

### `fe_ec.utils.retencion.RetencionRequest` / `fe_ec.utils.retencion_contract`

Superficie equivalente para retención.

**Functional contract**:

- modela la retención como contrato explícito de negocio
- admite adaptador YAML versionado
- preserva fallback compatible para los scripts actuales

### `fe_ec.utils.firmador_xml.FirmadorXML`

Sin cambios de interfaz pública previstos.

### `fe_ec.utils.sri.SRIService`

Sin cambios de interfaz pública previstos.

## Backward Compatibility

- Los consumidores actuales de factura no deben verse obligados a cambiar sus
  llamadas existentes.
- Cualquier parámetro, request model o contrato nuevo debe ser opcional o tener
  un default compatible.
- Los wrappers existentes (`test2.py`, `test_retencion.py`) conservan fallback
  por variables de entorno.
- No se agregan nuevos puntos de entrada arquitectónicos; los módulos nuevos
  viven dentro de `src/fe_ec/utils/`.
