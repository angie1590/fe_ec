# src/fe_ec/constants.py

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

XSD_PATH = "sri_docs/factura_V2.xsd"
P12_PATH = "firma.p12"
P12_PASSWORD = "Angie1590"  # En producción usar variable de entorno
AMBIENTE = "pruebas"