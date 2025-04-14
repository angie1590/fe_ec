from lxml import etree
from src.fe_ec.utils.firmador_xml import FirmadorXML
from src.fe_ec.constants import XSD_PATH, P12_PATH, P12_PASSWORD
import os

class ManejadorXML:
    def __init__(self, xsd_path: str = XSD_PATH):
        self.xsd_path = xsd_path
        self.firmador = FirmadorXML()

    def firmar_y_guardar_xml(self, json_data, output_path="fact_firmado.xml"):
        try:
            # Paso 1: Generar el XML desde JSON
            xml_str = self.dict_a_xml_string(json_data)

            # Paso 2: Guardar temporalmente el XML sin firmar
            temp_input_path = "temp_no_firmado.xml"
            with open(temp_input_path, "w", encoding="utf-8") as f:
                f.write(xml_str)

            if self.validar_estructura_xml("temp_no_firmado.xml"):
                # Paso 3: Firmar usando el JAR externo (XAdES-BES)
                xml_firmado_path = self.firmador.firmar_xml(
                    xml_path=temp_input_path,
                    output_path=output_path,
                    p12_path=P12_PATH,
                    p12_password=P12_PASSWORD
                )

                print(f"✅ XML firmado correctamente en: {xml_firmado_path}")
                return xml_firmado_path
            else:
                return None

        except Exception as e:
            raise RuntimeError(f"❌ Error durante la generación o firma del XML: {e}")
        finally:
            if os.path.exists(temp_input_path):
                os.remove(temp_input_path)


    def dict_a_xml_string(self, data: dict, as_bytes: bool = False):
        root = self.construir_elemento("factura", data)
        root.set("id", "comprobante")
        root.set("version", "2.0.0")

        if "infoAdicional" in data:
            info_add = self.construir_info_adicional(data["infoAdicional"])
            root.append(info_add)

        xml = etree.tostring(
            root,
            pretty_print=True,
            encoding="utf-8",
            xml_declaration=True
        )
        return xml if as_bytes else xml.decode("utf-8")

    def construir_elemento(self, tag: str, contenido):
        if contenido is None:
            return None

        # ⛔ Evitamos procesar infoAdicional aquí, ya se maneja por separado
        if tag == "infoAdicional":
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
            sin_contenedor = {"detalle", "impuesto", "totalImpuesto", "pago"}
            if tag in sin_contenedor:
                elementos = []
                for item in contenido:
                    child = self.construir_elemento(tag, item)
                    if child is not None:
                        elementos.append(child)
                return elementos

            el = etree.Element(tag)
            singular = tag[:-1] if tag.endswith("s") else tag
            for item in contenido:
                child = etree.Element(singular)
                for k, v in item.items():
                    subchild = self.construir_elemento(k, v)
                    if subchild is not None:
                        child.append(subchild)
                el.append(child)
            return el

        else:
            el = etree.Element(tag)
            el.text = str(contenido)
            return el

    def construir_info_adicional(self, datos):
        el = etree.Element("infoAdicional")
        for campo in datos.get("campoAdicional", []):
            campo_el = etree.Element("campoAdicional")
            campo_el.set("nombre", campo["nombre"])
            campo_el.text = campo["valor"]
            el.append(campo_el)
        return el


    def validar_estructura_xml(self, xml_path: str) -> bool:
        """
        Valida el XML generado contra el XSD oficial del SRI, removiendo temporalmente
        la firma digital para evitar errores de validación estructural.
        """

        try:
            schema = etree.XMLSchema(etree.parse(self.xsd_path))
            parser = etree.XMLParser(remove_blank_text=True)
            tree = etree.parse(xml_path, parser)

            ns = {'ds': 'http://www.w3.org/2000/09/xmldsig#'}
            signature = tree.find('.//ds:Signature', namespaces=ns)
            if signature is not None:
                signature.getparent().remove(signature)

            schema.assertValid(tree)
            return True
        except etree.DocumentInvalid as e:
            print("❌ XML inválido según el XSD:", e)
            return False

