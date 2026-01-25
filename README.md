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

## Headed + parallel (multiple visible browsers)

Run headed tests in parallel with `pytest-xdist`.
Start with `-n 2` browsers.

### Headed parallel run (recommended)

```sh
pytest --headed --slowmo 200 -s -n 2
```

### Headed parallel run (auto workers)

```sh
pytest --headed --slowmo 200 -s -n auto
```

## Run in multiple browsers

`pytest-playwright` can run the same tests against multiple browsers by repeating `--browser`.

## Parallel execution (faster)

We use `pytest-xdist` for parallel workers.

### Parallelize tests (single browser)

```sh
pytest -n auto
```

### Multi-browser + parallel workers

```sh
pytest --browser chromium --browser firefox --browser webkit -n auto
```

If you want a fixed number of workers:

```sh
pytest --browser chromium --browser firefox --browser webkit -n 3
```

## HTML report (document file)

We generate an HTML report using `pytest-html`.

### Generate report

```sh
mkdir -p reports
pytest --html=reports/playwright-report.html --self-contained-html
```

### Open report

Open this file in your browser:
- `reports/playwright-report.html`

## "Play button" / one-click runs in JetBrains (IntelliJ/PyCharm)

Markdown files can’t reliably run shell commands just by clicking a button.
For one-click execution inside JetBrains, use a **Run Configuration**:

### Option A: Pytest run configuration
- Run → Edit Configurations… → **+** → Python tests → **pytest**
- Target: the project folder or `tests/`
- Additional Arguments (examples):
  - Headless: `-q`
  - Headed: `--headed --slowmo 200 -s`
  - Headed + parallel: `--headed --slowmo 200 -s -n 2`
  - Multi-browser: `--browser chromium --browser firefox --browser webkit`
  - Parallel: `-n auto`
  - Multi-browser + parallel: `--browser chromium --browser firefox --browser webkit -n auto`
  - With HTML report: `--html=reports/playwright-report.html --self-contained-html`
- Working directory: `/Users/admin/IdeaProjects/Playwrite-tests`
- Python interpreter: your `.venv`

### Option B: Shell Script run configuration
- Run → Edit Configurations… → **+** → Shell Script
- Script text example:
  - `source .venv/bin/activate && pytest --headed --slowmo 200 -s -n 2`

## Notes
- Tests live in `tests/` and use the `pytest-playwright` `page` fixture.
- Default Playwright timeouts are set to **10 seconds** in `conftest.py`.
- Reports are saved under `reports/`.
- Version pins live in `requirements.txt` (recommended: update them together).

## Run API tests (city info)

The API exercise lives in `api/city_info.py` and is tested via `api_tests/test_city_info.py`.
These tests **mock** the external APIs (Wikipedia/OpenWeatherMap), so they don’t require an API key.

> When you run `api/city_info.py` yourself from the repo root, the file will be created under `./files/<City>.txt`.
> The sample/static files are kept under `./files/mocked_city_files/`.

### Run all API tests

```sh
pytest -q api_tests
```

### Run a single API test

```sh
pytest -q api_tests/test_city_info.py::test_write_city_into_file -vv
```

### Generate `<City>.txt` (writes into `./files/`)

You can pass either a city name (`Zagreb`) or a filename-style input (`Zagreb.txt`).

Examples:

```sh
python3 api/city_info.py Zagreb.txt
```
```sh
python3 api/city_info.py Berlin.txt
```

By default, `api/city_info.py` uses the built-in APPID for this exercise.
To override it, pass your own key as the 2nd argument or set an environment variable:

```sh
python3 api/city_info.py Zagreb.txt <OPENWEATHER_API_KEY>
```
or
```sh
export OPENWEATHER_API_KEY=<OPENWEATHER_API_KEY>
python3 api/city_info.py Zagreb.txt
```

### Live OpenWeather integration test (writes `./files/response_city.txt`)

We also have an **integration** test that calls the real OpenWeather API using the sample APPID and
writes the raw JSON response to:
- `./files/response_city.txt`

Run it explicitly:

```sh
pytest -q api_tests/test_city_info.py -m integration
```

## Run unit tests

Unit tests live under `unit_tests/`.

### Run a single unit test (positive)

```sh
pytest -q unit_tests/test_unit_city_info.py::test_get_city_summary_success
```

### Run a single unit test (negative)

```sh
pytest -q unit_tests/test_unit_city_info.py::test_get_city_summary_invalid_city
```