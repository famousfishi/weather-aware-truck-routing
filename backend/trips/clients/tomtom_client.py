"""TomTom: geocoding, place suggestions and truck routing (https://developer.tomtom.com)."""

from collections import defaultdict
from datetime import datetime, timezone
from urllib.parse import quote

import requests

from ..domain import GeoPoint, Place, RouteOption
from ..exceptions import ExternalServiceError
from .http import get_json


class TomTomClient:
    BASE_URL = "https://api.tomtom.com"

    def __init__(self, api_key: str, country_set: str, timeout: float = 25):
        self._api_key = api_key
        self._country_set = country_set
        self._timeout = timeout
        self._session = requests.Session()

    def geocode(self, query: str) -> Place | None:
        body = self._get(
            f"/search/2/geocode/{quote(query)}.json",
            [("limit", 1), ("countrySet", self._country_set)],
            "TomTom geocoding",
        )
        results = body.get("results") or []
        return to_place(results[0]) if results else None

    def suggest(self, query: str, limit: int = 5) -> list[Place]:
        body = self._get(
            f"/search/2/search/{quote(query)}.json",
            [("typeahead", "true"), ("limit", limit), ("countrySet",
                                                       self._country_set), ("idxSet", "Geo,PAD,Addr,POI")],
            "TomTom search",
        )
        return [to_place(result) for result in body.get("results") or []]

    def calculate_routes(
        self, waypoints: list[GeoPoint], departure_time: datetime, vehicle_weight_kg: int, max_alternatives: int
    ) -> list[RouteOption]:
        locations = ":".join(
            f"{point.lat:.6f},{point.lng:.6f}" for point in waypoints)
        params = [
            ("maxAlternatives", max_alternatives),
            ("routeType", "fastest"),
            ("travelMode", "truck"),
            ("vehicleWeight", vehicle_weight_kg),
            ("vehicleCommercial", "true"),
            ("traffic", "true"),
            ("departAt", depart_at_value(departure_time)),
            ("instructionsType", "coded"),
            ("extendedRouteRepresentation", "distance"),
            ("extendedRouteRepresentation", "travelTime"),
        ]
        body = self._get(
            f"/routing/1/calculateRoute/{locations}/json", params, "TomTom routing")
        return [to_route_option(raw) for raw in body.get("routes") or []]

    def _get(self, path: str, params: list[tuple], service: str) -> dict:
        if not self._api_key:
            raise ExternalServiceError(
                service, "TOMTOM_API_KEY is not set on the server")
        return get_json(self._session, self.BASE_URL + path, [*params, ("key", self._api_key)], service, self._timeout)


def depart_at_value(departure_time: datetime) -> str:
    """TomTom only accepts future departure times, so anything not in the future becomes "now"."""
    if departure_time <= datetime.now(timezone.utc):
        return "now"
    return departure_time.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def to_place(result: dict) -> Place:
    position = result["position"]
    point = GeoPoint(position["lat"], position["lon"])
    address = (result.get("address") or {}).get(
        "freeformAddress") or f"{point.lat:.4f}, {point.lng:.4f}"
    poi_name = (result.get("poi") or {}).get("name")
    return Place(label=f"{poi_name}, {address}" if poi_name else address, point=point)


def to_route_option(raw: dict) -> RouteOption:
    summary = raw["summary"]
    instructions = (raw.get("guidance") or {}).get("instructions") or []
    return RouteOption(
        points=[GeoPoint(p["latitude"], p["longitude"])
                for leg in raw["legs"] for p in leg["points"]],
        distance_meters=summary["lengthInMeters"],
        travel_time_seconds=summary["travelTimeInSeconds"],
        traffic_delay_seconds=summary.get("trafficDelayInSeconds", 0),
        time_profile=time_profile(raw, summary, instructions),
        via_roads=main_roads(instructions),
    )


def time_profile(raw: dict, summary: dict, instructions: list[dict]) -> list[tuple[float, float]]:
    """(meters, seconds) pairs along the route, so we can tell when the truck reaches any point.

    Prefers TomTom's per-point "progress" data; falls back to the turn-by-turn instructions.
    """
    pairs = [
        (p["distanceInMeters"], p["travelTimeInSeconds"])
        for p in raw.get("progress") or []
        if "distanceInMeters" in p and "travelTimeInSeconds" in p
    ]
    if not pairs:
        pairs = [
            (i["routeOffsetInMeters"], i["travelTimeInSeconds"])
            for i in instructions
            if "routeOffsetInMeters" in i and "travelTimeInSeconds" in i
        ]
    return [(0.0, 0.0), *sorted(pairs), (summary["lengthInMeters"], summary["travelTimeInSeconds"])]


def main_roads(instructions: list[dict], limit: int = 2) -> list[str]:
    """The road numbers (e.g. I-70) the route spends the most distance on."""
    meters_by_road: dict[str, float] = defaultdict(float)
    for current, following in zip(instructions, instructions[1:]):
        stretch = following.get("routeOffsetInMeters", 0) - \
            current.get("routeOffsetInMeters", 0)
        for road in current.get("roadNumbers") or []:
            name = road if isinstance(road, str) else (
                road or {}).get("text", "")
            if name:
                meters_by_road[name] += stretch
    return sorted(meters_by_road, key=meters_by_road.get, reverse=True)[:limit]
