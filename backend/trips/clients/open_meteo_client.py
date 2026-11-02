"""Open-Meteo: free hourly forecasts, no API key (https://open-meteo.com)."""

from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone

import requests

from ..domain import GeoPoint, HourlyWeather
from .http import get_json


class OpenMeteoClient:
    FREE_URL = "https://api.open-meteo.com/v1/forecast"
    PAID_URL = "https://customer-api.open-meteo.com/v1/forecast"
    LOCATIONS_PER_REQUEST = 100
    PARALLEL_REQUESTS = 4

    def __init__(self, api_key: str = "", timeout: float = 25):
        self._api_key = api_key
        self._url = self.PAID_URL if api_key else self.FREE_URL
        self._timeout = timeout
        self._session = requests.Session()

    def fetch_hourly(self, points: list[GeoPoint], start_date: date, end_date: date) -> list[HourlyWeather]:
        """Hourly wind/rain/snow for every point, in the same order as `points`.

        Open-Meteo accepts many locations in one call, so we send them in batches, a few batches at a time.
        """
        with ThreadPoolExecutor(max_workers=self.PARALLEL_REQUESTS) as pool:
            results = pool.map(lambda batch: self._fetch_batch(
                batch, start_date, end_date), self.batches(points))
        return [hourly for batch_result in results for hourly in batch_result]

    def browser_requests(self, points: list[GeoPoint], start_date: date, end_date: date) -> list[dict]:
        """The same batched requests as fetch_hourly, as ready-to-call URLs for the browser to fetch."""
        return [
            {"url": self._browser_url(batch, start_date, end_date), "points": [
                [p.lat, p.lng] for p in batch]}
            for batch in self.batches(points)
        ]

    def _browser_url(self, points: list[GeoPoint], start_date: date, end_date: date) -> str:
        """The free endpoint with its query string filled in (the browser never needs an API key)."""
        return requests.Request("GET", self.FREE_URL, params=self._params(points, start_date, end_date)).prepare().url

    def batches(self, points: list[GeoPoint]) -> list[list[GeoPoint]]:
        return [points[i: i + self.LOCATIONS_PER_REQUEST] for i in range(0, len(points), self.LOCATIONS_PER_REQUEST)]

    def _fetch_batch(self, points: list[GeoPoint], start_date: date, end_date: date) -> list[HourlyWeather]:
        params = self._params(points, start_date, end_date)
        if self._api_key:
            params["apikey"] = self._api_key
        return self.parse(get_json(self._session, self._url, params, "Open-Meteo weather", self._timeout))

    @staticmethod
    def parse(body) -> list[HourlyWeather]:
        """One location comes back as an object, several as a list; either way, one HourlyWeather per location."""
        locations = body if isinstance(body, list) else [body]
        return [to_hourly_weather(location["hourly"]) for location in locations]

    @staticmethod
    def _params(points: list[GeoPoint], start_date: date, end_date: date) -> dict:
        return {
            "latitude": ",".join(f"{p.lat:.4f}" for p in points),
            "longitude": ",".join(f"{p.lng:.4f}" for p in points),
            "hourly": "wind_speed_10m,rain,showers,snowfall",
            "wind_speed_unit": "mph",
            "precipitation_unit": "inch",
            "timezone": "GMT",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }


def to_hourly_weather(hourly: dict) -> HourlyWeather:
    """Rain for the risk rules = "rain" (steady rain) + "showers" (thunderstorm-type rain)."""
    return HourlyWeather(
        first_hour=datetime.fromisoformat(
            hourly["time"][0]).replace(tzinfo=timezone.utc),
        wind_mph=[value or 0.0 for value in hourly["wind_speed_10m"]],
        rain_in_hr=[(rain or 0.0) + (showers or 0.0)
                    for rain, showers in zip(hourly["rain"], hourly["showers"])],
        snow_in_hr=[value or 0.0 for value in hourly["snowfall"]],
    )
