import re
import requests

url = "https://muisca.dian.gov.co/WebRutMuisca/DefConsultaEstadoRUT.faces"
r = requests.get(
    url,
    timeout=30,
    headers={
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "es-CO,es;q=0.9",
    },
)
text = r.text
open("_muisca.html", "w", encoding="utf-8").write(text)

print("len", len(text))
print("form count", text.lower().count("<form"))
print("input count", text.lower().count("<input"))
print("ViewState", "ViewState" in text)
print("label_nit", "label_nit" in text)

for pat in [
    r"id=\"[^\"]+\"",
    r"name=\"[^\"]+\"",
    r"action=\"[^\"]+\"",
    r"https?://[^\\s\"']+",
]:
    pass

# JSF component ids
ids = set(re.findall(r'id="([^"]{5,80})"', text))
for i in sorted(ids):
    low = i.lower()
    if any(k in low for k in ("nit", "num", "doc", "consult", "btn", "form", "rut")):
        print("id:", i)

# ajax endpoints
for m in re.finditer(r"['\"](/[^'\"]+(?:faces|Consulta|Rut|Muisca)[^'\"]*)['\"]", text, re.I):
    print("path:", m.group(1)[:100])

# script src
for m in re.finditer(r'src="([^"]+)"', text):
    s = m.group(1)
    if "muisca" in s.lower() or "rut" in s.lower() or "consult" in s.lower():
        print("src:", s[:120])
