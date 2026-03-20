# Contract: Runtime Configuration for Nota de Credito

## Goal

Documentar el runtime oficial requerido para emitir nota de credito sin mezclar
secretos ni datos tributarios del comprobante.

## Runtime Variables

### Required in real signing/sending flows

- `FEEC_AMBIENTE`
  - Valores validos: `1`, `2`, `pruebas`, `produccion`
- `FEEC_P12_PATH`
  - Ruta del certificado `.p12`
- `FEEC_P12_PASSWORD`
  - Password del certificado

### Document-specific XSD overrides

- `FEEC_FACTURA_XSD_PATH`
- `FEEC_RETENCION_XSD_PATH`
- `FEEC_NOTA_CREDITO_XSD_PATH`
- `FEEC_NOTA_DEBITO_XSD_PATH`
- `FEEC_GUIA_REMISION_XSD_PATH`
- `FEEC_LIQUIDACION_COMPRA_XSD_PATH`

### Legacy compatibility

- `FEEC_XSD_PATH`
  - Alias legacy del flujo de factura

## What stays out of runtime

Los siguientes datos NO deben ir en `constants.py` ni en variables de entorno
como interfaz principal:

- comprador
- comprobante modificado
- motivo
- total sin impuestos
- valor de modificacion
- impuestos del encabezado
- detalles del ajuste
- info adicional del comprobante

Esos datos pertenecen a `NotaCreditoRequest` o a su contrato YAML versionado.

## Behavioral Rules

- La libreria no implementa retries ni polling automatico.
- El runtime define ambiente, firma y XSD efectivos.
- El documento de negocio define el contenido tributario concreto.
- El integrador externo decide su politica de reintentos, backoff y
  observabilidad.

## Packaging Notes

- Los XSD/XML oficiales deben seguir viviendo dentro de
  `src/fe_ec/schemas/<Tipo de Documento>/`.
- `pyproject.toml` ya incluye `src/fe_ec/schemas/**`, por lo que la nota de
  credito debe consumir esos assets empaquetados sin rutas hardcodeadas fuera
  del repo.
