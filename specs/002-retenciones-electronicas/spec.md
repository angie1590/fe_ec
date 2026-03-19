# Feature Specification: Emision de Comprobantes de Retencion Electronicos

**Feature Branch**: `002-retenciones-electronicas`  
**Created**: 2026-03-13  
**Last Updated**: 2026-03-19  
**Status**: Implemented  
**Input**: User description: "Definir la nueva funcionalidad para emitir comprobantes de retención electrónicos según la documentación oficial del SRI, reutilizando todo el flujo ya implementado para factura electrónica, respetando estrictamente la arquitectura vigente, evitando hard-code y manteniendo la configuración externalizada mediante el contrato oficial del proyecto."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Emitir retenciones oficiales validas (Priority: P1)

Como emisor obligado a generar documentos tributarios electrónicos, necesito
emitir comprobantes de retención electrónicos que coincidan con la estructura
oficial del SRI para que tengan validez tributaria y puedan ser procesados sin
rechazos por formato.

**Why this priority**: La retención electrónica es un documento tributario
oficial; si la estructura no coincide exactamente con la especificación del SRI,
el documento pierde valor operativo y tributario.

**Independent Test**: Con información completa y válida, el usuario puede
generar un comprobante de retención electrónico cuya estructura corresponde al
formato oficial del SRI y queda listo para firma y validación.

**Acceptance Scenarios**:

1. **Given** un agente de retención con toda la información obligatoria del
   emisor, del sujeto retenido y del documento sustento, **When** genera un
   comprobante de retención electrónico, **Then** obtiene un documento con el
   formato oficial de comprobante de retención ATS del SRI.
2. **Given** una retención con múltiples conceptos retenidos permitidos por el
   formato oficial, **When** se genera el comprobante, **Then** todos los
   conceptos quedan incluidos con su información tributaria y documental
   correspondiente.

---

### User Story 2 - Operar la retencion con el mismo flujo actual (Priority: P2)

Como usuario del sistema de emisión existente, necesito que la retención
electrónica siga el mismo flujo operativo general que hoy ya uso para factura
electrónica para no introducir un proceso paralelo ni una forma distinta de
trabajo.

**Why this priority**: La nueva capacidad debe integrarse al proceso actual de
emisión electrónica sin cambiar la forma en que el proyecto ya genera, firma y
prepara documentos tributarios.

**Independent Test**: El usuario puede recorrer el ciclo de emisión de la
retención desde la generación del XML hasta dejarla lista para envío y consulta,
sin depender de un flujo separado del ya existente.

**Acceptance Scenarios**:

1. **Given** una retención electrónica correctamente estructurada, **When** el
   usuario completa el flujo normal de emisión, **Then** el documento queda
   listo para firma, transmisión y consulta bajo el mismo modelo operativo de
   los comprobantes ya soportados.
2. **Given** que el usuario trabaja en ambiente de pruebas o producción,
   **When** emite la retención electrónica, **Then** el documento se genera
   respetando el ambiente tributario configurado para la operación.

---

### User Story 3 - Configurar la emision sin tocar el codigo (Priority: P3)

Como mantenedor e integrador del proyecto, necesito que la funcionalidad de
retención electrónica separe claramente la configuración runtime del sistema de
los datos tributarios del comprobante y no dependa de valores hard-codeados
para poder operar distintos ambientes y emisores sin editar el código fuente.

**Why this priority**: La emisión tributaria real exige cambiar ambientes,
certificados, rutas y parámetros operativos sin riesgo de introducir cambios
manuales en el código.

**Independent Test**: Un integrador puede preparar la emisión de retenciones
electrónicas ajustando solo el runtime oficial y el contrato de negocio del
comprobante, sin modificar la arquitectura ni editar valores embebidos en el
código.

**Acceptance Scenarios**:

1. **Given** un nuevo emisor o un cambio de ambiente tributario, **When** el
   integrador actualiza el runtime oficial y/o el contrato del comprobante,
   **Then** la emisión de retenciones se adapta sin requerir cambios en la
   arquitectura ni hard-code adicional.
2. **Given** que ya existe soporte de factura electrónica en producción,
   **When** se agrega la emisión de retenciones electrónicas, **Then** el
   comportamiento actual de factura permanece intacto.

---

### Edge Cases

- ¿Qué debe ocurrir cuando falta información obligatoria del documento sustento,
  del sujeto retenido o de una línea de retención?
- ¿Cómo debe responder el sistema cuando la información tributaria recibida no
  coincide con el formato oficial del comprobante de retención ATS del SRI?
- ¿Qué sucede cuando una retención incluye más de un documento sustento o más
  de un concepto retenido dentro del mismo comprobante?
- ¿Cómo se debe manejar un comprobante generado en ambiente incorrecto o con
  configuración incompleta para firma y transmisión?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow the emission of electronic withholding documents
  corresponding to the SRI official retention document format (`codDoc 07`) for
  the applicable retention ATS version defined by the official documentation.
- **FR-002**: System MUST generate the retention document with the same
  mandatory business structure, sections, field order, and official content
  rules established by the SRI documentation used for this feature.
- **FR-003**: System MUST include all mandatory issuer, tax, retained-party,
  supporting-document, and withholding-detail information required by the
  official retention format.
- **FR-004**: System MUST reject incomplete or structurally invalid retention
  data before the document enters the signing or transmission stage.
- **FR-005**: System MUST state which lifecycle stage(s) are affected
  (generation, signing, submission, authorization lookup) and preserve
  inspectable inputs/outputs for those stages.
