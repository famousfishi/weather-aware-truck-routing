"""Checks that real provider responses are parsed correctly (sample payloads, no network)."""

from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

from django.test import SimpleTestCase

from trips.clients.http import read_error_detail
from trips.clients.open_meteo_client import to_hourly_weather
from trips.clients.tomtom_client import depart_at_value, to_place, to_route_option

TOMTOM_ROUTE = {
    "summary": {"lengthInMeters": 10000, "travelTimeInSeconds": 600, "trafficDelayInSeconds": 30},
    "legs": [{"points": [{"latitude": 39.0, "longitude": -105.0}, {"latitude": 39.05, "longitude": -104.95}]}],
    "progress": [
        {"pointIndex": 0, "distanceInMeters": 0, "travelTimeInSeconds": 0},
        {"pointIndex": 1, "distanceInMeters": 10000, "travelTimeInSeconds": 600},
    ],
    "guidance": {
        "instructions": [
            {"routeOffsetInMeters": 0, "travelTimeInSeconds": 0,
                "roadNumbers": ["I-25"]},
            {"routeOffsetInMeters": 2000, "travelTimeInSeconds": 150,
                "roadNumbers": ["I-70", "US-40"]},
            {"routeOffsetInMeters": 10000, "travelTimeInSeconds": 600},
        ]
    },
}


class TomTomParsingTests(SimpleTestCase):
    def test_route_option(self):
        route = to_route_option(TOMTOM_ROUTE)
        self.assertEqual(len(route.points), 2)
        self.assertEqual(route.travel_time_seconds, 600)
        self.assertEqual(route.traffic_delay_seconds, 30)
        self.assertEqual(route.time_profile[0], (0.0, 0.0))
        self.assertEqual(route.time_profile[-1], (10000, 600))
        self.assertEqual(route.via_roads, ["I-70", "US-40"])

    def test_falls_back_to_instructions_when_progress_is_missing(self):
        raw = {**TOMTOM_ROUTE, "progress": None}
        self.assertIn((2000, 150), to_route_option(raw).time_profile)

    def test_place_label_includes_poi_name(self):
        place = to_place({"position": {"lat": 1, "lon": 2}, "address": {
                         "freeformAddress": "Dallas, TX"}, "poi": {"name": "Depot"}})
        self.assertEqual(place.label, "Depot, Dallas, TX")

    def test_past_departure_is_sent_as_now(self):
        self.assertEqual(depart_at_value(datetime.now(
            timezone.utc) - timedelta(minutes=5)), "now")
        future = datetime(2099, 1, 1, 8, 30, tzinfo=timezone.utc)
        self.assertEqual(depart_at_value(future), "2099-01-01T08:30:00+00:00")


class OpenMeteoParsingTests(SimpleTestCase):
    def test_rain_adds_showers_and_nulls_become_zero(self):
        hourly = to_hourly_weather({
            "time": ["2026-11-01T00:00", "2026-11-01T01:00"],
            "wind_speed_10m": [12.5, None],
            "rain": [0.05, 0.1],
            "showers": [0.07, None],
            "snowfall": [0.0, 0.6],
        })
        self.assertEqual(hourly.first_hour, datetime(
            2026, 11, 1, tzinfo=timezone.utc))
        self.assertEqual(hourly.wind_mph, [12.5, 0.0])
        self.assertAlmostEqual(hourly.rain_in_hr[0], 0.12)
        self.assertEqual(hourly.snow_in_hr, [0.0, 0.6])
        self.assertEqual(hourly.reading_at(
            datetime(2026, 11, 1, 0, 50, tzinfo=timezone.utc)).snow_in_hr, 0.6)


class ErrorDetailTests(SimpleTestCase):
    def response(self, body):
        response = Mock(status_code=400)
        response.json.return_value = body
        return response

    def test_reads_tomtom_and_open_meteo_error_shapes(self):
        self.assertEqual(read_error_detail(self.response(
            {"detailedError": {"message": "No route"}})), "No route")
        self.assertEqual(read_error_detail(self.response(
            {"error": {"description": "Bad key"}})), "Bad key")
        self.assertEqual(read_error_detail(self.response(
            {"error": True, "reason": "Too many days"})), "Too many days")
