import re
import requests

r = requests.get(
    "https://www.vue.gov.co/tramites-y-consultas/consulta-de-estado-del-rut",
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=30,
)
urls = sorted(set(re.findall(r"https?://[^\s\"']+", r.text)))
for u in urls:
    if any(k in u.lower() for k in ("api", "servicio", "consult", "rut", "dian", "ajax")):
        print(u)

print("--- scripts ---")
for s in re.findall(r'src="([^"]+\.js[^"]*)"', r.text):
    print(s)
