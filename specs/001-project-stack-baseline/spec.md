# Feature Specification: Baseline del Stack Tecnologico del Proyecto

**Feature Branch**: `001-project-stack-baseline`  
**Created**: 2026-03-13  
**Status**: Draft  
**Input**: User description: "Ejecutar `speckit.plan` y determinar el stack tecnológico real del proyecto con el mayor detalle posible."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Inventario Tecnico Confiable (Priority: P1)

Como mantenedor del paquete, necesito un inventario exacto del stack actual para
entender con qué runtime, dependencias, activos empaquetados, integraciones y
pruebas opera realmente la librería.

**Why this priority**: Sin una línea base confiable, cualquier refactor,
ampliación de comprobantes o cambio de compatibilidad se hace con supuestos.

**Independent Test**: El inventario es válido si un contribuidor puede ubicar
lenguaje, gestor de dependencias, módulos principales, artefactos empaquetados,
integraciones externas y comandos de validación usando solo estos artefactos.

**Acceptance Scenarios**:

1. **Given** el repositorio actual, **When** el mantenedor revisa el plan,
   **Then** puede identificar versiones de Python soportadas, dependencias
   directas y transitivas, y activos no Python incluidos en el paquete.
2. **Given** el código fuente y los tests, **When** el mantenedor revisa la
   documentación generada, **Then** puede mapear responsabilidades por módulo,
   flujo de ejecución y superficie pública consumida por integradores.

---

### User Story 2 - Contexto Operativo y de Desarrollo (Priority: P2)

Como contribuidor, necesito entender cómo se ejecuta, prueba, empaqueta y
configura la librería para poder trabajar sin depender de conocimiento tácito.

**Why this priority**: El proyecto mezcla Python, Java, XSD y SOAP; la fricción
de entrada es alta si el contexto operativo no queda formalizado.

**Independent Test**: El contexto es suficiente si un contribuidor puede
reproducir la instalación, correr la suite disponible y localizar los puntos de
configuración sin inspección adicional ad hoc.

**Acceptance Scenarios**:

1. **Given** un nuevo entorno local, **When** el contribuidor sigue el
   quickstart, **Then** puede instalar dependencias, ejecutar la validación
   automatizada disponible y entender prerequisitos como Java y certificados.
2. **Given** una incidencia de integración, **When** el contribuidor consulta
   los contratos y el research, **Then** puede ubicar variables de entorno,
   entradas/salidas del flujo XML y dependencias externas del SRI.

---

### User Story 3 - Base para Planeacion Futura (Priority: P3)

Como responsable técnico, necesito una línea base de planificación que permita
derivar specs y tareas futuras con gates alineados al stack real del proyecto.

**Why this priority**: El valor principal es habilitar trabajo futuro con
contexto consistente, no solo producir una foto estática del repositorio.

**Independent Test**: La base es útil si el plan deja resueltos los unknowns del
stack, identifica riesgos y define entidades/contratos reutilizables.

**Acceptance Scenarios**:

1. **Given** una futura feature sobre facturación, firma o SRI, **When** se use
   este baseline como referencia, **Then** el `Technical Context` puede
   completarse sin reinterpretar el stack desde cero.

---

### Edge Cases

- ¿Qué ocurre si el stack declarado en `README.md` no coincide con el stack
  ejecutable real del entorno o del empaquetado?
- ¿Cómo se documentan dependencias requeridas en runtime pero no administradas
  por Poetry, como Java o certificados `.p12`?
- ¿Cómo se representa una suite de pruebas que hoy corre con `unittest` aunque
  la documentación mencione `pytest`?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema de planificación MUST identificar el lenguaje,
  versiones soportadas, gestor de dependencias y método de empaquetado del
  proyecto.
- **FR-002**: El sistema de planificación MUST documentar las dependencias
  directas y las integraciones transitivas relevantes para XML, SOAP y firma.
- **FR-003**: El sistema de planificación MUST describir la arquitectura lógica
  del paquete, incluyendo generación de clave, generación/validación de XML,
  firma y consumo del SRI.
- **FR-004**: El sistema de planificación MUST inventariar los activos no Python
  empaquetados, incluidos XSD y JARs necesarios para la firma.
- **FR-005**: El sistema de planificación MUST documentar la superficie pública
  de configuración y consumo: módulos, clases, variables de entorno y
  artefactos de salida.
- **FR-006**: El sistema de planificación MUST state which lifecycle stage(s)
  are affected (generation, signing, submission, authorization lookup) and
  preserve inspectable inputs/outputs for those stages.
- **FR-007**: El sistema de planificación MUST definir los mecanismos de prueba
  realmente disponibles y diferenciar entre tooling documentado y tooling
  instalado/ejecutable.
- **FR-008**: El sistema de planificación MUST definir cómo se proveen secretos
  y configuración sensible sin hardcodearlos.
- **FR-009**: El sistema de planificación MUST identificar riesgos, lagunas y
  tensiones del stack que afecten futuras decisiones de diseño.

### Key Entities *(include if feature involves data)*

- **Runtime Contract**: Conjunto de versiones, binarios externos, variables de
  entorno y dependencias necesarias para ejecutar la librería.
- **Module Surface**: Mapa de módulos Python, clases públicas y
  responsabilidades funcionales de cada componente.
- **Packaged Asset**: Recurso no Python distribuido con el paquete, como XSD,
  JAR principal, librerías Java auxiliares y artefactos de build.
- **Validation Flow**: Secuencia desde payload Python hasta XML firmado y
  respuesta del SRI, con entradas, salidas y puntos de falla.

## Compliance & Contract Impact *(mandatory when behavior changes)*

- **Affected Schemas/Artifacts**: `src/fe_ec/schemas/factura_V1_1.xsd`,
  `src/fe_ec/utils/FirmaElectronica/FirmaElectronica.jar`, librerías Java en
  `src/fe_ec/utils/FirmaElectronica/lib/`, wheel y sdist en `dist/`.
- **Configuration Surface**: `FEEC_XSD_PATH`, `FEEC_P12_PATH`,
  `FEEC_P12_PASSWORD`, `FEEC_AMBIENTE`, `FEEC_JAVA_BIN`, además de archivos XML
  y certificados `.p12`.
- **Compatibility Notes**: La baseline es documental y no altera comportamiento,
  pero debe reflejar contratos actuales consumidos por integradores.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un lector técnico puede identificar el stack principal del
  proyecto en menos de 10 minutos sin explorar el repo manualmente.
- **SC-002**: El plan resuelve todos los unknowns del `Technical Context`
  relevantes para runtime, dependencias, pruebas, empaquetado e integraciones.
- **SC-003**: Los artefactos generados permiten mapear de forma explícita al
  menos cuatro dominios: XML/XSD, firma digital, integración SOAP SRI y
  distribución del paquete.
- **SC-004**: El quickstart deja documentado al menos un camino verificable para
  ejecutar la suite automatizada disponible en el entorno actual.
- **SC-005**: El inventario distingue claramente entre stack declarado,
  stack empaquetado y stack efectivamente ejecutable.
- **SC-006**: Los contratos generados cubren configuración, APIs públicas y
  artefactos de entrada/salida sin dejar ambigüedades críticas.
