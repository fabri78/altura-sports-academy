"""Descarga los videos (licencia libre) de Wikimedia Commons con su póster.

Uso: python -I tools/media/descargar_videos.py
"""
import io
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parents[2]
UA = "AlturaSportsStudentProject/1.0 (proyecto educativo UTP)"
PEDIDOS = {
    "basquet": "File:Basketball (2).ogv",
    "piscina": "File:Outdoor swimming pool 1 2019-09-13.webm",
}


def get(url):
    for intento in range(6):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            time.sleep(15 * (intento + 1))
    raise RuntimeError("Demasiados reintentos: " + url)


def api(params):
    return json.loads(get("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)))


def mejor(lista, max_alto=480):
    filtrada = [x for x in lista if x.get("height", 0) <= max_alto] or lista
    return sorted(filtrada, key=lambda x: x.get("height", 0))[-1] if filtrada else None


def main():
    archivo_cred = RAIZ / "docs" / "creditos-multimedia.json"
    creditos = json.loads(archivo_cred.read_text(encoding="utf-8"))
    destino = RAIZ / "assets" / "video"
    destino.mkdir(parents=True, exist_ok=True)
    for nombre, titulo in PEDIDOS.items():
        if (destino / f"{nombre}.mp4").exists():
            continue
        d = api({"action": "query", "format": "json", "titles": titulo, "prop": "videoinfo",
                 "viprop": "url|extmetadata|derivatives", "viurlwidth": 1280})
        v = list(d["query"]["pages"].values())[0]["videoinfo"][0]
        derivados = v.get("derivatives", [])
        mp4 = mejor([x for x in derivados if x.get("type", "").startswith("video/mp4")])
        webm = mejor([x for x in derivados if "webm" in x.get("type", "")])
        for x, ext in ((mp4, "mp4"), (webm, "webm")):
            if x:
                datos = get(x["src"])
                (destino / f"{nombre}.{ext}").write_bytes(datos)
                print(nombre, ext, x.get("height"), len(datos) // 1024, "KB")
                time.sleep(3)
        if v.get("thumburl"):
            img = Image.open(io.BytesIO(get(v["thumburl"]))).convert("RGB")
            img.save(destino / f"{nombre}-poster.webp", "WEBP", quality=75)
        meta = v.get("extmetadata", {})
        creditos.append({
            "archivo": f"assets/video/{nombre}.mp4", "titulo": titulo, "url": v["url"],
            "pagina": v.get("descriptionurl"),
            "autor": re.sub(r"<[^>]+>", "", meta.get("Artist", {}).get("value", "")).strip(),
            "licencia": meta.get("LicenseShortName", {}).get("value"),
        })
        archivo_cred.write_text(json.dumps(creditos, ensure_ascii=False, indent=2), encoding="utf-8")
        time.sleep(5)


if __name__ == "__main__":
    main()
