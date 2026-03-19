# Tasks: Emision de Comprobantes de Retencion Electronicos

**Input**: Design documents from `/specs/002-retenciones-electronicas/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Behavioral changes require tests. Include unit, integration, or
smoke tasks according to the constitution and the feature's risk profile.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths below use the current project architecture and MUST preserve it

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparar los assets y archivos compartidos que usarán todas las historias

- [ ] T001 Add the official retention ATS XSD asset in `src/fe_ec/schemas/retencion_ats_v2_0_0.xsd`
- [ ] T002 [P] Create reusable retention payload builders in `tests/fixtures_retencion.py`
- [ ] T003 [P] Create the retention XML test module scaffold in `tests/test_retencion_xml.py`
- [ ] T004 [P] Create the retention flow regression test module scaffold in `tests/test_retencion_flow.py`
- [ ] T005 [P] Create the retention example execution script scaffold in `test_retencion.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Dejar listo el soporte documental y técnico común antes de cualquier historia

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Add failing multi-document configuration tests in `tests/test_constants.py`
- [ ] T007 Extend document metadata and XSD environment resolution in `src/fe_ec/constants.py`
- [ ] T008 Add failing document-type selection and invoice-default regression tests in `tests/test_retencion_flow.py`
- [ ] T009 Implement document-type resolution, root/version switching, and effective XSD selection in `src/fe_ec/utils/manejador_xml.py`
- [ ] T010 Implement explicit repeated-tag mapping and document-specific validation hooks in `src/fe_ec/utils/manejador_xml.py`
- [ ] T011 Preserve pre-sign validation diagnostics and non-secret error reporting in `src/fe_ec/utils/manejador_xml.py`

**Checkpoint**: Foundation ready - retention implementation can now begin

---

## Phase 3: User Story 1 - Emitir retenciones oficiales validas (Priority: P1) 🎯 MVP

**Goal**: Generar comprobantes de retención ATS con la estructura oficial del SRI y validarlos contra el XSD oficial

**Independent Test**: Un payload completo de retención genera un XML `comprobanteRetencion` válido contra el XSD oficial, con `docsSustento`, `retenciones` y `Pagos` correctamente serializados

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T012 [US1] Add failing structure assertions for `infoCompRetencion`, `docsSustento`, `retenciones`, and `Pagos` in `tests/test_retencion_xml.py`
- [ ] T013 [US1] Add failing XSD validation cases for minimal and multi-retention payloads in `tests/test_retencion_xml.py`

### Implementation for User Story 1

- [ ] T014 [US1] Implement retention root and ATS header serialization in `src/fe_ec/utils/manejador_xml.py`
- [ ] T015 [US1] Implement `docSustento`, `impuestoDocSustento`, `retencion`, and `Pago` serialization rules in `src/fe_ec/utils/manejador_xml.py`
- [ ] T016 [US1] Implement conditional `reembolsos` and `dividendos` serialization rules in `src/fe_ec/utils/manejador_xml.py`
- [ ] T017 [US1] Add minimal and multi-detail retention payload examples in `test_retencion.py`
- [ ] T018 [US1] Enforce required retention blocks and field-presence checks in `src/fe_ec/utils/manejador_xml.py`

**Checkpoint**: At this point, retention XML generation should be valid and testable independently

---

## Phase 4: User Story 2 - Operar la retencion con el mismo flujo actual (Priority: P2)

**Goal**: Reusar el pipeline actual de generación, firma y preparación para envío sin romper factura

**Independent Test**: Un comprobante de retención puede recorrer el mismo flujo base que factura usando `GeneradorClaveAcceso`, `ManejadorXML`, firma y servicios SRI, mientras factura conserva su comportamiento por defecto

### Tests for User Story 2 ⚠️

- [ ] T019 [P] [US2] Add failing flow regression tests for `codDoc 07` and clave de acceso generation in `tests/test_retencion_flow.py`
- [ ] T020 [P] [US2] Add failing signing-handoff assertions for retention documents in `tests/test_smoke_firma.py`

### Implementation for User Story 2

- [ ] T021 [US2] Extend the retention example flow to reuse `GeneradorClaveAcceso`, `ManejadorXML`, and `SRIService` in `test_retencion.py`
- [ ] T022 [US2] Extend `test2.py` with a retention execution path that preserves the existing invoice flow
- [ ] T023 [US2] Add retention smoke coverage to `tests/test_smoke_firma.py` using the existing signing pipeline
- [ ] T024 [US2] Preserve invoice default behavior while enabling retention document selection in `src/fe_ec/utils/manejador_xml.py` and `tests/test_retencion_flow.py`

**Checkpoint**: At this point, retention and invoice flows should coexist and remain independently verifiable

---

## Phase 5: User Story 3 - Configurar la emision sin tocar el codigo (Priority: P3)

**Goal**: Permitir configuración por variables de entorno y contrato oficial, sin hard-code ni cambios manuales al código para cada emisor/ambiente

**Independent Test**: Un integrador puede cambiar el XSD y el ambiente de retención usando solo `constants.py` y variables `FEEC_*`, sin editar lógica runtime ni romper la compatibilidad de factura

