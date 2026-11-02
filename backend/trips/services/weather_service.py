"""Gets hourly forecasts for many points at once, with de-duplication and caching."""

from datetime import date, datetime

from ..domain import GeoPoint, HourlyWeather, WeatherReading
from ..exceptions import WeatherNeededError

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
    def __init__(self, weather_client, cache, from_browser: bool = False):
        self._client = weather_client
        self._cache = cache
        self._from_browser = from_browser

    def forecast_for(
        self, points: list[GeoPoint], start: datetime, end: datetime, browser_weather: list[dict] | None = None
    ) -> WeatherLookup:
        start_date, end_date = start.date(), end.date()
        if self._from_browser:
            return self._use_browser_weather(points, start_date, end_date, browser_weather or [])

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

    def _use_browser_weather(
        self, points: list[GeoPoint], start_date: date, end_date: date, browser_weather: list[dict]
    ) -> WeatherLookup:
        """The visitor's browser fetches the forecasts, so each visitor uses their own free Open-Meteo allowance.

        First call: nothing sent yet, so say which forecasts are needed. Second call: use what the browser sent.
        Browser data is only used for this one request, never cached for other visitors.
        """
        supplied: dict[tuple[float, float], HourlyWeather] = {}
        for batch in browser_weather:
            try:
                forecasts = self._client.parse(batch["body"])
            except (KeyError, IndexError, TypeError, ValueError):
                continue  # unreadable data: those points are simply asked for again
            for (lat, lng), hourly in zip(batch["points"], forecasts):
                supplied[(lat, lng)] = hourly

        needed = sorted({grid_key(point) for point in points})
        missing = [key for key in needed if key not in supplied]
        if missing:
            raise WeatherNeededError(
                self._client.browser_requests(
                    [GeoPoint(lat, lng) for lat, lng in missing], start_date, end_date)
            )
        return WeatherLookup({key: supplied[key] for key in needed})

    @staticmethod
    def _cache_key(key: tuple[float, float], start_date: date, end_date: date) -> str:
        return f"weather:{key[0]}:{key[1]}:{start_date}:{end_date}"
