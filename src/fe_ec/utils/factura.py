from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Sequence

from fe_ec.utils.emisor import EmisorProfile


DATE_FORMAT = "%d/%m/%Y"


def _texto(value) -> str:
    return str(value).strip() if value is not None else ""


def _texto_opcional(value) -> str | None:
    text = _texto(value)
    return text or None


def _requerido(value, field_name: str) -> str:
    text = _texto(value)
    if not text:
        raise ValueError(f"{field_name} es obligatorio.")
    return text


def _validar_fecha(value: str, field_name: str) -> str:
    text = _requerido(value, field_name)
    try:
        datetime.strptime(text, DATE_FORMAT)
    except ValueError as exc:
        raise ValueError(f"{field_name} debe tener formato DD/MM/AAAA.") from exc
    return text


@dataclass(frozen=True)
class CompradorFactura:
    tipo_identificacion: str
    razon_social: str
    identificacion: str
    direccion: str | None = None

    def to_dict(self) -> dict:
        data = {
            "tipoIdentificacionComprador": _requerido(
                self.tipo_identificacion,
                "comprador.tipo_identificacion",
            ),
            "razonSocialComprador": _requerido(
                self.razon_social,
                "comprador.razon_social",
            ),
            "identificacionComprador": _requerido(
                self.identificacion,
                "comprador.identificacion",
            ),
        }

        direccion = _texto_opcional(self.direccion)
        if direccion is not None:
            data["direccionComprador"] = direccion
        return data


@dataclass(frozen=True)
class TotalImpuestoFactura:
    codigo: str
    codigo_porcentaje: str
    base_imponible: str
    valor: str
    descuento_adicional: str | None = None
    valor_devolucion_iva: str | None = None

    def to_dict(self) -> dict:
        data = {
            "codigo": _requerido(self.codigo, "total_impuesto.codigo"),
            "codigoPorcentaje": _requerido(
                self.codigo_porcentaje,
                "total_impuesto.codigo_porcentaje",
            ),
        }

        descuento_adicional = _texto_opcional(self.descuento_adicional)
        if descuento_adicional is not None:
            data["descuentoAdicional"] = descuento_adicional

        data["baseImponible"] = _requerido(
            self.base_imponible,
            "total_impuesto.base_imponible",
        )
        data["valor"] = _requerido(self.valor, "total_impuesto.valor")

        valor_devolucion_iva = _texto_opcional(self.valor_devolucion_iva)
        if valor_devolucion_iva is not None:
            data["valorDevolucionIva"] = valor_devolucion_iva

        return data


@dataclass(frozen=True)
class ImpuestoDetalleFactura:
    codigo: str
    codigo_porcentaje: str
    tarifa: str
    base_imponible: str
    valor: str

    def to_dict(self) -> dict:
        return {
            "codigo": _requerido(self.codigo, "detalle.impuesto.codigo"),
            "codigoPorcentaje": _requerido(
                self.codigo_porcentaje,
                "detalle.impuesto.codigo_porcentaje",
            ),
            "tarifa": _requerido(self.tarifa, "detalle.impuesto.tarifa"),
            "baseImponible": _requerido(
                self.base_imponible,
                "detalle.impuesto.base_imponible",
            ),
            "valor": _requerido(self.valor, "detalle.impuesto.valor"),
        }


@dataclass(frozen=True)
class PagoFactura:
    forma_pago: str
    total: str
    plazo: str | None = None
    unidad_tiempo: str | None = None

    def to_dict(self) -> dict:
        data = {
            "formaPago": _requerido(self.forma_pago, "pago.forma_pago"),
            "total": _requerido(self.total, "pago.total"),
        }

        plazo = _texto_opcional(self.plazo)
        if plazo is not None:
            data["plazo"] = plazo

        unidad_tiempo = _texto_opcional(self.unidad_tiempo)
        if unidad_tiempo is not None:
            data["unidadTiempo"] = unidad_tiempo

        return data


@dataclass(frozen=True)
class DetalleFactura:
    codigo_principal: str
    descripcion: str
    cantidad: str
    precio_unitario: str
    descuento: str
    precio_total_sin_impuesto: str
    impuestos: Sequence[ImpuestoDetalleFactura]
    codigo_auxiliar: str | None = None
    unidad_medida: str | None = None

    def to_dict(self) -> dict:
        if not self.impuestos:
            raise ValueError("detalle.impuestos debe contener al menos un impuesto.")

        data = {
            "codigoPrincipal": _requerido(
                self.codigo_principal,
                "detalle.codigo_principal",
            ),
        }

        codigo_auxiliar = _texto_opcional(self.codigo_auxiliar)
        if codigo_auxiliar is not None:
            data["codigoAuxiliar"] = codigo_auxiliar

        data["descripcion"] = _requerido(self.descripcion, "detalle.descripcion")

        unidad_medida = _texto_opcional(self.unidad_medida)
        if unidad_medida is not None:
            data["unidadMedida"] = unidad_medida

        data.update(
            {
                "cantidad": _requerido(self.cantidad, "detalle.cantidad"),
                "precioUnitario": _requerido(
                    self.precio_unitario,
                    "detalle.precio_unitario",
                ),
                "descuento": _requerido(self.descuento, "detalle.descuento"),
                "precioTotalSinImpuesto": _requerido(
                    self.precio_total_sin_impuesto,
                    "detalle.precio_total_sin_impuesto",
                ),
                "impuestos": [impuesto.to_dict() for impuesto in self.impuestos],
            }
        )
        return data


