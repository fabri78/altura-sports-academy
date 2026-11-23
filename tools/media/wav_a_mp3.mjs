// Convierte los WAV sintetizados a MP3 (128 kbps) con lamejs, sin depender de ffmpeg.
import { readFileSync, writeFileSync, readdirSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

const aqui = dirname(fileURLToPath(import.meta.url));
// El paquete CommonJS de lamejs 1.2.1 tiene un bug (MPEGMode); se usa su build completo.
const ctx = {};
vm.createContext(ctx);
vm.runInContext(readFileSync(join(aqui, '..', '..', 'node_modules', 'lamejs', 'lame.all.js'), 'utf8') + ';this.lamejs=lamejs;', ctx);
const lamejs = ctx.lamejs;
const origen = join(aqui, 'tmp');
const destino = join(aqui, '..', '..', 'assets', 'audio');
mkdirSync(destino, { recursive: true });

for (const archivo of readdirSync(origen).filter((f) => f.endsWith('.wav'))) {
  const buf = readFileSync(join(origen, archivo));
  const wav = lamejs.WavHeader.readHeader(new DataView(buf.buffer, buf.byteOffset, buf.byteLength));
  const muestras = new Int16Array(buf.buffer, buf.byteOffset + wav.dataOffset, wav.dataLen / 2);
  const enc = new lamejs.Mp3Encoder(wav.channels, wav.sampleRate, 128);
  const partes = [];
  for (let i = 0; i < muestras.length; i += 1152) {
    const mp3 = enc.encodeBuffer(muestras.subarray(i, i + 1152));
    if (mp3.length) partes.push(Buffer.from(mp3));
  }
  partes.push(Buffer.from(enc.flush()));
  const salida = join(destino, archivo.replace('.wav', '.mp3'));
  writeFileSync(salida, Buffer.concat(partes));
  console.log('MP3', salida);
}
