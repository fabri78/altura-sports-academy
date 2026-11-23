"""Descarga las fotos reales elegidas para la tienda y genera las variantes de color de la zapatilla.

Las fotos son de Wikimedia Commons (licencias libres). Las variantes de color se obtienen
cambiando solo el tono de las zonas de color de la misma foto (técnica habitual de maquetas).
Uso: python -I tools/media/fotos_productos.py <candidatos.json>
"""
import io
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image

RAIZ = Path(__file__).resolve().parents[2]
DEST = RAIZ / "assets" / "img" / "tienda"
UA = "AlturaSportsStudentProject/1.0 (proyecto educativo UTP)"
cands = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))

ELEGIDAS = {  # archivo final: (producto en candidatos.json, índice, recorte)
    "zapatilla-base": ("zapatilla", 6, "cuadrado"),
    "pelota": ("pelota", 3, "cuadrado"),
    "camiseta": ("camiseta", 10, "cuadrado"),
    "lentes": ("lentes", 11, "cuadrado"),
    "botella": ("botella", 13, "cuadrado"),
    "mancuernas": ("mancuernas", 3, "cuadrado"),
    "colchoneta": ("colchoneta", 5, "cuadrado"),
    "mancuernas-ajustables": ("mancuernas", 7, "cuadrado"),
    "mochila": ("mochila", 11, "cuadrado"),
}


def get(url):
    for i in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=90) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            time.sleep(20 * (i + 1))
    raise RuntimeError("429")


def cuadrado(img, lado=900):
    w, h = img.size
    m = min(w, h)
    img = img.crop(((w - m) // 2, (h - m) // 2, (w - m) // 2 + m, (h - m) // 2 + m))
    return img.resize((lado, lado), Image.LANCZOS)


creditos_path = RAIZ / "docs" / "creditos-multimedia.json"
creditos = [c for c in json.loads(creditos_path.read_text(encoding="utf-8")) if "/tienda/" not in c["archivo"]]

for nombre, (prod, idx, modo) in ELEGIDAS.items():
    c = cands[prod][idx]
    destino = DEST / f"{nombre}.webp"
    if not destino.exists() and not (nombre == "zapatilla-base" and (DEST / "zapatilla-brasa.webp").exists() and (DEST / "zapatilla-brasa.webp").stat().st_size > 20000):
        # Se usan anchos de miniatura estándar de Wikimedia (ya generados en caché) para evitar el límite 429
        ancho = next(w for w in (1280, 960, 500, 330) if c["ancho"] > w)
        url = c["thumb"].replace("/320px-", f"/{ancho}px-")
        img = Image.open(io.BytesIO(get(url))).convert("RGB")
        cuadrado(img).save(destino, "WEBP", quality=82)
        time.sleep(4)
    if nombre != "zapatilla-base":
        creditos.append({"archivo": f"assets/img/tienda/{nombre}.webp", "titulo": c["titulo"], "url": c["url"],
                         "pagina": c["pagina"], "autor": c["autor"], "licencia": c["licencia"]})
    print("OK", nombre, c["titulo"][:60], c["licencia"])

# Variantes de color de la zapatilla: se cambia el tono de los píxeles rojos (detalles de la capellada)
base = Image.open(DEST / "zapatilla-base.webp").convert("RGB")
hsv = np.asarray(base.convert("HSV")).astype(np.int16)
h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
rojo = ((h < 18) | (h > 235)) & (s > 90) & (v > 40)
variantes = {
    "borgona": (250, 1.0, 0.72),   # rojo más oscuro
    "brasa": (14, 1.0, 1.08),      # naranja
    "glaciar": (140, 0.45, 1.35),  # celeste
    "grafito": (0, 0.0, 0.55),     # gris oscuro
}
for nombre, (tono, sat, luz) in variantes.items():
    n = hsv.copy()
    n[..., 0] = np.where(rojo, tono, h)
    n[..., 1] = np.where(rojo, np.clip(s * sat, 0, 255), s)
    n[..., 2] = np.where(rojo, np.clip(v * luz, 0, 255), v)
    Image.fromarray(n.astype(np.uint8), "HSV").convert("RGB").save(DEST / f"zapatilla-{nombre}.webp", "WEBP", quality=82)
c = cands["zapatilla"][6]
creditos.append({"archivo": "assets/img/tienda/zapatilla-borgona.webp", "titulo": c["titulo"], "url": c["url"], "pagina": c["pagina"],
                 "autor": c["autor"] + " (variantes de color editadas por el equipo)", "licencia": c["licencia"]})
(DEST / "zapatilla-base.webp").unlink(missing_ok=True)
creditos_path.write_text(json.dumps(creditos, ensure_ascii=False, indent=2), encoding="utf-8")
print("Variantes de la zapatilla:", ", ".join(variantes))
