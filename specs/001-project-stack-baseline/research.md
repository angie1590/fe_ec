# Research: Baseline del Stack Tecnologico

## Fuentes de evidencia

- `pyproject.toml`
- `poetry show --tree`
- `poetry run python --version`
- `poetry run python -m unittest discover -q`
- Código en `src/fe_ec/`
- Tests en `tests/`
- Artefactos de build en `dist/`

## Decision 1: El runtime principal es una libreria Python gestionada con Poetry

**Decision**: Tratar el proyecto como una librería Python instalable y
distribuible mediante Poetry.

**Rationale**: `pyproject.toml` declara un paquete `fe_ec` bajo `src/`, define
dependencias runtime, y el repositorio ya contiene wheel y sdist generados.
Poetry además gestiona un virtualenv local `.venv` con Python 3.10.12.

**Alternatives considered**:

- Proyecto "script-only": descartado porque existe empaquetado wheel/sdist.
- Aplicación web o servicio: descartado porque no hay servidor, router ni capa
  de persistencia.

## Decision 2: El stack XML se apoya en lxml + xmlschema

**Decision**: Considerar `lxml` como motor principal de construcción/parsing XML
y `xmlschema` como dependencia declarada de validación de esquemas.

**Rationale**: `manejador_xml.py` usa `lxml.etree` para construir, serializar y
validar XML; el esquema `src/fe_ec/schemas/factura_V1_1.xsd` se resuelve desde
`constants.py`. Aunque el código actual valida con `lxml.XMLSchema`, la
presencia de `xmlschema` en Poetry indica que sigue siendo parte del stack
decidido del proyecto.

**Alternatives considered**:

- `xml.etree.ElementTree`: no se usa y ofrece menor capacidad para validación
  XSD avanzada.
- Validación externa fuera de Python: descartada porque el repo ya contiene la
  lógica en el lado Python.

## Decision 3: La firma electronica depende de una toolchain Java empaquetada

**Decision**: Mantener la firma como integración híbrida Python + Java basada en
`subprocess`, `FirmaElectronica.jar` y una librería auxiliar de 65 JARs.

**Rationale**: `firmador_xml.py` compone un classpath local, detecta versión de
Java y ejecuta `firmaelectronica.FirmaElectronica`. El bundle ocupa
aproximadamente `37M` en `src/fe_ec/utils/FirmaElectronica`, lo que lo convierte
en una parte estructural del stack, no en una dependencia incidental.

**Alternatives considered**:

- Firma 100% Python: no hay implementación presente en el repo.
- Dependencia remota de un servicio firmador: no hay evidencia de integración
  externa de ese tipo.

## Decision 4: La integracion con el SRI es SOAP sin capa intermedia propia

**Decision**: Modelar la interacción con el SRI como una integración SOAP
directa usando Zeep sobre WSDLs de recepción y autorización.

**Rationale**: `sri.py` instancia `zeep.Client` contra endpoints de pruebas y
producción definidos en `constants.py`. Zeep introduce transitivamente
`requests`, `requests-file`, `requests-toolbelt`, `attrs`, `isodate`, `pytz` y
otros componentes del stack de red/serialización.

**Alternatives considered**:

- REST/JSON: no existe en el código ni en los endpoints declarados.
- Adaptador propio de transporte HTTP: no se implementa actualmente.

## Decision 5: El contrato de configuracion es environment-first

**Decision**: Documentar `FEEC_XSD_PATH`, `FEEC_P12_PATH`,
`FEEC_P12_PASSWORD`, `FEEC_AMBIENTE` y `FEEC_JAVA_BIN` como la superficie
principal de configuración runtime.

**Rationale**: `constants.py` resuelve XSD, ambiente y credenciales; el
firmador usa `FEEC_JAVA_BIN`; los scripts de ejemplo cargan además RUC,
establecimiento y secuenciales desde variables de entorno.

**Alternatives considered**:

- Archivo de configuración central: no existe.
- Inyección DI o settings objects formales: no está presente en la API pública.

## Decision 6: La suite ejecutable real es unittest, no pytest

**Decision**: Registrar `unittest` como framework de pruebas efectivamente
disponible y `pytest` como tooling referenciado, pero ausente del entorno
actual.

**Rationale**: `poetry run python -m unittest discover -q` ejecuta 9 tests con
1 skip; `poetry run pytest -q` falla porque `pytest` no está instalado. La
documentación de README menciona `pytest`, así que existe drift entre la capa
documental y la capa ejecutable.

**Alternatives considered**:

- Declarar `pytest` como stack real: descartado por falta de instalación.
- Tratar el proyecto como no testeable: descartado porque la suite `unittest`
  sí corre.

## Decision 7: El empaquetado actual muestra una discrepancia entre wheel y sdist

**Decision**: Tratar el sdist como el artefacto más completo del bundle actual y
registrar la wheel como potencialmente incompleta para firma.

**Rationale**: El `tar.gz` contiene `FirmaElectronica.jar` y todo el subdirectorio
`lib/`, pero la wheel listada en `dist/fe_ec-0.1.0-py3-none-any.whl` solo
incluye `FirmaElectronica.jar`, el XSD y los módulos Python visibles, sin el
directorio `lib/`. Si eso refleja el artefacto realmente distribuido, la firma
electrónica en instalaciones vía wheel podría quedar degradada.

**Alternatives considered**:

- Asumir que la wheel contiene el mismo bundle que el sdist: la evidencia del
  zip no lo confirma.
- Ignorar la diferencia por ser solo build local: descartado porque afecta
  directamente el contrato de distribución.

## Decision 8: La arquitectura funcional es lineal y orientada a pipeline

**Decision**: Describir la arquitectura como un pipeline de documentos
electrónicos:

1. Normalización de ambiente y endpoints
2. Generación de clave de acceso
3. Construcción de XML desde payload dict
4. Validación contra XSD
5. Firma Java XAdES-BES
6. Envío SOAP al SRI
7. Consulta de autorización

**Rationale**: El flujo se distribuye entre `constants.py`,
`generador_clave_acceso.py`, `manejador_xml.py`, `firmador_xml.py` y `sri.py`,
sin una capa orquestadora formal más allá de los scripts de ejemplo.

**Alternatives considered**:

- Arquitectura en capas con servicios/domain/models: no se observa esa
  separación en la estructura actual.

## Riesgos y notas para trabajo futuro

- `README.md` indica `pip install fe-ec-lib`, mientras `pyproject.toml` declara
  `name = "fe-ec"`.
- La wheel visible en `dist/` parece omitir `utils/FirmaElectronica/lib/`.
- Existe un archivo raíz `pytest.py` que podría interferir con importaciones si
  `pytest` se añade después sin limpiar nombres locales.
- `manejador_xml.py` escribe `temp_no_firmado.xml` en el directorio actual y
  usa `print`, no logging estructurado.
- El paquete soporta hoy un esquema principal de factura; la expansión a otros
  comprobantes requerirá validar si el diseño sigue siendo suficiente.

