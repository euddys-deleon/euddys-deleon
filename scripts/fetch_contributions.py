"""Descarga el calendario público de contribuciones (sin token) y calcula estadísticas.

Escribe data/contributions.json.
"""
import json
import os
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USER = os.environ.get("GH_USER", "euddys-deleon")
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "contributions.json"


def fetch(user: str) -> list[dict]:
    url = f"https://github.com/users/{user}/contributions"
    r = requests.get(url, headers={"User-Agent": "profile-readme-bot"}, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # Los conteos viven en <tool-tip for="contribution-day-component-X-Y">
    tips = {}
    for tip in soup.select("tool-tip"):
        target = tip.get("for")
        text = tip.get_text(strip=True)
        n = 0
        first = text.split(" ")[0]
        if first.isdigit():
            n = int(first)
        tips[target] = n

    days = []
    for cell in soup.select("td.ContributionCalendar-day[data-date]"):
        d = cell["data-date"]
        level = int(cell.get("data-level", 0))
        count = tips.get(cell.get("id"), 0)
        days.append({"date": d, "level": level, "count": count})
    days.sort(key=lambda x: x["date"])
    if not days:
        sys.exit("No se encontraron días de contribución: cambió el HTML de GitHub")
    return days


def stats(days: list[dict]) -> dict:
    total = sum(d["count"] for d in days)
    best = max(days, key=lambda d: d["count"])
    longest = cur = 0
    for d in days:
        cur = cur + 1 if d["count"] > 0 else 0
        longest = max(longest, cur)
    # racha actual: hoy puede estar en 0 sin romperla
    current = 0
    rev = list(reversed(days))
    if rev and rev[0]["count"] == 0:
        rev = rev[1:]
    for d in rev:
        if d["count"] > 0:
            current += 1
        else:
            break
    months = defaultdict(int)
    for d in days:
        months[d["date"][:7]] += d["count"]
    return {
        "total": total,
        "best_day": best,
        "longest_streak": longest,
        "current_streak": current,
        "active_days": sum(1 for d in days if d["count"] > 0),
        "monthly": dict(months),
    }


def main() -> None:
    days = fetch(USER)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"user": USER, "days": days, "stats": stats(days)}, indent=1))
    print(f"{len(days)} días, {sum(d['count'] for d in days)} contribuciones → {OUT}")


if __name__ == "__main__":
    main()
