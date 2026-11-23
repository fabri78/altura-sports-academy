"""Genera los videos del sitio a partir de las fotos del proyecto (efecto Ken Burns).

Son clips originales: cada foto se acerca y se desplaza lentamente y se funde con la siguiente.
Requiere: python -m pip install imageio-ffmpeg
Uso: python -I tools/media/generar_videos.py  ->  assets/video/*.mp4, *.webm y pósteres
"""
import subprocess
from pathlib import Path

import imageio_ffmpeg
from PIL import Image

RAIZ = Path(__file__).resolve().parents[2]
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
VIDEO = RAIZ / "assets" / "video"
FPS = 30

CLIPS = {
    "basquet": ["assets/img/galeria/g-basquet-2.webp", "assets/img/academias/basquet-tiro.webp", "assets/img/galeria/g-basquet-1.webp"],
    "piscina": ["assets/img/academias/natacion-carriles.webp", "assets/img/galeria/g-natacion.webp", "assets/img/academias/natacion-nado.webp"],
}
SEG = 4  # segundos por foto


def preparar(origen, destino):
    """Recorta a 16:9 y escala a 1920x1080 (zoompan necesita margen para acercar)."""
    img = Image.open(RAIZ / origen).convert("RGB")
    w, h = img.size
    objetivo = 16 / 9
    if w / h > objetivo:
        nw = int(h * objetivo)
        img = img.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = int(w / objetivo)
        img = img.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    img.resize((1920, 1080), Image.LANCZOS).save(destino, quality=92)


def main():
    tmp = RAIZ / "tools" / "media" / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    for nombre, fotos in CLIPS.items():
        entradas, filtros = [], []
        for i, foto in enumerate(fotos):
            jpg = tmp / f"{nombre}-{i}.jpg"
            preparar(foto, jpg)
            entradas += ["-i", str(jpg)]
            # zoom lento del 100 % al 112 %, desplazándose hacia la derecha o la izquierda
            x = "iw/2-(iw/zoom/2)+on*0.6" if i % 2 == 0 else "iw/2-(iw/zoom/2)-on*0.6"
            filtros.append(
                f"[{i}:v]zoompan=z='min(zoom+0.0009,1.12)':x='{x}':y='ih/2-(ih/zoom/2)':d={SEG * FPS}:s=1280x720:fps={FPS},"
                f"setsar=1,fade=t=in:st=0:d=0.6,fade=t=out:st={SEG - 0.6}:d=0.6[v{i}]"
            )
        # se unen los clips (cada uno ya tiene fundido de entrada y salida)
        filtros.append("".join(f"[v{i}]" for i in range(len(fotos))) + f"concat=n={len(fotos)}:v=1:a=0,format=yuv420p[out]")
        filtro = ";".join(filtros)
        comun = [FFMPEG, "-y", "-loglevel", "error", *entradas, "-filter_complex", filtro, "-map", "[out]"]
        subprocess.run([*comun, "-c:v", "libx264", "-preset", "slow", "-crf", "26", "-movflags", "+faststart", str(VIDEO / f"{nombre}.mp4")], check=True)
        subprocess.run([*comun, "-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "38", "-row-mt", "1", str(VIDEO / f"{nombre}.webm")], check=True)
        Image.open(tmp / f"{nombre}-0.jpg").resize((1280, 720)).save(VIDEO / f"{nombre}-poster.webp", "WEBP", quality=78)
        print("Video:", nombre, round((VIDEO / f"{nombre}.mp4").stat().st_size / 1024), "KB mp4,", round((VIDEO / f"{nombre}.webm").stat().st_size / 1024), "KB webm")


if __name__ == "__main__":
    main()
