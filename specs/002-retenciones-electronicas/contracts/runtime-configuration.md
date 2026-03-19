# Contract: Runtime Configuration for Retenciones

## Principle

Toda configuración runtime oficial debe pasar por `src/fe_ec/constants.py`.
Los datos tributarios concretos de factura o retención no forman parte de ese
runtime y deben viajar como requests tipados o contratos YAML versionados.

## Existing variables to preserve

- `FEEC_XSD_PATH`
- `FEEC_P12_PATH`
- `FEEC_P12_PASSWORD`
- `FEEC_AMBIENTE`
- `FEEC_JAVA_BIN`

## Planned explicit variables for multi-document support

- `FEEC_FACTURA_XSD_PATH`
- `FEEC_RETENCION_XSD_PATH`

## Compatibility rules

- Los consumidores actuales de factura siguen funcionando aunque no definan
  variables nuevas.
- La resolución del XSD de retención no debe depender de valores hardcodeados
  fuera de `constants.py`.
- La librería expone llamadas simples al SRI; la política de reintentos,
  polling y backoff corresponde al sistema integrador.
- `constants_copy.py` no forma parte del contrato runtime productivo.
- Los datos de negocio del comprobante no deben quedar atrapados en variables de
  entorno globales cuando exista un request tipado o un contrato YAML oficial.

## Effective resolution order

### Factura

1. `FEEC_FACTURA_XSD_PATH`
2. `FEEC_XSD_PATH` (legacy)
3. XSD empaquetado por defecto de factura

### Retención

1. `FEEC_RETENCION_XSD_PATH`
2. XSD oficial de retención empaquetado por defecto

## Secret handling

- La contraseña del `.p12` sigue viniendo desde `FEEC_P12_PASSWORD`
- No se agregan secretos nuevos hardcodeados
- Los catálogos ATS y datos tributarios del documento deben venir desde el
  integrador o su capa de negocio, no desde constantes sensibles en la librería

## Business Contract Boundary

- `EmisorProfile`, `FacturaRequest` y `RetencionRequest` representan contratos de
  negocio, no runtime global.
- Los contratos YAML (`contracts/*.yaml`) son adaptadores opcionales para esas
  estructuras de negocio.
- La librería debe seguir siendo consumible sin YAML, siempre que se provean los
  requests o payloads equivalentes por código.
