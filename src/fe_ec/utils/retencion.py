from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import re
from typing import Mapping, Sequence

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


def periodo_fiscal_desde_fecha(fecha_emision: str) -> str:
    fecha = datetime.strptime(_validar_fecha(fecha_emision, "fecha_emision"), DATE_FORMAT)
    return fecha.strftime("%m/%Y")


def extraer_metadata_clave_acceso(clave_acceso: str) -> dict | None:
    if not re.fullmatch(r"\d{49}", _texto(clave_acceso)):
        return None

    raw = _texto(clave_acceso)
    return {
        "fecha": raw[:8],
        "cod_doc": raw[8:10],
        "ruc": raw[10:23],
        "ambiente": raw[23],
        "serie": raw[24:30],
        "secuencial": raw[30:39],
    }


def fecha_desde_clave_acceso(clave_acceso: str) -> str | None:
    metadata = extraer_metadata_clave_acceso(clave_acceso)
    if metadata is None:
        return None

    return datetime.strptime(metadata["fecha"], "%d%m%Y").strftime(DATE_FORMAT)


def numero_documento_desde_clave_acceso(clave_acceso: str) -> str | None:
    metadata = extraer_metadata_clave_acceso(clave_acceso)
    if metadata is None:
        return None
    return f"{metadata['serie']}{metadata['secuencial']}"


def decimal_formateado(value, field_name: str, digits: str = "0.01") -> str:
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field_name} debe ser un numero decimal valido.") from exc

    return str(parsed.quantize(Decimal(digits), rounding=ROUND_HALF_UP))


@dataclass(frozen=True)
class EmisorRetencion(EmisorProfile):
    agente_retencion: str | None = None
    contribuyente_especial: str | None = None
    contribuyente_rimpe: str | None = None

    def build_info_tributaria(
        self,
        *,
        ambiente: str,
        tipo_emision: str,
        clave_acceso: str,
        secuencial: str,
    ) -> dict:
        return super().build_info_tributaria(
            cod_doc="07",
            ambiente=ambiente,
            tipo_emision=tipo_emision,
            clave_acceso=clave_acceso,
            secuencial=secuencial,
            extra_fields={
                "agenteRetencion": self.agente_retencion,
                "contribuyenteRimpe": self.contribuyente_rimpe,
            },
        )

    def build_info_comp_retencion(
        self,
        *,
        fecha_emision: str,
        sujeto_retenido: "SujetoRetenido",
        periodo_fiscal: str | None = None,
    ) -> dict:
        data = {
            "fechaEmision": _validar_fecha(fecha_emision, "fecha_emision"),
        }

        dir_establecimiento = self.resolve_dir_establecimiento()
        if dir_establecimiento is not None:
            data["dirEstablecimiento"] = dir_establecimiento

        contribuyente_especial = _texto_opcional(self.contribuyente_especial)
        if contribuyente_especial is not None:
            data["contribuyenteEspecial"] = contribuyente_especial

        obligado_contabilidad = self.resolve_obligado_contabilidad()
        if obligado_contabilidad is not None:
            data["obligadoContabilidad"] = obligado_contabilidad

        data["tipoIdentificacionSujetoRetenido"] = _requerido(
            sujeto_retenido.tipo_identificacion,
            "sujeto_retenido.tipo_identificacion",
        )

        tipo_sujeto_retenido = _texto_opcional(sujeto_retenido.tipo_sujeto_retenido)
        if tipo_sujeto_retenido is not None:
            data["tipoSujetoRetenido"] = tipo_sujeto_retenido

        data["parteRel"] = _si_no(
            sujeto_retenido.parte_rel,
            "sujeto_retenido.parte_rel",
        ) or "NO"
        data["razonSocialSujetoRetenido"] = _requerido(
            sujeto_retenido.razon_social,
            "sujeto_retenido.razon_social",
        )
        data["identificacionSujetoRetenido"] = _requerido(
            sujeto_retenido.identificacion,
            "sujeto_retenido.identificacion",
        )
        data["periodoFiscal"] = _texto_opcional(periodo_fiscal) or periodo_fiscal_desde_fecha(
            fecha_emision
        )
        return data


@dataclass(frozen=True)
class SujetoRetenido:
    tipo_identificacion: str
    identificacion: str
    razon_social: str
    parte_rel: str = "NO"
    tipo_sujeto_retenido: str | None = None


