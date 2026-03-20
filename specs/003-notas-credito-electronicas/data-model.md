# Data Model: Emision de Notas de Credito Electronicas

## 1. DocumentTypeConfig

- **Purpose**: Define la metadata oficial de cada tipo de documento soportado
  por la libreria sin alterar la arquitectura.
- **Fields**:
  - `document_type`: `factura` | `retencion` | `nota_credito`
  - `cod_doc`
  - `root_tag`
  - `xml_version`
  - `effective_xsd_path`
  - `container_item_map`
  - `repeated_item_tags`
- **Validation rules**:
  - `nota_credito` debe resolver `cod_doc = "04"`
  - `root_tag` para nota de credito debe ser `notaCredito`
  - `xml_version` para nota de credito debe ser `1.1.0`

## 2. NotaCreditoRequest

- **Purpose**: Agregado principal de datos de negocio para construir una nota
  de credito electronica.
- **Fields**:
  - `secuencial`
  - `fecha_emision`
  - `tipo_emision`
  - `emisor`
  - `comprador`
  - `comprobante_modificado`
  - `total_sin_impuestos`
  - `valor_modificacion`
  - `total_con_impuestos`
  - `detalles`
  - `motivo`
  - `moneda` (opcional, default `DOLAR`)
  - `compensaciones` (opcional)
  - `info_adicional` (opcional)
  - `output_xml`
- **Relationships**:
  - Usa `EmisorProfile`
  - Contiene un `CompradorNotaCredito`
  - Contiene un `ComprobanteModificado`
  - Contiene uno o mas `DetalleNotaCredito`
  - Contiene uno o mas `TotalImpuestoNotaCredito`

## 3. CompradorNotaCredito

- **Purpose**: Representa al receptor del comprobante ajustado.
- **Fields**:
  - `tipo_identificacion`
  - `razon_social`
  - `identificacion`
- **Validation rules**:
  - Todos los campos son obligatorios
  - Debe mapear a `tipoIdentificacionComprador`,
    `razonSocialComprador`, `identificacionComprador`

## 4. ComprobanteModificado

- **Purpose**: Identifica el documento original que la nota de credito corrige.
- **Fields**:
  - `cod_doc_modificado`
  - `num_doc_modificado`
  - `fecha_emision_doc_sustento`
- **Validation rules**:
  - `cod_doc_modificado` debe ser un codigo tributario valido del SRI
  - `num_doc_modificado` debe conservar formato `###-###-#########`
  - `fecha_emision_doc_sustento` usa formato `DD/MM/AAAA`

## 5. TotalImpuestoNotaCredito

- **Purpose**: Resume impuestos del encabezado en `totalConImpuestos`.
- **Fields**:
  - `codigo`
  - `codigo_porcentaje`
  - `base_imponible`
  - `valor`
  - `valor_devolucion_iva` (opcional)
- **Validation rules**:
  - Debe existir al menos un item en `totalConImpuestos.totalImpuesto`

## 6. CompensacionNotaCredito

- **Purpose**: Representa una compensacion oficial opcional dentro del
  encabezado.
- **Fields**:
  - `codigo`
  - `tarifa`
  - `valor`
- **Validation rules**:
  - Solo se incluye cuando el caso tributario realmente lo requiere

## 7. DetalleNotaCredito

- **Purpose**: Linea individual del ajuste documentado por la nota de credito.
- **Fields**:
  - `codigo_interno` (opcional)
  - `codigo_adicional` (opcional)
  - `descripcion`
  - `cantidad`
  - `precio_unitario`
  - `descuento` (opcional)
  - `precio_total_sin_impuesto`
  - `detalles_adicionales` (opcional)
  - `impuestos`
- **Relationships**:
  - Contiene cero o mas `DetalleAdicionalNotaCredito`
  - Contiene cero o mas `ImpuestoDetalleNotaCredito`
- **Validation rules**:
  - Debe existir al menos un detalle en la nota de credito
  - `descripcion`, `cantidad`, `precio_unitario` y
    `precio_total_sin_impuesto` son obligatorios

## 8. DetalleAdicionalNotaCredito

- **Purpose**: Atributo adicional opcional de un detalle.
- **Fields**:
  - `nombre`
  - `valor`
- **Validation rules**:
  - Maximo 3 por detalle segun el XSD oficial

## 9. ImpuestoDetalleNotaCredito

- **Purpose**: Impuesto individual asociado a un detalle.
- **Fields**:
  - `codigo`
  - `codigo_porcentaje`
  - `tarifa`
  - `base_imponible`
  - `valor`
- **Validation rules**:
  - Es opcional por detalle, pero cuando se incluye debe ser completo

## 10. CampoAdicionalNotaCredito

- **Purpose**: Campo libre de `infoAdicional`.
- **Fields**:
  - `nombre`
  - `valor`
- **Validation rules**:
  - Maximo 15 campos por comprobante

## 11. Payload NotaCredito

- **Purpose**: Estructura final que consume `ManejadorXML`.
- **Fields**:
  - `infoTributaria`
  - `infoNotaCredito`
  - `detalles`
  - `infoAdicional` (opcional)
- **Validation rules**:
  - `infoNotaCredito.motivo` es singular y obligatorio
  - `infoNotaCredito.valorModificacion` es obligatorio
  - `detalles.detalle` debe contener al menos un item
