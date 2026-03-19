from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

from fe_ec.utils.emisor import EmisorProfile
from fe_ec.utils.factura import (
    CompradorFactura,
    DetalleFactura,
    FacturaRequest,
    ImpuestoDetalleFactura,
    PagoFactura,
    TotalImpuestoFactura,
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


def _build_emisor(data: Mapping[str, Any]) -> EmisorProfile:
    return EmisorProfile(
        ruc=_required_text(data.get("ruc"), "factura.emisor.ruc"),
        razon_social=_required_text(
            data.get("razon_social"),
            "factura.emisor.razon_social",
        ),
        estab=_required_text(data.get("estab"), "factura.emisor.estab"),
        pto_emi=_required_text(data.get("pto_emi"), "factura.emisor.pto_emi"),
        dir_matriz=_required_text(
            data.get("dir_matriz"),
            "factura.emisor.dir_matriz",
        ),
        nombre_comercial=_optional_text(data.get("nombre_comercial")),
        dir_establecimiento=_optional_text(data.get("dir_establecimiento")),
        obligado_contabilidad=_optional_text(data.get("obligado_contabilidad")),
    )


def _build_comprador(data: Mapping[str, Any]) -> CompradorFactura:
    return CompradorFactura(
        tipo_identificacion=_required_text(
            data.get("tipo_identificacion"),
            "factura.comprador.tipo_identificacion",
        ),
        razon_social=_required_text(
            data.get("razon_social"),
            "factura.comprador.razon_social",
        ),
        identificacion=_required_text(
            data.get("identificacion"),
            "factura.comprador.identificacion",
        ),
        direccion=_optional_text(data.get("direccion")),
    )


def _build_total_impuesto(data: Mapping[str, Any], index: int) -> TotalImpuestoFactura:
    prefix = f"factura.total_con_impuestos[{index}]"
    return TotalImpuestoFactura(
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
        descuento_adicional=_optional_text(data.get("descuento_adicional")),
        valor_devolucion_iva=_optional_text(data.get("valor_devolucion_iva")),
    )


def _build_impuesto_detalle(
    data: Mapping[str, Any],
    detalle_index: int,
    impuesto_index: int,
) -> ImpuestoDetalleFactura:
    prefix = (
        f"factura.detalles[{detalle_index}].impuestos[{impuesto_index}]"
    )
    return ImpuestoDetalleFactura(
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


def _build_detalle(data: Mapping[str, Any], index: int) -> DetalleFactura:
    impuestos_data = _sequence(
        data.get("impuestos", []),
        f"factura.detalles[{index}].impuestos",
    )
    return DetalleFactura(
        codigo_principal=_required_text(
            data.get("codigo_principal"),
            f"factura.detalles[{index}].codigo_principal",
        ),
        codigo_auxiliar=_optional_text(data.get("codigo_auxiliar")),
        descripcion=_required_text(
            data.get("descripcion"),
            f"factura.detalles[{index}].descripcion",
        ),
        unidad_medida=_optional_text(data.get("unidad_medida")),
        cantidad=_required_text(
            data.get("cantidad"),
            f"factura.detalles[{index}].cantidad",
        ),
        precio_unitario=_required_text(
            data.get("precio_unitario"),
            f"factura.detalles[{index}].precio_unitario",
        ),
        descuento=_required_text(
            data.get("descuento"),
            f"factura.detalles[{index}].descuento",
        ),
        precio_total_sin_impuesto=_required_text(
            data.get("precio_total_sin_impuesto"),
            f"factura.detalles[{index}].precio_total_sin_impuesto",
        ),
        impuestos=[
            _build_impuesto_detalle(
                _mapping(
                    item,
                    f"factura.detalles[{index}].impuestos[]",
                ),
                index,
                impuesto_index,
            )
            for impuesto_index, item in enumerate(impuestos_data, start=1)
        ],
    )


def _build_pago(data: Mapping[str, Any], index: int) -> PagoFactura:
    prefix = f"factura.pagos[{index}]"
    return PagoFactura(
        forma_pago=_required_text(data.get("forma_pago"), f"{prefix}.forma_pago"),
        total=_required_text(data.get("total"), f"{prefix}.total"),
        plazo=_optional_text(data.get("plazo")),
        unidad_tiempo=_optional_text(data.get("unidad_tiempo")),
    )


def factura_request_from_dict(
    data: Mapping[str, Any],
    *,
    default_secuencial: str | None = None,
    default_fecha_emision: str | None = None,
    default_tipo_emision: str = "1",
    default_output_xml: str = "fact_firmado.xml",
) -> FacturaRequest:
    payload = _mapping(data, "contrato")
    version = payload.get("version", 1)
    if str(version).strip() != "1":
        raise ValueError("El contrato YAML de factura solo soporta version 1.")

    section = _mapping(payload.get("factura", payload), "factura")

    total_con_impuestos_data = _sequence(
        section.get("total_con_impuestos", []),
        "factura.total_con_impuestos",
    )
    detalles_data = _sequence(section.get("detalles", []), "factura.detalles")
    pagos_data = _sequence(section.get("pagos", []), "factura.pagos")
    info_adicional_data = _sequence(
        section.get("info_adicional", []),
        "factura.info_adicional",
    )

    request = FacturaRequest(
        secuencial=_required_text(
            section.get("secuencial", default_secuencial),
            "factura.secuencial",
        ),
        fecha_emision=_required_text(
            section.get("fecha_emision", default_fecha_emision),
            "factura.fecha_emision",
        ),
        tipo_emision=_required_text(
            section.get("tipo_emision", default_tipo_emision),
            "factura.tipo_emision",
        ),
        output_xml=_required_text(
            section.get("output_xml", default_output_xml),
            "factura.output_xml",
        ),
        moneda=_required_text(
            section.get("moneda", "DOLAR"),
            "factura.moneda",
        ),
        guia_remision=_optional_text(section.get("guia_remision")),
        emisor=_build_emisor(_mapping(section.get("emisor", {}), "factura.emisor")),
        comprador=_build_comprador(
            _mapping(section.get("comprador", {}), "factura.comprador"),
        ),
        total_sin_impuestos=_required_text(
            section.get("total_sin_impuestos"),
            "factura.total_sin_impuestos",
        ),
        total_descuento=_required_text(
            section.get("total_descuento"),
            "factura.total_descuento",
        ),
        total_con_impuestos=[
            _build_total_impuesto(
                _mapping(item, "factura.total_con_impuestos[]"),
                index,
            )
            for index, item in enumerate(total_con_impuestos_data, start=1)
        ],
        propina=_required_text(section.get("propina"), "factura.propina"),
        importe_total=_required_text(
            section.get("importe_total"),
            "factura.importe_total",
        ),
        detalles=[
            _build_detalle(_mapping(item, "factura.detalles[]"), index)
            for index, item in enumerate(detalles_data, start=1)
        ],
        pagos=[
            _build_pago(_mapping(item, "factura.pagos[]"), index)
            for index, item in enumerate(pagos_data, start=1)
        ],
        info_adicional=[
            {
                "nombre": _required_text(
                    _mapping(item, "factura.info_adicional[]").get("nombre"),
                    "factura.info_adicional[].nombre",
                ),
                "valor": _required_text(
                    _mapping(item, "factura.info_adicional[]").get("valor"),
                    "factura.info_adicional[].valor",
                ),
            }
            for item in info_adicional_data
        ],
    )

    if not request.total_con_impuestos:
        raise ValueError("factura.total_con_impuestos debe contener al menos un item.")
    if not request.detalles:
        raise ValueError("factura.detalles debe contener al menos un item.")
    if not request.pagos:
        raise ValueError("factura.pagos debe contener al menos un item.")
    return request


def _load_yaml_module():
    try:
        import yaml
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "PyYAML no esta instalado. Ejecuta 'poetry install' o 'poetry add PyYAML'."
        ) from exc
    return yaml


def load_factura_request_from_yaml(
    path: str | Path,
    *,
    default_secuencial: str | None = None,
    default_fecha_emision: str | None = None,
    default_tipo_emision: str = "1",
    default_output_xml: str = "fact_firmado.xml",
) -> FacturaRequest:
    contract_path = Path(path)
    yaml = _load_yaml_module()
    data = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    if data is None:
        raise ValueError(f"El contrato YAML {contract_path} esta vacio.")

    return factura_request_from_dict(
        data,
        default_secuencial=default_secuencial,
        default_fecha_emision=default_fecha_emision,
        default_tipo_emision=default_tipo_emision,
        default_output_xml=default_output_xml,
    )


__all__ = [
    "FacturaRequest",
    "factura_request_from_dict",
    "load_factura_request_from_yaml",
]
