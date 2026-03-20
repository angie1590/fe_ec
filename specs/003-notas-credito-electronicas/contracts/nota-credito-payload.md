# Contract: Nota de Credito Business Payload

## Purpose

Definir el contrato de negocio versionado para construir una nota de credito
electronica oficial sin mezclar runtime, secretos ni paths sensibles.

## YAML Shape

```yaml
version: 1
nota_credito:
  secuencial: "000000123"
  fecha_emision: "19/03/2026"
  tipo_emision: "1"
  output_xml: ".artifacts/xml/nota_credito_firmada.xml"
  emisor:
    ruc: "0103523908001"
    razon_social: "PINEDA ALVAREZ DANIEL FERNANDO"
    nombre_comercial: "PINEDA ALVAREZ DANIEL FERNANDO"
    estab: "001"
    pto_emi: "001"
    dir_matriz: "Cuenca"
    dir_establecimiento: "Cuenca"
    obligado_contabilidad: "NO"
  comprador:
    tipo_identificacion: "04"
    razon_social: "CLIENTE DE PRUEBA"
    identificacion: "0195125988001"
  comprobante_modificado:
    cod_doc_modificado: "01"
    num_doc_modificado: "001-001-000000321"
    fecha_emision_doc_sustento: "18/03/2026"
  total_sin_impuestos: "100.00"
  valor_modificacion: "115.00"
  moneda: "DOLAR"
  total_con_impuestos:
    - codigo: "2"
      codigo_porcentaje: "4"
      base_imponible: "100.00"
      valor: "15.00"
  compensaciones:
    - codigo: "1"
      tarifa: "0.00"
      valor: "0.00"
  motivo: "DEVOLUCION PARCIAL"
  detalles:
    - codigo_interno: "A001"
      codigo_adicional: "ALT-A001"
      descripcion: "Producto ajustado"
      cantidad: "1.00"
      precio_unitario: "100.00"
      descuento: "0.00"
      precio_total_sin_impuesto: "100.00"
      detalles_adicionales:
        - nombre: "lote"
          valor: "ABC-01"
      impuestos:
        - codigo: "2"
          codigo_porcentaje: "4"
          tarifa: "15.00"
          base_imponible: "100.00"
          valor: "15.00"
  info_adicional:
    - nombre: "email"
      valor: "cliente@ejemplo.com"
```

## Field Mapping

### `nota_credito.emisor`

Mapea a:

- `infoTributaria`
- campos comunes de emision derivados por `EmisorProfile`

### `nota_credito.comprador`

Mapea a:

- `infoNotaCredito.tipoIdentificacionComprador`
- `infoNotaCredito.razonSocialComprador`
- `infoNotaCredito.identificacionComprador`

### `nota_credito.comprobante_modificado`

Mapea a:

- `infoNotaCredito.codDocModificado`
- `infoNotaCredito.numDocModificado`
- `infoNotaCredito.fechaEmisionDocSustento`

### `nota_credito.total_con_impuestos[]`

Mapea a:

- `infoNotaCredito.totalConImpuestos.totalImpuesto[]`

### `nota_credito.compensaciones[]`

Mapea a:

- `infoNotaCredito.compensaciones.compensacion[]`

### `nota_credito.detalles[]`

Mapea a:

- `detalles.detalle[]`

Submapeos:

- `detalles_adicionales[]` -> `detallesAdicionales.detAdicional[]`
- `impuestos[]` -> `impuestos.impuesto[]`

## Validation Rules

- `version` debe ser `1`
- `motivo` es singular y obligatorio
- `total_con_impuestos` debe contener al menos un item
- `detalles` debe contener al menos un item
- `num_doc_modificado` debe mantener el formato oficial con guiones
- `output_xml` pertenece al contrato operativo del wrapper, no al runtime
- El contrato no debe incluir secretos, password del `.p12` ni endpoints

## Compatibility Notes

- El contrato YAML es opcional; el request tipado Python es la interfaz
  principal de la libreria.
- El wrapper de ejemplo puede aceptar fallback por variables de entorno cuando
  sea necesario, pero los datos de negocio deben vivir preferentemente aqui.
