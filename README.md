# ALTURA Sports Academy

Sitio web frontend del **Trabajo Final 04** del curso *Hojas de Estilo en Cascada Avanzado* (UTP, Arequipa).
Empresa ficticia del rubro **Deportes**: academia de básquet, aeróbicos y natación con tienda de artículos deportivos.

- **Grupo:** 04
- **Integrantes:** Mendoza Colque, Carlos Daniel (U25317351) · Quispe Morales, Fabricio Oscar (U25316441)
- **Plazo de desarrollo:** del 18 al 23 de noviembre de 2026
- **Componentes CSS asignados:** LESS, SASS y Material Design CSS (MDC Web 14)
- **Publicación:** https://fabri78.github.io/altura-sports/
- **Repositorio:** https://github.com/fabri78/altura-sports

## Páginas (17 + 404)

`index.html` y `404.html` en la raíz; el resto en `paginas/`:
nosotros, academias, basquet, aerobicos, natacion, horarios, entrenadores, tienda, producto,
eventos, galeria, blog, articulo, matricula, contacto, reclamos. Además `paginas/marcos.html`
demuestra `<frameset>` (HTML 4.01, fuera de la cuenta porque es obsoleto en HTML5).

## Estructura

```
src/html/        Plantillas: parciales (head, cabecera, pie) y cuerpo de cada página
src/less/        Fuentes LESS  -> assets/css/altura-less.css
src/scss/        Fuentes SASS  -> assets/css/altura-sass.css
assets/css/      base.css (CSS puro) y framework/ (layout, responsive, animaciones)
assets/js/       main.js (interacciones mínimas e inicio de Material Design)
assets/img/      logo, íconos SVG, fotos WebP, ilustraciones de productos
assets/video/    videos MP4/WebM con subtítulos .vtt
assets/audio/    pistas MP3 originales
tools/           ensamblador de páginas, métricas y scripts de multimedia
docs/            plan, métricas, créditos multimedia e informe
```

## Reparto del código de estilos

| Punto | Categoría | Meta | Archivo(s) |
|---|---|---|---|
| g.i | CSS externo | 10 % | `assets/css/base.css` |
| g.ii | LESS | 15 % | `src/less/*.less` |
| g.iii | SASS | 15 % | `src/scss/*.scss` |
| h | Animaciones, transiciones y transformaciones | 20 % | `assets/css/framework/animaciones.css` |
| i | Responsive: media queries y multimedia | 20 % | `assets/css/framework/responsive.css` |
| j | Responsive: Flexbox y Grid | 20 % | `assets/css/framework/layout.css` |

`npm run metricas` imprime el reparto real (líneas útiles, sin comentarios ni líneas vacías).

## Comandos

```bash
npm install          # instala less y sass
npm run build        # compila LESS, SASS y ensambla las 18 páginas
npm run metricas     # reparto del código de estilos
python -m http.server 5173   # servidor local
docker build -t altura . && docker run -p 8080:80 altura   # contenedor con nginx
```

Edite las páginas en `src/html/`; los `.html` de la raíz y de `paginas/` se generan con `npm run build:html`.

## Créditos

Fotos y videos de Wikimedia Commons con licencias libres (lista en la página Galería y en
`docs/creditos-multimedia.json`). Logo, íconos, avatares de entrenadores y audio son originales; las fotos de productos también vienen de Wikimedia Commons.
Proyecto académico: la empresa y sus datos son ficticios.
