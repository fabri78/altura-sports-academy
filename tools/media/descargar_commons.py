"""Descarga imagenes con licencia libre desde Wikimedia Commons y las convierte a WebP.

Uso:  python -I tools/media/descargar_commons.py
Genera assets/img/<carpeta>/<nombre>.webp y docs/creditos-multimedia.json
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

from PIL import Image

RAIZ = Path(__file__).resolve().parents[2]
UA = "AlturaSportsStudentProject/1.0 (proyecto educativo UTP)"
LICENCIAS_OK = ("CC0", "Public domain", "CC BY", "CC BY-SA", "PD")

# (carpeta, nombre, busqueda, indice del resultado a usar, ancho)
PEDIDOS = [
    ("hero", "hero-basquet", "basketball dunk night game", 0, 2000),
    ("hero", "hero-arena", "basketball arena dark lights", 0, 2000),
    ("academias", "basquet-ninos", "children basketball practice", 0, 1400),
    ("academias", "basquet-tiro", "basketball hoop net ball", 0, 1400),
    ("academias", "basquet-cancha", "basketball hoop outdoor court", 0, 1400),
    ("academias", "aerobicos-clase", "zumba class", 0, 1400),
    ("academias", "aerobicos-step", "fitness class gym group exercise", 0, 1400),
    ("academias", "funcional", "kettlebell training", 0, 1400),
    ("academias", "natacion-carriles", "swimming pool lanes", 0, 1400),
    ("academias", "natacion-nado", "swimmer underwater pool", 0, 1400),
    ("tienda", "pelota-basquet", "basketball ball", 0, 1000),
    ("tienda", "zapatillas", "running shoe white background", 0, 1000),
    ("tienda", "mancuernas", "dumbbells", 0, 1000),
    ("tienda", "lentes-natacion", "swimming goggles white background", 0, 1000),
    ("tienda", "colchoneta", "yoga mat rolled", 0, 1000),
    ("tienda", "botella", "stainless steel water bottle", 0, 1000),
    ("tienda", "camiseta", "sports jersey shirt", 0, 1000),
    ("tienda", "cuerda", "skipping rope", 0, 1000),
    ("blog", "misti", "Misti volcano Arequipa", 0, 1600),
    ("blog", "correr-montana", "trail running mountain", 0, 1400),
    ("blog", "nutricion", "healthy food vegetables", 0, 1400),
    ("blog", "estiramiento", "stretching athlete legs", 0, 1400),
    ("galeria", "g-basquet-1", "basketball game", 1, 1400),
    ("galeria", "g-basquet-2", "basketball layup", 0, 1400),
    ("galeria", "g-voley", "volleyball match", 0, 1400),
    ("galeria", "g-atletismo", "athletics running track", 0, 1400),
    ("galeria", "g-natacion", "swimming competition", 0, 1400),
    ("galeria", "g-gimnasio", "gymnasium sports hall", 0, 1400),
    ("galeria", "g-futbol", "youth football practice", 0, 1400),
    ("galeria", "g-arequipa", "Arequipa Plaza de Armas", 0, 1400),
]


def api(params):
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def limpiar(html):
    return re.sub(r"<[^>]+>", "", html or "").strip()


def buscar(q, ancho):
    d = api({
        "action": "query", "format": "json", "generator": "search",
        "gsrnamespace": 6, "gsrsearch": f"{q} filetype:bitmap", "gsrlimit": 20,
        "prop": "imageinfo", "iiprop": "url|size|extmetadata|mime", "iiurlwidth": ancho,
    })
    paginas = sorted(d.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))
    candidatos = []
    for p in paginas:
        ii = p["imageinfo"][0]
        meta = ii.get("extmetadata", {})
        lic = meta.get("LicenseShortName", {}).get("value", "")
        if ii.get("mime") not in ("image/jpeg", "image/png"):
            continue
        if ii["width"] < 1000 or ii["width"] < ii["height"]:  # solo horizontales y grandes
            continue
        if not any(lic.startswith(x) for x in LICENCIAS_OK):
            continue
        candidatos.append({
            "titulo": p["title"],
            "url": ii.get("thumburl") or ii["url"],
            "pagina": ii.get("descriptionurl"),
            "autor": limpiar(meta.get("Artist", {}).get("value")),
            "licencia": lic,
        })
    return candidatos


def main():
    archivo_cred = RAIZ / "docs" / "creditos-multimedia.json"
    creditos = json.loads(archivo_cred.read_text(encoding="utf-8")) if archivo_cred.exists() else []
    usados = {c["titulo"] for c in creditos}
    hechos = {c["archivo"] for c in creditos}
    for carpeta, nombre, q, idx, ancho in PEDIDOS:
        destino = RAIZ / "assets" / "img" / carpeta / f"{nombre}.webp"
        if str(destino.relative_to(RAIZ)).replace("\\", "/") in hechos and destino.exists():
            continue
        try:
            cands = [c for c in buscar(q, ancho) if c["titulo"] not in usados]
        except Exception as e:  # noqa: BLE001
            print("ERROR busqueda", q, e, file=sys.stderr)
            continue
        if not cands:
            print("SIN RESULTADOS", q)
            continue
        c = cands[min(idx, len(cands) - 1)]
        usados.add(c["titulo"])
        datos = None
        for intento in range(5):
            try:
                req = urllib.request.Request(c["url"], headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=60) as r:
                    datos = r.read()
                break
            except urllib.error.HTTPError as e:
                if e.code != 429:
                    raise
                time.sleep(8 * (intento + 1))
        if datos is None:
            print("FALLO descarga", c["titulo"])
            continue
        img = Image.open(io.BytesIO(datos)).convert("RGB")
        if img.width > ancho:
            img = img.resize((ancho, round(img.height * ancho / img.width)), Image.LANCZOS)
        destino.parent.mkdir(parents=True, exist_ok=True)
        img.save(destino, "WEBP", quality=78, method=6)
        creditos.append({"archivo": str(destino.relative_to(RAIZ)).replace("\\", "/"), **c,
                         "ancho": img.width, "alto": img.height})
        archivo_cred.write_text(json.dumps(creditos, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"OK {destino.name:28} {img.width}x{img.height} {c['licencia']:14} {c['titulo'][:60]}")
        time.sleep(2.5)
    (RAIZ / "docs" / "creditos-multimedia.json").write_text(
        json.dumps(creditos, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
