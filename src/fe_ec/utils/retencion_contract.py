from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from fe_ec.utils.retencion import (
    DocumentoSustentoRetencion,
    EmisorRetencion,
    ImpuestoDocSustento,
    PagoRetencion,
    RetencionLinea,
    SujetoRetenido,
    construir_payload_retencion,
)


def _mapping(value: Any, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} debe ser un objeto.")
    return value


def _sequence(value: Any, field_name: str) -> Sequence[Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError(f"{field_name} debe ser una lista.")
    return value


def _required_text(value: Any, field_name: str) -> str:
    text = str(value).strip() if value is not None else ""
    if not text:
        raise ValueError(f"{field_name} es obligatorio.")
    return text


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


@dataclass(frozen=True)
class RetencionRequest:
    secuencial: str
    fecha_emision: str
    tipo_emision: str
    emisor: EmisorRetencion
    sujeto_retenido: SujetoRetenido
    documentos_sustento: Sequence[DocumentoSustentoRetencion]
    info_adicional: Sequence[dict[str, str]] = ()
    output_xml: str = "retencion_firmada.xml"

    def to_payload(self, *, clave_acceso: str, ambiente: str) -> dict:
        return construir_payload_retencion(
            clave_acceso=clave_acceso,
            ambiente=ambiente,
            tipo_emision=self.tipo_emision,
            secuencial=self.secuencial,
            fecha_emision=self.fecha_emision,
            emisor=self.emisor,
            sujeto_retenido=self.sujeto_retenido,
            documentos_sustento=self.documentos_sustento,
            info_adicional=self.info_adicional,
        )


def _build_emisor(data: Mapping[str, Any]) -> EmisorRetencion:
    return EmisorRetencion(
        ruc=_required_text(data.get("ruc"), "retencion.emisor.ruc"),
        razon_social=_required_text(
            data.get("razon_social"),
            "retencion.emisor.razon_social",
        ),
        estab=_required_text(data.get("estab"), "retencion.emisor.estab"),
        pto_emi=_required_text(data.get("pto_emi"), "retencion.emisor.pto_emi"),
        dir_matriz=_required_text(
            data.get("dir_matriz"),
            "retencion.emisor.dir_matriz",
        ),
        nombre_comercial=_optional_text(data.get("nombre_comercial")),
        dir_establecimiento=_optional_text(data.get("dir_establecimiento")),
        obligado_contabilidad=_optional_text(data.get("obligado_contabilidad")),
        agente_retencion=_optional_text(data.get("agente_retencion")),
        contribuyente_especial=_optional_text(data.get("contribuyente_especial")),
        contribuyente_rimpe=_optional_text(data.get("contribuyente_rimpe")),
    )


def _build_sujeto_retenido(data: Mapping[str, Any]) -> SujetoRetenido:
    return SujetoRetenido(
        tipo_identificacion=_required_text(
            data.get("tipo_identificacion"),
            "retencion.sujeto_retenido.tipo_identificacion",
        ),
        identificacion=_required_text(
            data.get("identificacion"),
            "retencion.sujeto_retenido.identificacion",
        ),
        razon_social=_required_text(
            data.get("razon_social"),
            "retencion.sujeto_retenido.razon_social",
        ),
        parte_rel=_required_text(
            data.get("parte_rel", "NO"),
            "retencion.sujeto_retenido.parte_rel",
        ),
        tipo_sujeto_retenido=_optional_text(data.get("tipo_sujeto_retenido")),
    )


def _build_impuesto_doc_sustento(data: Mapping[str, Any], index: int) -> ImpuestoDocSustento:
    prefix = f"retencion.documentos_sustento[{index}].impuestos_doc_sustento[]"
    return ImpuestoDocSustento(
        cod_impuesto_doc_sustento=_required_text(
            data.get("cod_impuesto_doc_sustento"),
            f"{prefix}.cod_impuesto_doc_sustento",
        ),
        codigo_porcentaje=_required_text(
            data.get("codigo_porcentaje"),
            f"{prefix}.codigo_porcentaje",
        ),
        base_imponible=_required_text(
            data.get("base_imponible"),
            f"{prefix}.base_imponible",
        ),
        tarifa=_required_text(data.get("tarifa"), f"{prefix}.tarifa"),
        valor_impuesto=_required_text(
            data.get("valor_impuesto"),
            f"{prefix}.valor_impuesto",
        ),
    )


def _build_retencion_linea(data: Mapping[str, Any], index: int) -> RetencionLinea:
    prefix = f"retencion.documentos_sustento[{index}].retenciones[]"
    return RetencionLinea(
        codigo=_required_text(data.get("codigo"), f"{prefix}.codigo"),
        codigo_retencion=_required_text(
            data.get("codigo_retencion"),
            f"{prefix}.codigo_retencion",
        ),
        base_imponible=_required_text(
            data.get("base_imponible"),
            f"{prefix}.base_imponible",
        ),
        porcentaje_retener=_required_text(
            data.get("porcentaje_retener"),
            f"{prefix}.porcentaje_retener",
        ),
        valor_retenido=_required_text(
            data.get("valor_retenido"),
            f"{prefix}.valor_retenido",
        ),
    )


def _build_pago(data: Mapping[str, Any], index: int) -> PagoRetencion:
    prefix = f"retencion.documentos_sustento[{index}].pagos[]"
    return PagoRetencion(
        forma_pago=_required_text(data.get("forma_pago"), f"{prefix}.forma_pago"),
        total=_required_text(data.get("total"), f"{prefix}.total"),
    )


def _build_documento_sustento(data: Mapping[str, Any], index: int) -> DocumentoSustentoRetencion:
    impuestos_data = _sequence(
        data.get("impuestos_doc_sustento", []),
        f"retencion.documentos_sustento[{index}].impuestos_doc_sustento",
    )
    retenciones_data = _sequence(
        data.get("retenciones", []),
        f"retencion.documentos_sustento[{index}].retenciones",
    )
    pagos_data = _sequence(
        data.get("pagos", []),
        f"retencion.documentos_sustento[{index}].pagos",
    )

    return DocumentoSustentoRetencion(
        cod_sustento=_required_text(
            data.get("cod_sustento"),
            f"retencion.documentos_sustento[{index}].cod_sustento",
        ),
        cod_doc_sustento=_required_text(
            data.get("cod_doc_sustento"),
            f"retencion.documentos_sustento[{index}].cod_doc_sustento",
        ),
        num_doc_sustento=_required_text(
            data.get("num_doc_sustento"),
            f"retencion.documentos_sustento[{index}].num_doc_sustento",
        ),
        fecha_emision_doc_sustento=_required_text(
            data.get("fecha_emision_doc_sustento"),
            f"retencion.documentos_sustento[{index}].fecha_emision_doc_sustento",
        ),
        num_aut_doc_sustento=_optional_text(data.get("num_aut_doc_sustento")),
        fecha_registro_contable=_optional_text(data.get("fecha_registro_contable")),
        pago_loc_ext=_required_text(
            data.get("pago_loc_ext"),
            f"retencion.documentos_sustento[{index}].pago_loc_ext",
        ),
        total_sin_impuestos=_required_text(
            data.get("total_sin_impuestos"),
            f"retencion.documentos_sustento[{index}].total_sin_impuestos",
        ),
        importe_total=_required_text(
            data.get("importe_total"),
            f"retencion.documentos_sustento[{index}].importe_total",
        ),
        impuestos_doc_sustento=[
            _build_impuesto_doc_sustento(
                _mapping(item, f"retencion.documentos_sustento[{index}].impuestos_doc_sustento[]"),
                index,
            )
            for item in impuestos_data
        ],
        retenciones=[
            _build_retencion_linea(
                _mapping(item, f"retencion.documentos_sustento[{index}].retenciones[]"),
                index,
            )
            for item in retenciones_data
        ],
        pagos=[
            _build_pago(
                _mapping(item, f"retencion.documentos_sustento[{index}].pagos[]"),
                index,
            )
            for item in pagos_data
        ],
        tipo_regi=_optional_text(data.get("tipo_regi")),
        pais_efec_pago=_optional_text(data.get("pais_efec_pago")),
        aplic_conv_dob_trib=_optional_text(data.get("aplic_conv_dob_trib")),
        pag_ext_suj_ret_nor_leg=_optional_text(data.get("pag_ext_suj_ret_nor_leg")),
        pago_reg_fis=_optional_text(data.get("pago_reg_fis")),
        total_comprobantes_reembolso=_optional_text(
            data.get("total_comprobantes_reembolso")
        ),
        total_base_imponible_reembolso=_optional_text(
            data.get("total_base_imponible_reembolso")
        ),
        total_impuesto_reembolso=_optional_text(data.get("total_impuesto_reembolso")),
    )


def retencion_request_from_dict(
    data: Mapping[str, Any],
    *,
    default_secuencial: str | None = None,
    default_fecha_emision: str | None = None,
    default_tipo_emision: str = "1",
    default_output_xml: str = "retencion_firmada.xml",
) -> RetencionRequest:
    payload = _mapping(data, "contrato")
    version = payload.get("version", 1)
    if str(version).strip() != "1":
        raise ValueError("El contrato YAML de retencion solo soporta version 1.")

    section = payload.get("retencion", payload)
    section = _mapping(section, "retencion")

    documentos_sustento_data = _sequence(
        section.get("documentos_sustento", []),
        "retencion.documentos_sustento",
    )
    info_adicional_data = _sequence(
        section.get("info_adicional", []),
        "retencion.info_adicional",
    )

    request = RetencionRequest(
        secuencial=_required_text(
            section.get("secuencial", default_secuencial),
            "retencion.secuencial",
        ),
        fecha_emision=_required_text(
            section.get("fecha_emision", default_fecha_emision),
            "retencion.fecha_emision",
        ),
        tipo_emision=_required_text(
            section.get("tipo_emision", default_tipo_emision),
            "retencion.tipo_emision",
        ),
        output_xml=_required_text(
            section.get("output_xml", default_output_xml),
            "retencion.output_xml",
        ),
        emisor=_build_emisor(
            _mapping(section.get("emisor", {}), "retencion.emisor"),
        ),
        sujeto_retenido=_build_sujeto_retenido(
            _mapping(section.get("sujeto_retenido", {}), "retencion.sujeto_retenido"),
        ),
        documentos_sustento=[
            _build_documento_sustento(
                _mapping(item, "retencion.documentos_sustento[]"),
                index,
            )
            for index, item in enumerate(documentos_sustento_data, start=1)
        ],
        info_adicional=[
            {
                "nombre": _required_text(
                    _mapping(item, "retencion.info_adicional[]").get("nombre"),
                    "retencion.info_adicional[].nombre",
                ),
                "valor": _required_text(
                    _mapping(item, "retencion.info_adicional[]").get("valor"),
                    "retencion.info_adicional[].valor",
                ),
            }
            for item in info_adicional_data
        ],
    )

    if not request.documentos_sustento:
        raise ValueError("retencion.documentos_sustento debe contener al menos un item.")
    return request


def _load_yaml_module():
    try:
        import yaml
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "PyYAML no esta instalado. Ejecuta 'poetry install' o 'poetry add PyYAML'."
        ) from exc
    return yaml


def load_retencion_request_from_yaml(
    path: str | Path,
    *,
    default_secuencial: str | None = None,
    default_fecha_emision: str | None = None,
    default_tipo_emision: str = "1",
    default_output_xml: str = "retencion_firmada.xml",
) -> RetencionRequest:
    contract_path = Path(path)
    yaml = _load_yaml_module()
    data = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    if data is None:
        raise ValueError(f"El contrato YAML {contract_path} esta vacio.")

    return retencion_request_from_dict(
        data,
        default_secuencial=default_secuencial,
        default_fecha_emision=default_fecha_emision,
        default_tipo_emision=default_tipo_emision,
        default_output_xml=default_output_xml,
    )


__all__ = [
    "RetencionRequest",
    "load_retencion_request_from_yaml",
    "retencion_request_from_dict",
]
