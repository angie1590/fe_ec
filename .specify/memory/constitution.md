<!--
Sync Impact Report
Version change: 1.2.0 -> 1.2.1
Modified principles:
- II. Deterministic Invoice Lifecycle
- V. Stable Public API and Secret Hygiene
Modified sections:
- Operational Constraints
- Development Workflow & Quality Gates
Templates requiring updates:
- ✅ .specify/templates/plan-template.md
- ✅ .specify/templates/spec-template.md
Follow-up TODOs:
- None
-->
# FE-EC Constitution

## Core Principles

### I. SRI Schema Compliance First
Every feature that creates, transforms, signs, or transmits electronic tax
documents MUST preserve compliance with the official SRI structures supported by
this repository. XML output MUST validate against the bundled XSDs before
signing or submission, and any schema-version expansion MUST document the
affected comprobante type, the supported version, and the regression impact on
existing flows. Rationale: a feature that emits invalid XML is operationally
incorrect even when the surrounding Python code appears healthy.

### II. Deterministic Invoice Lifecycle
Generation, signing, submission, and authorization lookup MUST remain explicit,
auditable stages with inspectable inputs and outputs. Configuration MUST enter
the system through documented runtime variables, explicit parameters, or
versioned business contracts, never through implicit machine-specific state.
Runtime concerns such as environment, certificates, and XSD overrides MUST
remain distinct from per-document business data such as issuer profiles,
buyers, retained parties, supporting documents, taxes, or line items.
Features MUST preserve the ability to persist, inspect, and replay intermediate
artifacts such as unsigned XML, signed XML, and SRI responses. Rationale:
invoice incidents are resolved through reproducibility, not guesswork.

### III. Test-Backed Compliance Changes (NON-NEGOTIABLE)
Every behavioral change MUST add or update automated tests at the lowest
effective level, and changes affecting XML structure, digital signature
generation, Java invocation, or SRI exchanges MUST include integration or smoke
coverage when practical. Regressions with a known failure mode MUST begin with
a failing test before implementation. No change may be treated as complete
while required tests are failing or while the validation path remains manual
only. Rationale: compliance regressions usually arrive as small formatting or
environmental changes that tests must catch early.

### IV. Portable Runtime and Bundled Assets
The package MUST remain consumable as a standalone Python library on supported
runtime versions, with Poetry-managed dependencies and all required non-code
assets bundled or explicitly documented. XSD files, signing resources, and Java
compatibility expectations MUST travel with the package or have a documented
override mechanism. Features MUST not assume a developer-specific filesystem
layout, shell profile, or Java installation path. Rationale: downstream users
integrate the library into heterogeneous environments and need predictable
installation behavior.

### V. Stable Public API and Secret Hygiene
Public modules, environment variables, request models, versioned document
contracts, return shapes, emitted files, and documented workflows consumed by
integrators MUST be treated as versioned contracts. Backward-incompatible
behavior changes MUST include migration notes and a semantic version bump plan.
Secrets such as certificate files, passwords, or SRI credentials MUST never be
hardcoded, logged, or introduced as packaged defaults. Business data required
to emit a concrete comprobante MUST be modeled through explicit parameters,
typed request objects, or versioned contract files rather than hidden in
process-global secrets or machine-specific defaults. Rationale: this library
sits in regulated production flows and handles sensitive signing material.

### VI. Architecture Preservation (NON-NEGOTIABLE)
It is strictly forbidden to modify the project architecture. Contributors MUST
work within the existing architectural boundaries, module layout, integration
pattern, and repository structure unless the constitution itself is explicitly
amended first. New work MUST reuse and extend the current architecture instead
of introducing new layers, service splits, directory topologies, framework
shells, or structural rewrites. Rationale: the project depends on a stable and
already-integrated compliance pipeline, and architectural churn would create
avoidable operational risk.

## Operational Constraints

- Supported Python versions MUST remain aligned with the package metadata and
  be updated deliberately alongside test coverage.
- Java 8 is the baseline expectation for signing, and compatibility work for
  Java 9+ MUST remain explicit and tested when modified.
- Local development artifacts such as temporary XML outputs, certificates, and
  environment-specific probes MUST not become implicit production dependencies.
- New comprobante support or endpoint changes MUST identify the impacted SRI
  environment (`pruebas` or `produccion`) and keep environment normalization
  explicit.
- `constants.py` MUST remain the official home for runtime configuration and
  secrets indirection; per-document business data MUST be carried in explicit
  request models or versioned contract adapters.

## Development Workflow & Quality Gates

- Non-trivial work MUST start with a spec/plan/tasks flow or an equivalent
  written scope that names affected public contracts, validation rules, and
  required tests.
- Implementation plans MUST pass a constitution check covering schema
  compliance, lifecycle traceability, runtime/asset portability, secret
  handling, API compatibility, and preservation of the current architecture
  before design proceeds.
- Plans and specs for business-document features MUST state which inputs are
  runtime-only and which belong to the business contract for the emitted
  comprobante.
- Code review MUST verify that modified behaviors have automated coverage,
  packaged assets remain correct, public-facing changes include README or
  migration-note updates when relevant, and no architectural drift was
  introduced.
- Before merge, contributors MUST run the relevant `pytest` targets and any
  affected build or smoke validations required to exercise XML generation and
  signing behavior.

## Governance

This constitution overrides conflicting local habits, undocumented conventions,
and ad hoc process shortcuts for the FE-EC repository. Amendments MUST be made
through a documented change that updates this file and all affected templates or
guidance files in the same change set. Versioning follows semantic versioning
for governance: MAJOR for incompatible principle changes or removals, MINOR for
new principles or materially expanded obligations, and PATCH for clarifications
that do not alter required behavior. Compliance reviews MUST occur during
planning, code review, and release preparation for changes that affect XML
schemas, signing behavior, public interfaces, secret handling, or architectural
boundaries. Any proposal to alter the project architecture is invalid unless a
prior constitution amendment approves that change explicitly.

**Version**: 1.2.1 | **Ratified**: 2026-03-13 | **Last Amended**: 2026-03-19
