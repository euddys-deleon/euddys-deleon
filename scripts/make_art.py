"""Genera las piezas estáticas del perfil: hero.svg, terminal.svg y orbit.svg.

Todo vive dentro de cada SVG (CSS keyframes + SMIL): GitHub elimina JS y CSS externo,
pero anima los SVG cargados con <img>.
"""
import math
import random
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MONO = "ui-monospace,SFMono-Regular,'Cascadia Code',Menlo,Consolas,monospace"
SANS = "'Segoe UI',Inter,system-ui,-apple-system,Helvetica,Arial,sans-serif"

CYAN, MAGENTA, PURPLE, GREEN, YELLOW = "#00f0ff", "#ff2bd6", "#8a2be2", "#39ff14", "#ffd319"
BG = "#07020f"

NAME = "EUDDYS DE LEÓN"
ROLES = [
    "CTO & cofundador @ SIRYNIX",
    "Construyo SaaS multi-tenant",
    "Security by design",
    "Next.js · Supabase · TypeScript",
    "Hecho en República Dominicana",
]

random.seed(7)


# ───────────────────────────── HERO ─────────────────────────────
def hero() -> str:
    W, H = 860, 320
    HZ = 205  # línea del horizonte
    parts = []

    # Lluvia de caracteres
    glyphs = "01アイウエオカキクケコ<>/{}#$%&*+=SIRYNIX"
    rain = []
    for i in range(44):
        x = 8 + i * 19.5
        n = random.randint(10, 18)
        chars = "".join(random.choice(glyphs) for _ in range(n))
        dur = random.uniform(5, 11)
        delay = -random.uniform(0, dur)
        spans = "".join(
            f'<tspan x="{x:.1f}" dy="15" fill-opacity="{0.15 + 0.85 * (k / n):.2f}">{escape(c)}</tspan>'
            for k, c in enumerate(chars)
        )
        color = GREEN if i % 5 else CYAN
        rain.append(f'<text class="rain" fill="{color}" style="animation-duration:{dur:.1f}s;'
                    f'animation-delay:{delay:.1f}s">{spans}</text>')
    parts.append(f'<g clip-path="url(#sky)" opacity=".28">{"".join(rain)}</g>')

    # Sol synthwave con franjas que suben
    stripes = []
    for k in range(7):
        y0 = HZ - 8 - k * 11
        stripes.append(
            f'<rect x="300" y="{y0}" width="260" height="{2 + k * 0.6:.1f}" fill="#000">'
            f'<animate attributeName="y" values="{y0};{y0 - 11}" dur="1.6s" repeatCount="indefinite"/></rect>'
        )
    parts.append(f"""
  <mask id="sunMask"><rect width="{W}" height="{H}" fill="#fff"/>{''.join(stripes)}</mask>
  <g filter="url(#glowBig)" class="sunpulse">
    <circle cx="430" cy="{HZ}" r="80" fill="url(#sun)" mask="url(#sunMask)" clip-path="url(#sky)"/>
  </g>""")

    # Piso: rejilla en perspectiva que avanza sin fin
    vx = 430
    floor = []
    for k in range(-16, 17):
        floor.append(f'<line x1="{vx + k * 6}" y1="{HZ}" x2="{vx + k * 70}" y2="{H}"/>')
    n = 9
    ys = [HZ + (H - HZ) * ((i / n) ** 2.2) for i in range(n + 1)]
    for i in range(n):
        a, b = ys[i], ys[i + 1]
        floor.append(f'<line x1="0" x2="{W}" y1="{a:.1f}" y2="{a:.1f}">'
                     f'<animate attributeName="y1" values="{a:.1f};{b:.1f}" dur="1.2s" repeatCount="indefinite"/>'
                     f'<animate attributeName="y2" values="{a:.1f};{b:.1f}" dur="1.2s" repeatCount="indefinite"/></line>')
    parts.append(f'<rect y="{HZ}" width="{W}" height="{H - HZ}" fill="url(#floor)"/>'
                 f'<g stroke="{MAGENTA}" stroke-width="1.2" opacity=".75" filter="url(#glow)">{"".join(floor)}</g>'
                 f'<line x1="0" x2="{W}" y1="{HZ}" y2="{HZ}" stroke="{CYAN}" stroke-width="2" filter="url(#glow)"/>')

    # Nombre con glitch
    name = escape(NAME)
    ny = 92
    parts.append(f"""
  <g font-family="{SANS}" font-weight="900" font-size="58" text-anchor="middle" letter-spacing="3">
    <text x="430" y="{ny}" fill="{CYAN}" class="g1">{name}</text>
    <text x="430" y="{ny}" fill="{MAGENTA}" class="g2">{name}</text>
    <text x="430" y="{ny}" fill="#fff" filter="url(#glow)" class="g0">{name}</text>
  </g>""")

    # Roles que se escriben y se borran
    fs, cw = 19, 11.4
    slot, n = 3.6, len(ROLES)
    T = slot * n
    roles = []
    for i, r in enumerate(ROLES):
        w = len(r) * cw
        t0 = i * slot / T
        t1 = (i * slot + 1.2) / T
        t2 = (i * slot + 2.8) / T
        t3 = (i * slot + 3.3) / T
        kt = [0, t0, t1, t2, t3, 1]
        if t0 == 0:
            kt = [0, t1, t2, t3, 1]
            vals = f"0;{w:.0f};{w:.0f};0;0"
            xs = f"0;{w:.0f};{w:.0f};0;0"
        else:
            vals = f"0;0;{w:.0f};{w:.0f};0;0"
            xs = vals
        kts = ";".join(f"{k:.4f}" for k in kt)
        x0 = 430 - w / 2
        roles.append(f"""
    <clipPath id="r{i}"><rect x="{x0:.1f}" y="118" height="34" width="0">
      <animate attributeName="width" values="{vals}" keyTimes="{kts}" dur="{T}s" repeatCount="indefinite" calcMode="discrete-free"/>
    </rect></clipPath>
    <text x="{x0:.1f}" y="142" textLength="{w:.0f}" lengthAdjust="spacingAndGlyphs" clip-path="url(#r{i})">{escape(r)}</text>""")
    roles_svg = "".join(roles).replace(' calcMode="discrete-free"', "")
    pill_w = max(len(r) for r in ROLES) * cw + 56
    parts.append(f'<rect x="{430 - pill_w / 2:.0f}" y="116" width="{pill_w:.0f}" height="36" rx="18" fill="#0a0118" '
                 f'fill-opacity=".82" stroke="{CYAN}" stroke-opacity=".55"/>')
    parts.append(f'<g font-family="{MONO}" font-size="{fs}" fill="{CYAN}" filter="url(#glow)">{roles_svg}</g>')

    # Badges
    parts.append(f"""
  <g font-family="{MONO}" font-size="11" fill="#cfc6ff">
    <rect x="16" y="14" width="142" height="22" rx="11" fill="none" stroke="{PURPLE}"/>
    <text x="87" y="29" text-anchor="middle">SIRYNIX // CTO</text>
    <circle cx="742" cy="25" r="5" fill="{GREEN}" filter="url(#glow)"><animate attributeName="opacity" values="1;.2;1" dur="1.4s" repeatCount="indefinite"/></circle>
    <text x="754" y="29">SYSTEM ONLINE</text>
    <text x="430" y="300" text-anchor="middle" fill="#ffd6f5" opacity=".85">⟨ sirynix.com ⟩</text>
  </g>""")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Euddys De León · CTO y cofundador de SIRYNIX">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0a0118"/><stop offset=".62" stop-color="#2a0845"/><stop offset="1" stop-color="{BG}"/></linearGradient>
    <linearGradient id="sun" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{YELLOW}"/><stop offset=".5" stop-color="#ff2975"/><stop offset="1" stop-color="#8c1eff"/></linearGradient>
    <linearGradient id="floor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3b0a5c"/><stop offset="1" stop-color="{BG}"/></linearGradient>
    <clipPath id="sky"><rect width="{W}" height="{HZ}"/></clipPath>
    <filter id="glow" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <filter id="glowBig" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="9" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>
  <style>
    .rain{{font-family:{MONO};font-size:13px;animation:fall linear infinite}}
    @keyframes fall{{from{{transform:translateY(-280px)}}to{{transform:translateY(240px)}}}}
    .sunpulse{{animation:pulse 4s ease-in-out infinite;transform-origin:430px 205px}}
    @keyframes pulse{{50%{{transform:scale(1.04)}}}}
    .g1{{animation:gl1 3.2s steps(1) infinite;opacity:.85}}
    .g2{{animation:gl2 3.2s steps(1) infinite;opacity:.85}}
    .g0{{animation:gl0 3.2s steps(1) infinite}}
    @keyframes gl1{{0%{{transform:translate(-2px,0)}}88%{{transform:translate(-7px,2px)}}91%{{transform:translate(5px,-2px)}}94%{{transform:translate(-3px,1px)}}97%{{transform:translate(-2px,0)}}}}
    @keyframes gl2{{0%{{transform:translate(2px,0)}}88%{{transform:translate(7px,-2px)}}91%{{transform:translate(-6px,2px)}}94%{{transform:translate(3px,-1px)}}97%{{transform:translate(2px,0)}}}}
    @keyframes gl0{{0%{{transform:none;opacity:1}}89%{{transform:skewX(-12deg);opacity:.75}}92%{{transform:skewX(8deg) translateX(4px);opacity:1}}95%{{transform:none}}}}
    .g0,.g1,.g2{{transform-box:fill-box;transform-origin:center}}
  </style>
  <rect width="{W}" height="{H}" rx="14" fill="url(#bg)"/>
  {''.join(parts)}
  <rect width="{W}" height="{H}" rx="14" fill="none" stroke="{PURPLE}" stroke-opacity=".6"/>
