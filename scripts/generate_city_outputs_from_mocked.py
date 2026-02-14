"""Generate output files into the repo's ./files directory.

- Reads ./files/mocked_city_files/*.txt for city + summary.
- Fetches live OpenWeather JSON for each city.
- Writes:
  - ./files/<City>.txt
  - ./files/response_<City>.txt

This is intentionally NOT a test, so it won't interfere with your ability to delete files
or with pytest runs.

Usage:
  python3 scripts/generate_city_outputs_from_mocked.py
"""

from __future__ import annotations

import re
from pathlib import Path

import api.city_info as city_info


REPO_ROOT = Path(__file__).resolve().parents[1]
MOCKED_DIR = REPO_ROOT / "files" / "mocked_city_files"
OUT_DIR = REPO_ROOT / "files"


def discover_mocked_city_files() -> list[Path]:
    return sorted(p for p in MOCKED_DIR.glob("*.txt") if p.is_file())


def city_from_mock_file(path: Path) -> str:
    return path.stem.strip()


def parse_summary_from_mock_file(text: str) -> str:
    lines = [ln.rstrip() for ln in text.splitlines()]
    while lines and not lines[-1].strip():
        lines.pop()
    if lines and lines[-1].lower().startswith("the current temperature in "):
        lines = lines[:-1]
    return "\n".join(lines).strip()


def parse_temperature_from_mock_file(text: str) -> float | None:
    m = re.search(
        r"The current temperature in .*? is\s+(-?\d+(?:\.\d+)?)\s+degrees Celsius\.",
        text,
    )
    if not m:
        return None
    try:
        return float(m.group(1))
    except ValueError:
        return None


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    files = discover_mocked_city_files()
    if not files:
        print(f"No mocked files found in: {MOCKED_DIR}")
        return 2

    for p in files:
        raw = p.read_text(encoding="utf-8")
        city = city_from_mock_file(p)
        summary = parse_summary_from_mock_file(raw)
        mocked_temp = parse_temperature_from_mock_file(raw)

        ow_json = city_info.get_openweather_json(city, city_info.OPENWEATHER_APPID)
        temp_live = float(ow_json["main"]["temp"])

        city_path = city_info.write_city_info(city, summary, temp_live, output_dir=str(OUT_DIR))
        resp_path = city_info.write_openweather_response(city, ow_json, output_dir=str(OUT_DIR))

        msg = f"Generated {Path(city_path).name} and {Path(resp_path).name}"
        if mocked_temp is not None:
            msg += f" (mock temp was {mocked_temp})"
        print(msg)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

