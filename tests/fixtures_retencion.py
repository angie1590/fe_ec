def build_retencion_payload(
    clave_acceso: str,
    *,
    use_legacy_pago_aliases: bool = False,
    include_reembolso: bool = False,
    include_dividendos: bool = False,
) -> dict:
    pagos_key = "Pagos" if use_legacy_pago_aliases else "pagos"

    doc_sustento = {
        "codSustento": "01",
        "codDocSustento": "01",
        "numDocSustento": "001001000000123",
        "fechaEmisionDocSustento": "13/03/2026",
        "numAutDocSustento": "1303202601017901234500120010010000001231234567810",
        "pagoLocExt": "01",
        "totalSinImpuestos": "100.00",
        "importeTotal": "115.00",
        "impuestosDocSustento": [
            {
                "codImpuestoDocSustento": "2",
                "codigoPorcentaje": "4",
                "baseImponible": "100.00",
                "tarifa": "15.00",
                "valorImpuesto": "15.00",
            }
        ],
        "retenciones": [
            {
                "codigo": "1",
                "codigoRetencion": "332",
                "baseImponible": "100.00",
                "porcentajeRetener": "1.00",
                "valorRetenido": "1.00",
            },
            {
                "codigo": "2",
                "codigoRetencion": "1",
                "baseImponible": "15.00",
                "porcentajeRetener": "30.00",
                "valorRetenido": "4.50",
            },
        ],
        pagos_key: [
            {
                "formaPago": "01",
                "total": "115.00",
            }
        ],
    }

    if include_dividendos:
        doc_sustento["retenciones"][0]["dividendos"] = {
            "fechaPagoDiv": "13/03/2026",
            "imRentaSoc": "25.00",
            "ejerFisUtDiv": "2025",
        }
        doc_sustento["retenciones"][0]["compraCajBanano"] = {
            "numCajBan": "10",
            "precCajBan": "18.50",
        }

    if include_reembolso:
        doc_sustento["codDocSustento"] = "41"
        doc_sustento["totalComprobantesReembolso"] = "20.00"
        doc_sustento["totalBaseImponibleReembolso"] = "17.39"
        doc_sustento["totalImpuestoReembolso"] = "2.61"
        doc_sustento["reembolsos"] = [
            {
                "tipoIdentificacionProveedorReembolso": "04",
                "identificacionProveedorReembolso": "1790012345001",
                "codPaisPagoProveedorReembolso": "593",
                "tipoProveedorReembolso": "01",
                "codDocReembolso": "01",
                "estabDocReembolso": "001",
                "ptoEmiDocReembolso": "001",
                "secuencialDocReembolso": "000000321",
                "fechaEmisionDocReembolso": "13/03/2026",
                "numeroautorizacionDocReemb": (
                    "1303202601017901234500120010010000003211234567810"
                ),
                "detalleImpuestos": [
                    {
                        "codigo": "2",
                        "codigoPorcentaje": "4",
                        "tarifa": "15",
                        "baseImponibleReembolso": "17.39",
                        "impuestoReembolso": "2.61",
                    }
                ],
            }
        ]

    return {
        "infoTributaria": {
            "ambiente": "1",
            "tipoEmision": "1",
            "razonSocial": "EMPRESA DEMO S.A.",
            "nombreComercial": "EMPRESA DEMO",
            "ruc": "1790012345001",
            "claveAcceso": clave_acceso,
            "codDoc": "07",
            "estab": "001",
            "ptoEmi": "001",
            "secuencial": "000000123",
            "dirMatriz": "Av. Principal 123",
            "agenteRetencion": "1",
        },
        "infoCompRetencion": {
            "fechaEmision": "13/03/2026",
            "dirEstablecimiento": "Av. Secundaria 456",
            "obligadoContabilidad": "NO",
            "tipoIdentificacionSujetoRetenido": "04",
            "tipoSujetoRetenido": "01",
            "parteRel": "NO",
            "razonSocialSujetoRetenido": "PROVEEDOR DEMO S.A.",
            "identificacionSujetoRetenido": "1790012345001",
            "periodoFiscal": "03/2026",
        },
        "docsSustento": [doc_sustento],
        "infoAdicional": {
            "campoAdicional": [
                {"nombre": "email", "valor": "contabilidad@ejemplo.com"},
                {"nombre": "referencia", "valor": "RET-000000123"},
            ]
        },
    }
