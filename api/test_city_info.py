from pathlib import Path
import re

import api.city_info as city_info
import pytest


MOCKED_DIR = Path(__file__).resolve().parents[1] / "files" / "mocked_city_files"
REPO_FILES_DIR = Path(__file__).resolve().parents[1] / "files"


def discover_mocked_city_files() -> list[Path]:
    return sorted(p for p in MOCKED_DIR.glob("*.txt") if p.is_file())


def city_from_mock_file(path: Path) -> str:
    return path.stem.strip()


def summary_from_mock_file(text: str) -> str:
    # Keep everything except the trailing temperature line.
    lines = [ln.rstrip() for ln in text.splitlines()]
    while lines and not lines[-1].strip():
        lines.pop()
    if lines and lines[-1].lower().startswith("the current temperature in "):
        lines = lines[:-1]
    return "\n".join(lines).strip()


def mocked_city_cases() -> list[tuple[str, str]]:
    cases: list[tuple[str, str]] = []
    for p in discover_mocked_city_files():
        city = city_from_mock_file(p)
        summary = summary_from_mock_file(p.read_text(encoding="utf-8"))
        cases.append((city, summary))
    return cases


def mocked_city_case_ids() -> list[str]:
    return [city for city, _summary in mocked_city_cases()]


def case_id(case) -> str:
    try:
        return str(case[0])
    except Exception:
        return "case"


@pytest.mark.parametrize("script_name", ["city_info.py"])
def test_run_missing_city_name_exits_2(capsys, script_name):
    rc = city_info.run([script_name])  # no args
    assert rc == 2
    err = capsys.readouterr().err
    assert "Usage:" in err


@pytest.mark.parametrize("script_name", ["city_info.py"])
def test_run_empty_city_errors(capsys, script_name):
    rc = city_info.run([script_name, "   "])
    assert rc == 2
    err = capsys.readouterr().err
    assert "Invalid input" in err


@pytest.mark.parametrize(
    "case",
    mocked_city_cases(),
    ids=mocked_city_case_ids(),
)
def test_response_files_from_mocked_city_files(case):
    city, _mocked_summary = case
    summary = city_info.get_city_summary(city)

    REPO_FILES_DIR.mkdir(parents=True, exist_ok=True)
    city_txt = REPO_FILES_DIR / f"{city}.txt"
    response_txt = REPO_FILES_DIR / f"response_{city}.txt"

    ow_json = city_info.get_openweather_json(city, city_info.OPENWEATHER_APPID)
    temp = float(ow_json["main"]["temp"])

    written_city_file = city_info.write_city_info(
        city, summary, temp, output_dir=str(REPO_FILES_DIR)
    )
    written_response_file = city_info.write_openweather_response(
        city, ow_json, output_dir=str(REPO_FILES_DIR)
    )

    assert written_city_file == str(city_txt)
    assert written_response_file == str(response_txt)

    assert city_txt.exists()
    assert response_txt.exists()

    content = city_txt.read_text(encoding="utf-8")
    assert summary.splitlines()[0] in content
    assert re.search(
        rf"The current temperature in {re.escape(city)} is\s+[-+]?\d+(?:\.\d+)? degrees Celsius\.",
        content,
    )


@pytest.mark.parametrize(
    "city",
    [
        "asdasdasd",
        "00000000",
        "#$%^&*",
    ],
)
def test_openweather_live_invalid_city_returns_error_message(city):
    with pytest.raises(RuntimeError) as exc:
        city_info.get_openweather_json(city, city_info.OPENWEATHER_APPID)

    assert (
        "http" in str(exc.value).lower()
        or "not found" in str(exc.value).lower()
        or "request failed" in str(exc.value).lower()
    )


@pytest.mark.parametrize(
    "city",
    [city for city, _summary in mocked_city_cases()],
    ids=[city for city, _summary in mocked_city_cases()],
)
def test_get_city_summary_live(city):
    summary = city_info.get_city_summary(city)
    assert isinstance(summary, str)
    assert len(summary) > 30
    assert city.lower() in summary.lower()
