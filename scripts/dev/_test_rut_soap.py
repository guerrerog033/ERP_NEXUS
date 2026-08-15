import requests

URL = "https://muisca.dian.gov.co/ws-rut/services/DWSConsultaRutMCE"

for doc in ["1086499479", "860002964"]:
    body = f"""<?xml version="1.0" encoding="ISO-8859-1"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
 xmlns:xsd="http://www.w3.org/2001/XMLSchema"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<SOAP-ENV:Body>
<ns1:consultarRut xmlns:ns1="http://tempuri.org">
<nit>{doc}</nit>
</ns1:consultarRut>
</SOAP-ENV:Body>
</SOAP-ENV:Envelope>"""

    r = requests.post(
        URL,
        data=body.encode("iso-8859-1"),
        headers={
            "Content-Type": "text/xml; charset=ISO-8859-1",
            "SOAPAction": "",
            "User-Agent": "ERP-NEXUS/1.0",
        },
        timeout=30,
    )
    with open("_soap_out.txt", "a", encoding="utf-8") as f:
        f.write(f"=== {doc} status={r.status_code} ===\n")
        f.write(r.text)
        f.write("\n\n")
