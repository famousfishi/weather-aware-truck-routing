"""Gets 3 truck route options from the routing provider."""

import logging
import math
from datetime import datetime

from ..domain import GeoPoint, RouteOption
from ..exceptions import ExternalServiceError, RouteNotFoundError

logger = logging.getLogger(__name__)

ROUTES_WANTED = 3
EMPTY_TRACTOR_TRAILER_LB = 35_000
LEGAL_GROSS_LIMIT_LB = 80_000
KG_PER_LB = 0.45359237
DETOUR_OFFSETS = (0.15, -0.15, 0.3, -0.3)
SAME_ROUTE_DISTANCE_DIFFERENCE = 0.005


class RouteService:
    def __init__(self, router):
        self._router = router

    def find_routes(self, origin: GeoPoint, destination: GeoPoint, departure_time: datetime, load_weight_lb: int) -> list[RouteOption]:
        """Asks for the best route plus 2 alternatives. If the provider returns fewer than 3 distinct
        routes (common on short trips), we ask for routes through a point off to each side of the
        straight line to find genuinely different roads. Result is sorted fastest first.
        """
        weight_kg = gross_vehicle_weight_kg(load_weight_lb)
        routes = self._router.calculate_routes(
            [origin, destination], departure_time, weight_kg, ROUTES_WANTED - 1)
        if not routes:
            raise RouteNotFoundError()

        for via in detour_points(origin, destination):
            if len(routes) >= ROUTES_WANTED:
                break
            detour = self._try_route_through(
                origin, via, destination, departure_time, weight_kg)
            if detour and not any(is_same_route(detour, existing) for existing in routes):
                routes.append(detour)

        return sorted(routes, key=lambda route: route.travel_time_seconds)

    def _try_route_through(self, origin, via, destination, departure_time, weight_kg) -> RouteOption | None:
        try:
            routes = self._router.calculate_routes(
                [origin, via, destination], departure_time, weight_kg, 0)
        except ExternalServiceError as error:
            logger.info("Detour through %s skipped: %s", via, error)
            return None
        return routes[0] if routes else None


def gross_vehicle_weight_kg(load_weight_lb: int) -> int:
    """Routing restrictions care about the whole truck, not just the cargo (capped at the US legal limit)."""
    gross_lb = min(load_weight_lb + EMPTY_TRACTOR_TRAILER_LB,
                   LEGAL_GROSS_LIMIT_LB)
    return round(gross_lb * KG_PER_LB)


def detour_points(origin: GeoPoint, destination: GeoPoint) -> list[GeoPoint]:
    """Points beside the midpoint of the trip, pushed sideways by a share of the trip length."""
    mid_lat = (origin.lat + destination.lat) / 2
    mid_lng = (origin.lng + destination.lng) / 2
    lng_scale = math.cos(math.radians(mid_lat))
    east = (destination.lng - origin.lng) * lng_scale
    north = destination.lat - origin.lat
    return [GeoPoint(mid_lat + east * share, mid_lng - north * share / lng_scale) for share in DETOUR_OFFSETS]


def is_same_route(a: RouteOption, b: RouteOption) -> bool:
    longer = max(a.distance_meters, b.distance_meters) or 1
    return abs(a.distance_meters - b.distance_meters) / longer < SAME_ROUTE_DISTANCE_DIFFERENCE
