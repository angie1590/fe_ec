# Implementation Plan: Emision de Comprobantes de Retencion Electronicos

**Branch**: `002-retenciones-electronicas` | **Date**: 2026-03-13 | **Last Updated**: 2026-03-19 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-retenciones-electronicas/spec.md`

**Note**: Este plan mantiene intacta la arquitectura actual del proyecto y
extiende exclusivamente los módulos, assets y contratos ya existentes para
soportar comprobantes de retención ATS.

## Summary

Se implementará la emisión de comprobantes de retención electrónicos usando la
estructura oficial del SRI para comprobante de retención ATS versión `2.0.0`
(`codDoc 07`), tomando como base normativa la ficha técnica offline `v2.32`
entregada por el usuario. La solución reutilizará el pipeline ya existente de
factura electrónica: generación de clave de acceso, construcción XML, validación
XSD, firma XAdES-BES y envío/consulta al SRI. El cambio técnico central será
parametrizar el flujo actual por tipo de documento, agregar reglas explícitas de
serialización para las secciones oficiales de retención ATS y separar runtime de
datos de negocio mediante requests tipados y contratos YAML opcionales dentro de
los módulos existentes de `src/fe_ec/utils/`, sin crear nuevas capas ni
modificar la arquitectura del repositorio.

## Technical Context

**Language/Version**: Python `>=3.10,<3.12` con entorno actual validado en
CPython `3.10.12`  
**Primary Dependencies**: `lxml` para construcción/validación XML, `zeep` para
SOAP SRI, `cryptography` para soporte criptográfico Python, `PyYAML` para
adaptadores de contrato YAML, bundle Java existente para firma XAdES-BES,
Poetry para empaquetado  
**Storage**: Filesystem local para XSD oficiales, XML temporal, XML firmado,
certificados `.p12`, bundle Java y artefactos de build  
**Testing**: `unittest` ejecutable con `poetry run python -m unittest discover -q`;
smoke tests condicionales según certificado/contraseña disponibles  
**Target Platform**: Librería Python reutilizable en macOS/Linux y entornos
similares con Java disponible y salida HTTPS al SRI  
**Project Type**: Librería Python monolítica con assets empaquetados, sin capas
adicionales ni servicios separados  
**Performance Goals**: Prioridad absoluta en cumplimiento exacto del formato
oficial del SRI y en no romper el flujo actual de factura electrónica  
**Constraints**: Mantener arquitectura actual; no hard-code de configuración ni
secretos; usar `constants.py` como contrato oficial de runtime; separar runtime
de datos de negocio por comprobante; respetar `codDoc 07`, raíz
`comprobanteRetencion`, versión `2.0.0`, bloques ATS oficiales y condicionales
del anexo; conservar compatibilidad con factura  
**Scale/Scope**: Extensión de un único tipo documental dentro del pipeline
existente mediante nuevos assets XSD, metadata por documento, reglas de
serialización explícitas, tests de regresión y ejemplos de uso

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- PASS: El comprobante afectado queda identificado como comprobante de retención
  ATS `2.0.0`, `codDoc 07`, con raíz `comprobanteRetencion`.
- PASS: El lifecycle sigue siendo el actual: generación, validación, firma,
  envío y consulta, sin flujo paralelo ni nuevo servicio.
- PASS: La cobertura requerida incluye serialización XML, validación XSD,
  regresión de factura y smoke opcional de firma/envío.
- PASS: El impacto de runtime y empaquetado se limita a nuevos XSD oficiales,
  metadata en `constants.py` y pruebas en la estructura vigente.
- PASS: Las superficies públicas afectadas se limitan a extensión compatible de
  `constants.py`, `ManejadorXML`, nuevos request models y adaptadores YAML
  opcionales dentro de `utils/`, con fallback compatible para scripts.
- PASS: Los secretos se mantienen en variables de entorno y archivos externos.
- PASS: No se introducen nuevas capas, directorios raíz, servicios ni
  reorganizaciones estructurales.

Resultado del gate pre-diseño: aprobado. La propuesta respeta íntegramente la
constitución y la prohibición de modificar la arquitectura.

## Project Structure

### Documentation (this feature)

```text
specs/002-retenciones-electronicas/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── library-interface.md
│   ├── retencion-payload.md
│   └── runtime-configuration.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── fe_ec/
    ├── constants.py                          # Contrato oficial de runtime y metadata técnica
    ├── schemas/
    │   ├── factura_V1_1.xsd
    │   └── retencion_ats_v2_0_0.xsd          # Asset oficial del SRI
    └── utils/
        ├── emisor.py                         # Perfil común del emisor
        ├── factura.py                        # Dominio y payload de factura
        ├── factura_contract.py               # Adaptador YAML/dict -> FacturaRequest
        ├── retencion.py                      # Dominio y payload de retención
        ├── retencion_contract.py             # Adaptador YAML/dict -> RetencionRequest
        ├── generador_clave_acceso.py         # Reutilizado con codDoc 01 y 07
        ├── manejador_xml.py                  # Parametrización por tipo de documento
        ├── firmador_xml.py                   # Reutilizado sin cambio arquitectónico
        └── sri.py                            # Reutilizado sin cambio arquitectónico

contracts/
├── factura.example.yaml                      # Contrato de factura de ejemplo
└── retencion.example.yaml                    # Contrato de retención de ejemplo

tests/
├── test_constants.py                         # Extensión de configuración oficial
├── test_factura_builder.py                   # Dominio/payload de factura
├── test_factura_contract.py                  # Adaptador YAML de factura
├── test_firmador_xml.py                      # Sin cambios funcionales esperados
├── test_smoke_firma.py                       # Reutilización del smoke del pipeline
├── test_retencion_builder.py                 # Dominio/payload de retención
├── test_retencion_contract.py                # Adaptador YAML de retención
├── test_retencion_xml.py                     # Serialización/validación retención
└── test_retencion_flow.py                    # Regresión del flujo reutilizado

test.py
test2.py                                      # Wrapper de factura
test_retencion.py                             # Wrapper de retención
```

**Structure Decision**: Se preserva la estructura actual. La implementación
extiende `src/fe_ec/utils/` con módulos de dominio y adaptadores de contrato,
además de ejemplos YAML y pruebas dentro de directorios ya existentes. Esto no
constituye una nueva capa arquitectónica: el pipeline técnico compartido
(`constants.py`, `ManejadorXML`, firma, SRI) permanece intacto y los wrappers
`test2.py`/`test_retencion.py` solo traducen entrada externa a requests tipados.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
