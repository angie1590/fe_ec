from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


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


@dataclass(frozen=True)
class EmisorProfile:
    ruc: str
    razon_social: str
    estab: str
    pto_emi: str
    dir_matriz: str
    nombre_comercial: str | None = None
    dir_establecimiento: str | None = None
    obligado_contabilidad: str | None = None

    def build_info_tributaria(
        self,
        *,
        cod_doc: str,
        ambiente: str,
        tipo_emision: str,
        clave_acceso: str,
        secuencial: str,
        extra_fields: Mapping[str, str | None] | None = None,
    ) -> dict:
        data = {
            "ambiente": _requerido(ambiente, "ambiente"),
            "tipoEmision": _requerido(tipo_emision, "tipo_emision"),
            "razonSocial": _requerido(self.razon_social, "emisor.razon_social"),
        }

        nombre_comercial = _texto_opcional(self.nombre_comercial)
        if nombre_comercial is not None:
            data["nombreComercial"] = nombre_comercial

        data.update(
            {
                "ruc": _requerido(self.ruc, "emisor.ruc"),
                "claveAcceso": _requerido(clave_acceso, "clave_acceso"),
                "codDoc": _requerido(cod_doc, "cod_doc"),
                "estab": _requerido(self.estab, "emisor.estab"),
                "ptoEmi": _requerido(self.pto_emi, "emisor.pto_emi"),
                "secuencial": _requerido(secuencial, "secuencial"),
                "dirMatriz": _requerido(self.dir_matriz, "emisor.dir_matriz"),
            }
        )

        for key, value in (extra_fields or {}).items():
            resolved = _texto_opcional(value)
            if resolved is not None:
                data[key] = resolved

        return data

    def build_common_issue_data(self) -> dict:
        data = {}

        dir_establecimiento = self.resolve_dir_establecimiento()
        if dir_establecimiento is not None:
            data["dirEstablecimiento"] = dir_establecimiento

        obligado_contabilidad = self.resolve_obligado_contabilidad()
        if obligado_contabilidad is not None:
            data["obligadoContabilidad"] = obligado_contabilidad

        return data

    def resolve_dir_establecimiento(self) -> str | None:
        return _texto_opcional(self.dir_establecimiento or self.dir_matriz)

    def resolve_obligado_contabilidad(self) -> str | None:
        return _si_no(self.obligado_contabilidad, "emisor.obligado_contabilidad")


__all__ = ["EmisorProfile"]