</svg>
"""


# ───────────────────────────── TERMINAL ─────────────────────────────
def terminal() -> str:
    W, H = 490, 380
    fs, cw, lh = 13, 7.8, 21
    script = [
        ("cmd", "whoami"),
        ("out", "Euddys Daviel De León Feliz", "#fff"),
        ("out", "CTO & cofundador @ SIRYNIX", CYAN),
        ("cmd", "cat ahora.txt"),
        ("out", "▸ CrediFlow ........ plataforma de préstamos", "#c9d1d9"),
        ("out", "▸ Inventario De León  POS para cervecerías", "#c9d1d9"),
        ("out", "▸ Alert Hub ........ orquestación de alertas", "#c9d1d9"),
        ("cmd", "./stack --favoritos"),
        ("out", "[Next.js] [React] [TypeScript] [Supabase]", MAGENTA),
        ("cmd", "ping sirynix.com"),
        ("out", "64 bytes de sirynix.com: tiempo=0.42ms ✓", GREEN),
    ]
    t = 0.6
    rows = []
    y = 62
    for i, line in enumerate(script):
        if line[0] == "cmd":
            txt = line[1]
            w = len(txt) * cw
            dur = max(0.4, len(txt) * 0.055)
            rows.append(
                f'<text x="18" y="{y}"><tspan fill="{GREEN}">euddys@sirynix</tspan><tspan fill="#8b949e">:</tspan>'
                f'<tspan fill="{CYAN}">~</tspan><tspan fill="#8b949e">$ </tspan></text>'
                f'<clipPath id="c{i}"><rect x="157" y="{y - 15}" height="20" width="0">'
                f'<animate attributeName="width" from="0" to="{w + 2:.0f}" begin="{t:.2f}s" dur="{dur:.2f}s" fill="freeze"/></rect></clipPath>'
                f'<text x="157" y="{y}" fill="#fff" clip-path="url(#c{i})">{escape(txt)}</text>'
            )
            # el prompt aparece justo antes de escribir
            rows[-1] = f'<g opacity="0"><set attributeName="opacity" to="1" begin="{t - 0.25:.2f}s" fill="freeze"/>{rows[-1]}</g>'
            t += dur + 0.35
        else:
            txt, color = line[1], line[2]
            rows.append(f'<text x="18" y="{y}" fill="{color}" opacity="0">{escape(txt)}'
                        f'<set attributeName="opacity" to="1" begin="{t:.2f}s" fill="freeze"/></text>')
            t += 0.22
        y += lh
        if line[0] == "out" and i + 1 < len(script) and script[i + 1][0] == "cmd":
            y += 6
    # cursor final
    rows.append(
        f'<g opacity="0"><set attributeName="opacity" to="1" begin="{t:.2f}s" fill="freeze"/>'
        f'<text x="18" y="{y}"><tspan fill="{GREEN}">euddys@sirynix</tspan><tspan fill="#8b949e">:</tspan>'
        f'<tspan fill="{CYAN}">~</tspan><tspan fill="#8b949e">$ </tspan></text>'
        f'<rect x="158" y="{y - 13}" width="8" height="16" fill="{GREEN}">'
        f'<animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></rect></g>'
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Terminal: quién es Euddys De León">
  <defs>
    <linearGradient id="tb" x1="0" x2="1"><stop offset="0" stop-color="{PURPLE}"/><stop offset="1" stop-color="{MAGENTA}"/></linearGradient>
    <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#fff" opacity=".035"/></pattern>
  </defs>
  <style>text{{font-family:{MONO};font-size:{fs}px;white-space:pre}}</style>
  <rect width="{W}" height="{H}" rx="14" fill="#0b0716"/>
  <rect width="{W}" height="32" rx="14" fill="#160d2a"/><rect y="18" width="{W}" height="14" fill="#160d2a"/>
  <circle cx="20" cy="16" r="6" fill="#ff5f56"/><circle cx="40" cy="16" r="6" fill="#ffbd2e"/><circle cx="60" cy="16" r="6" fill="#27c93f"/>
  <text x="{W / 2}" y="20" text-anchor="middle" fill="#a99bd6" style="font-size:11px">euddys@sirynix: ~ — zsh</text>
  {''.join(rows)}
  <rect width="{W}" height="{H}" fill="url(#scan)"/>
  <rect x="0" y="-60" width="{W}" height="60" fill="#fff" opacity=".04"><animate attributeName="y" values="-60;{H}" dur="5s" repeatCount="indefinite"/></rect>
  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="none" stroke="url(#tb)" stroke-opacity=".8"/>
</svg>
"""


