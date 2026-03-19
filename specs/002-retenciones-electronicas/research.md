# Research: Emision de Comprobantes de Retencion Electronicos

## Decision 1: La referencia normativa base es el Anexo 10 del comprobante de retención ATS

**Decision**: Implementar la funcionalidad contra el formato oficial del
comprobante de retención ATS versión `2.0.0` (`codDoc 07`), tomando como fuente
normativa base la ficha técnica offline `v2.32` entregada por el usuario.

**Rationale**: La documentación oficial del SRI describe el comprobante de
retención ATS como `comprobanteRetencion id="comprobante" version="2.0.0"` y
lo ubica como anexo específico para retenciones ATS. El documento oficial más
reciente del proyecto debe primar sobre cualquier ejemplo de terceros.

**Alternatives considered**:

- Reutilizar formatos previos de retención: descartado por riesgo regulatorio.
- Diseñar el payload desde ejemplos de terceros: descartado por falta de
  autoridad normativa.

## Decision 2: Reutilizar el pipeline actual completo de emisión electrónica

**Decision**: Extender el pipeline actual en lugar de crear una vía nueva para
retenciones.

**Rationale**: `GeneradorClaveAcceso`, `ManejadorXML`, `FirmadorXML` y
`SRIService` ya resuelven las etapas del ciclo electrónico. La retención cambia
la estructura XML y `codDoc`, pero no el modelo operativo general ni los
endpoints del SRI.

**Alternatives considered**:

- Crear un módulo independiente solo para retenciones: descartado por violar la
  preservación de arquitectura y duplicar comportamiento.
- Crear un segundo cliente SRI: descartado porque los servicios de recepción y
  autorización son los mismos.

## Decision 3: Extender `constants.py` como contrato oficial de configuración

**Decision**: Mantener toda la configuración runtime oficial en `src/fe_ec/constants.py`
y no utilizar `constants_copy.py` para lógica productiva.

**Rationale**: El usuario pidió expresamente evitar hard-code y centralizar
configuración en el archivo oficial. Además, `constants_copy.py` contiene
valores hardcodeados y no debe convertirse en la referencia de runtime.

**Planned configuration strategy**:

- Mantener `FEEC_XSD_PATH` como alias legacy para factura si hace falta
  compatibilidad.
- Agregar variables explícitas por documento, por ejemplo:
  - `FEEC_FACTURA_XSD_PATH`
  - `FEEC_RETENCION_XSD_PATH`
- Definir metadata documental centralizada:
  - tag raíz
  - versión XML
  - `codDoc`
  - ruta XSD efectiva

**Alternatives considered**:

- Seguir con un único `XSD_PATH` genérico: descartado por ambigüedad al soportar
  más de un documento.
- Hardcodear rutas en `manejador_xml.py`: descartado por romper el contrato de
  configuración oficial.

## Decision 4: Parametrizar `ManejadorXML` por tipo de documento

**Decision**: Convertir `ManejadorXML` en un serializador parametrizado por tipo
de documento, conservando el comportamiento actual por defecto para factura.

**Rationale**: Hoy `dict_a_xml_string` fija la raíz `factura`, la versión
`2.0.0` y una ruta XSD única. Para retención ATS esto debe depender del tipo de
documento sin requerir una nueva clase arquitectónica.

**Alternatives considered**:

- Crear `ManejadorRetencionXML`: descartado por duplicación de flujo.
- Crear una factoría o capa de servicios nueva: descartado por violar la regla
  de preservación arquitectónica.

## Decision 5: Reemplazar la heurística de singularización por un mapeo explícito

**Decision**: Introducir un mapeo explícito de contenedor → ítem repetible
dentro del serializador actual para documentos que no siguen pluralizaciones
simples.

**Rationale**: La lógica actual solo resuelve bien algunos casos de factura.
Para retención ATS fallaría en secciones oficiales como:

- `docsSustento` → `docSustento`
- `impuestosDocSustento` → `impuestoDocSustento`
- `retenciones` → `retencion`
- `reembolsos` → `reembolsoDetalle`
- `detalleImpuestos` → `detalleImpuesto`
- `Pagos` → `Pago`

Sin este cambio, el XML generado no coincidiría con el anexo oficial.

**Alternatives considered**:

- Mantener singularización por cortar la última `s`: descartado por producir
  tags incorrectos.
- Resolver con payloads artificiales altamente anidados solo para complacer al
  serializador: descartado por fragilidad y mala ergonomía.

## Decision 6: Tratar las tablas ATS como datos externos del negocio

**Decision**: La biblioteca validará estructura, presencia de campos y
compatibilidad XSD, pero no embebirá masivamente todos los catálogos ATS como
constantes duras del código en esta primera extensión.

**Rationale**: Los catálogos ATS cambian y la fuente oficial es externa. El
valor principal de la librería aquí es generar el XML exacto y validar su
estructura; los códigos de sustento, retención, países o formas de pago deben
ser suministrados por el integrador conforme al catálogo oficial vigente.

**Alternatives considered**:

- Hardcodear todas las tablas ATS: descartado por mantenimiento alto y riesgo de
  obsolescencia regulatoria.
- No validar nada estructural: descartado porque la librería debe proteger el
  flujo antes de firmar/enviar.

## Decision 7: Reusar `GeneradorClaveAcceso` con `codDoc 07`

**Decision**: No crear un generador nuevo de clave de acceso.

**Rationale**: El algoritmo ya es genérico; solo requiere el `tipo_comprobante`
adecuado (`07`) y la configuración estándar de fecha, ruc, ambiente, serie,
secuencial y tipo de emisión.

**Alternatives considered**:

- Duplicar el generador para retenciones: descartado por innecesario.

## Decision 8: Mantener `SRIService` y `FirmadorXML` sin cambio estructural

**Decision**: Retención usará el mismo firmador y el mismo cliente SRI.

**Rationale**: La diferencia entre factura y retención está en el contenido XML,
no en el estándar de firma ni en la pareja de endpoints de recepción y
autorización.

**Alternatives considered**:

- Introducir condicionales de red específicos para retención: descartado por no
  aportar valor técnico.

## Decision 9: Añadir cobertura de regresión para factura y para el nuevo XML de retención

**Decision**: La implementación debe venir acompañada de tests unitarios y de
flujo para:

- metadata/configuración por documento
- generación de XML de retención
- validación contra el XSD oficial
- conservación del flujo actual de factura
- smoke opcional de firma cuando exista certificado

**Rationale**: El riesgo principal no es solo "emitir retención", sino romper
factura o generar tags XML incorrectos por la nueva parametrización.

**Alternatives considered**:

- Confiar solo en validación manual: descartado por la constitución del
  proyecto.

## Hallazgos normativos relevantes

- La raíz oficial es `comprobanteRetencion` con `version="2.0.0"`.
- `infoTributaria` incluye `codDoc 07`.
- `infoCompRetencion` contiene, entre otros, `fechaEmision`,
  `dirEstablecimiento`, `contribuyenteEspecial`, `obligadoContabilidad`,
  `tipoIdentificacionSujetoRetenido`, `razonSocialSujetoRetenido`,
  `identificacionSujetoRetenido` y `periodoFiscal`.
- `docsSustento/docSustento` es bloque obligatorio.
- `retenciones/retencion` es una sección con campos obligatorios cuando se
  incluye.
- `reembolsos` es obligatorio cuando `codDocSustento = 41`.
- `Pagos/Pago` forma parte de la estructura oficial del documento.

