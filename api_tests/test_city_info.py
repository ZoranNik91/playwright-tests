from pathlib import Path
import api.city_info as city_info
import requests
import json
import pytest

# API test for missing city name (no args)
@pytest.mark.parametrize("script_name", ["city_info.py"])
def test_run_missing_city_name_exits_2(capsys, script_name):
    rc = city_info.run([script_name])  # no args
    assert rc == 2
    err = capsys.readouterr().err
    assert "Usage:" in err

# API test with empty city name (spaces only)
def test_run_empty_city_errors(capsys):
    rc = city_info.run(["city_info.py", "   "])
    assert rc == 2
    err = capsys.readouterr().err
    assert "Invalid input" in err

# Api test with existing city
@pytest.mark.parametrize(
    "appid,city,expected_country,timeout_s",
    [
        ("7d2d3e43f13bb33a3ffc504a4ae499ca", "Zagreb", "HR", 20),
    ],
)
def test_openweather_live_saves_response_to_city_txt(appid, city, expected_country, timeout_s):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={appid}&units=metric"

    r = requests.get(url, timeout=timeout_s)
    assert r.status_code == 200

    data = r.json()
    assert str(data.get("cod")) == "200"
    assert "main" in data and "temp" in data["main"]

    if expected_country is not None:
        assert data.get("sys", {}).get("country") == expected_country

    repo_files_dir = Path(__file__).resolve().parents[1] / "files"
    repo_files_dir.mkdir(parents=True, exist_ok=True)
    out_file = repo_files_dir / f"response_{city}.txt"

    out_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    assert out_file.exists()

    saved = json.loads(out_file.read_text(encoding="utf-8"))
    assert "main" in saved and "temp" in saved["main"]
    assert str(saved.get("cod")) == "200"

# Api test with invalid city (random text)
@pytest.mark.parametrize(
    "appid,city,timeout_s,expected_status,expected_message_substring",
    [
        ("7d2d3e43f13bb33a3ffc504a4ae499ca", "asdasdsadas", 20, 404, "city not found"),
    ],
)
def test_openweather_live_invalid_city_returns_error_message(
    appid,
    city,
    timeout_s,
    expected_status,
    expected_message_substring,
):
    """Live API test: invalid city should return an error with a helpful message."""
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={appid}&units=metric"
    r = requests.get(url, timeout=timeout_s)
    assert r.status_code == expected_status

    data = r.json()
    assert str(data.get("cod")) == str(expected_status)
    assert expected_message_substring in str(data.get("message", "")).lower()
