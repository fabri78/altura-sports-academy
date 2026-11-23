# Historial de versiones

Cada versión corresponde a una etiqueta de Git y a una fila del "Historial de versiones" del informe.

## v1.0 · Alcance inicial
- Estructura del proyecto, `package.json`, compilación de LESS y SASS.
- Hojas de estilo: `base.css` (CSS), `altura-less.css` (LESS), `altura-sass.css` (SASS) y las tres hojas que trabajan con Material Design (`layout.css`, `responsive.css`, `animaciones.css`).
- Plantilla común (encabezado con menú, pie de página) y 8 páginas: inicio, nosotros, academias, básquet, aeróbicos, horarios, contacto y 404.

## v2.0 · Ampliación del alcance
- 10 páginas nuevas: natación, entrenadores, tienda, producto, eventos, galería, blog, artículo, matrícula y Libro de Reclamaciones (18 en total con la 404).
- Componentes de Material Design re-tematizados con SASS: campos de texto, casillas, botones de opción, pestañas, tabla de datos y snackbar.
- Multimedia: video con subtítulos, audio original, iframes (YouTube, OpenStreetMap y marco interno) y marquesinas.
- Ilustraciones SVG propias de los productos y selector de color hecho solo con CSS.
- Script `npm run metricas` y reparto del código ajustado a los porcentajes de los lineamientos.

## v3.0 · Incremento de resultados
- Hojas `layout.css`, `responsive.css` y `animaciones.css` completas: subgrid, consultas de contenedor, animaciones ligadas al scroll, View Transitions, tarjetas 3D y preferencias del sistema.
- Reparto del código ajustado: todas las categorías a menos de 1,5 puntos de su meta.
- `paginas/marcos.html` (frameset HTML 4.01) y `paginas/horario-semanal.html` para el iframe interno.
- Videos generados a partir de las fotos del proyecto (MP4 y WebM con subtítulos).
- Verificador de enlaces (`tools/verificar.mjs`), README, Dockerfile y flujo de GitHub Pages.
- Informe en la plantilla del docente con diagramas, capturas y tablas (`docs/informe`).
