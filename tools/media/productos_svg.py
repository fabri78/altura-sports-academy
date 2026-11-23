"""Genera las ilustraciones vectoriales (SVG) de los productos de la tienda.

Son dibujos originales del proyecto, así que no requieren créditos de terceros.
Uso: python -I tools/media/productos_svg.py  ->  assets/img/tienda/*.svg
"""
from pathlib import Path

DESTINO = Path(__file__).resolve().parents[2] / "assets" / "img" / "tienda"

ACABADOS = {
    "brasa": ("#ff8a50", "#ff6a2b", "#c8400f"),
    "glaciar": ("#e3f0fa", "#b9d3e6", "#7f9fb8"),
    "grafito": ("#5a5a5e", "#3a3a3c", "#1c1c1e"),
    "borgona": ("#a3283d", "#6e1626", "#3f0a14"),
}


def svg(cuerpo, defs="", vb="0 0 400 300", titulo="Producto ALTURA"):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label="{titulo}">
  <defs>
    <radialGradient id="sombra" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#000" stop-opacity=".28"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
    {defs}
  </defs>
{cuerpo}
</svg>
"""


def zapatilla(nombre, claro, medio, oscuro):
    defs = f"""<linearGradient id="u" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{claro}"/><stop offset=".55" stop-color="{medio}"/><stop offset="1" stop-color="{oscuro}"/></linearGradient>
    <linearGradient id="s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#d8d8de"/></linearGradient>"""
    cuerpo = f"""  <ellipse cx="205" cy="248" rx="160" ry="14" fill="url(#sombra)"/>
  <!-- Suela -->
  <path d="M52 208 C52 198 62 196 72 197 L330 192 C352 191 366 200 364 214 C362 228 350 234 332 235 L82 240 C62 240 50 226 52 208 Z" fill="url(#s)"/>
  <path d="M60 224 L360 216" stroke="#bfc0c6" stroke-width="3"/>
  <!-- Capellada -->
  <path d="M66 200 C66 160 92 128 132 120 L196 102 C222 94 244 104 256 124 C276 156 312 166 338 176 C356 183 358 196 344 198 L80 206 C70 206 66 204 66 200 Z" fill="url(#u)"/>
  <!-- Talón reforzado -->
  <path d="M66 200 C64 168 78 140 104 128 L112 196 Z" fill="{oscuro}" opacity=".55"/>
  <!-- Franja con la cumbre de la marca -->
  <path d="M128 196 L176 146 L198 170 L214 154 L262 194 Z" fill="#ffffff" opacity=".9"/>
  <!-- Cordones -->
  <g stroke="#ffffff" stroke-width="4" stroke-linecap="round" opacity=".95">
    <path d="M206 112 L226 126"/><path d="M220 120 L240 136"/><path d="M234 130 L254 146"/><path d="M248 142 L266 156"/>
  </g>
  <path d="M190 104 C200 96 214 94 222 100" stroke="{oscuro}" stroke-width="6" fill="none" stroke-linecap="round"/>
  <circle cx="96" cy="176" r="5" fill="#ffffff" opacity=".8"/>"""
    return svg(cuerpo, defs, titulo=f"Zapatilla Cumbre Pro color {nombre}")


def pelota():
    defs = """<radialGradient id="b" cx="38%" cy="32%" r="70%"><stop offset="0" stop-color="#ffa36b"/><stop offset=".6" stop-color="#ff6a2b"/><stop offset="1" stop-color="#a2370c"/></radialGradient>"""
    cuerpo = """  <ellipse cx="200" cy="262" rx="100" ry="12" fill="url(#sombra)"/>
  <circle cx="200" cy="145" r="108" fill="url(#b)"/>
  <g fill="none" stroke="#2b1208" stroke-width="5" stroke-linecap="round">
    <path d="M92 145 H308"/>
    <path d="M200 37 V253"/>
    <path d="M128 64 C170 110 170 180 128 226"/>
    <path d="M272 64 C230 110 230 180 272 226"/>
  </g>
  <text x="200" y="128" text-anchor="middle" font-family="Arial Black, Arial, sans-serif" font-size="15" letter-spacing="3" fill="#2b1208" opacity=".6">ALTURA</text>"""
    return svg(cuerpo, defs, titulo="Pelota de básquet ALTURA Game Ball")


def camiseta():
    defs = """<linearGradient id="c" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2a2a2d"/><stop offset="1" stop-color="#0d0d0e"/></linearGradient>
    <linearGradient id="g" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#8c1d2f"/><stop offset=".55" stop-color="#ff2e63"/><stop offset="1" stop-color="#ff6a2b"/></linearGradient>"""
    cuerpo = """  <ellipse cx="200" cy="270" rx="120" ry="10" fill="url(#sombra)"/>
  <path d="M150 34 C165 50 235 50 250 34 L318 62 L346 120 L304 136 L292 112 L292 258 L108 258 L108 112 L96 136 L54 120 L82 62 Z" fill="url(#c)"/>
  <path d="M150 34 C165 56 235 56 250 34" fill="none" stroke="#ff6a2b" stroke-width="5"/>
  <path d="M108 112 L96 136 M292 112 L304 136" stroke="#ff6a2b" stroke-width="4"/>
  <path d="M166 170 L192 120 L204 140 L212 128 L236 170 Z" fill="url(#g)"/>
  <text x="200" y="214" text-anchor="middle" font-family="Arial Black, Arial, sans-serif" font-size="42" fill="#f5f5f7">23</text>"""
    return svg(cuerpo, defs, titulo="Camiseta Dry ALTURA")


