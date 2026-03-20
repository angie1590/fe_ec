# Research: Emision de Notas de Credito Electronicas

## Decision 1: La referencia normativa base es el XSD oficial `NotaCredito_V1.1.0`

**Decision**: Implementar la funcionalidad contra el formato oficial del SRI
`notaCredito` version `1.1.0`, usando los assets ya descargados en
`src/fe_ec/schemas/Nota de Credito/`.

**Rationale**: El repositorio ya contiene el XSD/XML oficial organizado por
tipo de documento. El runtime actual resuelve esos assets desde `constants.py`,
por lo que la implementacion debe tomar esa ruta como baseline y no apoyarse en
ejemplos de terceros.

**Alternatives considered**:

- Usar versiones anteriores `1.0.0`: descartado porque la version `1.1.0` ya
  esta disponible localmente y es la referencia oficial mas reciente del repo.
- Derivar la estructura desde facturas o ejemplos no oficiales: descartado por
  riesgo regulatorio.

## Decision 2: Reutilizar el pipeline actual completo con `codDoc 04`

**Decision**: La nota de credito debe seguir exactamente el mismo pipeline
compartido ya usado por factura y retencion.

**Rationale**: El cambio real esta en el payload XML y en la metadata
documental. El algoritmo de clave, la firma y los endpoints SRI no cambian.

**Alternatives considered**:

- Crear un flujo propio solo para notas de credito: descartado por violar la
  preservacion de arquitectura.
- Crear un cliente SRI separado: descartado porque recepcion y autorizacion son
  los mismos.

## Decision 3: Modelar la nota de credito como contrato de negocio explicito

**Decision**: Crear `NotaCreditoRequest` y `nota_credito_contract.py` siguiendo
el mismo patron ya usado para factura y retencion.

**Rationale**: Los datos transaccionales de una nota de credito no deben vivir
en docenas de `FEEC_*`. El request tipado permite validar el documento
modificado, totales, detalle e impuestos antes de firmar.

**Alternatives considered**:

- Depender solo de variables de entorno: descartado por mala ergonomia y alto
  riesgo de mezclar operaciones.
- Leer YAML directamente en `test_nota_credito.py`: descartado porque el
  contrato debe poder consumirse tambien desde otros integradores Python.

## Decision 4: Reutilizar `EmisorProfile`, pero no forzar reutilizacion ciega de modelos de factura

**Decision**: Reutilizar `EmisorProfile` para el bloque comun del emisor y
crear modelos especificos para nota de credito donde el XSD no coincide 1:1 con
factura.

**Rationale**: Nota de credito comparte `infoTributaria` y varios conceptos con
factura, pero su detalle usa nombres distintos (`codigoInterno`,
`codigoAdicional`) y el encabezado incluye documento modificado, motivo y valor
de modificacion. Reusar dataclasses de factura sin adaptacion haria opaco el
payload final.

**Alternatives considered**:

- Reusar `DetalleFactura` y `CompradorFactura` sin tipos nuevos: descartado por
  diferencias semanticas y de nombres de campo.
- Duplicar `EmisorProfile`: descartado por innecesario.

## Decision 5: La serializacion compartida necesita reglas explicitas para nota de credito

**Decision**: Completar la metadata de `nota_credito` en `constants.py` para
que el serializador compartido trate correctamente las listas oficiales.

**Required list/tag behavior**:

- `totalConImpuestos` -> `totalImpuesto`
- `detalles` -> `detalle`
- `detallesAdicionales` -> `detAdicional`
- `impuestos` -> `impuesto`
- `compensaciones` -> `compensacion`

**Rationale**: Sin estas reglas, `ManejadorXML` puede producir contenedores o
tags duplicados incorrectos para nota de credito.

**Alternatives considered**:

- Dejar la singularizacion heuristica actual: descartado por fragilidad.
- Embutir payloads artificiales para complacer al serializador: descartado por
  mala ergonomia del contrato de negocio.

## Decision 6: El XSD oficial permite un unico `motivo` en `infoNotaCredito`

**Decision**: El modelo de negocio y el contrato YAML de la nota de credito
deben tratar `motivo` como campo singular obligatorio.

**Rationale**: El XSD `NotaCredito_V1.1.0.xsd` define `motivo` como un unico
elemento dentro de `infoNotaCredito`, no como lista repetible. La
implementacion debe seguir el documento oficial aunque algunos escenarios de
negocio pudieran querer varios motivos.

**Alternatives considered**:

- Permitir multiples motivos en el contrato y concatenarlos: descartado por no
  ser estructura oficial.
- Ignorar el motivo hasta la etapa SRI: descartado porque el documento seria
  incompleto desde la capa de negocio.

## Decision 7: `numDocModificado` debe conservar el formato oficial con guiones

**Decision**: Validar el numero del comprobante modificado con el formato
`###-###-#########`.

**Rationale**: A diferencia de retencion, la nota de credito oficial usa
`numDocModificado` con guiones y referencia explicita a la fecha del documento
de sustento (`fechaEmisionDocSustento`).

**Alternatives considered**:

- Aceptar numeros sin guiones y normalizar internamente: descartado por ocultar
  errores de datos.

## Decision 8: Mantener `constants.py` como contrato oficial de runtime

**Decision**: La configuracion runtime sigue viviendo en `src/fe_ec/constants.py`,
incluyendo `FEEC_NOTA_CREDITO_XSD_PATH` como override documental opcional.

**Rationale**: El proyecto ya separo runtime de negocio. La nota de credito no
debe revertir esa decision ni volver a introducir hard-code de paths.

**Alternatives considered**:

- Resolver el XSD de nota de credito dentro de `test_nota_credito.py`:
  descartado por romper el contrato oficial de runtime.

## Decision 9: Mantener politicas de retry fuera de la libreria

**Decision**: La nota de credito seguira el mismo criterio vigente para
factura y retencion: una llamada por etapa, sin polling ni retry automatico
dentro de la libreria.

**Rationale**: El sistema principal consumidor ya implementa esa orquestacion.
La libreria debe ser determinista y no duplicar politicas de backoff.

**Alternatives considered**:

- Reintroducir polling para `codDoc 04`: descartado por inconsistencia con la
  decision arquitectonica ya aplicada al resto del proyecto.

## Hallazgos normativos relevantes

- La raiz oficial es `notaCredito` con `version="1.1.0"`.
- `infoNotaCredito` exige `codDocModificado`, `numDocModificado`,
  `fechaEmisionDocSustento`, `totalSinImpuestos`, `valorModificacion`,
  `totalConImpuestos` y `motivo`.
- `detalles/detalle` es obligatorio y cada detalle puede incluir
  `detallesAdicionales/detAdicional` e `impuestos/impuesto`.
- `compensaciones` es opcional en el encabezado.
- `maquinaFiscal` es opcional y no forma parte del MVP salvo que el contrato
  concreto lo requiera.
