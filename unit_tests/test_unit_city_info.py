import re
from pathlib import Path
import pytest
import api.city_info as city_info

_MOCKED_DIR = Path(__file__).resolve().parents[1] / "files" / "mocked_city_files"

def discover_mocked_city_files() -> list[Path]:
    return sorted(p for p in _MOCKED_DIR.glob("*.txt") if p.is_file())


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
    m = re.search(r"The current temperature in .*? is\s+(-?\d+(?:\.\d+)?)\s+degrees Celsius\.", text)
    if not m:
        return None
    return float(m.group(1))

def mocked_cities() -> list[tuple[str, str, float | None]]:
    cases: list[tuple[str, str, float | None]] = []
    for p in discover_mocked_city_files():
        raw = p.read_text(encoding="utf-8")
        city = city_from_mock_file(p)
        summary = parse_summary_from_mock_file(raw)
        temp = parse_temperature_from_mock_file(raw)
        cases.append((city, summary, temp))
    return cases


def mocked_city_ids() -> list[str]:
    return [city for city, _summary, _temp in mocked_cities()]


@pytest.mark.parametrize(
    "city,summary,temp_in_mock",
    mocked_cities(),
    ids=mocked_city_ids(),
)
def test_generate_city_txt_and_response_from_mocked_city_files(tmp_path, city, summary, temp_in_mock):
    out_dir = tmp_path / "files"
    ow_json = city_info.get_openweather_json(city, city_info.OPENWEATHER_APPID)
    temp_live = float(ow_json["main"]["temp"])
    city_file = city_info.write_city_info(city, summary, temp_live, output_dir=str(out_dir))
    response_file = city_info.write_openweather_response(city, ow_json, output_dir=str(out_dir))
    city_path = out_dir / f"{city}.txt"
    response_path = out_dir / f"response_{city}.txt"
    assert city_file == str(city_path)
    assert response_file == str(response_path)
    assert city_path.exists()
    assert response_path.exists()
    content = city_path.read_text(encoding="utf-8")
    assert summary.splitlines()[0] in content
    assert f"The current temperature in {city} is" in content
    if temp_in_mock is not None:
        assert isinstance(temp_in_mock, float)


@pytest.mark.parametrize(
    "bad_city",
    [
        "",
        "   ",
    ],
)
def test_write_city_into_file_rejects_empty_city(tmp_path, bad_city):
    out_dir = tmp_path / "files"
    with pytest.raises(Exception):
        city_info.write_city_info(bad_city, "summary", 1, output_dir=str(out_dir))
