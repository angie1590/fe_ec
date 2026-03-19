import tempfile
import unittest
from pathlib import Path

from fe_ec.utils.factura_contract import (
    factura_request_from_dict,
    load_factura_request_from_yaml,
)


def _contract_dict() -> dict:
    return {
        "version": 1,
        "factura": {
            "fecha_emision": "17/03/2026",
            "secuencial": "000000123",
            "tipo_emision": "1",
            "output_xml": "fact_firmado.xml",
            "moneda": "DOLAR",
            "emisor": {
                "ruc": "0103523908001",
                "razon_social": "PRUEBAS SERVICIO DE RENTAS INTERNA",
                "nombre_comercial": "MiComercio",
                "estab": "001",
                "pto_emi": "001",
                "dir_matriz": "Av. Principal 123",
                "dir_establecimiento": "Av. Secundaria 456",
                "obligado_contabilidad": "NO",
            },
            "comprador": {
                "tipo_identificacion": "04",
                "razon_social": "PRUEBAS SERVICIO DE RENTAS INTERNA",
                "identificacion": "0195125988001",
                "direccion": "Guapondelig",
            },
            "total_sin_impuestos": "100.00",
            "total_descuento": "0.00",
            "propina": "0.00",
            "importe_total": "115.00",
            "total_con_impuestos": [
                {
                    "codigo": "2",
                    "codigo_porcentaje": "4",
                    "base_imponible": "100.00",
                    "valor": "15.00",
                }
            ],
            "pagos": [
                {
                    "forma_pago": "01",
                    "total": "115.00",
                    "plazo": "0",
                    "unidad_tiempo": "DIAS",
                }
            ],
            "detalles": [
                {
                    "codigo_principal": "P001",
                    "descripcion": "Producto de prueba",
                    "cantidad": "1.00",
                    "precio_unitario": "100.00",
                    "descuento": "0.00",
                    "precio_total_sin_impuesto": "100.00",
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


class FacturaContractTests(unittest.TestCase):
    def test_construye_request_desde_dict(self):
        request = factura_request_from_dict(_contract_dict())

        self.assertEqual(request.emisor.ruc, "0103523908001")
        self.assertEqual(request.comprador.identificacion, "0195125988001")
        self.assertEqual(request.detalles[0].codigo_principal, "P001")
        self.assertEqual(request.total_con_impuestos[0].valor, "15.00")

    def test_aplica_defaults_operativos(self):
        contract = _contract_dict()
        del contract["factura"]["secuencial"]
        del contract["factura"]["fecha_emision"]
        del contract["factura"]["output_xml"]

        request = factura_request_from_dict(
            contract,
            default_secuencial="000009999",
            default_fecha_emision="18/03/2026",
            default_output_xml="salida.xml",
        )

        self.assertEqual(request.secuencial, "000009999")
        self.assertEqual(request.fecha_emision, "18/03/2026")
        self.assertEqual(request.output_xml, "salida.xml")

    def test_carga_request_desde_yaml(self):
        yaml_content = """
version: 1
factura:
  fecha_emision: "17/03/2026"
  secuencial: "000000123"
  tipo_emision: "1"
  output_xml: "fact_firmado.xml"
  moneda: "DOLAR"
  emisor:
    ruc: "0103523908001"
    razon_social: "PRUEBAS SERVICIO DE RENTAS INTERNA"
    estab: "001"
    pto_emi: "001"
    dir_matriz: "Av. Principal 123"
  comprador:
    tipo_identificacion: "04"
    razon_social: "PRUEBAS SERVICIO DE RENTAS INTERNA"
    identificacion: "0195125988001"
  total_sin_impuestos: "100.00"
  total_descuento: "0.00"
  propina: "0.00"
  importe_total: "115.00"
  total_con_impuestos:
    - codigo: "2"
      codigo_porcentaje: "4"
      base_imponible: "100.00"
      valor: "15.00"
  pagos:
    - forma_pago: "01"
      total: "115.00"
  detalles:
    - codigo_principal: "P001"
      descripcion: "Producto de prueba"
      cantidad: "1.00"
      precio_unitario: "100.00"
      descuento: "0.00"
      precio_total_sin_impuesto: "100.00"
      impuestos:
        - codigo: "2"
          codigo_porcentaje: "4"
          tarifa: "15.00"
          base_imponible: "100.00"
          valor: "15.00"
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "factura.yaml"
            path.write_text(yaml_content, encoding="utf-8")
            request = load_factura_request_from_yaml(path)

        payload = request.to_payload(
            clave_acceso="1703202601010352390800110010010000001231234567811",
            ambiente="1",
        )
        self.assertEqual(payload["infoTributaria"]["codDoc"], "01")
        self.assertEqual(payload["infoFactura"]["importeTotal"], "115.00")


if __name__ == "__main__":
    unittest.main()
