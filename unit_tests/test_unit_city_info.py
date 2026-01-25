import os
import re

import pytest
import api.city_info as city_info


@pytest.mark.parametrize("city", [
    "Zagreb",
    "Berlin",
    "Vienna",
])
def test_get_city_summary_success(city):
    summary = city_info.get_city_summary(city)
    assert isinstance(summary, str)
    assert len(summary) > 50


@pytest.mark.parametrize("city", [
    "asdasdsadas",
    "00000000",
    "!@#$$%^&*(-_",
])
def test_get_city_summary_invalid_city(city):
    with pytest.raises(RuntimeError):
        city_info.get_city_summary(city)


@pytest.mark.parametrize("city", [
    "        ",
    "",
])
def test_get_city_summary_empty_city_raises_value_error(city):
    with pytest.raises(ValueError):
        city_info.get_city_summary(city)


@pytest.mark.parametrize(
    "city,appid,low,high",
    [
        ("Zagreb", city_info.OPENWEATHER_APPID, -80.0, 80.0),
    ],
)
def test_get_city_temperature_success_real_http(city, appid, low, high):
    temp = city_info.get_city_temperature(city, appid)
    assert isinstance(temp, float)
    # very wide sanity range to avoid false failures
    assert low <= temp <= high


@pytest.mark.parametrize(
    "city,appid",
    [
        ("asdasdsadas", city_info.OPENWEATHER_APPID),
    ],
)
def test_get_city_temperature_invalid_city_raises(city, appid):
    with pytest.raises(RuntimeError):
        city_info.get_city_temperature(city, appid)


# Unit test for writing city info into a file
@pytest.mark.parametrize(
    "output_dir_name,city,summary,temp",
    [
        ("files", "Zagreb", "Zagreb is the capital of Croatia.", 23),
    ],
)
def test_write_city_into_file(tmp_path, output_dir_name, city, summary, temp):
    out_dir = tmp_path / output_dir_name
    filename = city_info.write_city_info(city, summary, temp, output_dir=str(out_dir))

    out_file = out_dir / f"{city}.txt"
    assert filename == str(out_file)
    assert out_file.exists()

    content = out_file.read_text(encoding="utf-8")
    assert summary in content
    assert re.search(
        rf"The current temperature in {re.escape(city)} is {temp}(\.0)? degrees Celsius\.",
        content,
    )


@pytest.mark.parametrize(
    "script_name,city_input,expected_city",
    [
        ("city_info.py", "Zagreb.txt", "Zagreb"),
    ],
)
def test_city_success_creates_file(tmp_path, script_name, city_input, expected_city):
    old_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)

        rc = city_info.run([script_name, city_input])
        assert rc == 0

        out_file = tmp_path / "files" / f"{expected_city}.txt"
        assert out_file.exists()

        content = out_file.read_text(encoding="utf-8")
        assert f"The current temperature in {expected_city} is" in content
    finally:
        os.chdir(old_cwd)


@pytest.mark.parametrize(
    "script_name,city_input,expected_city",
    [
        ("city_info.py", "___.txt", "asdasdsadas"),
    ],
)
def test_invalid_city_not_creates_file(tmp_path, script_name, city_input, expected_city):
    old_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)

        rc = city_info.run([script_name, city_input])
        assert rc == 1

        out_file = tmp_path / "files" / f"{expected_city}.txt"
        assert not out_file.exists()
    finally:
        os.chdir(old_cwd)
