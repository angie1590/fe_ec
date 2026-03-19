# Contract: Retencion Payload

## Payload Shape

El payload lógico de retención debe expresarse como un `dict` compatible con el
serializador existente extendido.

## Top-level keys

- `infoTributaria`
- `infoCompRetencion`
- `docsSustento`
- `infoAdicional` (opcional)

## Expected document structure

### `infoTributaria`

Campos requeridos:

- `ambiente`
- `tipoEmision`
- `razonSocial`
- `ruc`
- `claveAcceso`
- `codDoc` = `07`
- `estab`
- `ptoEmi`
- `secuencial`
- `dirMatriz`

Campos opcionales:

- `nombreComercial`

### `infoCompRetencion`

Campos requeridos:

- `fechaEmision`
- `periodoFiscal`

Campos esperados según caso:

- `dirEstablecimiento`
- `contribuyenteEspecial`
- `obligadoContabilidad`
- `tipoIdentificacionSujetoRetenido`
- `tipoSujetoRetenido`
- `parteRel`
- `razonSocialSujetoRetenido`
- `identificacionSujetoRetenido`

### `docsSustento`

Debe contener una lista de `docSustento`.

Cada `docSustento` puede incluir:

- `codSustento`
- `codDocSustento`
- `numDocSustento`
- `fechaEmisionDocSustento`
- `fechaRegistroContable`
- `numAutDocSustento`
- `pagoLocExt`
- `tipoRegi`
- `paisEfecPago`
- `aplicConvDobTrib`
- `pagExtSujRetNorLeg`
- `pagoRegFis`
- `totalComprobantesReembolso`
- `totalBaseImponibleReembolso`
- `totalImpuestoReembolso`
- `totalSinImpuestos`
- `importeTotal`
- `impuestosDocSustento`
- `retenciones`
- `reembolsos`
- `pagos`

### `impuestosDocSustento`

Debe contener una lista de `impuestoDocSustento`.

Cada elemento incluye:

- `codImpuestoDocSustento`
- `codigoPorcentaje`
- `baseImponible`
- `tarifa`
- `valorImpuesto`

### `retenciones`

Debe contener una lista de `retencion`.

Cada `retencion` incluye:

- `codigo`
- `codigoRetencion`
- `baseImponible`
- `porcentajeRetener`
- `valorRetenido`
- `dividendos` (cuando corresponda)
- `compraCajBanano` (cuando corresponda)

### `reembolsos`

Condicional según `codDocSustento`.

Debe contener una lista de `reembolsoDetalle`.

### `pagos`

Debe contener una lista de `pago` con:

- `formaPago`
- `total`

## Validation Contract

- El serializador debe rechazar payloads que omitan bloques obligatorios.
- Los tags emitidos deben coincidir exactamente con la forma oficial del anexo.
- Los datos de catálogos ATS deben llegar ya resueltos por el integrador.
