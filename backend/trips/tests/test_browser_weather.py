"""Browser-weather mode: the server asks for forecasts (HTTP 428), the browser fetches them and sends them back."""

from datetime import date, datetime, timedelta, timezone
from unittest import mock
from urllib.parse import parse_qs, urlparse

from django.core.cache import cache
from django.test import SimpleTestCase, override_settings
from django.utils import timezone as django_timezone

from trips import container
from trips.clients.fake_clients import FakeOpenMeteoClient, FakeTomTomClient
from trips.clients.open_meteo_client import OpenMeteoClient
from trips.domain import GeoPoint
from trips.exceptions import WeatherNeededError
from trips.services.weather_service import WeatherService

START = datetime(2026, 11, 2, 12, tzinfo=timezone.utc)
END = START + timedelta(hours=48)


def open_meteo_body(points: list[list[float]], start_date: date, end_date: date) -> list[dict]:
    """What Open-Meteo would send the browser for these points (built from the demo weather)."""
    forecasts = FakeOpenMeteoClient().fetch_hourly(
        [GeoPoint(lat, lng) for lat, lng in points], start_date, end_date)
    return [
        {
            "hourly": {
                "time": [(f.first_hour + timedelta(hours=h)).isoformat()[:16] for h in range(len(f.wind_mph))],
                "wind_speed_10m": f.wind_mph,
                "rain": f.rain_in_hr,
                "showers": [0.0] * len(f.rain_in_hr),
                "snowfall": f.snow_in_hr,
            }
        }
        for f in forecasts
    ]


def answer(weather_requests: list[dict]) -> list[dict]:
    """Plays the browser: "fetches" every requested URL and returns the points with the bodies."""
    batches = []
    for weather_request in weather_requests:
        query = parse_qs(urlparse(weather_request["url"]).query)
        start_date, end_date = date.fromisoformat(
            query["start_date"][0]), date.fromisoformat(query["end_date"][0])
        body = open_meteo_body(weather_request["points"], start_date, end_date)
        batches.append({"points": weather_request["points"], "body": body})
    return batches


class BrowserWeatherServiceTests(SimpleTestCase):
    def setUp(self):
        cache.clear()
        self.service = WeatherService(
            OpenMeteoClient(), cache, from_browser=True)
        self.points = [
            GeoPoint(39.74, -104.99), GeoPoint(39.71, -104.97), GeoPoint(41.88, -87.63)]

    def test_asks_for_each_grid_point_once_as_ready_to_call_urls(self):
        with self.assertRaises(WeatherNeededError) as raised:
            self.service.forecast_for(self.points, START, END)

        weather_requests = raised.exception.weather_requests
        self.assertEqual(len(weather_requests), 1)
        self.assertEqual(weather_requests[0]["points"], [
                         # the first two share a cell
                         [39.7, -105.0], [41.9, -87.6]])
        self.assertTrue(weather_requests[0]["url"].startswith(
            "https://api.open-meteo.com/v1/forecast?"))
        self.assertIn("start_date=2026-11-02", weather_requests[0]["url"])

    def test_uses_the_forecasts_the_browser_sent(self):
        with self.assertRaises(WeatherNeededError) as raised:
            self.service.forecast_for(self.points, START, END)

        lookup = self.service.forecast_for(
            self.points, START, END, answer(raised.exception.weather_requests))
        self.assertGreater(lookup.reading_at(
            self.points[0], START).wind_mph, 0)

    def test_unreadable_data_is_asked_for_again(self):
        with self.assertRaises(WeatherNeededError) as raised:
            self.service.forecast_for(self.points, START, END, [
                                      {"points": [[39.7, -105.0]], "body": {"error": True}}])
        self.assertEqual(raised.exception.weather_requests[0]["points"], [
                         [39.7, -105.0], [41.9, -87.6]])


@override_settings(USE_FAKE_PROVIDERS=False, WEATHER_FROM_BROWSER=True)
class BrowserWeatherApiTests(SimpleTestCase):
    def setUp(self):
        container.reset()
        cache.clear()
        # Real Open-Meteo client (it only builds URLs and reads answers here), demo routes instead of TomTom.
        self.router = FakeTomTomClient()
        self.router.calculate_routes = mock.Mock(
            wraps=self.router.calculate_routes)
        self.tomtom = mock.patch.object(
            container, "tomtom_client", return_value=self.router)
        self.tomtom.start()

    def tearDown(self):
        self.tomtom.stop()
        container.reset()

    def plan(self, departure: str, **extra):
        body = {
            "origin": {"query": "Denver, CO"},
            "destination": {"query": "Chicago, IL"},
            "departure_time": departure,
            "load_weight_lb": 42_000,
            **extra,
        }
        return self.client.post("/api/trips/plan", body, content_type="application/json")

    def test_first_call_asks_for_weather_second_call_returns_the_plan(self):
        departure = (django_timezone.now() + timedelta(hours=2)).isoformat()
        first = self.plan(departure)
        self.assertEqual(first.status_code, 428, first.content)
        weather_requests = first.json()["weather_requests"]
        self.assertTrue(all(len(item["points"]) <=
                        100 for item in weather_requests))
        routing_calls = self.router.calculate_routes.call_count

        second = self.plan(departure, weather=answer(weather_requests))
        self.assertEqual(second.status_code, 200, second.content[:300])
        plan = second.json()
        self.assertEqual([route["id"]
                         for route in plan["routes"]], ["A", "B", "C"])
        self.assertEqual(len(plan["heatmap"]["cells"][0]["risk_level"]), 49)
        self.assertEqual(self.router.calculate_routes.call_count,
                         routing_calls)  # same routes, from the cache
