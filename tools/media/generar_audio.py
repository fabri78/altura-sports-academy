"""Sintetiza las pistas de audio originales del sitio (sin derechos de terceros).

Uso:  python -I tools/media/generar_audio.py  ->  tools/media/tmp/*.wav
Luego node tools/media/wav_a_mp3.mjs convierte a MP3 en assets/audio/.
"""
import math
import random
import struct
import wave
from pathlib import Path

SR = 44100
SALIDA = Path(__file__).resolve().parent / "tmp"


def kick(t):
    if t > 0.35:
        return 0.0
    f = 50 + 110 * math.exp(-t * 28)
    return math.sin(2 * math.pi * f * t) * math.exp(-t * 9)


def hat(t, rnd):
    if t > 0.06:
        return 0.0
    return (rnd.random() * 2 - 1) * math.exp(-t * 70) * 0.35


def clap(t, rnd):
    if t > 0.18:
        return 0.0
    return (rnd.random() * 2 - 1) * math.exp(-t * 22) * 0.45


def saw(f, t):
    x = (f * t) % 1.0
    return 2 * x - 1


def pista(segundos, bpm, notas_bajo, acordes, brillo=0.18, semilla=7):
    rnd = random.Random(semilla)
    n = int(segundos * SR)
    beat = 60 / bpm
    paso = beat / 4
    datos = []
    filtro = 0.0
    for i in range(n):
        t = i / SR
        b = t / beat
        compas = int(b // 4)
        tb = t % beat
        ts = t % paso
        idx_paso = int(t // paso) % 16
        s = 0.9 * kick(tb)
        if idx_paso % 2 == 1:
            s += hat(ts, rnd)
        if int(b) % 2 == 1:
            s += clap(tb, rnd)
        # bajo en corcheas
        nota = notas_bajo[compas % len(notas_bajo)]
        f_bajo = 440 * 2 ** ((nota - 69) / 12)
        env_b = math.exp(-((t % (beat / 2)) * 6))
        crudo = saw(f_bajo, t) * env_b * 0.32
        filtro += 0.12 * (crudo - filtro)
        s += filtro
        # acordes tipo pad
        acorde = acordes[compas % len(acordes)]
        pad = sum(math.sin(2 * math.pi * 440 * 2 ** ((m - 69) / 12) * t) for m in acorde) / len(acorde)
        s += pad * brillo * (0.6 + 0.4 * math.sin(2 * math.pi * t / (beat * 8)))
        # fundido de entrada y salida
        fade = min(1.0, t / 1.5, (segundos - t) / 2.0)
        datos.append(max(-1.0, min(1.0, s * 0.55 * fade)))
    return datos


def guardar(nombre, datos):
    SALIDA.mkdir(exist_ok=True)
    with wave.open(str(SALIDA / nombre), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h", int(x * 32767)) for x in datos))
    print("WAV", nombre, len(datos) / SR, "s")


if __name__ == "__main__":
    # 128 BPM: ritmo clasico de clase de aerobicos / step
    guardar("ritmo-aerobicos.wav", pista(42, 128, [45, 45, 41, 43], [[57, 60, 64], [57, 60, 64], [53, 57, 60], [55, 59, 62]]))
    # Jingle corto de marca para el podcast y la galeria
    guardar("jingle-altura.wav", pista(14, 100, [40, 43, 45, 47], [[52, 56, 59], [55, 59, 62], [57, 61, 64], [59, 63, 66]], brillo=0.28, semilla=3))
