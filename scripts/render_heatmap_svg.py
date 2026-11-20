"""Renderiza data/contributions.json como un mapa de calor SVG animado (keyframes CSS).

Escribe contrib-heatmap.svg. Con STATIC=1 genera una versión sin animación.
"""
import json
import os
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"
STATIC = os.environ.get("STATIC") == "1"

BG = "#0d1117"
FG = "#c9d1d9"
MUTED = "#8b949e"
ACCENT = "#39d353"
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
MONTHS_ES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
DAYS_ES = {1: "lun", 3: "mié", 5: "vie"}

CELL, GAP = 12, 3
LEFT, TOP = 36, 30
WIDTH = 860


def load() -> dict:
    if DATA.exists():
        return json.loads(DATA.read_text())
    # Marcador de posición hasta que corra el workflow
    today = date.today()
    start = today - timedelta(days=364 + (today.weekday() + 1) % 7)
    days = [{"date": (start + timedelta(i)).isoformat(), "level": 0, "count": 0}
            for i in range((today - start).days + 1)]
    return {"days": days, "stats": {"total": 0, "longest_streak": 0, "current_streak": 0,
                                    "active_days": 0, "best_day": {"date": "-", "count": 0}}}


def main() -> None:
    data = load()
    days = data["days"]
    s = data["stats"]
    first = date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7  # domingo = fila 0

    rects, labels = [], []
    last_month = None
    for i, d in enumerate(days):
        idx = i + offset
        col, row = divmod(idx, 7)
        x = LEFT + col * (CELL + GAP)
        y = TOP + row * (CELL + GAP)
        dt = date.fromisoformat(d["date"])
        if row == 0 or i == 0:
            if dt.month != last_month and col < 52:
                labels.append(f'<text x="{x}" y="{TOP - 10}" class="m">{MONTHS_ES[dt.month - 1]}</text>')
                last_month = dt.month
        delay = f"{col * 0.025:.3f}s"
        fill = PALETTE[min(d["level"], 4)]
        tip = f'{d["count"]} contribuciones el {d["date"]}'
        rects.append(
            f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" fill="{fill}" '
            f'class="c" style="animation-delay:{delay}"><title>{tip}</title></rect>'
        )

    for row, name in DAYS_ES.items():
        labels.append(f'<text x="2" y="{TOP + row * (CELL + GAP) + 10}" class="m">{name}</text>')

    grid_bottom = TOP + 7 * (CELL + GAP)
    # Leyenda
    lx = WIDTH - 5 * (CELL + GAP) - 70
    legend = [f'<text x="{lx - 40}" y="{grid_bottom + 18}" class="m">menos</text>']
    for k, color in enumerate(PALETTE):
        legend.append(f'<rect x="{lx + k * (CELL + GAP)}" y="{grid_bottom + 8}" width="{CELL}" '
                      f'height="{CELL}" rx="2.5" fill="{color}"/>')
    legend.append(f'<text x="{lx + 5 * (CELL + GAP) + 4}" y="{grid_bottom + 18}" class="m">más</text>')

    best = s["best_day"]
    footer_y = grid_bottom + 52
    stats = [
        ("contribuciones", s["total"]),
        ("racha actual", f'{s["current_streak"]} d'),
        ("racha más larga", f'{s["longest_streak"]} d'),
        ("días activos", s["active_days"]),
        ("mejor día", f'{best["count"]} · {best["date"]}'),
    ]
    col_w = WIDTH / len(stats)
    footer = []
    for k, (label, value) in enumerate(stats):
        cx = col_w * k + col_w / 2
        footer.append(f'<text x="{cx}" y="{footer_y}" class="v" text-anchor="middle">{value}</text>')
        footer.append(f'<text x="{cx}" y="{footer_y + 18}" class="m" text-anchor="middle">{label}</text>')

    height = footer_y + 32
    anim = "" if STATIC else """
    .c{opacity:0;animation:pop .35s ease-out forwards}
    @keyframes pop{0%{opacity:0;transform:scale(.4)}100%{opacity:1;transform:scale(1)}}
    .f{opacity:0;animation:fade .8s ease-out 1.6s forwards}
    @keyframes fade{to{opacity:1}}"""
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" role="img" aria-label="Mapa de contribuciones de GitHub">
  <style>
    text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}
    .m{{fill:{MUTED};font-size:10px}}
    .v{{fill:{ACCENT};font-size:15px;font-weight:700}}
    .c{{transform-box:fill-box;transform-origin:center}}{anim}
  </style>
  <rect width="100%" height="100%" rx="10" fill="{BG}"/>
  {''.join(labels)}
  {''.join(rects)}
  <g class="f">{''.join(legend)}{''.join(footer)}</g>
</svg>
"""
    OUT.write_text(svg)
    print(f"→ {OUT} ({len(days)} días)")


if __name__ == "__main__":
    main()
