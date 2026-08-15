import re
import requests

URL = "https://muisca.dian.gov.co/WebRutMuisca/DefConsultaEstadoRUT.faces"
DOC = "1086499479"

session = requests.Session()
session.headers.update(
    {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        ),
        "Accept-Language": "es-CO,es;q=0.9",
    }
)

lines = []
try:
    session.get("https://muisca.dian.gov.co/", timeout=30)
    r = session.get(URL, timeout=30)
    ct = r.headers.get("content-type", "")
    lines.append(f"GET status={r.status_code} len={len(r.content)} ct={ct}")
    lines.append(f"numNit={('numNit' in r.text)} ViewState={('ViewState' in r.text)}")
    lines.append(f"html={('<html' in r.text[:500].lower())}")

    if "ViewState" in r.text:
        from aplicacion.integraciones.dian.cliente_muisca import ClienteMuisca

        payload = ClienteMuisca._construir_payload(r.text, DOC)
        lines.append(f"payload_ok={payload is not None}")
        if payload:
            resp = session.post(
                URL,
                data=payload,
                timeout=30,
                headers={
                    "Referer": URL,
                    "Origin": "https://muisca.dian.gov.co",
                },
            )
            lines.append(f"POST status={resp.status_code} ct={resp.headers.get('content-type')}")
            for campo in [
                "primerNombre",
                "primerApellido",
                "razonSocial",
                "estado",
            ]:
                val = ClienteMuisca._extraer_valor_elemento(
                    resp.text,
                    f"vistaConsultaEstadoRUT:formConsultaEstadoRUT:{campo}",
                )
                lines.append(f"{campo}={val!r}")
            resultado = __import__(
                "aplicacion.integraciones.dian.modelos",
                fromlist=["ResultadoDian"],
            ).ResultadoDian()
            ClienteMuisca._interpretar_respuesta(resp.text, resultado)
            lines.append(f"encontrado={resultado.encontrado}")
            lines.append(f"nombre={resultado.primer_nombre} {resultado.primer_apellido}")
            lines.append(f"razon={resultado.razon_social}")
            lines.append(f"estado_rut={resultado.estado_rut}")
except Exception as e:
    lines.append(f"ERROR={e!r}")

with open("_muisca_debug.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
