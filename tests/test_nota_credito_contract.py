import tempfile
import unittest
from pathlib import Path

from fe_ec.utils.nota_credito_contract import (
    NotaCreditoRequest,
    load_nota_credito_request_from_yaml,
    nota_credito_request_from_dict,
)


def _contract_dict() -> dict:
    return {
        "version": 1,
        "nota_credito": {
            "fecha_emision": "19/03/2026",
            "secuencial": "000000123",
            "tipo_emision": "1",
            "output_xml": ".artifacts/xml/nota_credito.xml",
            "moneda": "DOLAR",
            "emisor": {
                "ruc": "0103523908001",
                "razon_social": "PINEDA ALVAREZ DANIEL FERNANDO",
                "nombre_comercial": "PINEDA ALVAREZ DANIEL FERNANDO",
                "estab": "001",
                "pto_emi": "001",
                "dir_matriz": "Av. Principal 123",
                "dir_establecimiento": "Av. Secundaria 456",
                "obligado_contabilidad": "NO",
            },
            "comprador": {
                "tipo_identificacion": "04",
                "razon_social": "CLIENTE DE PRUEBA S.A.",
                "identificacion": "0195125988001",
            },
            "comprobante_modificado": {
                "cod_doc_modificado": "01",
                "num_doc_modificado": "001-001-000000321",
                "fecha_emision_doc_sustento": "18/03/2026",
            },
            "total_sin_impuestos": "100.00",
            "valor_modificacion": "115.00",
            "motivo": "DEVOLUCION PARCIAL",
            "total_con_impuestos": [
                {
                    "codigo": "2",
                    "codigo_porcentaje": "4",
                    "base_imponible": "100.00",
                    "valor": "15.00",
                }
            ],
            "detalles": [
                {
                    "codigo_interno": "P001",
                    "descripcion": "Producto ajustado",
                    "cantidad": "1.00",
                    "precio_unitario": "100.00",
                    "descuento": "0.00",
                    "precio_total_sin_impuesto": "100.00",
                    "detalles_adicionales": [
                        {
                            "nombre": "lote",
                            "valor": "ABC123",
                        }
                    ],
                    "impuestos": [
                        {
                            "codigo": "2",
                            "codigo_porcentaje": "4",
                            "tarifa": "15.00",
                            "base_imponible": "100.00",
                            "valor": "15.00",
                        }
                    ],
                }
            ],
            "info_adicional": [
                {"nombre": "email", "valor": "cliente@ejemplo.com"},
            ],
        },
    }


class NotaCreditoContractTests(unittest.TestCase):
    def test_construye_request_desde_dict(self):
        request = nota_credito_request_from_dict(_contract_dict())

        self.assertIsInstance(request, NotaCreditoRequest)
        self.assertEqual(request.emisor.ruc, "0103523908001")
        self.assertEqual(request.comprador.identificacion, "0195125988001")
        self.assertEqual(
            request.comprobante_modificado.num_doc_modificado,
            "001-001-000000321",
        )
        self.assertEqual(request.detalles[0].detalles_adicionales[0].nombre, "lote")

    def test_aplica_defaults_operativos(self):
        contract = _contract_dict()
        del contract["nota_credito"]["secuencial"]
        del contract["nota_credito"]["fecha_emision"]
        del contract["nota_credito"]["output_xml"]

        request = nota_credito_request_from_dict(
            contract,
            default_secuencial="000009999",
            default_fecha_emision="20/03/2026",
            default_output_xml="salida.xml",
        )

        self.assertEqual(request.secuencial, "000009999")
        self.assertEqual(request.fecha_emision, "20/03/2026")
        self.assertEqual(request.output_xml, "salida.xml")

    def test_carga_request_desde_yaml(self):
        yaml_content = """
version: 1
nota_credito:
  fecha_emision: "19/03/2026"
  secuencial: "000000123"
  tipo_emision: "1"
  output_xml: ".artifacts/xml/nota_credito.xml"
  emisor:
    ruc: "0103523908001"
    razon_social: "PINEDA ALVAREZ DANIEL FERNANDO"
    estab: "001"
    pto_emi: "001"
    dir_matriz: "Av. Principal 123"
  comprador:
    tipo_identificacion: "04"
    razon_social: "CLIENTE DE PRUEBA S.A."
    identificacion: "0195125988001"
  comprobante_modificado:
    cod_doc_modificado: "01"
    num_doc_modificado: "001-001-000000321"
    fecha_emision_doc_sustento: "18/03/2026"
  total_sin_impuestos: "100.00"
  valor_modificacion: "115.00"
  motivo: "DEVOLUCION PARCIAL"
  total_con_impuestos:
    - codigo: "2"
      codigo_porcentaje: "4"
      base_imponible: "100.00"
      valor: "15.00"
  detalles:
    - descripcion: "Producto ajustado"
      cantidad: "1.00"
      precio_unitario: "100.00"
      precio_total_sin_impuesto: "100.00"
      impuestos:
        - codigo: "2"
          codigo_porcentaje: "4"
          tarifa: "15.00"
          base_imponible: "100.00"
          valor: "15.00"
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "nota_credito.yaml"
            path.write_text(yaml_content, encoding="utf-8")
            request = load_nota_credito_request_from_yaml(path)

        payload = request.to_payload(
            clave_acceso="1903202604010352390800110010010000001231234567819",
            ambiente="1",
        )
        self.assertEqual(payload["infoTributaria"]["codDoc"], "04")
        self.assertEqual(
            payload["infoNotaCredito"]["numDocModificado"],
            "001-001-000000321",
        )


if __name__ == "__main__":
    unittest.main()
