// Mide el reparto del código de estilos propio por categoría de los lineamientos.
// Cuenta líneas útiles: sin líneas vacías ni comentarios (/* */ y //).
// Uso: npm run metricas   ->  imprime la tabla y guarda docs/metricas.json
import { readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { join, dirname, relative } from 'node:path';
import { fileURLToPath } from 'node:url';

const RAIZ = join(dirname(fileURLToPath(import.meta.url)), '..');

const CATEGORIAS = [
  { punto: 'g.i', nombre: 'CSS externo', meta: 10, archivos: ['assets/css/base.css'] },
  { punto: 'g.ii', nombre: 'LESS', meta: 15, carpeta: 'src/less', ext: '.less' },
  { punto: 'g.iii', nombre: 'SASS', meta: 15, carpeta: 'src/scss', ext: '.scss' },
  { punto: 'h', nombre: 'Animaciones, transiciones y transformaciones', meta: 20, archivos: ['assets/css/framework/animaciones.css'] },
  { punto: 'i', nombre: 'Responsive: media queries y multimedia', meta: 20, archivos: ['assets/css/framework/responsive.css'] },
  { punto: 'j', nombre: 'Responsive: Flexbox y Grid Layout', meta: 20, archivos: ['assets/css/framework/layout.css'] },
];

function lineasUtiles(texto) {
  const sinBloques = texto.replace(/\/\*[\s\S]*?\*\//g, '');
  return sinBloques
    .split(/\r?\n/)
    .map((l) => l.replace(/(^|\s)\/\/.*$/, '').trim())
    .filter((l) => l.length > 0).length;
}

const filas = CATEGORIAS.map((c) => {
  const archivos = c.archivos
    ? c.archivos.map((a) => join(RAIZ, a))
    : readdirSync(join(RAIZ, c.carpeta)).filter((f) => f.endsWith(c.ext)).map((f) => join(RAIZ, c.carpeta, f));
  const lineas = archivos.reduce((s, a) => s + lineasUtiles(readFileSync(a, 'utf8')), 0);
  return { ...c, archivos: archivos.map((a) => relative(RAIZ, a).replaceAll('\\', '/')), lineas };
});

const total = filas.reduce((s, f) => s + f.lineas, 0);
console.log('\nReparto del código de estilos propio (líneas útiles)\n');
console.log('Punto  Categoría                                      Líneas    Real   Meta   Dif.');
console.log('-----  ---------------------------------------------  ------  ------  -----  -----');
for (const f of filas) {
  f.porcentaje = +(f.lineas * 100 / total).toFixed(1);
  f.diferencia = +(f.porcentaje - f.meta).toFixed(1);
  const ok = Math.abs(f.diferencia) <= 2 ? 'OK' : '!!';
  console.log(
    `${f.punto.padEnd(5)}  ${f.nombre.padEnd(45)}  ${String(f.lineas).padStart(6)}  ${f.porcentaje.toFixed(1).padStart(5)}%  ${String(f.meta).padStart(4)}%  ${(f.diferencia > 0 ? '+' : '') + f.diferencia.toFixed(1)} ${ok}`
  );
}
console.log(`\nTotal: ${total} líneas útiles de estilos propios (el CSS del framework por CDN no se cuenta).\n`);
writeFileSync(join(RAIZ, 'docs', 'metricas.json'), JSON.stringify({ fecha: new Date().toISOString(), total, filas }, null, 2));
