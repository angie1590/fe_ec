# Feature Specification: Emision de Notas de Credito Electronicas

**Feature Branch**: `003-notas-credito-electronicas`  
**Created**: 2026-03-19  
**Status**: Implemented  
**Input**: User description: "Continuar con el siguiente feature del proyecto para soportar notas de crédito electrónicas, siguiendo la misma arquitectura ya establecida, reutilizando el pipeline actual y manteniendo separación clara entre runtime y datos tributarios."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Emitir notas de credito oficiales validas (Priority: P1)

Como emisor de comprobantes electrónicos, necesito generar notas de crédito
electrónicas con la estructura oficial del SRI para registrar anulaciones o
ajustes de una factura ya emitida sin perder validez tributaria.

**Why this priority**: La nota de crédito es un documento tributario oficial;
si el XML no coincide con el formato del SRI o no referencia correctamente al
comprobante modificado, el ajuste no tiene utilidad operativa ni tributaria.

**Independent Test**: Con datos completos y válidos, el usuario puede generar
una nota de crédito electrónica cuya estructura corresponde al formato oficial
del SRI y queda lista para firma y validación.

**Acceptance Scenarios**:

1. **Given** un emisor y una factura previa válidos, **When** genera una nota
   de crédito electrónica, **Then** obtiene un documento `notaCredito`
   estructuralmente válido según la documentación oficial del SRI.
2. **Given** una nota de crédito con uno o más motivos y detalles correctos,
   **When** se genera el comprobante, **Then** todos los campos obligatorios del
   documento modificado, valores ajustados y motivos quedan incluidos en el XML
   emitido.

---

### User Story 2 - Reutilizar el mismo flujo operativo actual (Priority: P2)

Como usuario del sistema actual de emisión electrónica, necesito que la nota de
crédito siga el mismo flujo general de generación, validación, firma,
recepción y consulta que ya existe para factura y retención para no introducir
un proceso paralelo.

**Why this priority**: La nueva capacidad debe integrarse al pipeline ya
establecido y probado del proyecto, sin crear otra arquitectura ni un camino
operativo distinto.

**Independent Test**: El usuario puede recorrer el flujo completo de una nota
de crédito desde el armado del payload hasta dejarla lista para envío y
consulta usando las mismas capacidades compartidas del proyecto.

**Acceptance Scenarios**:

1. **Given** una nota de crédito estructuralmente correcta, **When** se procesa
   con el pipeline actual, **Then** el documento queda listo para firma,
   transmisión y consulta bajo el mismo modelo operativo de los comprobantes ya
   soportados.
2. **Given** un ambiente configurado como `pruebas` o `produccion`, **When** el
   usuario emite una nota de crédito, **Then** el documento se genera con el
   ambiente tributario correcto sin cambiar el comportamiento de factura ni de
   retención.

---

### User Story 3 - Configurar la nota de credito sin hard-code (Priority: P3)

Como integrador de la librería, necesito suministrar la configuración runtime y
los datos tributarios de la nota de crédito por contratos explícitos, sin
hard-code ni edición manual del código, para poder operar distintos emisores,
ambientes y ajustes de negocio con seguridad.

**Why this priority**: En producción los valores cambian por operación, pero la
arquitectura debe mantenerse estable y la configuración sensible debe seguir
fuera del código.

**Independent Test**: Un integrador puede preparar una nota de crédito para un
emisor y un comprobante modificado usando solo runtime documentado y un contrato
de negocio explícito, sin tocar la arquitectura ni la lógica existente.

**Acceptance Scenarios**:

1. **Given** un nuevo emisor o cambio de ambiente tributario, **When** el
   integrador actualiza el runtime oficial y/o el contrato de la nota de
   crédito, **Then** la emisión se adapta sin requerir cambios de arquitectura
   ni nuevos valores embebidos en el código.
2. **Given** que factura y retención ya están soportadas, **When** se incorpora
   nota de crédito, **Then** el comportamiento actual de esos comprobantes
   permanece intacto.

---

### Edge Cases

- ¿Qué debe ocurrir cuando la nota de crédito no referencia correctamente al
  comprobante modificado o el número del comprobante no coincide con la clave o
  autorización informada?
- ¿Cómo debe comportarse el sistema cuando el valor de modificación no cuadra
  con el total del ajuste o cuando faltan motivos obligatorios?
- ¿Qué sucede cuando la nota de crédito intenta emitirse con un `codDoc`
  incorrecto, versión XML incorrecta o campos incompatibles con la nota de
  crédito oficial del SRI?
- ¿Cómo se debe manejar un ajuste que requiera más de un detalle o más de un
  motivo dentro del mismo comprobante?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow the emission of electronic credit notes
  corresponding to the SRI official note de crédito format with `codDoc 04`.
- **FR-002**: System MUST generate the credit note using the official XML root
  `notaCredito` and the schema version established by the official SRI
  documentation used for this feature.
- **FR-003**: System MUST include all mandatory issuer, buyer, modified-document,
  tax, total, detail, and reason information required by the official note de
  crédito format.
- **FR-004**: System MUST require explicit reference to the modified document,
  including its document code, document number, and issuance date, as demanded
  by the official note de crédito structure.
- **FR-005**: System MUST reject incomplete or structurally invalid credit note
  data before the document enters signing or transmission.
- **FR-006**: System MUST state which lifecycle stage(s) are affected
  (generation, signing, submission, authorization lookup) and preserve
  inspectable inputs/outputs for those stages.
- **FR-007**: System MUST define schema, validation, and environment
  requirements for the credit note behavior it adds.
- **FR-008**: System MUST distinguish runtime configuration/secrets from
  per-document business data and define how both are supplied through the
  project's official contracts without hardcoding runtime values.
