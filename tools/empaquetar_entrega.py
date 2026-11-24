"""Arma el ZIP de entrega solo con el código funcional del sitio y sin comentarios.

Incluye: index.html, 404.html, paginas/, assets/ (css, js, img, video, audio),
src/less y src/scss (fuentes de los preprocesadores), package.json mínimo y Dockerfile.
Quita los comentarios de HTML, CSS, LESS, SASS y JavaScript.

Uso: python -I tools/empaquetar_entrega.py
Salida: entrega/Codigo-Fuente-Grupo04-ALTURA.zip  (y la carpeta entrega/codigo/ para revisarla)
"""
import json
import re
import shutil
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "entrega" / "codigo" / "altura-sports-academy"
ZIP = RAIZ / "entrega" / "Codigo-Fuente-Grupo04-ALTURA.zip"

INCLUIR = ["index.html", "404.html", "paginas", "assets", "src/less", "src/scss", "Dockerfile", ".dockerignore"]


def quitar_comentarios_c(texto, linea=True):
    """Quita /* */ (y // si linea=True) fuera de cadenas de texto."""
    salida, i, n, cadena = [], 0, len(texto), None
    while i < n:
        c = texto[i]
        if cadena:
            salida.append(c)
            if c == "\\" and i + 1 < n:
                salida.append(texto[i + 1])
                i += 2
                continue
            if c == cadena:
                cadena = None
            i += 1
            continue
        if c in "\"'`":
            cadena = c
            salida.append(c)
            i += 1
            continue
        if texto.startswith("/*", i):
            fin = texto.find("*/", i + 2)
            i = n if fin == -1 else fin + 2
            continue
        if linea and texto.startswith("//", i) and (i == 0 or texto[i - 1] != ":"):
            fin = texto.find("\n", i)
            i = n if fin == -1 else fin
            continue
        salida.append(c)
        i += 1
    return "".join(salida)


def ordenar_lineas(texto):
    lineas = [l.rstrip() for l in texto.splitlines()]
    limpio, vacia = [], False
    for l in lineas:
        if not l.strip():
            if not vacia and limpio:
                limpio.append("")
            vacia = True
        else:
            limpio.append(l)
            vacia = False
    return "\n".join(limpio).strip() + "\n"


def limpiar(ruta):
    ext = ruta.suffix.lower()
    t = ruta.read_text(encoding="utf-8")
    if ext == ".html":
        t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
    elif ext == ".css":
        t = quitar_comentarios_c(t, linea=False)
    elif ext in (".less", ".scss", ".js"):
        t = quitar_comentarios_c(t, linea=True)
    else:
        return
    ruta.write_text(ordenar_lineas(t), encoding="utf-8", newline="\n")


def main():
    if SALIDA.parent.exists():
        shutil.rmtree(SALIDA.parent)
    SALIDA.mkdir(parents=True)
    for item in INCLUIR:
        origen = RAIZ / item
        destino = SALIDA / item
        destino.parent.mkdir(parents=True, exist_ok=True)
        if origen.is_dir():
            shutil.copytree(origen, destino)
        else:
            shutil.copy2(origen, destino)
    for ruta in SALIDA.rglob("*"):
        if ruta.is_file() and ruta.suffix.lower() in (".html", ".css", ".less", ".scss", ".js"):
            limpiar(ruta)
    # package.json mínimo: solo lo necesario para compilar LESS y SASS
    pkg = json.loads((RAIZ / "package.json").read_text(encoding="utf-8"))
    nuevo = {
        "name": "altura-sports-academy",
        "version": "4.0.0",
        "description": pkg["description"],
        "private": True,
        "scripts": {
            "build:less": pkg["scripts"]["build:less"],
            "build:sass": pkg["scripts"]["build:sass"],
            "build": "npm run build:less && npm run build:sass",
        },
        "author": pkg["author"],
        "devDependencies": {k: v for k, v in pkg["devDependencies"].items() if k in ("less", "sass")},
    }
    (SALIDA / "package.json").write_text(json.dumps(nuevo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if ZIP.exists():
        ZIP.unlink()
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for ruta in sorted(SALIDA.rglob("*")):
            if ruta.is_file():
                z.write(ruta, ruta.relative_to(SALIDA.parent).as_posix())
    total = sum(1 for _ in SALIDA.rglob("*") if _.is_file())
    print(f"ZIP: {ZIP.name} | {total} archivos | {ZIP.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
