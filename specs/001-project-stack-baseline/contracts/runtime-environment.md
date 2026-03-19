# Contract: Runtime and Environment

## Environment Variables

### Core package variables

- `FEEC_XSD_PATH`: ruta alternativa al XSD del SRI
- `FEEC_P12_PATH`: ruta al certificado `.p12`
- `FEEC_P12_PASSWORD`: contraseña del `.p12`
- `FEEC_AMBIENTE`: `pruebas`, `produccion`, `1` o `2`
- `FEEC_JAVA_BIN`: binario Java alternativo

### Example-script variables

- `FEEC_RUC`
- `FEEC_ESTAB`
- `FEEC_PTO_EMI`
- `FEEC_SECUENCIAL`
- `FEEC_FECHA_EMISION`
- `FEEC_TIPO_EMISION`
- `FEEC_OUTPUT_XML`

## External Runtime Dependencies

- Python compatible con `>=3.10,<3.12`
- Java 8 recomendado; Java 9+ soportado mediante flags de compatibilidad
- Conectividad HTTPS hacia:
  - `https://celcer.sri.gob.ec/...`
  - `https://cel.sri.gob.ec/...`

## Local File Dependencies

- `src/fe_ec/schemas/factura_V1_1.xsd`
- `src/fe_ec/utils/FirmaElectronica/FirmaElectronica.jar`
- `src/fe_ec/utils/FirmaElectronica/lib/*`
- archivo `.p12` suministrado por el integrador

## Runtime Failure Contract

- Si Java no existe: `RuntimeError`
- Si no existe el XML a firmar: `RuntimeError`
- Si falta el `.p12`: `RuntimeError`
- Si falta `FEEC_P12_PASSWORD`: `RuntimeError`
- Si el XML es inválido contra XSD: retorno `False` en validación y `None` en
  `firmar_y_guardar_xml`
- Si falla SOAP con SRI: `RuntimeError` o `ValueError` desde `SRIService`

## Distribution Notes

- El sdist visible incluye el bundle Java auxiliar completo.
- La wheel visible parece incluir solo `FirmaElectronica.jar` sin el directorio
  `lib/`, lo que debe tratarse como riesgo de compatibilidad hasta confirmar el
  proceso de publicación final.