def botella():
    defs = """<linearGradient id="m" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#8a8a90"/><stop offset=".3" stop-color="#f5f5f7"/><stop offset=".55" stop-color="#b8b8bf"/><stop offset="1" stop-color="#6e6e73"/></linearGradient>
    <linearGradient id="t" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#8c1d2f"/><stop offset=".5" stop-color="#ff2e63"/><stop offset="1" stop-color="#8c1d2f"/></linearGradient>"""
    cuerpo = """  <ellipse cx="200" cy="276" rx="70" ry="9" fill="url(#sombra)"/>
  <rect x="172" y="22" width="56" height="38" rx="10" fill="url(#t)"/>
  <path d="M170 60 H230 C236 78 250 84 250 104 V258 C250 268 242 274 232 274 H168 C158 274 150 268 150 258 V104 C150 84 164 78 170 60 Z" fill="url(#m)"/>
  <rect x="150" y="150" width="100" height="58" fill="#1d1d1f"/>
  <path d="M182 196 L198 168 L206 180 L212 172 L226 196 Z" fill="#ff6a2b"/>
  <text x="200" y="232" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" letter-spacing="2" fill="#3a3a3c">750 ML</text>"""
    return svg(cuerpo, defs, titulo="Botella térmica ALTURA 750 ml")


def mancuernas():
    defs = """<linearGradient id="h" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4a4a4e"/><stop offset="1" stop-color="#111113"/></linearGradient>
    <linearGradient id="k" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f5f5f7"/><stop offset="1" stop-color="#8e8e93"/></linearGradient>"""
    par = """<g transform="translate({x},{y})">
    <rect x="58" y="36" width="104" height="18" rx="6" fill="url(#k)"/>
    <polygon points="0,45 14,10 46,10 60,45 46,80 14,80" fill="url(#h)"/>
    <polygon points="160,45 174,10 206,10 220,45 206,80 174,80" fill="url(#h)"/>
    <text x="30" y="50" text-anchor="middle" font-family="Arial Black, Arial" font-size="13" fill="#ff6a2b">5</text>
  </g>"""
    cuerpo = '  <ellipse cx="200" cy="262" rx="150" ry="12" fill="url(#sombra)"/>\n  ' + par.format(x=60, y=80) + "\n  " + par.format(x=100, y=160)
    return svg(cuerpo, defs, titulo="Mancuernas hexagonales de 5 kg")