@dataclass(frozen=True)
class ImpuestoDocSustento:
    cod_impuesto_doc_sustento: str
    codigo_porcentaje: str
    base_imponible: str
    tarifa: str
    valor_impuesto: str

    def to_dict(self) -> dict:
        return {
            "codImpuestoDocSustento": _requerido(
                self.cod_impuesto_doc_sustento,
                "impuesto_doc_sustento.cod_impuesto_doc_sustento",
            ),
            "codigoPorcentaje": _requerido(
                self.codigo_porcentaje,
                "impuesto_doc_sustento.codigo_porcentaje",
            ),
            "baseImponible": _requerido(
                self.base_imponible,
                "impuesto_doc_sustento.base_imponible",
            ),
            "tarifa": _requerido(self.tarifa, "impuesto_doc_sustento.tarifa"),
            "valorImpuesto": _requerido(
                self.valor_impuesto,
                "impuesto_doc_sustento.valor_impuesto",
            ),
        }


@dataclass(frozen=True)
class RetencionLinea:
    codigo: str
    codigo_retencion: str
    base_imponible: str
    porcentaje_retener: str
    valor_retenido: str
    dividendos: Mapping[str, str] | None = None
    compra_caj_banano: Mapping[str, str] | None = None

    def to_dict(self) -> dict:
        data = {
            "codigo": _requerido(self.codigo, "retencion.codigo"),
            "codigoRetencion": _requerido(
                self.codigo_retencion,
                "retencion.codigo_retencion",
            ),
            "baseImponible": _requerido(
                self.base_imponible,
                "retencion.base_imponible",
            ),
            "porcentajeRetener": _requerido(
                self.porcentaje_retener,
                "retencion.porcentaje_retener",
            ),
            "valorRetenido": _requerido(
                self.valor_retenido,
                "retencion.valor_retenido",
            ),
        }

        if self.dividendos:
            data["dividendos"] = dict(self.dividendos)

        if self.compra_caj_banano:
            data["compraCajBanano"] = dict(self.compra_caj_banano)

        return data


@dataclass(frozen=True)
class PagoRetencion:
    forma_pago: str
    total: str

    def to_dict(self) -> dict:
        return {
            "formaPago": _requerido(self.forma_pago, "pago.forma_pago"),
            "total": _requerido(self.total, "pago.total"),
        }


@dataclass(frozen=True)
class DocumentoSustentoRetencion:
    cod_sustento: str
    cod_doc_sustento: str
    num_doc_sustento: str
    fecha_emision_doc_sustento: str
    pago_loc_ext: str
    total_sin_impuestos: str
    importe_total: str
    impuestos_doc_sustento: Sequence[ImpuestoDocSustento]
    retenciones: Sequence[RetencionLinea]
    pagos: Sequence[PagoRetencion]
    num_aut_doc_sustento: str | None = None
    fecha_registro_contable: str | None = None
    tipo_regi: str | None = None
    pais_efec_pago: str | None = None
    aplic_conv_dob_trib: str | None = None
    pag_ext_suj_ret_nor_leg: str | None = None
    pago_reg_fis: str | None = None
    total_comprobantes_reembolso: str | None = None
    total_base_imponible_reembolso: str | None = None
    total_impuesto_reembolso: str | None = None
    reembolsos: Sequence[dict] | None = None

    def to_dict(self) -> dict:
        if not self.impuestos_doc_sustento:
            raise ValueError(
                "documento_sustento.impuestos_doc_sustento debe contener al menos un impuesto."
            )
        if not self.retenciones:
            raise ValueError(
                "documento_sustento.retenciones debe contener al menos una retencion."
            )
        if not self.pagos:
            raise ValueError(
                "documento_sustento.pagos debe contener al menos un pago."
            )

        data = {
            "codSustento": _requerido(self.cod_sustento, "documento_sustento.cod_sustento"),
            "codDocSustento": _requerido(
                self.cod_doc_sustento,
                "documento_sustento.cod_doc_sustento",
            ),
            "numDocSustento": _requerido(
                self.num_doc_sustento,
                "documento_sustento.num_doc_sustento",
            ),
            "fechaEmisionDocSustento": _validar_fecha(
                self.fecha_emision_doc_sustento,
                "documento_sustento.fecha_emision_doc_sustento",
            ),
        }

        fecha_registro_contable = _texto_opcional(self.fecha_registro_contable)
        if fecha_registro_contable is not None:
            data["fechaRegistroContable"] = _validar_fecha(
                fecha_registro_contable,
                "documento_sustento.fecha_registro_contable",
            )

        num_aut_doc_sustento = _texto_opcional(self.num_aut_doc_sustento)
        if num_aut_doc_sustento is not None:
            data["numAutDocSustento"] = num_aut_doc_sustento

        data["pagoLocExt"] = _requerido(
            self.pago_loc_ext,
            "documento_sustento.pago_loc_ext",
        )

        tipo_regi = _texto_opcional(self.tipo_regi)
        if tipo_regi is not None:
            data["tipoRegi"] = tipo_regi

        pais_efec_pago = _texto_opcional(self.pais_efec_pago)
        if pais_efec_pago is not None:
            data["paisEfecPago"] = pais_efec_pago

        aplic_conv_dob_trib = _si_no(
            self.aplic_conv_dob_trib,
            "documento_sustento.aplic_conv_dob_trib",
        )
        if aplic_conv_dob_trib is not None:
            data["aplicConvDobTrib"] = aplic_conv_dob_trib

        pag_ext_suj_ret_nor_leg = _si_no(
            self.pag_ext_suj_ret_nor_leg,
            "documento_sustento.pag_ext_suj_ret_nor_leg",
        )
        if pag_ext_suj_ret_nor_leg is not None:
            data["pagExtSujRetNorLeg"] = pag_ext_suj_ret_nor_leg

        pago_reg_fis = _si_no(
            self.pago_reg_fis,
            "documento_sustento.pago_reg_fis",
        )
        if pago_reg_fis is not None:
            data["pagoRegFis"] = pago_reg_fis

        total_comprobantes_reembolso = _texto_opcional(self.total_comprobantes_reembolso)
        if total_comprobantes_reembolso is not None:
            data["totalComprobantesReembolso"] = total_comprobantes_reembolso

        total_base_imponible_reembolso = _texto_opcional(
            self.total_base_imponible_reembolso
        )
        if total_base_imponible_reembolso is not None:
            data["totalBaseImponibleReembolso"] = total_base_imponible_reembolso

        total_impuesto_reembolso = _texto_opcional(self.total_impuesto_reembolso)
        if total_impuesto_reembolso is not None:
            data["totalImpuestoReembolso"] = total_impuesto_reembolso

        data["totalSinImpuestos"] = _requerido(
            self.total_sin_impuestos,
            "documento_sustento.total_sin_impuestos",
        )
        data["importeTotal"] = _requerido(
            self.importe_total,
            "documento_sustento.importe_total",
        )
        data["impuestosDocSustento"] = [
            impuesto.to_dict() for impuesto in self.impuestos_doc_sustento
        ]
        data["retenciones"] = [retencion.to_dict() for retencion in self.retenciones]

        if self.reembolsos:
            data["reembolsos"] = [dict(reembolso) for reembolso in self.reembolsos]

        data["pagos"] = [pago.to_dict() for pago in self.pagos]
        return data


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


