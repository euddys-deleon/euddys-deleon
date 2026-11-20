"""Retrato ASCII monocromo que se imprime fila por fila (SMIL) y queda fijo. Escribe avi-ascii.svg.

Si existe source-prepped.png (tu foto con fondo blanco) se usa como fuente;
si no, se dibuja un monograma con las iniciales.
"""
import os
from html import escape
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source-prepped.png"
OUT = ROOT / "avi-ascii.svg"
STATIC = os.environ.get("STATIC") == "1"
MONOGRAM = os.environ.get("MONOGRAM", "EDL")

RAMP = " .:-=+*#%@"  # de claro a denso
COLS, ROWS = 44, 24
W = 370
BG, INK = "#0d1117", "#39d353"


def monogram() -> Image.Image:
    """Iniciales en negrita, estiradas para llenar el lienzo (se ven mejor en ASCII)."""
    fpath = next((p for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                              "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf")
                  if Path(p).exists()), None)
    font = ImageFont.truetype(fpath, 200) if fpath else ImageFont.load_default()
    probe = ImageDraw.Draw(Image.new("L", (1, 1)))
    box = probe.textbbox((0, 0), MONOGRAM, font=font)
    text = Image.new("L", (box[2] - box[0], box[3] - box[1]), 255)
    ImageDraw.Draw(text).text((-box[0], -box[1]), MONOGRAM, font=font, fill=0)
    canvas = Image.new("L", (460, 460), 255)  # mismo aspecto que la rejilla final
    tw, th = int(460 * 0.84), int(460 * 0.62)
    canvas.paste(text.resize((tw, th)), ((460 - tw) // 2, (460 - th) // 2))
    return canvas


def to_ascii(img: Image.Image) -> list[str]:
    img = ImageOps.grayscale(img).resize((COLS, ROWS))
    px = img.load()
    lines = []
    for y in range(ROWS):
        row = ""
        for x in range(COLS):
            v = px[x, y] / 255
            row += RAMP[int((1 - v) * (len(RAMP) - 1))]
        lines.append(row)
    return lines


def main() -> None:
    img = Image.open(SRC) if SRC.exists() else monogram()
    lines = to_ascii(img)
    pad = 14
    fs = (W - 2 * pad) / COLS / 0.6
    lh = fs * 1.05
    height = int(ROWS * lh + pad * 2)
    rows = []
    for i, line in enumerate(lines):
        y = pad + (i + 1) * lh - lh * 0.2
        text = escape(line).replace(" ", " ")
        if STATIC:
            rows.append(f'<text x="{pad}" y="{y:.1f}" textLength="{W - 2 * pad}" lengthAdjust="spacingAndGlyphs">{text}</text>')
            continue
        begin = f"{0.15 + i * 0.07:.2f}s"
        clip = f"r{i}"
        rows.append(
            f'<clipPath id="{clip}"><rect x="0" y="{y - lh:.1f}" height="{lh + 2:.1f}" width="0">'
            f'<animate attributeName="width" from="0" to="{W}" begin="{begin}" dur="0.35s" fill="freeze"/>'
            f"</rect></clipPath>"
            f'<text x="{pad}" y="{y:.1f}" textLength="{W - 2 * pad}" lengthAdjust="spacingAndGlyphs" clip-path="url(#{clip})">{text}</text>'
        )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" role="img" aria-label="Retrato ASCII">
  <style>text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:{fs:.2f}px;fill:{INK};white-space:pre}}</style>
  <rect width="100%" height="100%" rx="10" fill="{BG}"/>
  {''.join(rows)}
</svg>
"""
    OUT.write_text(svg)
    print(f"→ {OUT} ({'foto' if SRC.exists() else 'monograma ' + MONOGRAM})")


if __name__ == "__main__":
    main()
