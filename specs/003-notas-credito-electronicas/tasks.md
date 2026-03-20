# Tasks: Emision de Notas de Credito Electronicas

**Input**: Design documents from `/specs/003-notas-credito-electronicas/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Behavioral changes require automated coverage. Esta feature debe
incluir pruebas unitarias del dominio, pruebas de contrato YAML, validacion
XML/XSD y regresion de factura/retencion.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirmar alcance, assets oficiales y modulos afectados sin mover
la arquitectura.

- [x] T001 Auditar los assets oficiales de nota de credito en `src/fe_ec/schemas/Nota de Credito/` y reflejar la version objetivo `1.1.0` en `specs/003-notas-credito-electronicas/research.md`
- [x] T002 [P] Documentar el contrato de negocio y runtime de nota de credito en `specs/003-notas-credito-electronicas/contracts/nota-credito-payload.md` y `specs/003-notas-credito-electronicas/contracts/runtime-configuration.md`
- [x] T003 [P] Confirmar en `specs/003-notas-credito-electronicas/plan.md` que la feature solo toca `src/fe_ec/utils/`, `src/fe_ec/constants.py`, `contracts/` y `tests/`
- [x] T004 [P] Definir el ejemplo operativo esperado en `specs/003-notas-credito-electronicas/quickstart.md` y reservar `contracts/nota_credito.example.yaml`
- [x] T005 Confirmar por escrito que factura y retencion quedan fuera de cambios funcionales en `specs/003-notas-credito-electronicas/plan.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Completar la infraestructura comun que desbloquea cualquier
implementacion de nota de credito.

**⚠️ CRITICAL**: Ninguna historia puede implementarse antes de terminar esta fase.

- [x] T006 Verificar y extender la metadata `nota_credito` en `src/fe_ec/constants.py` para cubrir `totalImpuesto`, `detalle`, `impuesto`, `detAdicional`, `compensacion` e `infoAdicional`
- [x] T007 [P] Ajustar `src/fe_ec/utils/manejador_xml.py` si hace falta para serializar correctamente `totalConImpuestos.totalImpuesto[]` y `compensaciones.compensacion[]`
- [x] T008 [P] Extender `tests/test_constants.py` con la configuracion efectiva de `nota_credito` y sus inferencias por `codDoc` y `root_tag`
- [x] T009 Crear `src/fe_ec/utils/nota_credito.py` con el esqueleto de dominio y helpers de validacion de fecha/texto
- [x] T010 Crear `src/fe_ec/utils/nota_credito_contract.py` con el esqueleto del adaptador `dict/YAML -> NotaCreditoRequest`
- [x] T011 Definir en `test_nota_credito.py` la politica de diagnosticos sin retries: fallos de validacion, firma, recepcion y autorizacion deben quedar inspeccionables

**Checkpoint**: Foundation ready - ya se puede implementar la nota de credito sin riesgo de romper el pipeline compartido.

---

## Phase 3: User Story 1 - Emitir notas de credito oficiales validas (Priority: P1) 🎯 MVP

**Goal**: Generar una nota de credito `notaCredito` oficial y valida contra el
XSD del SRI.

**Independent Test**: Con un request o contrato completo, el sistema genera un
xml `notaCredito` valido segun `NotaCredito_V1.1.0.xsd`.

### Tests for User Story 1

- [x] T012 [P] [US1] Crear pruebas unitarias del dominio en `tests/test_nota_credito_builder.py`
- [x] T013 [P] [US1] Crear prueba de contrato YAML en `tests/test_nota_credito_contract.py`
- [x] T014 [P] [US1] Crear prueba de serializacion y validacion XSD en `tests/test_nota_credito_xml.py`

### Implementation for User Story 1

- [x] T015 [P] [US1] Implementar `CompradorNotaCredito`, `ComprobanteModificado`, `TotalImpuestoNotaCredito`, `CompensacionNotaCredito`, `DetalleNotaCredito`, `DetalleAdicionalNotaCredito` e `ImpuestoDetalleNotaCredito` en `src/fe_ec/utils/nota_credito.py`
- [x] T016 [US1] Implementar `NotaCreditoRequest` y `construir_payload_nota_credito(...)` en `src/fe_ec/utils/nota_credito.py`
- [x] T017 [US1] Agregar validaciones de negocio para `motivo`, `num_doc_modificado`, `fecha_emision_doc_sustento`, `valor_modificacion`, `total_con_impuestos` y `detalles` en `src/fe_ec/utils/nota_credito.py`
- [x] T018 [US1] Implementar `nota_credito_request_from_dict(...)` y `load_nota_credito_request_from_yaml(...)` en `src/fe_ec/utils/nota_credito_contract.py`
- [x] T019 [US1] Crear `contracts/nota_credito.example.yaml` con un caso minimo oficial y coherente
- [x] T020 [US1] Validar que `ManejadorXML(document_type=\"nota_credito\")` genera la raiz/version correctas y pasa el XSD oficial usando el payload de `NotaCreditoRequest`

**Checkpoint**: La historia 1 queda funcional y testeable de forma independiente.

---

## Phase 4: User Story 2 - Reutilizar el mismo flujo operativo actual (Priority: P2)

