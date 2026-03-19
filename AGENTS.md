# fe_ec Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-13

## Active Technologies
- Python `>=3.10,<3.12` via Poetry
- `lxml 5.3.2` for XML construction and XSD validation
- `xmlschema 3.4.5` declared for schema tooling
- `zeep 4.3.1` for SOAP integration with SRI
- `cryptography 40.0.2` for Python-side crypto primitives
- Bundled Java signing toolchain for XAdES-BES (`FirmaElectronica.jar` + `lib/`)

## Project Structure

```text
src/
tests/
```

## Commands

poetry install
poetry show --tree
poetry run python -m unittest discover -q
poetry build

## Code Style

Python 3.10+: follow standard library-first conventions and keep runtime
configuration explicit via `FEEC_*` environment variables. Respect the current
project architecture at all times; do not introduce structural rewrites, new
layers, or directory reorganizations.

## Recent Changes
- 002-retenciones-electronicas: planned support for retention ATS 2.0.0 by
  extending the existing XML/signing/SRI pipeline without changing architecture

- 001-project-stack-baseline: documented the runtime stack, packaging model,
  SOAP integration, Java signing toolchain, and executable test surface

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