@dataclass(frozen=True)
class FacturaRequest:
    secuencial: str
    fecha_emision: str
    tipo_emision: str
    emisor: EmisorProfile
    comprador: CompradorFactura
    total_sin_impuestos: str
    total_descuento: str
    total_con_impuestos: Sequence[TotalImpuestoFactura]
    propina: str
    importe_total: str
    detalles: Sequence[DetalleFactura]
    pagos: Sequence[PagoFactura]
    info_adicional: Sequence[dict[str, str]] = ()
    output_xml: str = "fact_firmado.xml"
    moneda: str = "DOLAR"
    guia_remision: str | None = None

    def to_payload(self, *, clave_acceso: str, ambiente: str) -> dict:
        return construir_payload_factura(
            clave_acceso=clave_acceso,
            ambiente=ambiente,
            tipo_emision=self.tipo_emision,
            secuencial=self.secuencial,
            fecha_emision=self.fecha_emision,
            emisor=self.emisor,
            comprador=self.comprador,
            total_sin_impuestos=self.total_sin_impuestos,
            total_descuento=self.total_descuento,
            total_con_impuestos=self.total_con_impuestos,
            propina=self.propina,
            importe_total=self.importe_total,
            moneda=self.moneda,
            pagos=self.pagos,
            detalles=self.detalles,
            info_adicional=self.info_adicional,
            guia_remision=self.guia_remision,
        )


def _build_info_adicional(info_adicional: Sequence[dict] | Sequence[tuple[str, str]]) -> dict:
    campos = []
    for campo in info_adicional:
        if isinstance(campo, tuple):
            nombre, valor = campo
        else:
            nombre = campo["nombre"]
            valor = campo["valor"]

        campos.append(
            {
                "nombre": _requerido(nombre, "info_adicional.nombre"),
                "valor": _requerido(valor, "info_adicional.valor"),
            }
        )

    return {"campoAdicional": campos}


def construir_payload_factura(
    *,
    clave_acceso: str,
    ambiente: str,
    tipo_emision: str,
    secuencial: str,
    fecha_emision: str,
    emisor: EmisorProfile,
    comprador: CompradorFactura,
    total_sin_impuestos: str,
    total_descuento: str,
    total_con_impuestos: Sequence[TotalImpuestoFactura],
    propina: str,
    importe_total: str,
    moneda: str,
    pagos: Sequence[PagoFactura],
    detalles: Sequence[DetalleFactura],
    info_adicional: Sequence[dict] | Sequence[tuple[str, str]] | None = None,
    guia_remision: str | None = None,
) -> dict:
    fecha_emision = _validar_fecha(fecha_emision, "fecha_emision")

    if not total_con_impuestos:
        raise ValueError("total_con_impuestos debe contener al menos un impuesto.")
    if not pagos:
        raise ValueError("pagos debe contener al menos un pago.")
    if not detalles:
        raise ValueError("detalles debe contener al menos un detalle.")

    info_factura = {
        "fechaEmision": fecha_emision,
    }
    info_factura.update(emisor.build_common_issue_data())
    info_factura.update(comprador.to_dict())

    guia_remision = _texto_opcional(guia_remision)
    if guia_remision is not None:
        info_factura["guiaRemision"] = guia_remision

    info_factura.update(
        {
            "totalSinImpuestos": _requerido(
                total_sin_impuestos,
                "factura.total_sin_impuestos",
            ),
            "totalDescuento": _requerido(
                total_descuento,
                "factura.total_descuento",
            ),
            "totalConImpuestos": {
                "totalImpuesto": [
                    impuesto.to_dict() for impuesto in total_con_impuestos
                ]
            },
            "propina": _requerido(propina, "factura.propina"),
            "importeTotal": _requerido(importe_total, "factura.importe_total"),
            "moneda": _requerido(moneda, "factura.moneda"),
            "pagos": [pago.to_dict() for pago in pagos],
        }
    )

    payload = {
        "infoTributaria": emisor.build_info_tributaria(
            cod_doc="01",
            ambiente=ambiente,
            tipo_emision=tipo_emision,
            clave_acceso=clave_acceso,
            secuencial=secuencial,
        ),
        "infoFactura": info_factura,
        "detalles": [detalle.to_dict() for detalle in detalles],
    }

    if info_adicional:
        payload["infoAdicional"] = _build_info_adicional(info_adicional)

    return payload


__all__ = [
    "CompradorFactura",
    "DetalleFactura",
    "FacturaRequest",
    "ImpuestoDetalleFactura",
    "PagoFactura",
    "TotalImpuestoFactura",
    "construir_payload_factura",
]
