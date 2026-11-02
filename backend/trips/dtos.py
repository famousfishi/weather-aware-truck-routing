"""Response shapes the API sends to the React app (the JSON contract)."""

from dataclasses import dataclass, field
from datetime import datetime

from .domain import Place


@dataclass
class PlaceDto:
    label: str
    lat: float
    lng: float

    @classmethod
    def from_place(cls, place: Place) -> "PlaceDto":
        return cls(label=place.label, lat=place.point.lat, lng=place.point.lng)


@dataclass
class WeatherDto:
    wind_mph: float
    rain_in_hr: float
    snow_in_hr: float


@dataclass
class CheckpointDto:
    mile: float
    lat: float
    lng: float
    eta: datetime
    weather: WeatherDto
    risk_level: int
    risk_label: str
    reasons: list[str]


@dataclass
class RiskSegmentDto:
    risk_level: int
    path: list[list[float]]


@dataclass
class RouteSummaryDto:
    low_miles: float
    moderate_miles: float
    high_miles: float
    severe_miles: float
    no_travel_miles: float
    average_risk: float
    worst_risk_level: int


@dataclass
class RouteDto:
    id: str
    name: str
    via: list[str]
    distance_miles: float
    duration_seconds: int
    traffic_delay_seconds: int
    departure_time: datetime
    arrival_time: datetime
    summary: RouteSummaryDto
    segments: list[RiskSegmentDto]
    checkpoints: list[CheckpointDto]
    rank: int = 0
    is_recommended: bool = False


@dataclass
class RecommendationDto:
    route_id: str
    headline: str
    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class HeatCellDto:
    lat: float
    lng: float
    risk_level: list[int]
    wind_mph: list[float]
    rain_in_hr: list[float]
    snow_in_hr: list[float]


@dataclass
class HeatmapDto:
    start_time: datetime
    hours: int
    cell_size_deg: float
    cells: list[HeatCellDto]


@dataclass
class TripPlanDto:
    origin: PlaceDto
    destination: PlaceDto
    load_weight_lb: int
    sample_interval_miles: int
    routes: list[RouteDto]
    recommendation: RecommendationDto
    heatmap: HeatmapDto
