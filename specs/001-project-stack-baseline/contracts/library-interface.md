# Contract: Library Interface

## Public Python Surface

### `fe_ec.constants`

- `SRI_ENDPOINTS`: mapa de endpoints SOAP por ambiente
- `normalizar_ambiente(value: str) -> str`
- `DEFAULT_XSD_PATH`
- `XSD_PATH`
- `P12_PATH`
- `P12_PASSWORD`
- `AMBIENTE`

### `fe_ec.utils.generador_clave_acceso.GeneradorClaveAcceso`

- `generar(fecha_emision, tipo_comprobante, ruc, tipo_ambiente, serie, secuencial, tipo_emision="1") -> str`

**Input contract**:

- `fecha_emision`: `dd/mm/YYYY` o `ddmmYYYY`
- `tipo_comprobante`: string numérico de dos dígitos esperados por SRI
- `ruc`: string de 13 dígitos
- `tipo_ambiente`: `"1"` o `"2"`
- `serie`: establecimiento + punto de emisión
- `secuencial`: 9 dígitos o menos, se rellena

**Output contract**:

- retorna clave de acceso string con dígito verificador módulo 11

### `fe_ec.utils.manejador_xml.ManejadorXML`

- `__init__(xsd_path=None, p12_path=None, p12_password=None, firmador=None)`
- `firmar_y_guardar_xml(json_data, output_path="fact_firmado.xml") -> str | None`
- `dict_a_xml_string(data: dict, as_bytes: bool = False) -> str | bytes`
- `validar_estructura_xml(xml_path: str) -> bool`

**Input contract**:

- `json_data` debe representar un payload compatible con factura SRI
- `output_path` define el destino del XML firmado

**Output contract**:

- devuelve `str` con la ruta de salida cuando firma correctamente
- devuelve `None` cuando la estructura XML no valida
- levanta `RuntimeError` ante errores operativos de generación/firma

### `fe_ec.utils.firmador_xml.FirmadorXML`

- `parse_java_major_version(version_output: str) -> int`
- `compat_jvm_args(java_major_version: int) -> list[str]`
- `firmar_xml(xml_path, output_path, p12_path, p12_password) -> str`

**Runtime contract**:

- requiere Java accesible
- requiere `FirmaElectronica.jar` y `lib/`
- requiere archivo `.p12` existente y contraseña no vacía

### `fe_ec.utils.sri.SRIService`

- `enviar_recepcion(xml_bytes)`
- `consultar_autorizacion(clave_acceso: str)`

**Network contract**:

- usa WSDL SOAP del SRI según el ambiente normalizado
- retorna objetos de Zeep sin una capa DTO propia
- levanta `RuntimeError` o `ValueError` con mensajes traducidos

## Script Surface

### `test.py`

- script de ejemplo simple para generar, firmar y enviar una factura

### `test2.py`

- script de ejemplo más completo con parametrización por variables de entorno y
  trazas detalladas del flujo SRI

## Artifact Contract

- entrada principal: payload Python tipo `dict`
- salida intermedia: `temp_no_firmado.xml`
- salida final esperada: XML firmado (`fact_firmado.xml` por defecto)
- salida remota: respuesta SOAP de recepción y autorización del SRI

