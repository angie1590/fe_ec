# Contract: Library Interface for Electronic Documents

## Goal

Extender la API publica actual para soportar notas de credito electronicas sin
alterar la arquitectura ni romper los flujos ya existentes de factura y
retencion.

## Public Runtime Contract

### `fe_ec.constants`

Debe seguir siendo la fuente oficial de configuracion runtime y metadata por
documento.

**Extensiones esperadas**:

- metadata oficial para `nota_credito`
- resolucion explicita del XSD oficial de nota de credito
- override opcional `FEEC_NOTA_CREDITO_XSD_PATH`
- compatibilidad intacta para factura y retencion

### `fe_ec.utils.emisor.EmisorProfile`

Se reutiliza sin cambio arquitectonico.

**Functional contract**:

- encapsula los datos estables del emisor
- construye `infoTributaria` base por `codDoc`
- expone datos comunes de emision para factura, retencion y nota de credito

### `fe_ec.utils.generador_clave_acceso.GeneradorClaveAcceso`

Sin cambio estructural. Debe seguir aceptando `tipo_comprobante` y permitir
`"04"` para nota de credito.

### `fe_ec.utils.manejador_xml.ManejadorXML`

Se reutiliza de forma compatible.

**Planned compatible surface**:

- `document_type="factura"`
- `document_type="retencion"`
- `document_type="nota_credito"`

**Functional contract**:

- usa metadata oficial del documento seleccionado
- genera la raiz XML correcta
- valida contra el XSD correcto
- reutiliza firma y flujo posterior sin cambiar el pipeline

### `fe_ec.utils.nota_credito.NotaCreditoRequest`

Nueva superficie publica para modelar la nota de credito como request tipado.

**Functional contract**:

- representa los datos de negocio de una nota de credito concreta
- convierte esos datos a payload SRI mediante `to_payload(...)`
- valida estructura y datos obligatorios antes de firmar

### `fe_ec.utils.nota_credito_contract`

Nuevo adaptador opcional de entrada.

**Functional contract**:

- admite `dict` y contrato YAML versionado
- traduce datos externos a `NotaCreditoRequest`
- permite que el wrapper de ejemplo siga aceptando fallback compatible cuando
  aplique

### `fe_ec.utils.firmador_xml.FirmadorXML`

Sin cambios de interfaz publica previstos.

### `fe_ec.utils.sri.SRIService`

Sin cambios de interfaz publica previstos.

## Backward Compatibility

- Los consumidores actuales de factura y retencion no deben verse obligados a
  cambiar sus llamadas existentes.
- Los nuevos modelos y contratos de nota de credito deben ser opt-in.
- El wrapper nuevo `test_nota_credito.py` no debe afectar `test2.py` ni
  `test_retencion.py`.
- No se agregan nuevas capas ni nuevos directorios raiz; los modulos nuevos
  viven dentro de `src/fe_ec/utils/`.
