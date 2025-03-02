import re
import xmlschema

class Validador:
    """
    Clase para validar comprobantes electrónicos antes de enviarlos al SRI.
    """

    @staticmethod
    def validar_ruc(ruc: str) -> bool:
        """
        Valida un RUC ecuatoriano según la estructura definida por el SRI.
        """

        if not re.match(r"^\d{13}$", ruc):  # Verifica que sean 13 dígitos numéricos
            return False

        provincia = int(ruc[:2])  # Los dos primeros dígitos corresponden a la provincia (01-24)
        tercer_digito = int(ruc[2])  # Indica el tipo de contribuyente
        cedula = ruc[:10]  # Para personas naturales, corresponde a la cédula
        digito_verificador = int(ruc[9])  # Dígito verificador para módulo 10 y 11
        ultimos_tres = ruc[10:]  # Últimos tres dígitos deben ser "001"

        # Verificar provincia válida (01-24)
        if provincia < 1 or provincia > 24:
            return False

        # Verificar que los últimos tres dígitos sean '001'
        if ultimos_tres != "001":
            return False

        # Validación específica según el tipo de RUC
        if 0 <= tercer_digito <= 5:  # Personas Naturales (0-5)
            return Validador._verificar_modulo_10(cedula)

        elif tercer_digito == 9:  # Sociedades privadas y extranjeros no residentes
            coeficientes = [4, 3, 2, 7, 6, 5, 4, 3, 2]
            return Validador._verificar_modulo_11(ruc[:9], coeficientes, digito_verificador)

        elif tercer_digito == 6:  # Sociedades públicas
            coeficientes = [3, 2, 7, 6, 5, 4, 3, 2]
            return Validador._verificar_modulo_11(ruc[:8], coeficientes, digito_verificador)

        return False

    @staticmethod
    def _verificar_modulo_10(cedula: str) -> bool:
        """
        Valida una cédula ecuatoriana aplicando el algoritmo de módulo 10.
        """
        coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
        suma = 0

        for i in range(9):  # Solo se evalúan los primeros 9 dígitos
            resultado = int(cedula[i]) * coeficientes[i]
            if resultado >= 10:
                resultado -= 9
            suma += resultado

        decena_superior = (suma + 9) // 10 * 10
        digito_calculado = decena_superior - suma if decena_superior - suma < 10 else 0

        return digito_calculado == int(cedula[9])  # Comparar con el último dígito de la cédula

    @staticmethod
    def _verificar_modulo_11(numero: str, coeficientes: list, digito_verificador: int) -> bool:
        """
        Aplica el algoritmo de módulo 11 para validar el número.
        """
        suma = sum(int(numero[i]) * coeficientes[i] for i in range(len(coeficientes)))
        modulo = suma % 11
        digito_calculado = 11 - modulo if modulo >= 2 else 0

        return digito_calculado == digito_verificador

    @staticmethod
    def validar_fecha(fecha: str) -> bool:
        """
        Valida el formato de una fecha.

        :param fecha: Fecha en formato de string.
        :return: True si es válida, False en caso contrario.
        """
        return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", fecha))

    @staticmethod
    def validar_xml(xml_path: str, xsd_path: str) -> bool:
        """
        Valida la estructura de un XML contra el esquema XSD del SRI.

        :param xml_path: Ruta del archivo XML a validar.
        :param xsd_path: Ruta del archivo XSD del SRI.
        :return: True si el XML es válido, False si hay errores de validación.
        """
        try:
            schema = xmlschema.XMLSchema(xsd_path)
            return schema.is_valid(xml_path)
        except xmlschema.XMLSchemaException as e:
            print(f"Error en validación de XML: {e}")
            return False
