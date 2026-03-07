import os
from pathlib import Path

SRI_ENDPOINTS = {
    "pruebas": {
        "recepcion": "https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl",
        "autorizacion": "https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl"
    },
    "produccion": {
        "recepcion": "https://cel.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl",
        "autorizacion": "https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl"
    }
}

_ENVIRONMENT_ALIASES = {
    "1": "pruebas",
    "2": "produccion",
    "pruebas": "pruebas",
    "produccion": "produccion",
}


def normalizar_ambiente(value: str) -> str:
    normalized = (value or "pruebas").strip().lower()
    try:
        return _ENVIRONMENT_ALIASES[normalized]
    except KeyError as exc:
        raise ValueError(
            "FEEC_AMBIENTE debe ser 'pruebas', 'produccion', '1' o '2'."
        ) from exc


# Estos valores deberían ser definidos en el cliente o pasados como parámetros
DEFAULT_XSD_PATH = Path(__file__).resolve().parent / "schemas" / "factura_V1_1.xsd"

XSD_PATH = os.getenv("FEEC_XSD_PATH", str(DEFAULT_XSD_PATH))
P12_PATH = os.getenv("FEEC_P12_PATH", "firma.p12")
P12_PASSWORD = os.getenv("FEEC_P12_PASSWORD", "")
AMBIENTE = normalizar_ambiente(os.getenv("FEEC_AMBIENTE", "pruebas"))