def lentes():
    defs = """<linearGradient id="l" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7cc4ff"/><stop offset=".5" stop-color="#2997ff"/><stop offset="1" stop-color="#0a3d7a"/></linearGradient>"""
    cuerpo = """  <ellipse cx="200" cy="246" rx="140" ry="12" fill="url(#sombra)"/>
  <path d="M40 150 C40 120 80 110 110 120 M360 150 C360 120 320 110 290 120" stroke="#1d1d1f" stroke-width="10" fill="none" stroke-linecap="round"/>
  <ellipse cx="148" cy="150" rx="60" ry="44" fill="#1d1d1f"/>
  <ellipse cx="252" cy="150" rx="60" ry="44" fill="#1d1d1f"/>
  <ellipse cx="148" cy="150" rx="50" ry="35" fill="url(#l)"/>
  <ellipse cx="252" cy="150" rx="50" ry="35" fill="url(#l)"/>
  <path d="M200 148 C196 136 204 136 200 148" stroke="#1d1d1f" stroke-width="12"/>
  <path d="M120 132 C130 122 146 120 158 124" stroke="#fff" stroke-width="5" fill="none" opacity=".7" stroke-linecap="round"/>
  <path d="M224 132 C234 122 250 120 262 124" stroke="#fff" stroke-width="5" fill="none" opacity=".7" stroke-linecap="round"/>"""
    return svg(cuerpo, defs, titulo="Lentes de natación Hidro")


def colchoneta():
    defs = """<linearGradient id="p" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ff5c86"/><stop offset="1" stop-color="#b3123f"/></linearGradient>"""
    cuerpo = """  <ellipse cx="200" cy="246" rx="160" ry="12" fill="url(#sombra)"/>
  <rect x="70" y="120" width="250" height="110" rx="12" fill="url(#p)"/>
  <circle cx="300" cy="175" r="58" fill="#ff2e63"/>
  <g fill="none" stroke="#8c1d2f" stroke-width="5">
    <circle cx="300" cy="175" r="44"/><circle cx="300" cy="175" r="30"/><circle cx="300" cy="175" r="16"/>
  </g>
  <rect x="110" y="114" width="20" height="122" rx="4" fill="#1d1d1f"/>
  <rect x="210" y="114" width="20" height="122" rx="4" fill="#1d1d1f"/>"""
    return svg(cuerpo, defs, titulo="Colchoneta Flow de 6 mm")


def cuerda():
    cuerpo = """  <ellipse cx="200" cy="262" rx="150" ry="10" fill="url(#sombra)"/>
  <path d="M96 90 C96 260 304 260 304 90" stroke="#2997ff" stroke-width="5" fill="none"/>
  <rect x="80" y="26" width="32" height="76" rx="16" fill="#1d1d1f"/>
  <rect x="288" y="26" width="32" height="76" rx="16" fill="#1d1d1f"/>
  <rect x="80" y="70" width="32" height="10" fill="#ff6a2b"/>
  <rect x="288" y="70" width="32" height="10" fill="#ff6a2b"/>"""
    return svg(cuerpo, titulo="Cuerda de velocidad con rodamientos")


def mochila():
    defs = """<linearGradient id="k" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#4a4a4e"/><stop offset="1" stop-color="#151516"/></linearGradient>"""
    cuerpo = """  <ellipse cx="200" cy="272" rx="110" ry="10" fill="url(#sombra)"/>
  <path d="M170 40 C170 22 230 22 230 40" stroke="#1d1d1f" stroke-width="10" fill="none"/>
  <rect x="112" y="44" width="176" height="224" rx="44" fill="url(#k)"/>
  <rect x="140" y="150" width="120" height="92" rx="22" fill="#2a2a2d" stroke="#ff6a2b" stroke-width="3"/>
  <path d="M140 162 H260" stroke="#86868b" stroke-width="3" stroke-dasharray="6 5"/>
  <path d="M182 128 L198 100 L206 112 L212 104 L226 128 Z" fill="#ff6a2b"/>"""
    return svg(cuerpo, defs, titulo="Mochila Cumbre de 25 litros")


def main():
    DESTINO.mkdir(parents=True, exist_ok=True)
    archivos = {f"zapatilla-{n}.svg": zapatilla(n, *c) for n, c in ACABADOS.items()}
    archivos.update({
        "pelota.svg": pelota(), "camiseta.svg": camiseta(), "botella.svg": botella(),
        "mancuernas.svg": mancuernas(), "lentes.svg": lentes(), "colchoneta.svg": colchoneta(),
        "cuerda.svg": cuerda(), "mochila.svg": mochila(),
    })
    for nombre, contenido in archivos.items():
        (DESTINO / nombre).write_text(contenido, encoding="utf-8")
    print("SVG generados:", len(archivos))


if __name__ == "__main__":
    main()
