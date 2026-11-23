// Ensambla las páginas HTML finales a partir de las plantillas de src/html.
// Cada página fuente (src/html/paginas/*.html) empieza con un comentario JSON de metadatos
// y contiene solo su <main>. Este script le agrega <head>, encabezado y pie de página comunes,
// para que las 18 páginas compartan exactamente la misma estructura (punto c de los lineamientos).
//
// Uso: npm run build:html
// Importante: edite los archivos de src/html, no los .html generados (se sobrescriben).

import { readFileSync, writeFileSync, readdirSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const RAIZ = join(dirname(fileURLToPath(import.meta.url)), '..');
const SRC = join(RAIZ, 'src', 'html');
const REPO = '/altura-sports/'; // ruta base en GitHub Pages (solo para 404.html)

const leer = (ruta) => readFileSync(join(SRC, ruta), 'utf8');
const cabecera = leer('parciales/cabecera.html');
const pie = leer('parciales/pie.html');
const head = leer('parciales/head.html');

const DESTINO = { index: '', '404': '' }; // el resto va a /paginas

// Lista de créditos de fotos y videos con licencia libre (Wikimedia Commons)
function listaCreditos() {
  const ruta = join(RAIZ, 'docs', 'creditos-multimedia.json');
  const vistos = new Set();
  const items = JSON.parse(readFileSync(ruta, 'utf8')).filter((c) => !vistos.has(c.archivo) && vistos.add(c.archivo));
  const esc = (t) => String(t || 'Autor desconocido').replace(/&/g, '&amp;').replace(/</g, '&lt;').slice(0, 90);
  return items
    .map((c) => `<li><code>${c.archivo.split('/').pop()}</code> · ${esc(c.autor)} · ${esc(c.licencia)} · <a href="${c.pagina}" target="_blank" rel="noopener noreferrer">Wikimedia Commons</a></li>`)
    .join('\n            ');
}

let total = 0;
for (const archivo of readdirSync(join(SRC, 'paginas')).filter((f) => f.endsWith('.html'))) {
  const nombre = archivo.replace('.html', '');
  const fuente = leer(join('paginas', archivo));
  const m = fuente.match(/^<!--\s*(\{[\s\S]*?\})\s*-->\s*/);
  if (!m) throw new Error(`Falta el bloque de metadatos en ${archivo}`);
  const meta = JSON.parse(m[1]);
  // {{incluir:nombre}} inserta src/html/parciales/nombre.html (bloques compartidos entre páginas)
  const cuerpo = fuente.slice(m[0].length).replace(/\{\{incluir:([\w-]+)\}\}/g, (_, n) => leer(`parciales/${n}.html`));

  const enRaiz = nombre in DESTINO;
  const R = nombre === '404' ? REPO : enRaiz ? '' : '../';
  const P = nombre === '404' ? `${REPO}paginas/` : enRaiz ? 'paginas/' : '';

  let html = `<!DOCTYPE html>
<html lang="es-PE" class="no-js">
${head}
<body class="${meta.clase || 'tema-oscuro'}" id="arriba">
${meta.simple ? '' : cabecera}
${cuerpo.trim()}
${meta.simple ? '' : pie}
</body>
</html>
`;
  html = html
    .replaceAll('{{titulo}}', meta.titulo)
    .replaceAll('{{descripcion}}', meta.descripcion)
    .replaceAll('{{palabras}}', meta.palabras || 'academia deportiva, Arequipa, básquet, aeróbicos, natación, artículos deportivos')
    .replaceAll('{{archivo}}', enRaiz ? `${nombre}.html` : `paginas/${nombre}.html`)
    .replaceAll('{{creditos}}', html.includes('{{creditos}}') ? listaCreditos() : '')
    .replaceAll('{{R}}', R)
    .replaceAll('{{P}}', P);

  // Marca la opción activa del menú (aria-current) según "activo" en los metadatos.
  if (meta.activo) {
    html = html.replace(new RegExp(`(<a[^>]*data-menu="${meta.activo}")`), '$1 aria-current="page"');
  }

  const salida = enRaiz ? join(RAIZ, `${nombre}.html`) : join(RAIZ, 'paginas', `${nombre}.html`);
  mkdirSync(dirname(salida), { recursive: true });
  writeFileSync(salida, html, 'utf8');
  total += 1;
}
console.log(`Páginas ensambladas: ${total}`);
