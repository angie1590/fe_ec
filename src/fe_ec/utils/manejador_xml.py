# from lxml import etree
# from typing import Dict
# from src.fe_ec.utils.firmador_xml import firmar_xml_con_p12
# from src.fe_ec.constants import XSD_PATH, P12_PATH, P12_PASSWORD


# class ManejadorXML:
#     def __init__(self, xsd_path: str = XSD_PATH):
#         with open(xsd_path, 'rb') as xsd_file:
#             self.schema_doc = etree.parse(xsd_file)
#             self.schema = etree.XMLSchema(self.schema_doc)

#     def dict_a_xml(self, data: Dict, root_tag="factura") -> etree.Element:
#         def construir_elemento(tag, contenido):
#             if isinstance(contenido, dict):
#                 el = etree.Element(tag)
#                 for k, v in contenido.items():
#                     child = construir_elemento(k, v)
#                     if child is not None:
#                         if isinstance(child, list):
#                             for sub_child in child:
#                                 el.append(sub_child)
#                         else:
#                             el.append(child)
#                 return el
#             elif isinstance(contenido, list):
#                 elementos = []
#                 for item in contenido:
#                     child = construir_elemento(tag, item)
#                     if child is not None:
#                         elementos.append(child)
#                 return elementos
#             else:
#                 el = etree.Element(tag)
#                 el.text = str(contenido)
#                 return el

#         root = etree.Element(root_tag)  # Sin id

#         for k, v in data.items():
#             elem = construir_elemento(k, v)
#             if elem is not None:
#                 if isinstance(elem, list):
#                     for sub_elem in elem:
#                         root.append(sub_elem)
#                 else:
#                     root.append(elem)

#         return root

#     def generar_xml(self, json_data: Dict, output_path: str = "salida.xml") -> str:
#         xml_root = self.dict_a_xml(json_data)
#         xml_tree = etree.ElementTree(xml_root)

#         if not self.schema.validate(xml_tree):
#             errores = self.schema.error_log
#             raise ValueError(f"Errores de validación del XML: {errores}")

#         xml_tree.write(output_path, pretty_print=True, xml_declaration=True, encoding="UTF-8")
#         return output_path

#     def firmar_y_guardar_xml(
#         self,
#         json_data: Dict,
#         p12_path: str,
#         p12_password: str,
#         output_path: str = "fact_firmado.xml"
#     ) -> str:
#         try:
#             # 1. Generar el nodo <factura> a partir del diccionario
#             factura_element = self.dict_a_xml(json_data)

#             # 2. Envolver dentro del nodo <comprobante id="comprobante">
#             comprobante = etree.Element("comprobante", id="comprobante")
#             comprobante.append(factura_element)

#             # 3. Convertir a cadena XML
#             xml_str = etree.tostring(comprobante, encoding="utf-8").decode("utf-8")

#             # 4. Firmar el XML
#             from src.fe_ec.utils.firmador_xml import firmar_xml_con_p12
#             xml_firmado = firmar_xml_con_p12(xml_str, p12_path, p12_password)

#             # 5. Guardar en archivo
#             with open(output_path, "wb") as f:
#                 f.write(xml_firmado)

#             return output_path

#         except Exception as e:
#             raise ValueError(f"❌ Error durante la generación o firma del XML: {e}")

# from lxml import etree
# from src.fe_ec.utils.firmador_xml import firmar_xml_con_p12
# from src.fe_ec.constants import XSD_PATH, P12_PATH, P12_PASSWORD

# class ManejadorXML:
#     def __init__(self, xsd_path: str = XSD_PATH):
#         self.xsd_path = xsd_path

#     def firmar_y_guardar_xml(
#         self,
#         json_data: dict,
#         p12_path: str = P12_PATH,
#         p12_password: str = P12_PASSWORD,
#         output_path: str = "fact_firmado.xml"
#     ):
#         xml_str = self.dict_a_xml_string(json_data)
#         xml_firmado = firmar_xml_con_p12(xml_str, p12_path, p12_password)

#         with open(output_path, "wb") as f:
#             f.write(xml_firmado)

#         return output_path

#     def dict_a_xml_string(self, data: dict) -> str:
#         root = self.construir_elemento("factura", data)
#         root.set("id", "comprobante")
#         root.set("version", "2.0.0")
#         return etree.tostring(root, pretty_print=True, encoding="utf-8", xml_declaration=True).decode("utf-8")

#     def construir_elemento(self, tag: str, contenido):
#         if contenido is None:
#             return None

#         if isinstance(contenido, dict):
#             el = etree.Element(tag)
#             for k, v in contenido.items():
#                 child = self.construir_elemento(k, v)
#                 if child is not None:
#                     el.append(child)
#             return el

#         elif isinstance(contenido, list):
#             el = etree.Element(tag)
#             for item in contenido:
#                 if isinstance(item, dict):
#                     # singularizar si el tag termina en 's', ej: detalles → detalle
#                     singular = tag[:-1] if tag.endswith("s") else tag
#                     child = etree.Element(singular)
#                     for k, v in item.items():
#                         subchild = self.construir_elemento(k, v)
#                         if subchild is not None:
#                             child.append(subchild)
#                     el.append(child)
#                 else:
#                     subchild = self.construir_elemento(tag, item)
#                     if subchild is not None:
#                         el.append(subchild)
#             return el

#         else:
#             el = etree.Element(tag)
#             el.text = str(contenido)
#             return el
from lxml import etree
from src.fe_ec.utils.firmador_xml import firmar_xml_con_p12
from src.fe_ec.constants import XSD_PATH, P12_PATH, P12_PASSWORD

class ManejadorXML:
    def __init__(self, xsd_path: str = XSD_PATH):
        self.xsd_path = xsd_path

    def firmar_y_guardar_xml(
        self,
        json_data: dict,
        p12_path: str = P12_PATH,
        p12_password: str = P12_PASSWORD,
        output_path: str = "fact_firmado.xml"
    ):
        xml_str = self.dict_a_xml_string(json_data)
        xml_firmado = firmar_xml_con_p12(xml_str, p12_path, p12_password)

        with open(output_path, "wb") as f:
            f.write(xml_firmado)

        return output_path

    def dict_a_xml_string(self, data: dict) -> str:
        root = self.construir_elemento("factura", data)
        root.set("id", "comprobante")
        root.set("version", "2.0.0")
        return etree.tostring(root, pretty_print=True, encoding="utf-8", xml_declaration=True).decode("utf-8")

    def construir_elemento(self, tag: str, contenido):
        if contenido is None:
            return None

        if isinstance(contenido, dict):
            el = etree.Element(tag)
            for k, v in contenido.items():
                child = self.construir_elemento(k, v)
                if isinstance(child, list):
                    for item in child:
                        el.append(item)
                elif child is not None:
                    el.append(child)
            return el

        elif isinstance(contenido, list):
            elementos = []
            for item in contenido:
                child = etree.Element(tag)
                for k, v in item.items():
                    subchild = self.construir_elemento(k, v)
                    if isinstance(subchild, list):
                        for s in subchild:
                            child.append(s)
                    elif subchild is not None:
                        child.append(subchild)
                elementos.append(child)
            return elementos

        else:
            el = etree.Element(tag)
            el.text = str(contenido)
            return el
