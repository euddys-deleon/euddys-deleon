"""Convierte data/contributions.json en una ciudad isométrica de neón animada → city.svg.

Cada día es una baldosa; los días con contribuciones se levantan como edificios.
Con DEMO=1 usa datos sintéticos (solo para previsualizar en local).
"""
import json
import math
import os
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "contributions.json"
OUT = ROOT / "city.svg"

MONO = "ui-monospace,SFMono-Regular,'Cascadia Code',Menlo,Consolas,monospace"
CYAN, MAGENTA, PURPLE, GREEN = "#00f0ff", "#ff2bd6", "#8a2be2", "#39ff14"
TOPS = ["#1b1033", "#2de2e6", "#3d7cff", "#b14aed", "#ff2bd6"]

W = 860
UX, UY = 13.0, 2.4       # vector de una semana (pantalla)
VX, VY = -7.6, 6.6       # vector de un día (pantalla)
MAXH = 125
OX, OY = 95, 175         # esquina de la semana 0 / domingo
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def shade(hex_color: str, f: float) -> str:
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return f"#{int(r * f):02x}{int(g * f):02x}{int(b * f):02x}"


def load() -> dict:
    if os.environ.get("DEMO") == "1":
        random.seed(3)
        today = date.today()
        start = today - timedelta(days=364 + (today.weekday() + 1) % 7)
        days = []
        for i in range((today - start).days + 1):
            c = max(0, int(random.gauss(2, 4))) if random.random() < .55 else 0
            days.append({"date": (start + timedelta(i)).isoformat(), "count": c})
    elif DATA.exists():
        days = json.loads(DATA.read_text())["days"]
    else:
        today = date.today()
        start = today - timedelta(days=364 + (today.weekday() + 1) % 7)
        days = [{"date": (start + timedelta(i)).isoformat(), "count": 0} for i in range((today - start).days + 1)]
    return days


def stats(days: list[dict]) -> dict:
    total = sum(d["count"] for d in days)
    longest = cur = 0
    for d in days:
        cur = cur + 1 if d["count"] else 0
        longest = max(longest, cur)
    rev = [d for d in reversed(days)]
    if rev and not rev[0]["count"]:
        rev = rev[1:]
    current = 0
    for d in rev:
        if not d["count"]:
            break
        current += 1
    best = max(days, key=lambda d: d["count"])
    return {"total": total, "longest": longest, "current": current,
            "active": sum(1 for d in days if d["count"]), "best": best["count"]}


