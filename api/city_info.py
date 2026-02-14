from urllib.parse import quote
import sys
import requests
import os
import re
import json

DEFAULT_TIMEOUT_S: float = 10.0
OPENWEATHER_APPID = "7d2d3e43f13bb33a3ffc504a4ae499ca"


def format_city_file(city_name: str) -> str:
    city_name = city_name.strip()
    # Replace path separators and other problematic characters
    city_name = re.sub(r"[\\/\0]", "_", city_name)
    city_name = re.sub(r"\s+", " ", city_name)
    return city_name


def city_from_input(value: str) -> str:
    v = value.strip()
    if not v:
        return ""
    if v.lower().endswith(".txt"):
        v = v[:-4]
    return v.strip()


def get_city_summary(city_name: str) -> str:
    city_name = city_name.strip()
    if not city_name:
        raise ValueError("City name cannot be empty")
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(city_name)}"
    headers = {
        # Wikipedia REST API may return 403 without a descriptive User-Agent.
        "User-Agent": "playwright-test",
        "Accept": "application/json",
    }
    try:
        resp = requests.get(url, timeout=DEFAULT_TIMEOUT_S, headers=headers)
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch Wikipedia summary: {e}") from e
    # Wikipedia returns 404 with a JSON body for unknown pages.
    if resp.status_code != 200:
        raise RuntimeError(f"Wikipedia summary not found for '{city_name}' (HTTP {resp.status_code})")
    try:
        data = resp.json()
    except ValueError as e:
        raise RuntimeError("Wikipedia response was not valid JSON") from e
    summary = data.get("extract")
    if not summary:
        raise RuntimeError(f"Wikipedia did not return a summary for '{city_name}'")
    return summary


def fetch_openweather_response(city_name: str, api_key: str) -> requests.Response:
    city_name = city_name.strip()
    if not city_name:
        raise ValueError("City name cannot be empty")
    if not api_key or not api_key.strip():
        raise ValueError("OpenWeatherMap API key is missing")
    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={quote(city_name)}&appid={quote(api_key.strip())}&units=metric"
    )
    try:
        resp = requests.get(url, timeout=DEFAULT_TIMEOUT_S)
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch OpenWeatherMap response: {e}") from e
    # OpenWeather uses non-200 for errors
    if resp.status_code != 200:
        try:
            data = resp.json()
            msg = data.get("message")
        except Exception:
            msg = None
        detail = f": {msg}" if msg else ""
        raise RuntimeError(
            f"OpenWeatherMap request failed for '{city_name}' (HTTP {resp.status_code}){detail}"
        )
    return resp


def get_city_temperature(city_name: str, api_key: str) -> float:
    resp = fetch_openweather_response(city_name, api_key)
    try:
        data = resp.json()
        temp = data["main"]["temp"]
    except Exception as e:
        raise RuntimeError("OpenWeatherMap response did not contain main.temp") from e
    return float(temp)


def get_openweather_json(city_name: str, api_key: str) -> dict:
    resp = fetch_openweather_response(city_name, api_key)
    try:
        return resp.json()
    except ValueError as e:
        raise RuntimeError("OpenWeatherMap response was not valid JSON") from e


def write_city_info(city_name: str, summary: str, temperature: float, *, output_dir: str = "files") -> str:
    city_name = city_name.strip()
    if not city_name:
        raise ValueError("City name cannot be empty")
    safe_city = format_city_file(city_name)
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"{safe_city}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"{summary}\n")
        f.write(
            f"The current temperature in {city_name} is {temperature} degrees Celsius.\n"
        )
    return filename


def write_openweather_response(city_name: str, openweather_json: dict, *, output_dir: str = "files") -> str:
    safe_city = format_city_file(city_name)
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"response_{safe_city}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(json.dumps(openweather_json, ensure_ascii=False, indent=2))
    return filename


USAGE_MESSAGE = "Usage: python api/city_info.py <city_or_city.txt> [openweathermap_api_key]"


def print_usage(message: str = USAGE_MESSAGE):
    print(message, file=sys.stderr)


def print_invalid_city(message: str):
    print(message, file=sys.stderr)


def resolve_api_key(argv: list[str], env_var_name: str) -> str:
    return argv[2] if len(argv) >= 3 else (os.getenv(env_var_name) or OPENWEATHER_APPID)


def run(argv: list[str]) -> int:
    if len(argv) < 2:
        print_usage(USAGE_MESSAGE)
        return 2

    city_name = city_from_input(argv[1])
    if not city_name:
        print_invalid_city("Invalid input: city name cannot be empty")
        return 2

    api_key = resolve_api_key(argv, "OPENWEATHER_API_KEY")
    if not api_key or not api_key.strip():
        print_invalid_city(
            "Missing OpenWeatherMap API key. Pass it as the 2nd argument or set OPENWEATHER_API_KEY."
        )
        return 2

    try:
        summary = get_city_summary(city_name)
        ow_json = get_openweather_json(city_name, api_key)
        temperature = float(ow_json["main"]["temp"])

        city_file = write_city_info(city_name, summary, temperature, output_dir="files")
        response_file = write_openweather_response(city_name, ow_json, output_dir="files")

    except (KeyError, TypeError):
        print_invalid_city("OpenWeatherMap response did not contain main.temp")
        return 1
    except (ValueError, RuntimeError) as e:
        print_invalid_city(str(e))
        return 1

    print(f"Output written to {city_file}")
    print(f"Response written to {response_file}")
    return 0


def main() -> None:
    raise SystemExit(run(sys.argv))


if __name__ == "__main__":
    main()