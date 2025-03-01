import datetime
import hashlib

class GeneradorClaveAcceso:
    """
    Genera la clave de acceso para comprobantes electrónicos según la normativa del SRI Ecuador.
    """
    @staticmethod
    def generar(tipo_comprobante: str, fecha_emision: str, ruc: str,
                ambiente: str, serie: str, secuencial: str,
                codigo_numerico: str, tipo_emision: str) -> str:
        """
        Genera la clave de acceso según la estructura definida por el SRI.
        """
        fecha_emision = fecha_emision.replace("-", "")
        clave_base = (f"{fecha_emision}{tipo_comprobante}{ruc}{ambiente}{serie}"
                      f"{secuencial}{codigo_numerico}{tipo_emision}")
        clave = clave_base + GeneradorClaveAcceso._calcular_digito_verificador(clave_base)
        return clave

    @staticmethod
    def _calcular_digito_verificador(clave: str) -> str:
        """
        Calcula el dígito verificador según el algoritmo módulo 11 del SRI.
        """
        coeficientes = [2, 3, 4, 5, 6, 7]
        suma = 0
        for i, num in enumerate(reversed(clave)):
            suma += int(num) * coeficientes[i % len(coeficientes)]
        modulo = suma % 11
        verificador = 11 - modulo if modulo > 1 else 0
        return str(verificador)