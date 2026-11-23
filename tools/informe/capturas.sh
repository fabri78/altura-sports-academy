#!/usr/bin/env bash
# Toma capturas de todas las páginas (escritorio y móvil) con Chrome sin interfaz.
# Requiere el servidor local en http://127.0.0.1:5173 (python -m http.server 5173)
CHROME="/c/Program Files/Google/Chrome/Application/chrome.exe"
OUT="docs/capturas"
mkdir -p "$OUT"
BASE="http://127.0.0.1:5173"
captura () { # nombre url ancho alto
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --mute-audio \
    --window-size="$3,$4" --virtual-time-budget=6000 --screenshot="$(cygpath -w "$PWD/$OUT/$1.png")" "$2" >/dev/null 2>&1
}
captura inicio "$BASE/index.html" 1440 900
for p in nosotros academias basquet aerobicos natacion horarios entrenadores tienda producto eventos galeria blog articulo matricula contacto reclamos; do
  captura "$p" "$BASE/paginas/$p.html" 1440 900
done
captura e404 "$BASE/404.html" 1440 900
for p in tienda matricula basquet; do captura "movil-$p" "$BASE/paginas/$p.html" 390 844; done
captura movil-inicio "$BASE/index.html" 390 844
ls "$OUT" | wc -l