- **FR-006**: System MUST define schema, validation, and environment
  requirements for the retention document behavior it adds.
- **FR-007**: System MUST allow retention documents with the official
  supporting-document and retention-detail cardinality permitted by the SRI
  format, including cases with multiple retained concepts.
- **FR-008**: System MUST distinguish runtime configuration/secrets from
  per-document retention business data and define how both are supplied through
  the project's official contracts without hardcoding runtime values.
- **FR-009**: System MUST preserve the current project architecture and specify
  which existing capabilities are extended instead of proposing a new
  architecture.
- **FR-010**: System MUST identify any public API, request model, emitted file,
  or environment/business-contract changes and whether backward compatibility is
  preserved.
- **FR-011**: System MUST preserve the existing electronic invoice capability
  without altering its current behavior, outputs, or operating model.
- **FR-012**: System MUST surface validation, signing, and authorization
  failures in a way that allows the operator to identify why the retention
  document was not accepted.
- **FR-013**: System MUST support an explicit retention request model and an
  optional versioned YAML contract adapter while preserving the existing
  environment-variable fallback used by scripts and current integrators.
- **FR-014**: System MUST reuse a shared issuer profile abstraction across
  electronic document types when that reuse fits within the existing module
  layout and does not modify the project architecture.

### Key Entities *(include if feature involves data)*

- **Comprobante de Retención Electrónico**: Documento tributario oficial de
  retención emitido electrónicamente, con información tributaria del emisor,
  identificación del documento y estructura oficial del SRI.
- **Documento Sustento**: Comprobante base sobre el cual se aplica la retención,
  con sus datos de emisión, identificación, montos y soporte tributario.
- **Detalle de Retención**: Concepto individual retenido dentro del comprobante,
  con su código, base imponible, porcentaje y valor retenido.
- **Configuración Oficial de Emisión**: Conjunto de parámetros operativos del
  proyecto que determinan ambiente, certificados, rutas y demás datos de
  emisión sin recurrir a hard-code.
- **Perfil de Emisor**: Datos estables del emisor reutilizados entre tipos de
  comprobante, separados del runtime y de los datos transaccionales del
  documento.
- **Contrato de Retención**: Representación versionada y explícita de la
  información de negocio del comprobante, ya sea como request tipado o como
  contrato YAML.

## Compliance & Contract Impact *(mandatory when behavior changes)*

- **Affected Schemas/Artifacts**: Documento oficial del SRI para comprobante de
  retención ATS, XML del comprobante de retención, artefactos firmados,
  respuestas de recepción/autorización, contratos YAML de entrada y
  representación de los datos retenidos.
- **Configuration Surface**: El runtime oficial sigue pasando por
  `constants.py` y variables `FEEC_*` para ambiente, firma y XSD. Los datos de
  negocio del comprobante se suministran mediante `RetencionRequest` o
  contratos YAML versionados, manteniendo fallback compatible por entorno para
  los scripts actuales; la política de reintentos y polling queda del lado del
  integrador.
- **Compatibility Notes**: La capacidad de factura electrónica existente debe
  permanecer sin cambios de comportamiento. La nueva funcionalidad añade un
  request tipado, un adaptador YAML y módulos de dominio dentro de `utils/`,
  pero conserva el pipeline actual de XML/firma/SRI y el fallback por variables
  de entorno para scripts.
- **Architecture Impact**: La arquitectura actual del proyecto se mantiene
  intacta. La funcionalidad de retención reutiliza el pipeline existente de
  emisión electrónica y extiende `src/fe_ec/utils/` con módulos de dominio y
  adaptadores, sin crear nuevas capas ni reorganizar el repositorio.

## Assumptions

- La especificación se basa en la ficha técnica oficial del SRI entregada por el
  usuario en su versión offline `2.32` y en la definición oficial del formato
  XML de comprobante de retención ATS versión `2.0.0`.
- El alcance funcional cubre la generación del documento electrónico,
  preparación para firma, transmisión y consulta dentro del mismo modelo
  operativo ya existente para comprobantes electrónicos del proyecto.
- Se adopta un esquema híbrido: `constants.py` para runtime y secretos
  indirectos; requests tipados y contratos YAML para datos tributarios por
  comprobante.
- La representación impresa amigable (RIDE) no forma parte de esta funcionalidad
  salvo que ya exista dentro del alcance vigente del proyecto.
- La nueva capacidad está dirigida a emisores que requieren operar con
  comprobantes de retención electrónicos válidos según la normativa oficial del
  SRI.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un operador puede generar un comprobante de retención electrónico
  completo y estructuralmente válido a partir de datos oficiales de negocio sin
  necesitar ajustes manuales posteriores al documento emitido.
- **SC-002**: El 100% de los campos obligatorios definidos por el formato
  oficial del SRI para el escenario soportado quedan representados en el
  documento emitido.
- **SC-003**: Un integrador puede habilitar la emisión de retenciones
  electrónicas para un emisor y ambiente configurados sin editar el código
  fuente, usando solo runtime documentado y un contrato de negocio explícito.
- **SC-004**: La emisión de facturas electrónicas ya existente continúa
  comportándose igual después de incorporar la emisión de retenciones.
- **SC-005**: Un operador puede identificar y corregir datos inválidos antes de
  que la retención continúe a las etapas de firma o transmisión.
- **SC-006**: La funcionalidad permite emitir retenciones con más de un detalle
  retenido o más de un documento sustento cuando el formato oficial lo requiera.
- **SC-007**: El 100% de los secretos y datos runtime sensibles permanecen fuera
  de los contratos de negocio del comprobante.