- **FR-009**: System MUST preserve the current project architecture and specify
  which existing capabilities are extended instead of proposing a new
  architecture.
- **FR-010**: System MUST identify any public API, request model, emitted file,
  or environment/business-contract changes and whether backward compatibility is
  preserved.
- **FR-011**: System MUST preserve the existing electronic invoice and
  retention capabilities without altering their current behavior, outputs, or
  operating model.
- **FR-012**: System MUST surface validation, signing, reception, and
  authorization failures in a way that allows the operator to inspect why the
  note de crédito was not accepted.
- **FR-013**: System MUST support an explicit credit note request model and an
  optional versioned YAML contract adapter while preserving a compatible
  environment-variable fallback for scripts when applicable.
- **FR-014**: System MUST reuse the shared issuer profile abstraction and the
  shared XML/signing/SRI pipeline when that reuse stays within the current
  module layout and does not modify the project architecture.

### Key Entities *(include if feature involves data)*

- **Nota de Crédito Electrónica**: Documento tributario oficial que corrige,
  anula o ajusta un comprobante previamente emitido, con estructura oficial del
  SRI y referencia obligatoria al comprobante modificado.
- **Comprobante Modificado**: Documento tributario original sobre el cual se
  aplica la nota de crédito, identificado por su tipo, número y fecha de
  emisión.
- **Motivo de Modificación**: Justificación tributaria y operativa del ajuste
  aplicado en la nota de crédito.
- **Detalle de Nota de Crédito**: Línea individual del ajuste con descripción,
  cantidad, precios, descuentos e impuestos según el formato oficial.
- **Contrato de Nota de Crédito**: Representación versionada y explícita de la
  información de negocio del comprobante, ya sea como request tipado o como
  contrato YAML.

## Compliance & Contract Impact *(mandatory when behavior changes)*

- **Affected Schemas/Artifacts**: Ficha técnica oficial del SRI, esquema XML de
  nota de crédito, XML firmado de nota de crédito, respuestas de recepción y
  autorización, contratos YAML de entrada y request model de negocio.
- **Configuration Surface**: El runtime oficial sigue pasando por
  `constants.py` y variables `FEEC_*` para ambiente, firma y XSD. Los datos de
  negocio de la nota de crédito deben suministrarse mediante un request tipado
  o contratos YAML versionados; la política de reintentos y polling permanece
  del lado del integrador.
- **Compatibility Notes**: Factura y retención deben seguir funcionando sin
  cambios de comportamiento. La nueva funcionalidad añade un nuevo contrato de
  negocio y módulos de dominio dentro de `src/fe_ec/utils/`, pero conserva el
  pipeline actual de XML, firma y SRI.
- **Architecture Impact**: La arquitectura actual del proyecto se mantiene
  intacta. La nota de crédito reutiliza el pipeline existente y extiende los
  módulos actuales dentro de `src/fe_ec/utils/` sin crear nuevas capas ni
  reorganizar el repositorio.

## Assumptions

- La especificación se basa en la ficha técnica oficial offline del SRI
  publicada en la página oficial de facturación electrónica al 19 de marzo de
  2026 y en el formato XML oficial de nota de crédito `notaCredito` versión
  `1.1.0`.
- El alcance funcional cubre generación del documento electrónico, preparación
  para firma, transmisión y consulta dentro del mismo modelo operativo ya
  existente para otros comprobantes electrónicos del proyecto.
- Se mantiene el esquema híbrido del proyecto: `constants.py` para runtime y
  secretos indirectos; requests tipados y contratos YAML para datos tributarios
  por comprobante.
- La representación impresa amigable (RIDE) no forma parte de esta feature
  salvo que ya exista dentro del alcance vigente del proyecto.
- El MVP de la nota de crédito se enfoca en la corrección de facturas
  electrónicas ya emitidas, no en otros tipos de comprobantes modificados.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un operador puede generar una nota de crédito electrónica
  completa y estructuralmente válida a partir de datos oficiales de negocio sin
  ajustes manuales posteriores al XML emitido.
- **SC-002**: El 100% de los campos obligatorios definidos por el formato
  oficial del SRI para la nota de crédito soportada quedan representados en el
  documento emitido.
- **SC-003**: Un integrador puede habilitar la emisión de notas de crédito para
  un emisor y ambiente configurados sin editar el código fuente, usando solo
  runtime documentado y un contrato de negocio explícito.
- **SC-004**: La emisión de factura y retención ya existente continúa
  comportándose igual después de incorporar la emisión de notas de crédito.
- **SC-005**: Un operador puede identificar y corregir datos inválidos del
  comprobante modificado o del ajuste antes de que la nota de crédito continúe a
  las etapas de firma o transmisión.
- **SC-006**: La funcionalidad permite emitir notas de crédito con más de un
  detalle o más de un motivo cuando el formato oficial lo permita y el caso de
  negocio lo requiera.
- **SC-007**: El 100% de los secretos y datos runtime sensibles permanecen
  fuera de los contratos de negocio del comprobante.

## Implementation Outcome

- La feature quedó implementada dentro de `src/fe_ec/utils/` sin alterar la
  arquitectura del proyecto ni el flujo existente de factura y retención.
- Se incorporaron `nota_credito.py`, `nota_credito_contract.py`,
  `test_nota_credito.py` y cobertura dedicada para dominio, contrato YAML,
  XML/XSD y flujo operativo.
- El runtime sigue separado de los datos tributarios: `constants.py` conserva
  la configuración técnica y `NotaCreditoRequest`/YAML contienen la
  información de negocio.
- El smoke real en ambiente `PRUEBAS` quedó validado con autorización SRI para
  la clave `1903202604010352390800110010013477495009099979314` el
  `19/03/2026`.
