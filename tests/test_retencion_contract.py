import tempfile
import unittest
from pathlib import Path

from fe_ec.utils.retencion_contract import (
    RetencionRequest,
    load_retencion_request_from_yaml,
    retencion_request_from_dict,
)


def _contract_dict() -> dict:
    return {
        "version": 1,
        "retencion": {
            "fecha_emision": "14/03/2026",
            "secuencial": "000000123",
            "tipo_emision": "1",
            "output_xml": "retencion_firmada.xml",
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
            "sujeto_retenido": {
                "tipo_identificacion": "04",
                "identificacion": "0104228093001",
                "razon_social": "GABRIELA CONTRERAS",
                "parte_rel": "NO",
            },
            "documentos_sustento": [
                {
                    "cod_sustento": "01",
                    "cod_doc_sustento": "01",
                    "num_doc_sustento": "001002000004725",
                    "fecha_emision_doc_sustento": "14/03/2026",
                    "fecha_registro_contable": "14/03/2026",
                    "num_aut_doc_sustento": "1403202601010422809300120010020000047251106242116",
                    "pago_loc_ext": "01",
                    "total_sin_impuestos": "43.91",
                    "importe_total": "50.50",
                    "impuestos_doc_sustento": [
                        {
                            "cod_impuesto_doc_sustento": "2",
                            "codigo_porcentaje": "4",
                            "base_imponible": "43.91",
                            "tarifa": "15.00",
                            "valor_impuesto": "6.59",
                        }
                    ],
                    "retenciones": [
                        {
                            "codigo": "1",
                            "codigo_retencion": "304A",
                            "base_imponible": "43.91",
                            "porcentaje_retener": "10.000000",
                            "valor_retenido": "4.39",
                        },
                        {
                            "codigo": "2",
                            "codigo_retencion": "2",
                            "base_imponible": "6.59",
                            "porcentaje_retener": "70.000000",
                            "valor_retenido": "4.61",
                        },
                    ],
                    "pagos": [
                        {
                            "forma_pago": "19",
                            "total": "50.50",
                        }
                    ],
                }
            ],
            "info_adicional": [
                {"nombre": "email", "valor": "cliente@ejemplo.com"},
                {"nombre": "referencia", "valor": "RET-000000123"},
            ],
        },
    }


class RetencionContractTests(unittest.TestCase):
    def test_construye_request_desde_dict(self):
        request = retencion_request_from_dict(_contract_dict())

        self.assertIsInstance(request, RetencionRequest)
        self.assertEqual(request.emisor.ruc, "0103523908001")
        self.assertEqual(request.sujeto_retenido.identificacion, "0104228093001")
        self.assertEqual(request.documentos_sustento[0].num_doc_sustento, "001002000004725")
        self.assertEqual(request.documentos_sustento[0].retenciones[1].valor_retenido, "4.61")

    def test_aplica_defaults_para_campos_operativos(self):
        contract = _contract_dict()
        del contract["retencion"]["secuencial"]
        del contract["retencion"]["fecha_emision"]
        del contract["retencion"]["output_xml"]

        request = retencion_request_from_dict(
            contract,
            default_secuencial="000009999",
            default_fecha_emision="15/03/2026",
            default_output_xml="salida.xml",
        )

        self.assertEqual(request.secuencial, "000009999")
        self.assertEqual(request.fecha_emision, "15/03/2026")
        self.assertEqual(request.output_xml, "salida.xml")

    def test_carga_request_desde_yaml(self):
        yaml_content = """
version: 1
retencion:
  fecha_emision: "14/03/2026"
  secuencial: "000000123"
  tipo_emision: "1"
  output_xml: "retencion_firmada.xml"
  emisor:
    ruc: "0103523908001"
    razon_social: "PINEDA ALVAREZ DANIEL FERNANDO"
    estab: "001"
    pto_emi: "001"
    dir_matriz: "Av. Principal 123"
  sujeto_retenido:
    tipo_identificacion: "04"
    identificacion: "0104228093001"
    razon_social: "GABRIELA CONTRERAS"
  documentos_sustento:
    - cod_sustento: "01"
      cod_doc_sustento: "01"
      num_doc_sustento: "001002000004725"
      fecha_emision_doc_sustento: "14/03/2026"
      num_aut_doc_sustento: "1403202601010422809300120010020000047251106242116"
      pago_loc_ext: "01"
      total_sin_impuestos: "43.91"
      importe_total: "50.50"
      impuestos_doc_sustento:
        - cod_impuesto_doc_sustento: "2"
          codigo_porcentaje: "4"
          base_imponible: "43.91"
          tarifa: "15.00"
          valor_impuesto: "6.59"
      retenciones:
        - codigo: "1"
          codigo_retencion: "304A"
          base_imponible: "43.91"
          porcentaje_retener: "10.000000"
          valor_retenido: "4.39"
      pagos:
        - forma_pago: "19"
          total: "50.50"
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "retencion.yaml"
            path.write_text(yaml_content, encoding="utf-8")
            request = load_retencion_request_from_yaml(path)

        self.assertEqual(request.documentos_sustento[0].pagos[0].forma_pago, "19")
        payload = request.to_payload(
            clave_acceso="1403202607010352390800110010010000001231234567810",
            ambiente="1",
        )
        self.assertEqual(payload["infoTributaria"]["codDoc"], "07")
        self.assertEqual(
            payload["docsSustento"][0]["numAutDocSustento"],
            "1403202601010422809300120010020000047251106242116",
        )


if __name__ == "__main__":
    unittest.main()
