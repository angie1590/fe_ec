import pytest
import responses
from fe_ec.core.sri import SriServicio

@pytest.fixture
def xml_firmado():
    """
    XML de prueba firmado digitalmente.
    """
    return """<factura>
                <infoTributaria>
                    <claveAcceso>1234567890123456789012345678901234567890123456789</claveAcceso>
                </infoTributaria>
             </factura>"""

@pytest.fixture
def sri_servicio():
    """
    Instancia del servicio SRI con el ambiente de pruebas por defecto.
    """
    return SriServicio(ambiente="1")  # "1" es ambiente de pruebas, "2" sería producción

@responses.activate
def test_enviar_factura_exitoso(sri_servicio, xml_firmado):
    """
    Prueba el envío exitoso de una factura al SRI.
    """
    responses.add(
        responses.POST,
        sri_servicio.url_sri,
        body="<respuesta><estado>RECIBIDA</estado></respuesta>",
        status=200,
        content_type="application/xml"
    )

    respuesta = sri_servicio.enviar_factura(xml_firmado)
    assert respuesta is True

@responses.activate
def test_enviar_factura_fallida(sri_servicio, xml_firmado):
    """
    Prueba el fallo en el envío de una factura al SRI.
    """
    responses.add(
        responses.POST,
        sri_servicio.url_sri,
        body="<respuesta><estado>DEVUELTA</estado></respuesta>",
        status=400,
        content_type="application/xml"
    )

    respuesta = sri_servicio.enviar_factura(xml_firmado)
    assert respuesta is False

@responses.activate
def test_enviar_factura_error_sri(sri_servicio, xml_firmado):
    """
    Prueba el manejo de errores cuando el SRI no está disponible.
    """
    responses.add(
        responses.POST,
        sri_servicio.url_sri,
        body="Error interno del servidor",
        status=500,
        content_type="text/plain"
    )

    respuesta = sri_servicio.enviar_factura(xml_firmado)
    assert respuesta is False

def test_cambio_ambiente():
    """
    Prueba el cambio de ambiente entre pruebas y producción.
    """
    sri_test = SriServicio(ambiente="1")
    sri_prod = SriServicio(ambiente="2")

    assert sri_test.url_sri == "https://cel.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantes"
    assert sri_prod.url_sri == "https://cel.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesProduccion"
