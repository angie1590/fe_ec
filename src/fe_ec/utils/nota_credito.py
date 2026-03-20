from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re
from typing import Sequence

from fe_ec.utils.emisor import EmisorProfile


DATE_FORMAT = "%d/%m/%Y"
NUM_DOC_MODIFICADO_RE = re.compile(r"^\d{3}-\d{3}-\d{1,9}$")


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


def _si_no(value, field_name: str) -> str | None:
    text = _texto_opcional(value)
    if text is None:
        return None

    normalized = text.upper()
    if normalized not in {"SI", "NO"}:
        raise ValueError(f"{field_name} debe ser 'SI' o 'NO'.")
    return normalized


def _validar_fecha(value: str, field_name: str) -> str:
    text = _requerido(value, field_name)
    try:
        datetime.strptime(text, DATE_FORMAT)
    except ValueError as exc:
        raise ValueError(f"{field_name} debe tener formato DD/MM/AAAA.") from exc
    return text


@dataclass(frozen=True)
class EmisorNotaCredito(EmisorProfile):
    agente_retencion: str | None = None
    contribuyente_rimpe: str | None = None
    contribuyente_especial: str | None = None
    rise: str | None = None

    def build_info_tributaria(
        self,
        *,
        ambiente: str,
        tipo_emision: str,
        clave_acceso: str,
        secuencial: str,
    ) -> dict:
        return super().build_info_tributaria(
            cod_doc="04",
            ambiente=ambiente,
            tipo_emision=tipo_emision,
            clave_acceso=clave_acceso,
            secuencial=secuencial,
            extra_fields={
                "agenteRetencion": self.agente_retencion,
                "contribuyenteRimpe": self.contribuyente_rimpe,
            },
        )


