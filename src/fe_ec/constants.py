import os
from pathlib import Path

SRI_ENDPOINTS = {
    "pruebas": {
        "recepcion": "https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl",
        "autorizacion": "https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl",
    },
    "produccion": {
        "recepcion": "https://cel.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl",
        "autorizacion": "https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl",
    },
}

_ENVIRONMENT_ALIASES = {
    "1": "pruebas",
    "2": "produccion",
    "pruebas": "pruebas",
    "produccion": "produccion",
}

SCHEMAS_DIR = Path(__file__).resolve().parent / "schemas"


def _discover_packaged_schema(filename: str, fallback: str) -> Path:
    matches = sorted(SCHEMAS_DIR.rglob(filename))
    if matches:
        return matches[0]
    return SCHEMAS_DIR / fallback


DEFAULT_FACTURA_XSD_PATH = SCHEMAS_DIR / "factura_V1_1.xsd"
DEFAULT_RETENCION_XSD_PATH = _discover_packaged_schema(
    "ComprobanteRetencion_V2.0.0.xsd",
    "retencion_ats_v2_0_0.xsd",
)


def normalizar_ambiente(value: str) -> str:
    normalized = (value or "pruebas").strip().lower()
    try:
        return _ENVIRONMENT_ALIASES[normalized]
    except KeyError as exc:
        raise ValueError(
            "FEEC_AMBIENTE debe ser 'pruebas', 'produccion', '1' o '2'."
        ) from exc


def _resolve_xsd_path(*env_names: str, default: Path) -> str:
    for env_name in env_names:
        value = os.getenv(env_name)
        if value:
            return value
    return str(default)


FACTURA_XSD_PATH = _resolve_xsd_path(
    "FEEC_FACTURA_XSD_PATH",
    "FEEC_XSD_PATH",
    default=DEFAULT_FACTURA_XSD_PATH,
)
RETENCION_XSD_PATH = _resolve_xsd_path(
    "FEEC_RETENCION_XSD_PATH",
    default=DEFAULT_RETENCION_XSD_PATH,
)

# Legacy aliases preserved for the current factura flow.
DEFAULT_XSD_PATH = DEFAULT_FACTURA_XSD_PATH
XSD_PATH = FACTURA_XSD_PATH

P12_PATH = os.getenv("FEEC_P12_PATH", "firma.p12")
P12_PASSWORD = os.getenv("FEEC_P12_PASSWORD", "")
AMBIENTE = normalizar_ambiente(os.getenv("FEEC_AMBIENTE", "pruebas"))

DOCUMENT_METADATA = {
    "factura": {
        "cod_doc": "01",
        "root_tag": "factura",
        "xml_version": "2.0.0",
        "xsd_path": FACTURA_XSD_PATH,
        "required_blocks": ("infoTributaria", "infoFactura", "detalles"),
        "tag_aliases": {},
        "container_item_map": {
            "detalles": "detalle",
            "impuestos": "impuesto",
            "pagos": "pago",
        },
        "repeated_item_tags": {
            "detalle",
            "impuesto",
            "totalImpuesto",
            "pago",
            "campoAdicional",
        },
    },
    "retencion": {
        "cod_doc": "07",
        "root_tag": "comprobanteRetencion",
        "xml_version": "2.0.0",
        "xsd_path": RETENCION_XSD_PATH,
        "required_blocks": ("infoTributaria", "infoCompRetencion", "docsSustento"),
        "tag_aliases": {
            "Pagos": "pagos",
            "Pago": "pago",
            "formapago": "formaPago",
            "numeroautorizacionDocReemb": "numeroAutorizacionDocReemb",
            "codImpuestoReembolso": "codigo",
            "codigoPorcentajeReembolso": "codigoPorcentaje",
            "tarifaReembolso": "tarifa",
        },
        "container_item_map": {
            "detalles": "detalle",
            "impuestos": "impuesto",
            "pagos": "pago",
            "docsSustento": "docSustento",
            "impuestosDocSustento": "impuestoDocSustento",
            "retenciones": "retencion",
            "reembolsos": "reembolsoDetalle",
            "detalleImpuestos": "detalleImpuesto",
        },
        "repeated_item_tags": {
            "detalle",
            "impuesto",
            "totalImpuesto",
            "pago",
            "docSustento",
            "impuestoDocSustento",
            "retencion",
            "reembolsoDetalle",
            "detalleImpuesto",
            "campoAdicional",
        },
    },
}

COD_DOC_TO_DOCUMENT_TYPE = {
    metadata["cod_doc"]: document_type
    for document_type, metadata in DOCUMENT_METADATA.items()
}
ROOT_TAG_TO_DOCUMENT_TYPE = {
    metadata["root_tag"]: document_type
    for document_type, metadata in DOCUMENT_METADATA.items()
}


def infer_document_type(cod_doc: str | None) -> str | None:
    if not cod_doc:
        return None
    return COD_DOC_TO_DOCUMENT_TYPE.get(str(cod_doc).strip())


def get_document_config(document_type: str) -> dict:
    normalized = (document_type or "").strip().lower()
    try:
        config = DOCUMENT_METADATA[normalized]
    except KeyError as exc:
        raise ValueError(
            f"Tipo de documento no soportado: {document_type!r}. "
            f"Use uno de: {', '.join(sorted(DOCUMENT_METADATA))}."
        ) from exc
    return dict(config)
