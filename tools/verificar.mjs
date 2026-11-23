// Verificación rápida del sitio: enlaces internos rotos, estilos en línea y recursos faltantes.
// Uso: node tools/verificar.mjs
import { readFileSync, existsSync, readdirSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const RAIZ = join(dirname(fileURLToPath(import.meta.url)), '..');
const paginas = ['index.html', '404.html', ...readdirSync(join(RAIZ, 'paginas')).filter((f) => f.endsWith('.html')).map((f) => `paginas/${f}`)];
let errores = 0;
for (const p of paginas) {
  const html = readFileSync(join(RAIZ, p), 'utf8');
  if (/\sstyle\s*=/.test(html) || /<style[\s>]/i.test(html)) { console.log(`ESTILO EN LÍNEA: ${p}`); errores++; }
  const ids = new Set([...html.matchAll(/\sid="([^"]+)"/g)].map((m) => m[1]));
  for (const [, url] of html.matchAll(/\s(?:href|src|srcset|poster)="([^"]+)"/g)) {
    if (/^(https?:|mailto:|tel:|data:|\/\/)/.test(url) || p === '404.html') continue;
    const [ruta, ancla] = url.split('#');
    if (!ruta) { if (ancla && ancla !== 'cerrar' && ancla !== 'arriba' && !ids.has(ancla)) { console.log(`ANCLA ROTA: ${p} -> #${ancla}`); errores++; } continue; }
    const destino = resolve(join(RAIZ, dirname(p)), ruta.split('?')[0]);
    if (!existsSync(destino)) { console.log(`ROTO: ${p} -> ${url}`); errores++; }
  }
}
console.log(`\n${paginas.length} páginas revisadas, ${errores} problema(s).`);
process.exitCode = errores ? 1 : 0;
