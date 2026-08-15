import re
import requests

js = requests.get(
    "https://www.vue.gov.co/ResourcePackages/Bootstrap5/assets/vue/js/custom.js?package=Bootstrap5",
    timeout=30,
).text
patterns = re.findall(r"[\w/.:-]+(?:rut|RUT|consulta|Consulta|dian|DIAN)[\w/.:-]*", js)
for p in sorted(set(patterns)):
    print(p)