@dataclass(frozen=True)
class CompradorNotaCredito:
    tipo_identificacion: str
    razon_social: str
    identificacion: str

    def to_dict(self) -> dict:
        return {
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


@dataclass(frozen=True)
class ComprobanteModificado:
    cod_doc_modificado: str
    num_doc_modificado: str
    fecha_emision_doc_sustento: str

    def to_dict(self) -> dict:
        num_doc_modificado = _requerido(
            self.num_doc_modificado,
            "comprobante_modificado.num_doc_modificado",
        )
        if not NUM_DOC_MODIFICADO_RE.fullmatch(num_doc_modificado):
            raise ValueError(
                "comprobante_modificado.num_doc_modificado debe tener formato "
                "###-###-#########."
            )

        return {
            "codDocModificado": _requerido(
                self.cod_doc_modificado,
                "comprobante_modificado.cod_doc_modificado",
            ),
            "numDocModificado": num_doc_modificado,
            "fechaEmisionDocSustento": _validar_fecha(
                self.fecha_emision_doc_sustento,
                "comprobante_modificado.fecha_emision_doc_sustento",
            ),
        }


@dataclass(frozen=True)
class TotalImpuestoNotaCredito:
    codigo: str
    codigo_porcentaje: str
    base_imponible: str
    valor: str
    valor_devolucion_iva: str | None = None

    def to_dict(self) -> dict:
        data = {
            "codigo": _requerido(self.codigo, "total_impuesto.codigo"),
            "codigoPorcentaje": _requerido(
                self.codigo_porcentaje,
                "total_impuesto.codigo_porcentaje",
            ),
            "baseImponible": _requerido(
                self.base_imponible,
                "total_impuesto.base_imponible",
            ),
            "valor": _requerido(self.valor, "total_impuesto.valor"),
        }

        valor_devolucion_iva = _texto_opcional(self.valor_devolucion_iva)
        if valor_devolucion_iva is not None:
            data["valorDevolucionIva"] = valor_devolucion_iva
        return data


@dataclass(frozen=True)
class CompensacionNotaCredito:
    codigo: str
    tarifa: str
    valor: str

    def to_dict(self) -> dict:
        return {
            "codigo": _requerido(self.codigo, "compensacion.codigo"),
            "tarifa": _requerido(self.tarifa, "compensacion.tarifa"),
            "valor": _requerido(self.valor, "compensacion.valor"),
        }


@dataclass(frozen=True)
class DetalleAdicionalNotaCredito:
    nombre: str
    valor: str

    def to_dict(self) -> dict:
        return {
            "nombre": _requerido(self.nombre, "detalle_adicional.nombre"),
            "valor": _requerido(self.valor, "detalle_adicional.valor"),
        }


@dataclass(frozen=True)
class ImpuestoDetalleNotaCredito:
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
class DetalleNotaCredito:
    descripcion: str
    cantidad: str
    precio_unitario: str
    precio_total_sin_impuesto: str
    codigo_interno: str | None = None
    codigo_adicional: str | None = None
    descuento: str | None = None
    detalles_adicionales: Sequence[DetalleAdicionalNotaCredito] = ()
    impuestos: Sequence[ImpuestoDetalleNotaCredito] = ()

    def to_dict(self) -> dict:
        data = {}

        codigo_interno = _texto_opcional(self.codigo_interno)
        if codigo_interno is not None:
            data["codigoInterno"] = codigo_interno

        codigo_adicional = _texto_opcional(self.codigo_adicional)
        if codigo_adicional is not None:
            data["codigoAdicional"] = codigo_adicional

        data["descripcion"] = _requerido(self.descripcion, "detalle.descripcion")
        data["cantidad"] = _requerido(self.cantidad, "detalle.cantidad")
        data["precioUnitario"] = _requerido(
            self.precio_unitario,
            "detalle.precio_unitario",
        )

        descuento = _texto_opcional(self.descuento)
        if descuento is not None:
            data["descuento"] = descuento

        data["precioTotalSinImpuesto"] = _requerido(
            self.precio_total_sin_impuesto,
            "detalle.precio_total_sin_impuesto",
        )

        if self.detalles_adicionales:
            data["detallesAdicionales"] = [
                detalle.to_dict() for detalle in self.detalles_adicionales
            ]

        data["impuestos"] = [impuesto.to_dict() for impuesto in self.impuestos]
        return data


@dataclass(frozen=True)
class NotaCreditoRequest:
    secuencial: str
    fecha_emision: str
    tipo_emision: str
    emisor: EmisorNotaCredito
    comprador: CompradorNotaCredito
    comprobante_modificado: ComprobanteModificado
    total_sin_impuestos: str
    valor_modificacion: str
    total_con_impuestos: Sequence[TotalImpuestoNotaCredito]
    detalles: Sequence[DetalleNotaCredito]
    motivo: str
    compensaciones: Sequence[CompensacionNotaCredito] = ()
    info_adicional: Sequence[dict[str, str]] = ()
    output_xml: str = ".artifacts/xml/nota_credito_firmada.xml"
    moneda: str = "DOLAR"

    def to_payload(self, *, clave_acceso: str, ambiente: str) -> dict:
        return construir_payload_nota_credito(
            clave_acceso=clave_acceso,
            ambiente=ambiente,
            tipo_emision=self.tipo_emision,
            secuencial=self.secuencial,
            fecha_emision=self.fecha_emision,
            emisor=self.emisor,
            comprador=self.comprador,
            comprobante_modificado=self.comprobante_modificado,
            total_sin_impuestos=self.total_sin_impuestos,
            valor_modificacion=self.valor_modificacion,
            total_con_impuestos=self.total_con_impuestos,
            detalles=self.detalles,
            motivo=self.motivo,
            compensaciones=self.compensaciones,
            info_adicional=self.info_adicional,
            moneda=self.moneda,
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


def construir_payload_nota_credito(
    *,
    clave_acceso: str,
    ambiente: str,
    tipo_emision: str,
    secuencial: str,
    fecha_emision: str,
    emisor: EmisorNotaCredito,
    comprador: CompradorNotaCredito,
    comprobante_modificado: ComprobanteModificado,
    total_sin_impuestos: str,
    valor_modificacion: str,
    total_con_impuestos: Sequence[TotalImpuestoNotaCredito],
    detalles: Sequence[DetalleNotaCredito],
    motivo: str,
    compensaciones: Sequence[CompensacionNotaCredito] = (),
    info_adicional: Sequence[dict] | Sequence[tuple[str, str]] | None = None,
    moneda: str = "DOLAR",
) -> dict:
    fecha_emision = _validar_fecha(fecha_emision, "fecha_emision")

    if not total_con_impuestos:
        raise ValueError("total_con_impuestos debe contener al menos un impuesto.")
    if not detalles:
        raise ValueError("detalles debe contener al menos un detalle.")

    info_nota_credito = {
        "fechaEmision": fecha_emision,
    }

    dir_establecimiento = emisor.resolve_dir_establecimiento()
    if dir_establecimiento is not None:
        info_nota_credito["dirEstablecimiento"] = dir_establecimiento

    info_nota_credito.update(comprador.to_dict())

    contribuyente_especial = _texto_opcional(emisor.contribuyente_especial)
    if contribuyente_especial is not None:
        info_nota_credito["contribuyenteEspecial"] = contribuyente_especial

    obligado_contabilidad = emisor.resolve_obligado_contabilidad()
    if obligado_contabilidad is not None:
        info_nota_credito["obligadoContabilidad"] = obligado_contabilidad

    rise = _texto_opcional(emisor.rise)
    if rise is not None:
        info_nota_credito["rise"] = rise

    info_nota_credito.update(comprobante_modificado.to_dict())
    info_nota_credito["totalSinImpuestos"] = _requerido(
        total_sin_impuestos,
        "nota_credito.total_sin_impuestos",
    )

    if compensaciones:
        info_nota_credito["compensaciones"] = {
            "compensacion": [
                compensacion.to_dict() for compensacion in compensaciones
            ]
        }

    info_nota_credito["valorModificacion"] = _requerido(
        valor_modificacion,
        "nota_credito.valor_modificacion",
    )

    moneda = _texto_opcional(moneda)
    if moneda is not None:
        info_nota_credito["moneda"] = moneda

    info_nota_credito["totalConImpuestos"] = {
        "totalImpuesto": [
            impuesto.to_dict() for impuesto in total_con_impuestos
        ]
    }
    info_nota_credito["motivo"] = _requerido(motivo, "nota_credito.motivo")

    payload = {
        "infoTributaria": emisor.build_info_tributaria(
            ambiente=ambiente,
            tipo_emision=tipo_emision,
            clave_acceso=clave_acceso,
            secuencial=secuencial,
        ),
        "infoNotaCredito": info_nota_credito,
        "detalles": [detalle.to_dict() for detalle in detalles],
    }

    if info_adicional:
        payload["infoAdicional"] = _build_info_adicional(info_adicional)

    return payload


__all__ = [
    "ComprobanteModificado",
    "CompensacionNotaCredito",
    "CompradorNotaCredito",
    "DetalleAdicionalNotaCredito",
    "DetalleNotaCredito",
    "EmisorNotaCredito",
    "ImpuestoDetalleNotaCredito",
    "NotaCreditoRequest",
    "TotalImpuestoNotaCredito",
    "construir_payload_nota_credito",
]
