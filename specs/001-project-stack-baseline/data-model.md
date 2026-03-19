# Data Model: Baseline del Stack Tecnologico

## 1. RuntimeContract

- **Purpose**: Representa el conjunto mínimo para ejecutar la librería.
- **Fields**:
  - `python_range`: `>=3.10,<3.12`
  - `active_python`: `3.10.12`
  - `package_manager`: `Poetry`
  - `java_requirement`: `Java 8 baseline; Java 9+ con compat flags`
  - `network_requirement`: `HTTPS hacia endpoints del SRI`
  - `filesystem_requirement`: acceso a XSD, JARs, XML temporales y `.p12`
- **Relationships**:
  - Usa `PackagedAsset`
  - Habilita `ValidationFlow`
  - Consume `EnvironmentConfig`
- **Validation rules**:
  - Debe existir un intérprete Python compatible.
  - Debe existir Java en PATH o en `FEEC_JAVA_BIN`.
  - Deben existir certificados y contraseñas cuando se invoca firma.

## 2. EnvironmentConfig

- **Purpose**: Superficie de configuración por variables de entorno.
- **Fields**:
  - `FEEC_XSD_PATH`
  - `FEEC_P12_PATH`
  - `FEEC_P12_PASSWORD`
  - `FEEC_AMBIENTE`
  - `FEEC_JAVA_BIN`
  - Variables auxiliares usadas por scripts de ejemplo: `FEEC_RUC`,
    `FEEC_ESTAB`, `FEEC_PTO_EMI`, `FEEC_SECUENCIAL`, `FEEC_FECHA_EMISION`,
    `FEEC_TIPO_EMISION`, `FEEC_OUTPUT_XML`
- **Relationships**:
  - Controla `SRIEndpointConfig`
  - Alimenta `SignatureCommand`
  - Modula `ValidationFlow`
- **Validation rules**:
  - `FEEC_AMBIENTE` debe normalizar a `pruebas` o `produccion`.
  - `FEEC_P12_PASSWORD` no puede estar vacío al firmar.

## 3. PackagedAsset

- **Purpose**: Recurso no Python necesario para cumplimiento o ejecución.
- **Fields**:
  - `asset_type`: `xsd`, `jar`, `jar_library`, `build_artifact`, `fixture`
  - `path`
  - `distribution_scope`: `repo_only`, `sdist`, `wheel`
  - `size_class`: `small`, `medium`, `large`
- **Relationships**:
  - Es requerido por `RuntimeContract`
  - Es consumido por `SignatureCommand` o `ValidationFlow`
- **Validation rules**:
  - El XSD empaquetado debe existir.
  - El bundle Java requerido por la firma debe estar presente en distribución
    compatible con el tipo de instalación.

## 4. ModuleSurface

- **Purpose**: Mapa de módulos Python y responsabilidades.
- **Fields**:
  - `module_name`
  - `responsibility`
  - `public_symbols`
  - `external_dependencies`
- **Instances**:
  - `fe_ec.constants`: endpoints, aliases de ambiente, configuración base
  - `fe_ec.utils.generador_clave_acceso`: algoritmo de clave de acceso
  - `fe_ec.utils.manejador_xml`: construcción, serialización y validación XML
  - `fe_ec.utils.firmador_xml`: bridge Python-Java para firma
  - `fe_ec.utils.sri`: cliente SOAP al SRI

## 5. ValidationFlow

- **Purpose**: Pipeline operativo del comprobante electrónico.
- **States**:
  - `payload_defined`
  - `clave_generada`
  - `xml_construido`
  - `xml_validado`
  - `xml_firmado`
  - `recepcion_enviada`
  - `autorizacion_consultada`
- **Transitions**:
  - `payload_defined -> clave_generada`
  - `clave_generada -> xml_construido`
  - `xml_construido -> xml_validado`
  - `xml_validado -> xml_firmado`
  - `xml_firmado -> recepcion_enviada`
  - `recepcion_enviada -> autorizacion_consultada`
- **Failure points**:
  - XSD inválido
  - Java no encontrado
  - certificado `.p12` ausente o contraseña incorrecta
  - WSDL no accesible o respuesta SRI no recibida

## 6. SignatureCommand

- **Purpose**: Comando final construido para invocar la firma.
- **Fields**:
  - `java_bin`
  - `compat_flags`
  - `classpath`
  - `main_class`
  - `xml_path`
  - `p12_path`
  - `output_path`
- **Relationships**:
  - Consume `EnvironmentConfig`
  - Requiere `PackagedAsset`
  - Produce `SignedXMLArtifact`
- **Validation rules**:
  - `xml_path`, `jar_path`, `lib_dir` y `p12_path` deben existir.
  - La contraseña debe estar presente.

## 7. TestSuiteCapability

- **Purpose**: Describe la capacidad real de validación automatizada del repo.
- **Fields**:
  - `framework`
  - `execution_command`
  - `status`
  - `coverage_scope`
- **Instances**:
  - `unittest`: `poetry run python -m unittest discover -q`, `available`
  - `pytest`: `poetry run pytest -q`, `missing_from_env`