### Tests for User Story 3 ⚠️

- [ ] T025 [P] [US3] Add failing environment-resolution tests for `FEEC_FACTURA_XSD_PATH`, `FEEC_RETENCION_XSD_PATH`, and legacy `FEEC_XSD_PATH` in `tests/test_constants.py`
- [ ] T026 [P] [US3] Add failing missing/invalid retention configuration tests in `tests/test_retencion_flow.py`

### Implementation for User Story 3

- [ ] T027 [US3] Finalize multi-document environment variable resolution and compatibility defaults in `src/fe_ec/constants.py`
- [ ] T028 [US3] Mark `src/fe_ec/constants_copy.py` as non-runtime reference and keep runtime lookups centralized in `src/fe_ec/constants.py`
- [ ] T029 [US3] Update environment-only retention setup examples in `test_retencion.py` and `test2.py`
- [ ] T030 [US3] Update retention configuration guidance in `README.md` and `specs/002-retenciones-electronicas/contracts/runtime-configuration.md`

**Checkpoint**: All supported retention setup paths should now work without hard-coded runtime edits

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Cerrar regresiones, documentación y compatibilidad pública

- [ ] T031 [P] Validate user-facing instructions in `README.md` and `specs/002-retenciones-electronicas/quickstart.md`
- [ ] T032 Run and stabilize full regression coverage in `tests/test_constants.py`, `tests/test_retencion_xml.py`, `tests/test_retencion_flow.py`, and `tests/test_smoke_firma.py`
- [ ] T033 Review public API compatibility notes in `specs/002-retenciones-electronicas/contracts/library-interface.md` and `README.md`
- [ ] T034 Clean up retention example ergonomics in `test_retencion.py` and `test2.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion
- **User Story 2 (Phase 4)**: Depends on User Story 1 because it reuses the generated retention document path and validates coexistence with factura
- **User Story 3 (Phase 5)**: Depends on Foundational completion; final operator examples should land after User Story 1 is available
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - no dependency on other stories
- **User Story 2 (P2)**: Depends on User Story 1 because it validates reuse of the existing emission pipeline with a working retention XML
- **User Story 3 (P3)**: Can start after Foundational (Phase 2), but its final examples and compatibility review should incorporate User Story 1 behavior

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Shared configuration and serializer foundations must exist before story work
- XML generation must be stable before flow reuse tasks
- Runtime configuration updates must preserve backward compatibility
- Work MUST stay within the existing architecture; do not add new architectural layers or restructure the repository

### Parallel Opportunities

- `T002`, `T003`, `T004`, and `T005` can run in parallel after `T001`
- `T006` and `T008` can run in parallel before `T007` and `T009`
- `T019` and `T020` can run in parallel within User Story 2
- `T025` and `T026` can run in parallel within User Story 3
- `T031` and `T033` can run in parallel during Polish

---

## Parallel Example: User Story 1

```bash
# After Phase 2 is complete, prepare the core validation and example inputs in parallel:
Task: "Add failing structure assertions for infoCompRetencion, docsSustento, retenciones, and Pagos in tests/test_retencion_xml.py"
Task: "Add minimal and multi-detail retention payload examples in test_retencion.py"
```

## Parallel Example: User Story 2

```bash
# Once User Story 1 is working, validate flow reuse in parallel:
Task: "Add failing flow regression tests for codDoc 07 and clave de acceso generation in tests/test_retencion_flow.py"
Task: "Add failing signing-handoff assertions for retention documents in tests/test_smoke_firma.py"
```

## Parallel Example: User Story 3

```bash
# Configuration validation can be split across separate files:
Task: "Add failing environment-resolution tests for FEEC_FACTURA_XSD_PATH, FEEC_RETENCION_XSD_PATH, and legacy FEEC_XSD_PATH in tests/test_constants.py"
Task: "Add failing missing/invalid retention configuration tests in tests/test_retencion_flow.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Confirm retention XML generation and XSD validation
5. Demo a minimal retention document before integrating the full execution flow

### Incremental Delivery

1. Complete Setup + Foundational → retention-ready foundation
2. Add User Story 1 → validate official XML output
3. Add User Story 2 → validate flow reuse and factura regression safety
4. Add User Story 3 → validate environment-only configuration and operator setup
5. Finish with documentation, compatibility review, and full regression run

### Parallel Team Strategy

With multiple developers:

1. Developer A: Phase 2 foundations in `src/fe_ec/constants.py` and `src/fe_ec/utils/manejador_xml.py`
2. Developer B: User Story 1 tests and examples in `tests/test_retencion_xml.py` and `test_retencion.py`
3. Developer C: User Story 3 configuration coverage in `tests/test_constants.py` and `README.md` once foundational tasks land

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently verifiable from the generated artifacts and test flow
- Suggested MVP scope: complete through Phase 3 (User Story 1) before extending flow reuse and configuration polish
- Total tasks: 34
- User Story task counts: US1 = 7, US2 = 6, US3 = 6