**Goal**: Recorrer clave, XML, firma y SRI con el mismo modelo operativo ya
existente para factura y retencion.

**Independent Test**: Una nota de credito valida puede recorrer el wrapper de
ejemplo y dejar artefactos inspeccionables sin alterar el comportamiento de los
otros comprobantes.

### Tests for User Story 2

- [x] T021 [P] [US2] Crear prueba de flujo compartido en `tests/test_nota_credito_flow.py`
- [x] T022 [P] [US2] Crear regresion de factura y retencion en `tests/test_factura_builder.py` y `tests/test_retencion_xml.py` para asegurar que la nueva feature no cambia su comportamiento

### Implementation for User Story 2

- [x] T023 [US2] Crear `test_nota_credito.py` como wrapper fino siguiendo el patron de `test2.py` y `test_retencion.py`
- [x] T024 [US2] Integrar `GeneradorClaveAcceso` con `codDoc 04` y salida por defecto a `.artifacts/xml/` en `test_nota_credito.py`
- [x] T025 [US2] Reutilizar `FirmadorXML` y `SRIService` en `test_nota_credito.py` sin retries y con mensajes de fallo inspeccionables
- [x] T026 [US2] Ajustar solo si es necesario `src/fe_ec/utils/manejador_xml.py` y `src/fe_ec/constants.py` para inferir `nota_credito` desde `codDoc` o `root_tag` sin romper `factura` ni `retencion`

**Checkpoint**: La historia 2 queda funcional y el pipeline compartido sigue estable.

---

## Phase 5: User Story 3 - Configurar la nota de credito sin hard-code (Priority: P3)

**Goal**: Permitir que la nota de credito se consuma desde contrato YAML o
request tipado, manteniendo runtime y secretos fuera de los datos de negocio.

**Independent Test**: Un integrador puede emitir una nota de credito cambiando
solo contrato de negocio y runtime oficial, sin editar el codigo.

### Tests for User Story 3

- [x] T027 [P] [US3] Agregar pruebas de overrides runtime y defaults en `tests/test_constants.py` y `tests/test_nota_credito_contract.py`
- [x] T028 [P] [US3] Agregar prueba de fallback compatible del wrapper en `tests/test_nota_credito_contract.py` o `tests/test_nota_credito_flow.py`

### Implementation for User Story 3

- [x] T029 [US3] Documentar `FEEC_NOTA_CREDITO_XSD_PATH` y los limites runtime/negocio en `README.md` y `specs/003-notas-credito-electronicas/contracts/runtime-configuration.md`
- [x] T030 [US3] Implementar soporte `--contract` en `test_nota_credito.py` y dejar el fallback por variables de entorno solo como compatibilidad operativa
- [x] T031 [US3] Exponer la nueva superficie publica en `specs/003-notas-credito-electronicas/contracts/library-interface.md` y mantener intacta la compatibilidad de factura/retencion

**Checkpoint**: Las tres historias quedan cubiertas y la configuracion sigue la arquitectura vigente.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Cerrar regresiones, documentacion y validacion final.

- [x] T032 [P] Actualizar ejemplos y seccion de uso en `README.md`
- [x] T033 [P] Ejecutar `poetry run python -m unittest discover -q` y registrar el resultado
- [x] T034 Validar el quickstart de `specs/003-notas-credito-electronicas/quickstart.md` contra `contracts/nota_credito.example.yaml`
- [x] T035 Revisar packaging y paths de assets para asegurar que `src/fe_ec/schemas/Nota de Credito/` siga incluido en el paquete

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: puede empezar de inmediato
- **Foundational (Phase 2)**: depende de Phase 1 y bloquea todas las historias
- **User Stories (Phase 3+)**: dependen de Phase 2
- **Polish (Phase 6)**: depende de las historias completadas

### User Story Dependencies

- **US1 (P1)**: puede empezar despues de Phase 2; no depende de otras historias
- **US2 (P2)**: depende del payload/modelo implementado en US1
- **US3 (P3)**: depende de los contratos y wrapper implementados en US1/US2

### Within Each User Story

- Las pruebas deben existir antes de cerrar la implementacion
- El dominio y contratos van antes del wrapper operativo
- El wrapper operativo va antes del smoke de firma/envio
- Ninguna tarea puede introducir nuevas capas ni mover la arquitectura actual

### Parallel Opportunities

- `T002`, `T003`, `T004`
- `T007`, `T008`, `T009`, `T010`
- `T012`, `T013`, `T014`
- `T021`, `T022`
- `T027`, `T028`
- `T032`, `T033`

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Completar Setup
2. Completar Foundational
3. Completar US1
4. Validar XML/XSD de nota de credito
5. Revisar regresion de factura/retencion

### Incremental Delivery

1. Setup + Foundational
2. US1: builder + contrato + XML valido
3. US2: wrapper + flujo compartido
4. US3: ergonomia de consumo y documentacion
5. Polish: suite final y quickstart

## Notes

- `[P]` = tareas paralelizables en archivos distintos
- `[US1]`, `[US2]`, `[US3]` = trazabilidad directa a historias del spec
- El XSD oficial manda sobre cualquier supuesto de negocio: `motivo` es
  singular y `numDocModificado` conserva guiones
