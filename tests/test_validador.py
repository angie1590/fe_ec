import pytest
from src.fe_ec.core.validador import Validador

def test_validar_ruc():
    """
    Prueba la validación de RUCs.
    """
    assert Validador.validar_ruc("0104815956001")
    assert not Validador.validar_ruc("0012345678001")
    assert not Validador.validar_ruc("1799999999001")
    assert not Validador.validar_ruc("17ABC5678001")
    assert not Validador.validar_ruc("123456")

def test_validar_fecha():
    """
    Prueba la validación de fechas en formato YYYY-MM-DD.
    """
    assert Validador.validar_fecha("2024-02-29")
    assert not Validador.validar_fecha("29-02-2024")
    assert not Validador.validar_fecha("2024/02/29")
    assert not Validador.validar_fecha("20240229")
