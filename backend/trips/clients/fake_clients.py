"""Stand-ins for TomTom and Open-Meteo used by the tests and by demo mode (USE_FAKE_PROVIDERS=true).

They return believable, repeatable data with no API keys and no internet: three curved routes between
any two known cities, and a storm that drifts east across the Plains with a snow band to the north.
"""

import math
from datetime import date, datetime, time, timezone

from ..domain import GeoPoint, HourlyWeather, Place, RouteOption
from ..geo import METERS_PER_MILE, cumulative_miles, distance_miles

KNOWN_PLACES = {
    "denver": Place("Denver, CO", GeoPoint(39.7392, -104.9903)),
    "chicago": Place("Chicago, IL", GeoPoint(41.8781, -87.6298)),
    "dallas": Place("Dallas, TX", GeoPoint(32.7767, -96.7970)),
    "kansas city": Place("Kansas City, MO", GeoPoint(39.0997, -94.5786)),
    "omaha": Place("Omaha, NE", GeoPoint(41.2565, -95.9345)),
    "st. louis": Place("St. Louis, MO", GeoPoint(38.6270, -90.1994)),
    "oklahoma city": Place("Oklahoma City, OK", GeoPoint(35.4676, -97.5164)),
    "minneapolis": Place("Minneapolis, MN", GeoPoint(44.9778, -93.2650)),
    "salt lake city": Place("Salt Lake City, UT", GeoPoint(40.7608, -111.8910)),
    "atlanta": Place("Atlanta, GA", GeoPoint(33.7490, -84.3880)),
}

ROUTE_SHAPES = [(0.0, 60, ["I-80", "I-76"]), (0.12, 57,
                                              ["I-80", "I-29"]), (-0.18, 58, ["I-70"])]


class FakeTomTomClient:
    def geocode(self, query: str) -> Place | None:
        text = query.lower().strip()
        return next((place for name, place in KNOWN_PLACES.items() if text.startswith(name)), None)

    def suggest(self, query: str, limit: int = 5) -> list[Place]:
        text = query.lower().strip()
        return [place for name, place in KNOWN_PLACES.items() if text in name][:limit]

    def calculate_routes(self, waypoints, departure_time, vehicle_weight_kg, max_alternatives) -> list[RouteOption]:
        if len(waypoints) > 2:
            return [self._route(join_straight_lines(waypoints), 55, ["US-36"])]
        origin, destination = waypoints
        return [
            self._route(curved_line(origin, destination, bend), speed, roads)
            for bend, speed, roads in ROUTE_SHAPES[: max_alternatives + 1]
        ]

    @staticmethod
    def _route(points: list[GeoPoint], speed_mph: float, roads: list[str]) -> RouteOption:
        miles = cumulative_miles(points)[-1]
        seconds = int(miles / speed_mph * 3600)
        meters = miles * METERS_PER_MILE
        return RouteOption(points, meters, seconds, 0, [(0.0, 0.0), (meters, seconds)], roads)


class FakeOpenMeteoClient:
    def fetch_hourly(self, points: list[GeoPoint], start_date: date, end_date: date) -> list[HourlyWeather]:
        first_hour = datetime.combine(start_date, time(0), tzinfo=timezone.utc)
        hours = ((end_date - start_date).days + 1) * 24
        return [self._forecast(point, first_hour, hours) for point in points]

    @staticmethod
    def _forecast(point: GeoPoint, first_hour: datetime, hours: int) -> HourlyWeather:
        wind, rain, snow = [], [], []
        for hour in range(hours):
            storm_center = GeoPoint(40.2, -101.0 + 0.3 * (hour % 72))
            storm = math.exp(-((distance_miles(point, storm_center) / 110) ** 2))
            snow_band = math.exp(-((distance_miles(point,
                                 GeoPoint(42.4, -95.5)) / 90) ** 2))
            wind.append(round(12 + 46 * storm, 1))
            rain.append(round(0.85 * storm, 2))
            snow.append(round(2.6 * snow_band, 2))
        return HourlyWeather(first_hour, wind, rain, snow)


def curved_line(origin: GeoPoint, destination: GeoPoint, bend: float, steps: int = 300) -> list[GeoPoint]:
    """A smooth arc from origin to destination; `bend` pushes the middle sideways."""
    mid = GeoPoint((origin.lat + destination.lat) / 2,
                   (origin.lng + destination.lng) / 2)
    control = GeoPoint(mid.lat + (destination.lng - origin.lng)
                       * bend, mid.lng - (destination.lat - origin.lat) * bend)
    points = []
    for step in range(steps + 1):
        t = step / steps
        a, b, c = (1 - t) ** 2, 2 * (1 - t) * t, t**2
        points.append(GeoPoint(a * origin.lat + b * control.lat + c *
                      destination.lat, a * origin.lng + b * control.lng + c * destination.lng))
    return points


def join_straight_lines(waypoints: list[GeoPoint], steps: int = 100) -> list[GeoPoint]:
    points = [waypoints[0]]
    for start, end in zip(waypoints, waypoints[1:]):
        for step in range(1, steps + 1):
            t = step / steps
            points.append(GeoPoint(start.lat + (end.lat - start.lat)
                          * t, start.lng + (end.lng - start.lng) * t))
    return points
