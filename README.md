# Playwright tests (Python)

## Prerequisites
- Python 3.10+

## Setup

### 1) Create & activate a virtualenv

```sh
python3 -m venv .venv
```
```sh
source .venv/bin/activate
```

### 2) Install Python dependencies

This installs:
- Playwright (Python)
- pytest (version `pytest==9.0.2`)
- pytest-playwright (version `pytest-playwright==0.7.2` compatible with pytest 9.x)
- *pytest-html (HTML report) (optional)*
- *pytest-xdist (parallel runs) (optional)*

```sh
pip install -U pip
```
```sh
pip install -r requirements.txt
```

### 3) Install Playwright browsers

```sh
python -m playwright install
```

## Run tests

### Run all tests (headless)

```sh
pytest
```

### Run with a visible browser

```sh
pytest --headed --slowmo 200 -s
```

### Sell Script
- Run e2e tests headed with shell script:
  - `source .venv/bin/activate && pytest --headed --slowmo 200 -s`

## Notes
- Tests live in `tests/` and use the `pytest-playwright` `page` fixture.
- Default Playwright timeouts are set to **10 seconds** in `conftest.py`.
- Reports are saved under `reports/`.
- Version pins live in `requirements.txt`

## Run API tests

The API exercise lives in `api/city_info.py` and is tested via `api/test_city_info.py`.

- `test_get_city_summary_live` fetches data **live from Wikipedia**.
- Some other API tests may fetch data **live from OpenWeatherMap**.

If you see an error like `No module named 'pytest_playwright'`, make sure your virtualenv is activated and dependencies are installed:

```sh
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install
```

### Run all API tests

```sh
pytest -q api
```

### Run a single API test (Wikipedia summary)

```sh
pytest -q api/test_city_info.py::test_get_city_summary_live -s
```

## Run unit tests

Unit tests live under `unit_tests/`.

### Run a single unit test (positive)

```sh
pytest -q unit_tests/test_unit_city_info.py::test_generate_city_txt_and_response_from_mocked_city_files
```

### Run a single unit test (negative)

```sh
pytest -q unit_tests/test_unit_city_info.py::test_write_city_into_file_rejects_empty_city
```

## Run the city_info CLI

This command fetches the Wikipedia summary + OpenWeather temperature and writes:
- `files/<City>.txt`
- `files/response_<City>.txt`

Add name of city as argument.
- `python api/city_info.py "City Name"`
```sh
source .venv/bin/activate
python api/city_info.py
```

If you prefer not to activate the venv:

```sh
.venv/bin/python api/city_info.py
```
