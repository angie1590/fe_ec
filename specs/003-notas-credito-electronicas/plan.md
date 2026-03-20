# Implementation Plan: Emision de Notas de Credito Electronicas

**Branch**: `003-notas-credito-electronicas` | **Date**: 2026-03-19 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-notas-credito-electronicas/spec.md`

**Note**: Este plan preserva la arquitectura actual del proyecto. La nota de
credito se implementa como un nuevo contrato de negocio dentro de
`src/fe_ec/utils/`, reutilizando `constants.py`, `GeneradorClaveAcceso`,
`ManejadorXML`, `FirmadorXML` y `SRIService`, sin crear nuevas capas ni rutas
arquitectonicas.

## Summary

Se implemento la emision de notas de credito electronicas sobre el formato
oficial del SRI `notaCredito` version `1.1.0` (`codDoc 04`), reutilizando el
pipeline actual de generacion de clave, serializacion XML, validacion XSD,
firma XAdES-BES y flujo SRI de una sola llamada por etapa. El cambio tecnico
central fue incorporar un dominio explicito `NotaCreditoRequest`, su adaptador
YAML opcional, y completar la metadata del documento para que el serializador
compartido soporte los bloques oficiales de nota de credito
(`infoNotaCredito`, `totalConImpuestos`, `detalles`, `detallesAdicionales`,
`infoAdicional`) sin romper factura ni retencion.

## Technical Context

**Language/Version**: Python `>=3.10,<3.12` con entorno actual validado en
CPython `3.10.12`  
**Primary Dependencies**: `lxml` para XML/XSD, `zeep` para SOAP SRI,
`cryptography` para soporte criptografico Python, `PyYAML` para contratos YAML,
bundle Java existente para firma XAdES-BES, Poetry para empaquetado  
**Storage**: Filesystem local para XSD/XML oficiales del SRI, XML temporal,
XML firmado, certificado `.p12`, bundle Java y artefactos de prueba  
**Testing**: `unittest` con `poetry run python -m unittest discover -q`; smoke
de firma/envio condicional cuando exista certificado y password  
**Target Platform**: Libreria Python reutilizable en macOS/Linux y entornos
similares con Java disponible y salida HTTPS al SRI  
**Project Type**: Libreria Python monolitica con assets empaquetados y wrappers
de prueba, sin servicios ni capas adicionales  
**Performance Goals**: Prioridad absoluta en exactitud del XML oficial del SRI
y en mantener estable el flujo ya soportado para factura y retencion  
**Constraints**: Mantener arquitectura actual; no hard-code de runtime ni
secretos; usar `constants.py` como contrato oficial de runtime; separar runtime
de datos tributarios; respetar `codDoc 04`, raiz `notaCredito`, version
`1.1.0`; no agregar politicas de retry/polling dentro de la libreria  
**Scale/Scope**: Extension de un nuevo tipo documental dentro del pipeline
existente mediante metadata por documento, dominio tipado, contrato YAML,
ejemplo de wrapper y cobertura de regresion

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- PASS: El comprobante afectado queda identificado como nota de credito oficial
  `notaCredito` `1.1.0`, `codDoc 04`.
- PASS: El lifecycle se mantiene: generacion, validacion, firma, recepcion y
  consulta de autorizacion, sin flujo paralelo.
- PASS: La cobertura requerida incluye dominio, contrato YAML, XML/XSD de nota
  de credito y regresion de factura/retencion.
- PASS: El impacto de runtime y empaquetado se limita a metadata documental,
  XSD oficiales ya presentes en `src/fe_ec/schemas/Nota de Credito/` y
  documentacion de contrato.
- PASS: Se preserva la separacion entre runtime (`constants.py`, `FEEC_*`) y
  datos transaccionales (`NotaCreditoRequest` y contrato YAML).
- PASS: No se agregan secretos hardcodeados, ni paths de maquina, ni reintentos
  automáticos dentro de la libreria.
- PASS: No se modifican las capas ni el layout del repositorio; solo se
  extienden modulos ya existentes dentro de `src/fe_ec/utils/`.

Resultado del gate pre-diseno: aprobado.

## Project Structure

### Documentation (this feature)

```text
specs/003-notas-credito-electronicas/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── library-interface.md
│   ├── nota-credito-payload.md
│   └── runtime-configuration.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── fe_ec/
    ├── constants.py                          # Contrato oficial de runtime y metadata documental
    ├── schemas/
    │   ├── Factura/
    │   ├── Nota de Credito/
    │   ├── Nota de Debito/
    │   ├── Guia de Remision/
    │   ├── Liquidacion/
    │   └── Retencion/
    └── utils/
        ├── emisor.py                         # Perfil comun del emisor
        ├── factura.py                        # Dominio y payload de factura
        ├── factura_contract.py               # Adaptador YAML/dict -> FacturaRequest
        ├── retencion.py                      # Dominio y payload de retencion
        ├── retencion_contract.py             # Adaptador YAML/dict -> RetencionRequest
        ├── generador_clave_acceso.py         # Reutilizado con codDoc 01, 04 y 07
        ├── manejador_xml.py                  # Serializador/validador parametrizado por documento
        ├── firmador_xml.py                   # Reutilizado sin cambio estructural
        └── sri.py                            # Reutilizado sin cambio estructural

contracts/
├── factura.example.yaml
├── retencion.example.yaml
├── nota_credito.example.yaml                 # Contrato de ejemplo
└── nota_credito.smoke.yaml                   # Smoke contract autorizado en pruebas

tests/
├── test_constants.py
├── test_factura_builder.py
├── test_factura_contract.py
├── test_retencion_builder.py
├── test_retencion_contract.py
├── test_retencion_xml.py
├── test_nota_credito_builder.py              # Nuevo
├── test_nota_credito_contract.py             # Nuevo
├── test_nota_credito_xml.py                  # Nuevo
└── test_nota_credito_flow.py                 # Nuevo

test2.py                                      # Wrapper de factura
test_retencion.py                             # Wrapper de retencion
test_nota_credito.py                          # Nuevo wrapper de nota de credito
```

**Structure Decision**: Se preserva la estructura actual. La implementacion
agrega `nota_credito.py`, `nota_credito_contract.py`, `test_nota_credito.py`,
contratos YAML y pruebas dentro de directorios ya existentes. El pipeline
tecnico compartido (`constants.py`, `GeneradorClaveAcceso`, `ManejadorXML`,
`FirmadorXML`, `SRIService`) no cambia de arquitectura ni se duplica.

## Implementation Result

- Dominio implementado en `src/fe_ec/utils/nota_credito.py`.
- Adaptador YAML implementado en `src/fe_ec/utils/nota_credito_contract.py`.
- Wrapper operativo implementado en `test_nota_credito.py`.
- Contratos de ejemplo y smoke disponibles en `contracts/`.
- Metadata documental y serializacion compartida ajustadas en
  `src/fe_ec/constants.py` y `src/fe_ec/utils/manejador_xml.py`.
- Cobertura automatizada agregada para dominio, contrato, XML/XSD y flujo.
- Smoke real validado en `PRUEBAS` con autorizacion SRI.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
