# Quickstart: Inspeccion y Validacion del Stack

## 1. Preparar entorno Python

```bash
poetry install
poetry run python --version
```

Resultado esperado:

- Entorno virtual creado en `.venv/`
- Python compatible con `>=3.10,<3.12`

## 2. Inspeccionar dependencias principales y transitivas

```bash
poetry show --tree
```

Puntos a verificar:

- `lxml`
- `xmlschema`
- `zeep`
- `cryptography`
- transitivos de red vía `requests`

## 3. Validar la suite automatizada realmente disponible

```bash
poetry run python -m unittest discover -q
```

Resultado esperado en el entorno actual:

- 9 tests ejecutados
- 1 skip condicionado por variables/certificado para smoke signing

Comprobación de drift documental:

```bash
poetry run pytest -q
```

Resultado esperado en el entorno actual:

- Falla por ausencia del comando `pytest` en el virtualenv

## 4. Verificar prerequisitos operativos no Python

```bash
java -version
```

Verificar además:

- existencia de `src/fe_ec/utils/FirmaElectronica/FirmaElectronica.jar`
- existencia del subdirectorio `src/fe_ec/utils/FirmaElectronica/lib/`
- disponibilidad de un archivo `.p12`
- definición de `FEEC_P12_PASSWORD`

## 5. Ejecutar un flujo local de ejemplo

Variables recomendadas:

```bash
export FEEC_P12_PATH=firma.p12
export FEEC_P12_PASSWORD='***'
export FEEC_AMBIENTE=1
```

Ejecución:

```bash
poetry run python test2.py
```

Este flujo:

1. Genera clave de acceso
2. Construye XML factura
3. Valida contra XSD
4. Firma usando Java
5. Envía a recepción SRI
6. Consulta autorización si recepción fue exitosa

## 6. Verificar empaquetado

```bash
unzip -l dist/fe_ec-0.1.0-py3-none-any.whl | sed -n '1,80p'
tar -tzf dist/fe_ec-0.1.0.tar.gz | sed -n '1,80p'
```

Objetivo:

- confirmar qué archivos llegan a wheel
- comparar si el sdist contiene más activos que la wheel

