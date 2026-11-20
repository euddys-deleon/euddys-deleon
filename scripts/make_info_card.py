"""Tarjeta estilo neofetch que aparece línea por línea. Escribe info-card.svg.

Edita el bloque CARD para cambiar el contenido. STATIC=1 genera una versión sin animación.
"""
import os
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "info-card.svg"
STATIC = os.environ.get("STATIC") == "1"

USER = "euddys"
HOST = "sirynix"
CARD = [
    ("Nombre", "Euddys Daviel De León Feliz"),
    ("Rol", "CTO y cofundador · SIRYNIX"),
    ("Base", "República Dominicana"),
    ("Web", "sirynix.com"),
    None,
    ("Ahora", "CrediFlow · plataforma de préstamos"),
    ("", "Inventario De León · POS"),
    ("", "Alert Hub · alertas de ciberseguridad"),
    None,
    ("Stack", "Next.js · React · TypeScript"),
    ("", "Supabase · PostgreSQL · Tailwind"),
    ("", "Vercel · Capacitor (Android)"),
    None,
    ("Enfoque", "SaaS multi-tenant · security by design"),
]

BG, FG, MUTED, KEY, ACCENT = "#0d1117", "#c9d1d9", "#8b949e", "#58a6ff", "#39d353"
W, LINE, PAD = 490, 21, 22
SWATCH = ["#f85149", "#d29922", "#39d353", "#58a6ff", "#bc8cff", "#39c5cf", "#c9d1d9"]


def main() -> None:
    rows = []
    y = PAD + 14
    title = f"{USER}@{HOST}"
    rows.append(f'<text x="{PAD}" y="{y}"><tspan class="a">{USER}</tspan><tspan class="mu">@</tspan>'
                f'<tspan class="a">{HOST}</tspan></text>')
    y += LINE - 6
    rows.append(f'<text x="{PAD}" y="{y}" class="mu">{"─" * len(title)}</text>')
    y += LINE
    for item in CARD:
        if item is None:
            y += LINE // 2
            continue
        k, v = item
        key = f'<tspan class="k">{escape(k)}</tspan>' if k else ""
        rows.append(f'<text x="{PAD}" y="{y}">{key}<tspan x="{PAD + 78}" class="v">{escape(v)}</tspan></text>')
        y += LINE
    y += 6
    sw = "".join(f'<rect x="{PAD + i * 26}" y="{y}" width="22" height="12" rx="2" fill="{c}"/>'
                 for i, c in enumerate(SWATCH))
    rows.append(f"<g>{sw}</g>")
    height = y + 12 + PAD

    animated = []
    for i, r in enumerate(rows):
        delay = f"{0.25 + i * 0.12:.2f}s"
        cls = "" if STATIC else f' class="l" style="animation-delay:{delay}"'
        animated.append(f"<g{cls}>{r}</g>")

    anim = "" if STATIC else """
    .l{opacity:0;animation:in .45s ease-out forwards}
    @keyframes in{from{opacity:0;transform:translateX(-6px)}to{opacity:1;transform:none}}"""
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" role="img" aria-label="Tarjeta de perfil">
  <style>
    text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:13px}}
    .k{{fill:{KEY};font-weight:700}} .v{{fill:{FG}}} .mu{{fill:{MUTED}}} .a{{fill:{ACCENT};font-weight:700}}{anim}
  </style>
  <rect width="100%" height="100%" rx="10" fill="{BG}"/>
  {''.join(animated)}
</svg>
"""
    OUT.write_text(svg)
    print(f"→ {OUT}")


if __name__ == "__main__":
    main()
