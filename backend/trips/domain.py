"""Internal models the services pass between each other (never sent to the browser directly)."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum


class RiskLevel(IntEnum):
    LOW = 0
    MODERATE = 1
    HIGH = 2
    SEVERE = 3
    NO_TRAVEL = 4

    @property
    def label(self) -> str:
        return self.name.replace("_", " ").title()


@dataclass(frozen=True)
class GeoPoint:
    lat: float
    lng: float


@dataclass(frozen=True)
class Place:
    label: str
    point: GeoPoint


@dataclass(frozen=True)
class LocationInput:
    query: str
    lat: float | None = None
    lng: float | None = None

    @property
    def has_coordinates(self) -> bool:
        return self.lat is not None and self.lng is not None


@dataclass(frozen=True)
class TripRequest:
    origin: LocationInput
    destination: LocationInput
    departure_time: datetime
    load_weight_lb: int
    sample_interval_miles: int
    # forecasts the browser fetched (browser-weather mode)
    browser_weather: list[dict] = field(default_factory=list)


@dataclass
class RouteOption:
    """One drivable route as the routing provider returned it."""

    points: list[GeoPoint]
    distance_meters: float
    travel_time_seconds: int
    traffic_delay_seconds: int
    # (meters from start, seconds from start)
    time_profile: list[tuple[float, float]]
    via_roads: list[str]


@dataclass
class Checkpoint:
    """A spot on a route where we sample the weather, and the stretch of road it stands for."""

    mile: float
    point: GeoPoint
    eta: datetime
    covers_from_mile: float
    covers_to_mile: float

    @property
    def covered_miles(self) -> float:
        return self.covers_to_mile - self.covers_from_mile


@dataclass(frozen=True)
class WeatherReading:
    wind_mph: float
    rain_in_hr: float
    snow_in_hr: float


@dataclass
class HourlyWeather:
    """Hour-by-hour forecast for one location, starting at first_hour (UTC)."""

    first_hour: datetime
    wind_mph: list[float]
    rain_in_hr: list[float]
    snow_in_hr: list[float]

    def reading_at(self, when: datetime) -> WeatherReading:
        hours_from_start = (when - self.first_hour).total_seconds() / 3600
        index = min(max(round(hours_from_start), 0), len(self.wind_mph) - 1)
        return WeatherReading(self.wind_mph[index], self.rain_in_hr[index], self.snow_in_hr[index])


@dataclass
class RiskAssessment:
    level: RiskLevel
    reasons: list[str]
