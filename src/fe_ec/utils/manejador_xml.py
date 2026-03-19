import os
import tempfile
from pathlib import Path

from lxml import etree

from fe_ec.constants import (
    DEFAULT_XMLDSIG_XSD_PATH,
    P12_PASSWORD,
    P12_PATH,
    ROOT_TAG_TO_DOCUMENT_TYPE,
    get_document_config,
    infer_document_type,
)
from fe_ec.utils.firmador_xml import FirmadorXML


class _SchemaImportResolver(etree.Resolver):
    def resolve(self, system_url, public_id, context):
        if Path(system_url).name != "xmldsig-core-schema.xsd":
            return None
        xmldsig_path = Path(DEFAULT_XMLDSIG_XSD_PATH)
        if not xmldsig_path.exists():
            return None
        return self.resolve_filename(str(xmldsig_path), context)


class ManejadorXML:
    def __init__(
        self,
        document_type: str | None = None,
        xsd_path: str | None = None,
        p12_path: str | None = None,
        p12_password: str | None = None,
        firmador: FirmadorXML | None = None,
    ):
        self.document_type = (document_type or "").strip().lower() or None
        self.xsd_path_override = xsd_path
        self.p12_path = p12_path or P12_PATH
        self.p12_password = p12_password if p12_password is not None else P12_PASSWORD
        self.firmador = firmador

    def firmar_y_guardar_xml(self, json_data, output_path="fact_firmado.xml"):
        temp_input_path = None
        try:
            xml_str = self.dict_a_xml_string(json_data)

            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                suffix=".xml",
                delete=False,
            ) as temp_file:
                temp_file.write(xml_str)
                temp_input_path = temp_file.name

            if not self.validar_estructura_xml(temp_input_path):
                return None

            firmador = self.firmador or FirmadorXML()
            xml_firmado_path = firmador.firmar_xml(
                xml_path=temp_input_path,
                output_path=output_path,
                p12_path=self.p12_path,
                p12_password=self.p12_password,
            )

            print(f"XML firmado correctamente en: {xml_firmado_path}")
            return xml_firmado_path
        except RuntimeError:
            raise
        except Exception as exc:
            raise RuntimeError(
                f"Error durante la generacion o firma del XML: {exc}"
            ) from exc
        finally:
            if temp_input_path and os.path.exists(temp_input_path):
                os.remove(temp_input_path)

    def dict_a_xml_string(
        self,
        data: dict,
        as_bytes: bool = False,
        document_type: str | None = None,
    ):
        config = self._resolve_document_config(data=data, document_type=document_type)
        self._validate_required_blocks(data, config)

        root = etree.Element(config["root_tag"])
        root.set("id", "comprobante")
        root.set("version", config["xml_version"])

        for tag, contenido in data.items():
            if tag == "infoAdicional":
                continue

            child = self.construir_elemento(tag, contenido, config)
            if isinstance(child, list):
                for item in child:
                    root.append(item)
            elif child is not None:
                root.append(child)

        if "infoAdicional" in data:
            root.append(self.construir_info_adicional(data["infoAdicional"], config))

        xml = etree.tostring(
            root,
            pretty_print=True,
            encoding="utf-8",
            xml_declaration=True,
        )
        return xml if as_bytes else xml.decode("utf-8")

    def construir_elemento(self, tag: str, contenido, config: dict):
        if contenido is None:
            return None

        normalized_tag = self._normalize_tag(tag, config)
        if normalized_tag == "infoAdicional":
            return None

        if isinstance(contenido, dict):
            element = etree.Element(normalized_tag)
            for child_tag, child_value in contenido.items():
                child = self.construir_elemento(child_tag, child_value, config)
                if isinstance(child, list):
                    for item in child:
                        element.append(item)
                elif child is not None:
                    element.append(child)
            return element

        if isinstance(contenido, list):
            return self._construir_lista(normalized_tag, contenido, config)

        element = etree.Element(normalized_tag)
        element.text = str(contenido)
        return element

    def construir_info_adicional(self, datos, config: dict):
        info_adicional = etree.Element("infoAdicional")

        if isinstance(datos, dict):
            campos = datos.get("campoAdicional", [])
        else:
            campos = datos or []

        for campo in campos:
            campo_el = etree.Element("campoAdicional")
            campo_el.set("nombre", str(campo["nombre"]))
            campo_el.text = str(campo["valor"])
            info_adicional.append(campo_el)

        return info_adicional

    def validar_estructura_xml(
        self,
        xml_path: str,
        document_type: str | None = None,
    ) -> bool:
        try:
            parser = etree.XMLParser(remove_blank_text=True)
            tree = etree.parse(xml_path, parser)
            config = self._resolve_document_config(
                document_type=document_type,
                xml_tree=tree,
            )
            xsd_path = Path(config["xsd_path"])

            if not xsd_path.exists():
                raise RuntimeError(
                    f"No se encontro el XSD configurado para {config['root_tag']}: {xsd_path}"
                )

            xsd_parser = etree.XMLParser(remove_blank_text=True)
            xsd_parser.resolvers.add(_SchemaImportResolver())
            schema = etree.XMLSchema(etree.parse(str(xsd_path), parser=xsd_parser))

            ns = {"ds": "http://www.w3.org/2000/09/xmldsig#"}
            signature = tree.find(".//ds:Signature", namespaces=ns)
            if signature is not None:
                signature.getparent().remove(signature)

            schema.assertValid(tree)
            return True
        except etree.DocumentInvalid as exc:
            print(f"XML invalido segun el XSD: {exc}")
            return False
        except etree.XMLSyntaxError as exc:
            raise RuntimeError(f"El XML no pudo parsearse correctamente: {exc}") from exc
        except etree.XMLSchemaParseError as exc:
            raise RuntimeError(f"El XSD configurado no es valido: {exc}") from exc

    def _construir_lista(self, tag: str, contenido: list, config: dict):
        repeated_item_tags = set(config.get("repeated_item_tags", ()))
        if tag in repeated_item_tags:
            elementos = []
            for item in contenido:
                child = self.construir_elemento(tag, item, config)
                if child is not None:
                    elementos.append(child)
            return elementos

        container = etree.Element(tag)
        item_tag = config.get("container_item_map", {}).get(tag, self._infer_item_tag(tag))
        item_tag = self._normalize_tag(item_tag, config)

        for item in contenido:
            child = self.construir_elemento(item_tag, item, config)
            if isinstance(child, list):
                for subchild in child:
                    container.append(subchild)
            elif child is not None:
                container.append(child)
        return container

    def _resolve_document_config(
        self,
        data: dict | None = None,
        document_type: str | None = None,
        xml_tree: etree._ElementTree | None = None,
    ) -> dict:
        selected_document_type = (
            (document_type or "").strip().lower()
            or self.document_type
            or self._infer_document_type_from_payload(data)
            or self._infer_document_type_from_tree(xml_tree)
            or "factura"
        )
        config = get_document_config(selected_document_type)
        if self.xsd_path_override:
            config["xsd_path"] = self.xsd_path_override
        self._validate_cod_doc(data, config)
        return config

    def _infer_document_type_from_payload(self, data: dict | None) -> str | None:
        if not isinstance(data, dict):
            return None

        info_tributaria = data.get("infoTributaria")
        if not isinstance(info_tributaria, dict):
            return None

        return infer_document_type(info_tributaria.get("codDoc"))

    def _infer_document_type_from_tree(
        self,
        xml_tree: etree._ElementTree | None,
    ) -> str | None:
        if xml_tree is None:
            return None

        root_tag = etree.QName(xml_tree.getroot()).localname
        return ROOT_TAG_TO_DOCUMENT_TYPE.get(root_tag)

    def _validate_cod_doc(self, data: dict | None, config: dict) -> None:
        if not isinstance(data, dict):
            return

        info_tributaria = data.get("infoTributaria")
        if not isinstance(info_tributaria, dict):
            return

        cod_doc = info_tributaria.get("codDoc")
        if cod_doc is None:
            return

        if str(cod_doc).strip() != config["cod_doc"]:
            raise ValueError(
                "El payload no coincide con el tipo de documento configurado: "
                f"se esperaba codDoc {config['cod_doc']} y se recibio {cod_doc}."
            )

    def _validate_required_blocks(self, data: dict, config: dict) -> None:
        missing = [
            block for block in config.get("required_blocks", ()) if not data.get(block)
        ]
        if missing:
            raise ValueError(
                "Faltan bloques obligatorios para "
                f"{config['root_tag']}: {', '.join(missing)}."
            )

    def _normalize_tag(self, tag: str, config: dict) -> str:
        return config.get("tag_aliases", {}).get(tag, tag)

    def _infer_item_tag(self, tag: str) -> str:
        return tag[:-1] if tag.endswith("s") else tag
