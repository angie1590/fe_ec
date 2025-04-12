from fe_ec.utils.sri import SRIService
import html

sri = SRIService(ambiente="pruebas", espera_autorizacion=7)
#respuesta_autorizacion = sri.consultar_autorizacion("0804202501030125532900110010010000003830000038314")
respuesta_autorizacion = sri.consultar_autorizacion("0804202501010481595600110010500000000061728372614")
print("✅ Respuesta de autorización del SRI:")
print("Número:", respuesta_autorizacion["numero_autorizacion"])
print("Fecha :", respuesta_autorizacion["fecha_autorizacion"])
print("XML   :", respuesta_autorizacion["xml_autorizado"])

# Dentro de test.py luego de recibir el xml_autorizado
xml_escapado = respuesta_autorizacion.get("xml_autorizado")

if xml_escapado:
    xml_legible = html.unescape(xml_escapado)

    with open("aut.xml", "w", encoding="utf-8") as f:
        f.write(xml_legible)