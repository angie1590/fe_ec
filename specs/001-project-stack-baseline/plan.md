# Implementation Plan: Baseline del Stack Tecnologico del Proyecto

**Branch**: `001-project-stack-baseline` | **Date**: 2026-03-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-project-stack-baseline/spec.md`

**Note**: Este plan ejecuta `speckit.plan` como baseline documental del stack
actual del repositorio, no como diseño de una nueva capacidad funcional.

## Summary

El objetivo es producir una línea base precisa del stack tecnológico real de
`fe_ec`: runtime, dependencias, arquitectura modular, activos empaquetados,
integraciones externas, estrategia de pruebas y flujo operativo. La
investigación confirma que el proyecto es una librería Python distribuida con
Poetry, orientada a facturación electrónica del SRI, con validación XML/XSD en
Python y firma XAdES-BES delegada a una toolchain Java empaquetada. También
identifica discrepancias operativas importantes entre documentación, wheel y
entorno ejecutable actual.

## Technical Context

**Language/Version**: Python `>=3.10,<3.12` declarado en Poetry; entorno local
validado en CPython `3.10.12`  
**Primary Dependencies**: Poetry, `lxml 5.3.2`, `xmlschema 3.4.5`, `zeep 4.3.1`,
`cryptography 40.0.2`, `requests` transitivo vía Zeep, `subprocess` para
integración Java  
**Storage**: Sin base de datos; uso de filesystem local para XSD, XML temporal,
XML firmado, certificados `.p12`, bundle Java, wheel/sdist y fixtures  
**Testing**: `unittest` estándar ejecutable con `poetry run python -m unittest discover -q`;
`pytest` está documentado pero no está instalado en el entorno Poetry actual  
**Target Platform**: Librería Python para macOS/Linux y potencialmente Windows,
siempre que exista Java accesible y conectividad HTTPS hacia endpoints SRI  
**Project Type**: Librería Python empaquetable con scripts de ejemplo locales y
una integración externa SOAP  
**Performance Goals**: Prioridad en corrección y cumplimiento del flujo de
facturación; no hay benchmarks formales ni objetivos de throughput definidos  
**Constraints**: Cumplimiento XSD del SRI, acceso a certificado `.p12`,
disponibilidad de Java, compatibilidad Java 8 como baseline y flags para Java
9+, conectividad a WSDL del SRI, secretos vía variables de entorno  
**Scale/Scope**: Un paquete `src/fe_ec` pequeño con 4 módulos runtime, 1 XSD
principal, 1 JAR principal, 65 JARs auxiliares, 3 tests unitarios/funcionales
más 1 smoke test condicional, y artefactos de build en `dist/`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- PASS: El comprobante soportado y la frontera de esquema quedan identificados
  como `factura` con XSD `factura_V1_1.xsd`.
- PASS: El lifecycle está explicitado como generación de clave, construcción de
  XML, validación XSD, firma Java, recepción SRI y consulta de autorización.
- PASS WITH NOTE: Existe cobertura automatizada ejecutable mediante `unittest`;
  la referencia a `pytest` se conserva como drift documental a corregir.
- PASS: El impacto de runtime y empaquetado queda documentado para Python,
  Poetry, Java, XSD y bundle Java.
- PASS: La superficie pública queda identificada en módulos, clases, variables
  de entorno y artefactos de salida.
- PASS: El manejo de secretos depende de variables de entorno y archivos
  externos; no se requieren cambios de diseño para esta baseline.

Resultado del gate: sin bloqueos para el baseline documental. Se registran
riesgos y discrepancias operativas en `research.md`.

## Project Structure

### Documentation (this feature)

```text
specs/001-project-stack-baseline/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── library-interface.md
│   └── runtime-environment.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── fe_ec/
    ├── __init__.py
    ├── constants.py
    ├── schemas/
    │   └── factura_V1_1.xsd
    └── utils/
        ├── firmador_xml.py
        ├── generador_clave_acceso.py
        ├── manejador_xml.py
        ├── sri.py
        └── FirmaElectronica/
            ├── FirmaElectronica.jar
            └── lib/                # 65 JARs auxiliares + 1 archivo .p12 empaquetado en repo

tests/
├── test_constants.py
├── test_firmador_xml.py
└── test_smoke_firma.py

dist/
├── fe_ec-0.1.0-py3-none-any.whl
└── fe_ec-0.1.0.tar.gz

test.py
test2.py
pytest.py
fact_firmado.xml
temp_probe.xml
```

**Structure Decision**: Se mantiene la estructura de proyecto único con un
paquete Python principal y activos Java/XSD incluidos. No hay separación por
capas en directorios dedicados; la arquitectura es funcional por módulos
utilitarios más configuración centralizada.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
