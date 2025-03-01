from lxml import etree

class ManejadorXML:
    """
    Utilidades para la generación y manipulación de archivos XML de comprobantes electrónicos.
    """
    @staticmethod
    def crear_xml(datos_factura: dict) -> str:
        """
        Genera una representación XML de la factura basada en los datos ingresados.
        """
        factura = etree.Element("factura")
        info_tributaria = etree.SubElement(factura, "infoTributaria")
        for key, value in datos_factura.get("infoTributaria", {}).items():
            etree.SubElement(info_tributaria, key).text = str(value)

        detalles = etree.SubElement(factura, "detalles")
        for item in datos_factura.get("detalles", []):
            detalle = etree.SubElement(detalles, "detalle")
            for key, value in item.items():
                etree.SubElement(detalle, key).text = str(value)

            impuestos = etree.SubElement(detalle, "impuestos")
            for impuesto in item.get("impuestos", []):
                impuesto_xml = etree.SubElement(impuestos, "impuesto")
                for key, value in impuesto.items():
                    etree.SubElement(impuesto_xml, key).text = str(value)

        return etree.tostring(factura, pretty_print=True, encoding='UTF-8', xml_declaration=True).decode('UTF-8')