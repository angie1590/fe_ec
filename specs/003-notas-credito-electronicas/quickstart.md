# Quickstart: Implementacion de Notas de Credito Electronicas

## 1. Preparar runtime oficial

La nota de credito debe seguir usando el contrato runtime actual del proyecto:

```bash
export FEEC_AMBIENTE=1
export FEEC_P12_PATH=firma.p12
export FEEC_P12_PASSWORD='***'
export FEEC_NOTA_CREDITO_XSD_PATH='src/fe_ec/schemas/Nota de Credito/NotaCredito_V1.1.0.xsd'
```

Notas:

- `FEEC_NOTA_CREDITO_XSD_PATH` es override opcional; por defecto el runtime
  debe resolver el XSD oficial ya empaquetado.
- `FEEC_XSD_PATH` se mantiene solo como alias legacy del flujo de factura.
- La libreria no debe introducir retries o polling automatico.

## 2. Preparar el contrato de negocio

La entrada recomendada debe ser un contrato YAML versionado, por ejemplo:

```yaml
version: 1
nota_credito:
  secuencial: "000000123"
  fecha_emision: "19/03/2026"
  tipo_emision: "1"
  output_xml: ".artifacts/xml/nota_credito_firmada.xml"
  emisor:
    ruc: "0103523908001"
    razon_social: "PINEDA ALVAREZ DANIEL FERNANDO"
    nombre_comercial: "PINEDA ALVAREZ DANIEL FERNANDO"
    estab: "001"
    pto_emi: "001"
    dir_matriz: "Cuenca"
    dir_establecimiento: "Cuenca"
    obligado_contabilidad: "NO"
  comprador:
    tipo_identificacion: "04"
    razon_social: "CLIENTE DE PRUEBA"
    identificacion: "0195125988001"
  comprobante_modificado:
    cod_doc_modificado: "01"
    num_doc_modificado: "001-001-000000321"
    fecha_emision_doc_sustento: "18/03/2026"
  total_sin_impuestos: "100.00"
  valor_modificacion: "115.00"
  total_con_impuestos:
    - codigo: "2"
      codigo_porcentaje: "4"
      base_imponible: "100.00"
      valor: "15.00"
  motivo: "DEVOLUCION PARCIAL"
  detalles:
    - descripcion: "Ajuste producto"
      cantidad: "1.00"
      precio_unitario: "100.00"
      precio_total_sin_impuesto: "100.00"
      impuestos:
        - codigo: "2"
          codigo_porcentaje: "4"
          tarifa: "15.00"
          base_imponible: "100.00"
          valor: "15.00"
```

## 3. Generar clave y payload

Despues de implementar, el flujo esperado debe verse asi:

```python
from fe_ec.utils.generador_clave_acceso import GeneradorClaveAcceso
from fe_ec.utils.nota_credito_contract import load_nota_credito_request_from_yaml
from fe_ec.utils.manejador_xml import ManejadorXML

request = load_nota_credito_request_from_yaml("contracts/nota_credito.example.yaml")

clave = GeneradorClaveAcceso.generar(
    fecha_emision=request.fecha_emision,
    tipo_comprobante="04",
    ruc=request.emisor.ruc,
    tipo_ambiente="1",
    serie=f"{request.emisor.estab}{request.emisor.pto_emi}",
    secuencial=request.secuencial,
    tipo_emision=request.tipo_emision,
)

payload = request.to_payload(clave_acceso=clave, ambiente="1")
manejador = ManejadorXML(document_type="nota_credito")
xml_firmado = manejador.firmar_y_guardar_xml(payload, request.output_xml)
```

## 4. Ejecutar el wrapper de ejemplo

El wrapper esperado de la feature debe permitir:

```bash
poetry run python test_nota_credito.py --contract contracts/nota_credito.example.yaml
```

Para un smoke reproducible contra el SRI en `PRUEBAS`, usar el contrato ya
validado:

```bash
FEEC_P12_PASSWORD='***' \
FEEC_AMBIENTE=1 \
poetry run python test_nota_credito.py --contract contracts/nota_credito.smoke.yaml
```

`contracts/nota_credito.smoke.yaml` omite `fecha_emision` y `secuencial` para
que el wrapper use la fecha actual y genere un secuencial nuevo por ejecucion.

Expectativas del wrapper:

- genera la clave con `codDoc 04`
- construye el payload desde contrato o fallback compatible
- firma una sola vez
- envia a recepcion una sola vez
- consulta autorizacion una sola vez

## 5. Verificar cobertura y regresion

```bash
poetry run python -m unittest discover -q
```

La cobertura debe demostrar:

- XML de nota de credito valido contra el XSD oficial
- request/contrato detectan datos invalidos antes de firmar
- factura y retencion siguen funcionando igual

## 6. Validar comportamiento operacional

Una vez emitido el XML firmado, la nota de credito debe entrar al mismo modelo
operativo ya existente para factura y retencion, sin nuevas capas, sin nuevos
clientes SRI y sin reintentos dentro de la libreria.
