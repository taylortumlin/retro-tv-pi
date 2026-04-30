"""Weather data fetcher (Open-Meteo). Behavior identical to the monolith."""

from __future__ import annotations

import time

import requests

from . import _state

WMO_CODES = {
    0: "Clear", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
    45: "Fog", 48: "Rime Fog",
    51: "Light Drizzle", 53: "Drizzle", 55: "Heavy Drizzle",
    56: "Freezing Drizzle", 57: "Heavy Freezing Drizzle",
    61: "Light Rain", 63: "Rain", 65: "Heavy Rain",
    66: "Freezing Rain", 67: "Heavy Freezing Rain",
    71: "Light Snow", 73: "Snow", 75: "Heavy Snow", 77: "Snow Grains",
    80: "Light Showers", 81: "Showers", 82: "Heavy Showers",
    85: "Light Snow Showers", 86: "Heavy Snow Showers",
    95: "Thunderstorm", 96: "Thunderstorm w/ Hail", 99: "Heavy Thunderstorm w/ Hail",
}


def fetch_weather() -> None:
    ticker_cfg = _state.CONFIG.get("ticker", {})
    weather_cfg = ticker_cfg.get("weather", {})
    lat = weather_cfg.get("latitude", 33.749)
    lon = weather_cfg.get("longitude", -84.388)
    unit = weather_cfg.get("temperature_unit", "fahrenheit")
    location = weather_cfg.get("location_name", "Atlanta")
    forecast_days = ticker_cfg.get("forecast_days", 7)
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,apparent_temperature,weather_code,wind_speed_10m,relative_humidity_2m,uv_index"
            f"&hourly=temperature_2m,weather_code,precipitation_probability"
            f"&daily=temperature_2m_max,temperature_2m_min,weather_code,precipitation_probability_max,uv_index_max"
            f"&temperature_unit={unit}"
            f"&wind_speed_unit=mph"
            f"&forecast_days={forecast_days}&timezone=auto"
        )
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        d = data.get("current", {})
        code = d.get("weather_code", 0)
        _state.weather_cache["data"] = {
            "temperature": d.get("temperature_2m"),
            "feels_like": d.get("apparent_temperature"),
            "condition": WMO_CODES.get(code, "Unknown"),
            "weather_code": code,
            "wind_speed": d.get("wind_speed_10m"),
            "humidity": d.get("relative_humidity_2m"),
            "uv_index": d.get("uv_index"),
            "unit": "F" if unit == "fahrenheit" else "C",
            "location": location,
        }
        # Hourly forecast (next 24 hours).
        hourly_raw = data.get("hourly", {})
        hourly = []
        h_times = hourly_raw.get("time", [])
        h_temps = hourly_raw.get("temperature_2m", [])
        h_codes = hourly_raw.get("weather_code", [])
        h_precip = hourly_raw.get("precipitation_probability", [])
        for i in range(min(24, len(h_times))):
            hourly.append({
                "time": h_times[i] if i < len(h_times) else None,
                "temperature": h_temps[i] if i < len(h_temps) else None,
                "weather_code": h_codes[i] if i < len(h_codes) else 0,
                "condition": WMO_CODES.get(h_codes[i] if i < len(h_codes) else 0, "Unknown"),
                "precip_probability": h_precip[i] if i < len(h_precip) else 0,
            })
        _state.weather_cache["hourly"] = hourly
        # Daily forecast.
        daily_raw = data.get("daily", {})
        daily = []
        d_times = daily_raw.get("time", [])
        d_max = daily_raw.get("temperature_2m_max", [])
        d_min = daily_raw.get("temperature_2m_min", [])
        d_codes = daily_raw.get("weather_code", [])
        d_precip = daily_raw.get("precipitation_probability_max", [])
        d_uv = daily_raw.get("uv_index_max", [])
        for i in range(min(forecast_days, len(d_times))):
            daily.append({
                "date": d_times[i] if i < len(d_times) else None,
                "high": d_max[i] if i < len(d_max) else None,
                "low": d_min[i] if i < len(d_min) else None,
                "weather_code": d_codes[i] if i < len(d_codes) else 0,
                "condition": WMO_CODES.get(d_codes[i] if i < len(d_codes) else 0, "Unknown"),
                "precip_probability": d_precip[i] if i < len(d_precip) else 0,
                "uv_index": d_uv[i] if i < len(d_uv) else None,
            })
        _state.weather_cache["daily"] = daily
        _state.weather_cache["last_fetch"] = time.time()
        print(f"Weather updated: {_state.weather_cache['data']['temperature']}°{_state.weather_cache['data']['unit']} {_state.weather_cache['data']['condition']}")
    except Exception as e:
        print(f"Weather fetch error: {e}")
