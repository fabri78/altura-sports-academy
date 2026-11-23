"""Lista y descarga miniaturas de fotos candidatas (licencia libre) para cada producto de la tienda.

Uso: python -I tools/media/candidatos_productos.py <carpeta_salida>
Genera <carpeta>/<producto>.jpg (hoja de contacto numerada) y <carpeta>/candidatos.json
"""
import io
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw

UA = "AlturaSportsStudentProject/1.0 (proyecto educativo UTP)"
LIC = ("CC0", "Public domain", "CC BY", "CC BY-SA", "PD")
SALIDA = Path(sys.argv[1])
SALIDA.mkdir(parents=True, exist_ok=True)

BUSQUEDAS = {
    "zapatilla": ["basketball shoe", "basketball sneaker", "high top sneaker"],
    "pelota": ["basketball ball", "basketball isolated"],
    "camiseta": ["basketball jersey", "sports jersey shirt"],
    "lentes": ["swimming goggles", "swim goggles"],
    "botella": ["water bottle sport", "reusable water bottle"],
    "mancuernas": ["dumbbells", "hex dumbbell"],
    "colchoneta": ["yoga mat", "exercise mat"],
    "cuerda": ["jump rope", "skipping rope handles"],
    "mochila": ["backpack", "sports backpack"],
}


def get(url):
    for intento in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            time.sleep(20 * (intento + 1))
    raise RuntimeError("429 persistente")


def buscar(q):
    params = {"action": "query", "format": "json", "generator": "search", "gsrnamespace": 6,
              "gsrsearch": f"{q} filetype:bitmap", "gsrlimit": 12, "prop": "imageinfo",
              "iiprop": "url|size|extmetadata|mime", "iiurlwidth": 320}
    d = json.loads(get("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)))
    salida = []
    for p in sorted(d.get("query", {}).get("pages", {}).values(), key=lambda x: x.get("index", 99)):
        ii = p["imageinfo"][0]
        m = ii.get("extmetadata", {})
        lic = m.get("LicenseShortName", {}).get("value", "")
        if ii.get("mime") not in ("image/jpeg", "image/png") or ii["width"] < 700:
            continue
        if not any(lic.startswith(x) for x in LIC):
            continue
        salida.append({"titulo": p["title"], "thumb": ii["thumburl"], "url": ii["url"], "pagina": ii["descriptionurl"],
                       "ancho": ii["width"], "alto": ii["height"], "licencia": lic,
                       "autor": re.sub(r"<[^>]+>", "", m.get("Artist", {}).get("value", "")).strip()[:80]})
    return salida


todos = {}
for prod, consultas in BUSQUEDAS.items():
    vistos, cands = set(), []
    for q in consultas:
        for c in buscar(q):
            if c["titulo"] not in vistos:
                vistos.add(c["titulo"])
                cands.append(c)
        time.sleep(1.5)
    cands = cands[:15]
    todos[prod] = cands
    hoja = Image.new("RGB", (5 * 260, ((len(cands) + 4) // 5) * 230), "white")
    d = ImageDraw.Draw(hoja)
    for i, c in enumerate(cands):
        try:
            im = Image.open(io.BytesIO(get(c["thumb"]))).convert("RGB")
            im.thumbnail((250, 200))
            x, y = (i % 5) * 260, (i // 5) * 230
            hoja.paste(im, (x + 5, y + 5))
            d.text((x + 6, y + 208), f"{i}: {c['licencia']} {c['ancho']}x{c['alto']}", fill="black")
        except Exception as e:  # noqa: BLE001
            print("fallo miniatura", prod, i, e)
        time.sleep(1.2)
    hoja.save(SALIDA / f"{prod}.jpg", quality=80)
    print(prod, len(cands))
(SALIDA / "candidatos.json").write_text(json.dumps(todos, ensure_ascii=False, indent=1), encoding="utf-8")
