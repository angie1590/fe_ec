# Data Model: Emision de Comprobantes de Retencion Electronicos

## 1. DocumentTypeConfig

- **Purpose**: Define la metadata oficial de cada tipo de documento soportado por
  la librería sin cambiar la arquitectura.
- **Fields**:
  - `document_type`: `factura` | `retencion`
  - `cod_doc`
  - `root_tag`
  - `xml_version`
  - `effective_xsd_path`
  - `repeated_tag_map`
- **Validation rules**:
  - `retencion` debe resolver `cod_doc = "07"`
  - `root_tag` para retención debe ser `comprobanteRetencion`
  - `xml_version` para retención debe ser `2.0.0`

## 2. RetencionPayload

- **Purpose**: Agregado principal de datos para construir el comprobante de
  retención.
- **Fields**:
  - `infoTributaria`
  - `infoCompRetencion`
  - `docsSustento`
  - `infoAdicional` (opcional)
- **Relationships**:
  - Contiene uno o más `DocSustento`
  - Usa `DocumentTypeConfig`

## 3. InfoTributaria

- **Purpose**: Identificación tributaria estándar del comprobante.
- **Fields**:
  - `ambiente`
  - `tipoEmision`
  - `razonSocial`
  - `nombreComercial` (opcional)
  - `ruc`
  - `claveAcceso`
  - `codDoc`
  - `estab`
  - `ptoEmi`
  - `secuencial`
  - `dirMatriz`
- **Validation rules**:
  - `codDoc` debe ser `07` para retención
  - `claveAcceso` debe tener 49 dígitos

## 4. InfoCompRetencion

- **Purpose**: Encabezado funcional específico del comprobante de retención ATS.
- **Fields**:
  - `fechaEmision`
  - `dirEstablecimiento` (opcional)
- `contribuyenteEspecial` (opcional)
- `obligadoContabilidad` (opcional)
- `tipoIdentificacionSujetoRetenido`
- `tipoSujetoRetenido` (opcional)
- `parteRel` (cuando corresponda)
- `razonSocialSujetoRetenido`
- `identificacionSujetoRetenido`
  - `periodoFiscal`
- **Validation rules**:
  - `fechaEmision` usa formato `dd/mm/aaaa`
  - `periodoFiscal` usa formato `mm/aaaa`

## 5. DocSustento

- **Purpose**: Documento base sobre el que se practica la retención.
- **Fields**:
  - `codSustento`
  - `codDocSustento`
  - `numDocSustento` (cuando corresponda)
  - `fechaEmisionDocSustento`
  - `fechaRegistroContable` (opcional)
  - `numAutDocSustento` (opcional)
  - `pagoLocExt`
  - `tipoRegi` (condicional)
  - `paisEfecPago` (condicional)
  - `aplicConvDobTrib` (condicional)
  - `pagExtSujRetNorLeg` (condicional)
  - `pagoRegFis` (condicional según caso ATS)
  - `totalComprobantesReembolso` (condicional)
  - `totalBaseImponibleReembolso` (condicional)
  - `totalImpuestoReembolso` (condicional)
  - `totalSinImpuestos`
  - `importeTotal`
  - `impuestosDocSustento`
  - `retenciones`
  - `reembolsos` (condicional)
  - `pagos`
- **Relationships**:
  - Contiene uno o más `ImpuestoDocSustento`
  - Contiene una o más `RetencionItem`
  - Puede contener `ReembolsoDetalle`
  - Contiene uno o más `Pago`

## 6. ImpuestoDocSustento

- **Purpose**: Impuesto informado en el documento sustento.
- **Fields**:
  - `codImpuestoDocSustento`
  - `codigoPorcentaje`
  - `baseImponible`
  - `tarifa`
  - `valorImpuesto`

## 7. RetencionItem

- **Purpose**: Línea individual retenida dentro del comprobante.
- **Fields**:
  - `codigo`
  - `codigoRetencion`
  - `baseImponible`
  - `porcentajeRetener`
  - `valorRetenido`
  - `dividendos` (condicional)
  - `compraCajBanano` (condicional)
- **Validation rules**:
  - Todos sus campos son obligatorios cuando la línea se incluye
  - `dividendos` es obligatorio en los casos condicionados por `codSustento`

## 8. Dividendos

- **Purpose**: Bloque ATS condicionado para retenciones asociadas a dividendos.
- **Fields**:
  - `fechaPagoDiv`
  - `imRentaSoc`
  - `ejerFisUtDiv`

## 9. ReembolsoDetalle

- **Purpose**: Detalle de reembolso asociado a documentos sustento específicos.
- **Fields**:
  - `tipoIdentificacionProveedorReembolso`
  - `identificacionProveedorReembolso`
  - `codPaisPagoProveedorReembolso`
- `tipoProveedorReembolso`
- `codDocReembolso`
- `estabDocReembolso`
- `ptoEmiDocReembolso`
- `secuencialDocReembolso`
- `fechaEmisionDocReembolso`
  - `numeroAutorizacionDocReemb`
  - `detalleImpuestos`
- **Validation rules**:
  - Es obligatorio cuando `codDocSustento = 41`

## 10. DetalleImpuestoReembolso

- **Purpose**: Impuesto individual reportado dentro de un reembolso.
- **Fields**:
  - `codigo`
  - `codigoPorcentaje`
  - `tarifa`
  - `baseImponibleReembolso`
  - `impuestoReembolso`

## 11. Pago

- **Purpose**: Medio de pago reportado dentro del documento sustento.
- **Fields**:
  - `formaPago`
  - `total`

## 12. InfoAdicionalField

- **Purpose**: Campo adicional libre del comprobante.
- **Fields**:
  - `nombre`
  - `valor`