# ───────────────────────────── ÓRBITAS ─────────────────────────────
def ellipse_path(cx, cy, rx, ry, tilt_deg, pts=96) -> str:
    a = math.radians(tilt_deg)
    out = []
    for k in range(pts + 1):
        th = 2 * math.pi * k / pts
        x, y = rx * math.cos(th), ry * math.sin(th)
        out.append((cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a)))
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in out) + "Z"


def orbit() -> str:
    W = H = 370
    cx, cy = W / 2, H / 2 + 6
    rings = [
        (70, 27, 9, CYAN, ["React", "Next.js"]),
        (108, 42, 15, MAGENTA, ["TypeScript", "Supabase", "Tailwind"]),
        (138, 58, 22, GREEN, ["PostgreSQL", "Vercel", "Capacitor", "Python"]),
    ]
    tilt = -18
    parts = []
    # estrellas
    for _ in range(55):
        x, y = random.uniform(0, W), random.uniform(0, H)
        d = random.uniform(1.5, 4)
        parts.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{random.choice([.6, .8, 1.1])}" fill="#fff">'
                     f'<animate attributeName="opacity" values=".1;1;.1" dur="{d:.1f}s" begin="-{random.uniform(0, d):.1f}s" repeatCount="indefinite"/></circle>')
    for i, (rx, ry, dur, color, items) in enumerate(rings):
        path = ellipse_path(cx, cy, rx, ry, tilt)
        parts.append(f'<path id="o{i}" d="{path}" fill="none" stroke="{color}" stroke-opacity=".35" stroke-dasharray="3 5"/>')
        for k, label in enumerate(items):
            w = len(label) * 6.6 + 16
            parts.append(f"""
    <g filter="url(#glow)">
      <rect x="{-w / 2:.1f}" y="-11" width="{w:.1f}" height="22" rx="11" fill="#0b0716" stroke="{color}" stroke-width="1.4"/>
      <text text-anchor="middle" y="4" fill="#fff">{label}</text>
      <animateMotion dur="{dur}s" begin="-{dur * k / len(items):.2f}s" repeatCount="indefinite"><mpath href="#o{i}"/></animateMotion>
    </g>""")
    core = f"""
  <g transform="translate({cx},{cy})">
    <circle r="40" fill="url(#core)" filter="url(#glowBig)"><animate attributeName="r" values="36;42;36" dur="3s" repeatCount="indefinite"/></circle>
    <circle r="50" fill="none" stroke="{CYAN}" stroke-width="1.5" stroke-dasharray="6 10" opacity=".8">
      <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="8s" repeatCount="indefinite"/></circle>
    <circle r="56" fill="none" stroke="{MAGENTA}" stroke-width="1" stroke-dasharray="2 14" opacity=".7">
      <animateTransform attributeName="transform" type="rotate" from="360" to="0" dur="12s" repeatCount="indefinite"/></circle>
    <text text-anchor="middle" y="7" font-family="{SANS}" font-weight="900" font-size="21" fill="#fff" letter-spacing="1">EDL</text>
  </g>"""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H + 10}" viewBox="0 0 {W} {H + 10}" role="img" aria-label="Stack tecnológico en órbita">
  <defs>
    <radialGradient id="core"><stop offset="0" stop-color="#fff"/><stop offset=".35" stop-color="{MAGENTA}"/><stop offset="1" stop-color="{PURPLE}" stop-opacity=".2"/></radialGradient>
    <radialGradient id="neb" cx=".5" cy=".55" r=".6"><stop offset="0" stop-color="#3a0d63"/><stop offset="1" stop-color="#0b0716"/></radialGradient>
    <filter id="glow" x="-30%" y="-60%" width="160%" height="220%"><feGaussianBlur stdDeviation="1.6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <filter id="glowBig" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="10" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>
  <style>text{{font-family:{MONO};font-size:11px}}</style>
  <rect width="{W}" height="{H + 10}" rx="14" fill="url(#neb)"/>
  <text x="18" y="26" fill="#a99bd6">~/stack $ orbit --live</text>
  {''.join(parts)}
  {core}
  <rect x=".5" y=".5" width="{W - 1}" height="{H + 9}" rx="14" fill="none" stroke="{PURPLE}" stroke-opacity=".6"/>
</svg>
"""


def main() -> None:
    for name, fn in (("hero.svg", hero), ("terminal.svg", terminal), ("orbit.svg", orbit)):
        (ROOT / name).write_text(fn())
        print(f"→ {name}")


if __name__ == "__main__":
    main()
