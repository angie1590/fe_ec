from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

from fe_ec.utils.nota_credito import (
    ComprobanteModificado,
    CompensacionNotaCredito,
    CompradorNotaCredito,
    DetalleAdicionalNotaCredito,
    DetalleNotaCredito,
    EmisorNotaCredito,
    ImpuestoDetalleNotaCredito,
    NotaCreditoRequest,
    TotalImpuestoNotaCredito,
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


def _build_emisor(data: Mapping[str, Any]) -> EmisorNotaCredito:
    return EmisorNotaCredito(
        ruc=_required_text(data.get("ruc"), "nota_credito.emisor.ruc"),
        razon_social=_required_text(
            data.get("razon_social"),
            "nota_credito.emisor.razon_social",
        ),
        estab=_required_text(data.get("estab"), "nota_credito.emisor.estab"),
        pto_emi=_required_text(data.get("pto_emi"), "nota_credito.emisor.pto_emi"),
        dir_matriz=_required_text(
            data.get("dir_matriz"),
            "nota_credito.emisor.dir_matriz",
        ),
        nombre_comercial=_optional_text(data.get("nombre_comercial")),
        dir_establecimiento=_optional_text(data.get("dir_establecimiento")),
        obligado_contabilidad=_optional_text(data.get("obligado_contabilidad")),
        agente_retencion=_optional_text(data.get("agente_retencion")),
        contribuyente_rimpe=_optional_text(data.get("contribuyente_rimpe")),
        contribuyente_especial=_optional_text(data.get("contribuyente_especial")),
        rise=_optional_text(data.get("rise")),
    )


def _build_comprador(data: Mapping[str, Any]) -> CompradorNotaCredito:
    return CompradorNotaCredito(
        tipo_identificacion=_required_text(
            data.get("tipo_identificacion"),
            "nota_credito.comprador.tipo_identificacion",
        ),
        razon_social=_required_text(
            data.get("razon_social"),
            "nota_credito.comprador.razon_social",
        ),
        identificacion=_required_text(
            data.get("identificacion"),
            "nota_credito.comprador.identificacion",
        ),
    )


def _build_comprobante_modificado(data: Mapping[str, Any]) -> ComprobanteModificado:
    return ComprobanteModificado(
        cod_doc_modificado=_required_text(
            data.get("cod_doc_modificado"),
            "nota_credito.comprobante_modificado.cod_doc_modificado",
        ),
        num_doc_modificado=_required_text(
            data.get("num_doc_modificado"),
            "nota_credito.comprobante_modificado.num_doc_modificado",
        ),
        fecha_emision_doc_sustento=_required_text(
            data.get("fecha_emision_doc_sustento"),
            "nota_credito.comprobante_modificado.fecha_emision_doc_sustento",
        ),
    )


def _build_total_impuesto(
    data: Mapping[str, Any],
    index: int,
) -> TotalImpuestoNotaCredito:
    prefix = f"nota_credito.total_con_impuestos[{index}]"
    return TotalImpuestoNotaCredito(
        codigo=_required_text(data.get("codigo"), f"{prefix}.codigo"),
        codigo_porcentaje=_required_text(
            data.get("codigo_porcentaje"),
            f"{prefix}.codigo_porcentaje",
        ),
        base_imponible=_required_text(
            data.get("base_imponible"),
            f"{prefix}.base_imponible",
        ),
        valor=_required_text(data.get("valor"), f"{prefix}.valor"),
        valor_devolucion_iva=_optional_text(data.get("valor_devolucion_iva")),
    )


def _build_compensacion(
    data: Mapping[str, Any],
    index: int,
) -> CompensacionNotaCredito:
    prefix = f"nota_credito.compensaciones[{index}]"
    return CompensacionNotaCredito(
        codigo=_required_text(data.get("codigo"), f"{prefix}.codigo"),
        tarifa=_required_text(data.get("tarifa"), f"{prefix}.tarifa"),
        valor=_required_text(data.get("valor"), f"{prefix}.valor"),
    )


def _build_detalle_adicional(
    data: Mapping[str, Any],
    detalle_index: int,
    adicional_index: int,
) -> DetalleAdicionalNotaCredito:
    prefix = (
        f"nota_credito.detalles[{detalle_index}].detalles_adicionales[{adicional_index}]"
    )
    return DetalleAdicionalNotaCredito(
        nombre=_required_text(data.get("nombre"), f"{prefix}.nombre"),
        valor=_required_text(data.get("valor"), f"{prefix}.valor"),
    )


def _build_impuesto_detalle(
    data: Mapping[str, Any],
    detalle_index: int,
    impuesto_index: int,
) -> ImpuestoDetalleNotaCredito:
    prefix = f"nota_credito.detalles[{detalle_index}].impuestos[{impuesto_index}]"
    return ImpuestoDetalleNotaCredito(
        codigo=_required_text(data.get("codigo"), f"{prefix}.codigo"),
        codigo_porcentaje=_required_text(
            data.get("codigo_porcentaje"),
            f"{prefix}.codigo_porcentaje",
        ),
        tarifa=_required_text(data.get("tarifa"), f"{prefix}.tarifa"),
        base_imponible=_required_text(
            data.get("base_imponible"),
            f"{prefix}.base_imponible",
        ),
        valor=_required_text(data.get("valor"), f"{prefix}.valor"),
    )


def _build_detalle(data: Mapping[str, Any], index: int) -> DetalleNotaCredito:
    detalles_adicionales_data = _sequence(
        data.get("detalles_adicionales", []),
        f"nota_credito.detalles[{index}].detalles_adicionales",
    )
    impuestos_data = _sequence(
        data.get("impuestos", []),
        f"nota_credito.detalles[{index}].impuestos",
    )
    return DetalleNotaCredito(
        codigo_interno=_optional_text(data.get("codigo_interno")),
        codigo_adicional=_optional_text(data.get("codigo_adicional")),
        descripcion=_required_text(
            data.get("descripcion"),
            f"nota_credito.detalles[{index}].descripcion",
        ),
        cantidad=_required_text(
            data.get("cantidad"),
            f"nota_credito.detalles[{index}].cantidad",
        ),
        precio_unitario=_required_text(
            data.get("precio_unitario"),
            f"nota_credito.detalles[{index}].precio_unitario",
        ),
        descuento=_optional_text(data.get("descuento")),
        precio_total_sin_impuesto=_required_text(
            data.get("precio_total_sin_impuesto"),
            f"nota_credito.detalles[{index}].precio_total_sin_impuesto",
        ),
        detalles_adicionales=[
            _build_detalle_adicional(
                _mapping(
                    item,
                    f"nota_credito.detalles[{index}].detalles_adicionales[]",
                ),
                index,
                adicional_index,
            )
            for adicional_index, item in enumerate(detalles_adicionales_data, start=1)
        ],
        impuestos=[
            _build_impuesto_detalle(
                _mapping(
                    item,
                    f"nota_credito.detalles[{index}].impuestos[]",
                ),
                index,
                impuesto_index,
            )
            for impuesto_index, item in enumerate(impuestos_data, start=1)
        ],
    )


def nota_credito_request_from_dict(
    data: Mapping[str, Any],
    *,
    default_secuencial: str | None = None,
    default_fecha_emision: str | None = None,
    default_tipo_emision: str = "1",
    default_output_xml: str = ".artifacts/xml/nota_credito_firmada.xml",
) -> NotaCreditoRequest:
    payload = _mapping(data, "contrato")
    version = payload.get("version", 1)
    if str(version).strip() != "1":
        raise ValueError("El contrato YAML de nota_credito solo soporta version 1.")

    section = _mapping(payload.get("nota_credito", payload), "nota_credito")

    total_con_impuestos_data = _sequence(
        section.get("total_con_impuestos", []),
        "nota_credito.total_con_impuestos",
    )
    compensaciones_data = _sequence(
        section.get("compensaciones", []),
        "nota_credito.compensaciones",
    )
    detalles_data = _sequence(
        section.get("detalles", []),
        "nota_credito.detalles",
    )
    info_adicional_data = _sequence(
        section.get("info_adicional", []),
        "nota_credito.info_adicional",
    )

    request = NotaCreditoRequest(
        secuencial=_required_text(
            section.get("secuencial", default_secuencial),
            "nota_credito.secuencial",
        ),
        fecha_emision=_required_text(
            section.get("fecha_emision", default_fecha_emision),
            "nota_credito.fecha_emision",
        ),
        tipo_emision=_required_text(
            section.get("tipo_emision", default_tipo_emision),
            "nota_credito.tipo_emision",
        ),
        output_xml=_required_text(
            section.get("output_xml", default_output_xml),
            "nota_credito.output_xml",
        ),
        moneda=_required_text(
            section.get("moneda", "DOLAR"),
            "nota_credito.moneda",
        ),
        emisor=_build_emisor(
            _mapping(section.get("emisor", {}), "nota_credito.emisor"),
        ),
        comprador=_build_comprador(
            _mapping(section.get("comprador", {}), "nota_credito.comprador"),
        ),
        comprobante_modificado=_build_comprobante_modificado(
            _mapping(
                section.get("comprobante_modificado", {}),
                "nota_credito.comprobante_modificado",
            ),
        ),
        total_sin_impuestos=_required_text(
            section.get("total_sin_impuestos"),
            "nota_credito.total_sin_impuestos",
        ),
        valor_modificacion=_required_text(
            section.get("valor_modificacion"),
            "nota_credito.valor_modificacion",
        ),
        total_con_impuestos=[
            _build_total_impuesto(
                _mapping(item, "nota_credito.total_con_impuestos[]"),
                index,
            )
            for index, item in enumerate(total_con_impuestos_data, start=1)
        ],
        detalles=[
            _build_detalle(_mapping(item, "nota_credito.detalles[]"), index)
            for index, item in enumerate(detalles_data, start=1)
        ],
        motivo=_required_text(
            section.get("motivo"),
            "nota_credito.motivo",
        ),
        compensaciones=[
            _build_compensacion(
                _mapping(item, "nota_credito.compensaciones[]"),
                index,
            )
            for index, item in enumerate(compensaciones_data, start=1)
        ],
        info_adicional=[
            {
                "nombre": _required_text(
                    _mapping(item, "nota_credito.info_adicional[]").get("nombre"),
                    "nota_credito.info_adicional[].nombre",
                ),
                "valor": _required_text(
                    _mapping(item, "nota_credito.info_adicional[]").get("valor"),
                    "nota_credito.info_adicional[].valor",
                ),
            }
            for item in info_adicional_data
        ],
    )

    if not request.total_con_impuestos:
        raise ValueError(
            "nota_credito.total_con_impuestos debe contener al menos un item."
        )
    if not request.detalles:
        raise ValueError("nota_credito.detalles debe contener al menos un item.")
    return request


def _load_yaml_module():
    try:
        import yaml
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "PyYAML no esta instalado. Ejecuta 'poetry install' o 'poetry add PyYAML'."
        ) from exc
    return yaml


def load_nota_credito_request_from_yaml(
    path: str | Path,
    *,
    default_secuencial: str | None = None,
    default_fecha_emision: str | None = None,
    default_tipo_emision: str = "1",
    default_output_xml: str = ".artifacts/xml/nota_credito_firmada.xml",
) -> NotaCreditoRequest:
    contract_path = Path(path)
    yaml = _load_yaml_module()
    data = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    if data is None:
        raise ValueError(f"El contrato YAML {contract_path} esta vacio.")

    return nota_credito_request_from_dict(
        data,
        default_secuencial=default_secuencial,
        default_fecha_emision=default_fecha_emision,
        default_tipo_emision=default_tipo_emision,
        default_output_xml=default_output_xml,
    )


__all__ = [
    "NotaCreditoRequest",
    "load_nota_credito_request_from_yaml",
    "nota_credito_request_from_dict",
]