def main() -> None:
    days = load()
    s = stats(days)
    mx = max(1, max(d["count"] for d in days))
    first = date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7

    cells = []
    for i, d in enumerate(days):
        w, dd = divmod(i + offset, 7)
        cells.append((w, dd, d["count"], d["date"]))
    cells.sort(key=lambda c: (c[0] * UY + c[1] * VY, c[0]))  # orden del pintor

    def pt(w, dd, dy=0.0):
        return OX + w * UX + dd * VX, OY + w * UY + dd * VY - dy

    def poly(points):
        return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)

    tiles, blds, months = [], [], []
    seen = set()
    for w, dd, c, ds in cells:
        A, B, C, D = pt(w, dd), pt(w + 1, dd), pt(w + 1, dd + 1), pt(w, dd + 1)
        depth = w + dd * 0.5
        if dd == 0 and ds[5:7] not in seen and w < 52:
            seen.add(ds[5:7])
            mx_, my_ = pt(w, 7)
            months.append(f'<text x="{mx_:.0f}" y="{my_ + 17:.0f}" class="mo">{MESES[int(ds[5:7]) - 1]}</text>')
        if c == 0:
            tiles.append(f'<polygon points="{poly([A, B, C, D])}" class="t" style="animation-delay:{depth * 0.08:.2f}s"/>')
            continue
        lvl = 1 + min(3, int(4 * c / (mx + 1)))
        h = 6 + MAXH * math.sqrt(c / mx)
        col = TOPS[lvl]
        up = lambda p_: (p_[0], p_[1] - h)
        front = poly([D, C, up(C), up(D)])
        side = poly([C, B, up(B), up(C)])
        top = poly([up(A), up(B), up(C), up(D)])
        wins = []
        for k in range(int(h // 8)):
            if random.random() < .55:
                yy = 5 + k * 8
                wins.append(f'<line x1="{D[0] + 3:.1f}" y1="{D[1] - yy:.1f}" x2="{C[0] - 3:.1f}" y2="{C[1] - yy:.1f}" class="w" '
                            f'style="animation-delay:{random.uniform(0, 4):.1f}s"/>')
        blds.append(
            f'<g class="b" style="animation-delay:{depth * 0.03:.2f}s">'
            f'<polygon points="{front}" fill="{shade(col, .5)}"/>'
            f'<polygon points="{side}" fill="{shade(col, .32)}"/>'
            f'{"".join(wins)}'
            f'<polygon points="{top}" fill="{col}"><title>{c} contribuciones · {ds}</title></polygon></g>'
        )

    bottom = int(pt(53, 7)[1] + 30)
    H = int(bottom + 92)
    labels = [("contribuciones", s["total"]), ("racha actual", f'{s["current"]}d'),
              ("racha récord", f'{s["longest"]}d'), ("días activos", s["active"]), ("mejor día", s["best"])]
    colw = W / len(labels)
    footer = "".join(
        f'<text x="{colw * k + colw / 2:.0f}" y="{bottom + 44}" text-anchor="middle" class="v" '
        f'style="animation-delay:{2.2 + k * .15:.2f}s">{v}</text>'
        f'<text x="{colw * k + colw / 2:.0f}" y="{bottom + 64}" text-anchor="middle" class="l">{n}</text>'
        for k, (n, v) in enumerate(labels)
    )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Ciudad de contribuciones: {s['total']} en el último año">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#05010d"/><stop offset=".55" stop-color="#1a0533"/><stop offset="1" stop-color="#05010d"/></linearGradient>
    <linearGradient id="beam" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset=".5" stop-color="{CYAN}" stop-opacity=".22"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></linearGradient>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>
  <style>
    .t{{fill:#140a26;stroke:{PURPLE};stroke-width:.6;stroke-opacity:.55;animation:wave 4.5s ease-in-out infinite}}
    @keyframes wave{{0%,100%{{fill:#140a26}}50%{{fill:#2a1250;stroke-opacity:1}}}}
    .b{{transform-box:fill-box;transform-origin:50% 100%;transform:scaleY(0);animation:rise .9s cubic-bezier(.2,1.4,.4,1) forwards}}
    @keyframes rise{{to{{transform:scaleY(1)}}}}
    .w{{stroke:#fff6a8;stroke-width:1.6;opacity:.15;animation:blink 3.5s steps(2) infinite}}
    @keyframes blink{{50%{{opacity:.95}}}}
    .v{{font:700 22px {MONO};fill:{CYAN};opacity:0;animation:in .6s forwards}}
    .l{{font:11px {MONO};fill:#a99bd6}}
    .mo{{font:10px {MONO};fill:#8f7fc4}}
    @keyframes in{{to{{opacity:1}}}}
    .beam{{animation:sweep 6s linear infinite}}
    @keyframes sweep{{from{{transform:translateX(-260px) skewX(-25deg)}}to{{transform:translateX({W + 60}px) skewX(-25deg)}}}}
  </style>
  <rect width="{W}" height="{H}" rx="14" fill="url(#sky)"/>
  <text x="22" y="34" font-family="{MONO}" font-size="14" fill="{GREEN}">euddys@sirynix<tspan fill="#8b949e">:</tspan><tspan fill="{CYAN}">~</tspan><tspan fill="#8b949e">$</tspan> <tspan fill="#fff">./skyline --ultimo-año</tspan></text>
  <text x="{W - 22}" y="34" text-anchor="end" font-family="{MONO}" font-size="11" fill="#a99bd6">cada edificio = un día de código</text>
  <g>{''.join(tiles)}</g>
  <g>{''.join(months)}</g>
  <g filter="url(#glow)">{''.join(blds)}</g>
  <rect class="beam" x="0" y="50" width="160" height="{bottom - 60}" fill="url(#beam)"/>
  <line x1="40" x2="{W - 40}" y1="{bottom + 16}" y2="{bottom + 16}" stroke="{MAGENTA}" stroke-opacity=".4"/>
  {footer}
  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="none" stroke="{PURPLE}" stroke-opacity=".6"/>
</svg>
"""
    OUT.write_text(svg)
    print(f"→ {OUT} ({s['total']} contribuciones, {len(blds)} edificios)")


if __name__ == "__main__":
    main()
