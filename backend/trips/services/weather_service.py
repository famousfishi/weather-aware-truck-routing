"""Gets hourly forecasts for many points at once, with de-duplication and caching."""

from datetime import date, datetime

from ..domain import GeoPoint, HourlyWeather, WeatherReading

# 0.1° ≈ 7 miles: nearby samples (and overlapping routes) share one forecast
GRID_DECIMALS = 1
CACHE_SECONDS = 30 * 60


def grid_key(point: GeoPoint) -> tuple[float, float]:
    return round(point.lat, GRID_DECIMALS), round(point.lng, GRID_DECIMALS)


class WeatherLookup:
    """Answers "what is the weather at this point at this time?" from already-fetched forecasts."""

    def __init__(self, forecasts: dict[tuple[float, float], HourlyWeather]):
        self._forecasts = forecasts

    def reading_at(self, point: GeoPoint, when: datetime) -> WeatherReading:
        return self._forecasts[grid_key(point)].reading_at(when)


class WeatherService:
    def __init__(self, weather_client, cache):
        self._client = weather_client
        self._cache = cache

    def forecast_for(self, points: list[GeoPoint], start: datetime, end: datetime) -> WeatherLookup:
        start_date, end_date = start.date(), end.date()
        forecasts: dict[tuple[float, float], HourlyWeather] = {}
        missing: list[tuple[float, float]] = []

        for key in {grid_key(point) for point in points}:
            cached = self._cache.get(
                self._cache_key(key, start_date, end_date))
            if cached:
                forecasts[key] = cached
            else:
                missing.append(key)

        if missing:
            fetched = self._client.fetch_hourly(
                [GeoPoint(lat, lng) for lat, lng in missing], start_date, end_date)
            for key, hourly in zip(missing, fetched):
                self._cache.set(self._cache_key(
                    key, start_date, end_date), hourly, CACHE_SECONDS)
                forecasts[key] = hourly

        return WeatherLookup(forecasts)

    @staticmethod
    def _cache_key(key: tuple[float, float], start_date: date, end_date: date) -> str:
        return f"weather:{key[0]}:{key[1]}:{start_date}:{end_date}"
