import requests

doc = "1086499479"
urls = [
    ("personas nit", "https://www.datos.gov.co/resource/cas9-r54x.json", {"nit": doc, "$limit": 1}),
    ("personas id", "https://www.datos.gov.co/resource/cas9-r54x.json", {"numero_identificacion": doc, "$limit": 1}),
    ("empresas nit", "https://www.datos.gov.co/resource/c82u-588k.json", {"nit": doc, "$limit": 1}),
]
for name, url, params in urls:
    r = requests.get(url, params=params, timeout=30)
    print(name, r.status_code, r.text[:200])