def construir_payload_retencion(
    *,
    clave_acceso: str,
    ambiente: str,
    tipo_emision: str,
    secuencial: str,
    fecha_emision: str,
    emisor: EmisorRetencion,
    sujeto_retenido: SujetoRetenido,
    documentos_sustento: Sequence[DocumentoSustentoRetencion],
    info_adicional: Sequence[dict] | Sequence[tuple[str, str]] | None = None,
    periodo_fiscal: str | None = None,
) -> dict:
    fecha_emision = _validar_fecha(fecha_emision, "fecha_emision")

    if not documentos_sustento:
        raise ValueError("documentos_sustento debe contener al menos un documento.")

    for index, documento in enumerate(documentos_sustento, start=1):
        num_aut_doc_sustento = _texto_opcional(documento.num_aut_doc_sustento)
        if num_aut_doc_sustento == clave_acceso:
            raise ValueError(
                "documentos_sustento["
                f"{index}] no puede reutilizar la misma clave de acceso de la retencion."
            )

    payload = {
        "infoTributaria": emisor.build_info_tributaria(
            ambiente=ambiente,
            tipo_emision=tipo_emision,
            clave_acceso=clave_acceso,
            secuencial=secuencial,
        ),
        "infoCompRetencion": emisor.build_info_comp_retencion(
            fecha_emision=fecha_emision,
            sujeto_retenido=sujeto_retenido,
            periodo_fiscal=periodo_fiscal,
        ),
        "docsSustento": [documento.to_dict() for documento in documentos_sustento],
    }

    if info_adicional:
        payload["infoAdicional"] = _build_info_adicional(info_adicional)

    return payload


__all__ = [
    "DocumentoSustentoRetencion",
    "EmisorRetencion",
    "ImpuestoDocSustento",
    "PagoRetencion",
    "RetencionLinea",
    "SujetoRetenido",
    "construir_payload_retencion",
    "decimal_formateado",
    "extraer_metadata_clave_acceso",
    "fecha_desde_clave_acceso",
    "numero_documento_desde_clave_acceso",
    "periodo_fiscal_desde_fecha",
]
