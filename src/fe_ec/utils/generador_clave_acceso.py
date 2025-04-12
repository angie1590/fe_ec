from datetime import datetime
import hashlib


class GeneradorClaveAcceso:
    @staticmethod
    def generar(
        fecha_emision: str,      # Formato: dd/mm/aaaa o ddmmaaaa
        tipo_comprobante: str,   # Ej: "01" para factura
        ruc: str,                # RUC de la empresa
        tipo_ambiente: str,      # "1" pruebas, "2" producción
        serie: str,              # Ej: "001002"
        secuencial: str,         # Ej: "000000123"
        tipo_emision: str = "1"  # "1" para emisión normal
    ) -> str:
        # Normalizar fecha a ddmmaaaa
        if "/" in fecha_emision:
            fecha_emision = datetime.strptime(fecha_emision, "%d/%m/%Y").strftime("%d%m%Y")

        # Generar código numérico con función hash
        codigo_numerico = GeneradorClaveAcceso._generar_codigo_numerico(serie, secuencial, fecha_emision)

        # Construcción de los 48 primeros dígitos (sin el dígito verificador)
        clave_sin_dv = (
            fecha_emision +
            tipo_comprobante.zfill(2) +
            ruc.zfill(13) +
            tipo_ambiente +
            serie.zfill(6) +
            secuencial.zfill(9) +
            codigo_numerico +
            tipo_emision
        )

        # Calcular dígito verificador usando módulo 11
        dv = GeneradorClaveAcceso._calcular_digito_verificador(clave_sin_dv)

        # Clave final
        return clave_sin_dv + str(dv)

    @staticmethod
    def _generar_codigo_numerico(serie: str, secuencial: str, fecha_emision: str) -> str:
        base = f"{serie}-{secuencial}-{fecha_emision}"
        hash_code = hashlib.sha256(base.encode()).hexdigest()
        return str(int(hash_code[:16], 16))[:8].zfill(8)

    @staticmethod
    def _calcular_digito_verificador(clave: str) -> int:
        factores = [2, 3, 4, 5, 6, 7]
        suma = 0
        inverso = list(map(int, reversed(clave)))

        for i, n in enumerate(inverso):
            factor = factores[i % len(factores)]
            suma += n * factor

        mod = suma % 11
        verificador = 11 - mod
        if verificador == 11:
            return 0
        elif verificador == 10:
            return 1
        else:
            return verificador
