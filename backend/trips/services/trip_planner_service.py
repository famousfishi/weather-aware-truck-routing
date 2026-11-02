"""The orchestrator: one method that runs the whole "plan a trip" use case, step by step."""

from datetime import timedelta

from ..domain import Checkpoint, GeoPoint, RouteOption, TripRequest
from ..dtos import PlaceDto, RouteDto, TripPlanDto
from ..geo import METERS_PER_MILE, cumulative_miles, thin_path
from . import route_assessment_service as assessment
from .checkpoint_service import place_checkpoints
from .heatmap_service import HEATMAP_HOURS, build_corridor, build_heatmap
from .place_service import PlaceService
from .recommendation_service import build_recommendation, rank_routes
from .risk_service import assess
from .route_service import RouteService
from .weather_service import WeatherLookup, WeatherService

DISPLAY_POINT_SPACING_MILES = 0.25


class TripPlannerService:
    def __init__(self, places: PlaceService, routes: RouteService, weather: WeatherService):
        self._places = places
        self._routes = routes
        self._weather = weather

    def plan_trip(self, request: TripRequest) -> TripPlanDto:
        # 1. Where are we going?
        origin = self._places.resolve(request.origin)
        destination = self._places.resolve(request.destination)

        # 2. Three ways to get there.
        options = self._routes.find_routes(
            origin.point, destination.point, request.departure_time, request.load_weight_lb)
        route_miles = [cumulative_miles(option.points) for option in options]

        # 3. Checkpoints every N miles, each with the time the truck gets there.
        checkpoints = [
            place_checkpoints(
                option, miles, request.sample_interval_miles, request.departure_time)
            for option, miles in zip(options, route_miles)
        ]

        # 4. Lighter route lines for the map, and the heatmap grid around them.
        display_paths = [thin_path(option.points, miles, DISPLAY_POINT_SPACING_MILES)
                         for option, miles in zip(options, route_miles)]
        corridor = build_corridor(display_paths)

        # 5. One weather fetch for every checkpoint and heatmap cell, covering the whole time window.
        heatmap_start = request.departure_time.replace(
            minute=0, second=0, microsecond=0)
        last_arrival = max(
            route_checkpoints[-1].eta for route_checkpoints in checkpoints)
        weather = self._weather.forecast_for(
            points=[
                c.point for route_checkpoints in checkpoints for c in route_checkpoints] + corridor.cells,
            start=heatmap_start,
            end=max(last_arrival, heatmap_start +
                    timedelta(hours=HEATMAP_HOURS)),
        )

        # 6. Score each route, then rank and explain.
        routes = [
            self._build_route(chr(ord("A") + index), option,
                              route_checkpoints, display_path, weather, request)
            for index, (option, route_checkpoints, display_path) in enumerate(zip(options, checkpoints, display_paths))
        ]
        ranked = rank_routes(routes)

        return TripPlanDto(
            origin=PlaceDto.from_place(origin),
            destination=PlaceDto.from_place(destination),
            load_weight_lb=request.load_weight_lb,
            sample_interval_miles=request.sample_interval_miles,
            routes=routes,
            recommendation=build_recommendation(ranked),
            heatmap=build_heatmap(
                corridor, weather, heatmap_start, request.load_weight_lb),
        )

    @staticmethod
    def _build_route(
        route_id: str,
        option: RouteOption,
        checkpoints: list[Checkpoint],
        display_path: tuple[list[GeoPoint], list[float]],
        weather: WeatherLookup,
        request: TripRequest,
    ) -> RouteDto:
        assessed = []
        for checkpoint in checkpoints:
            reading = weather.reading_at(checkpoint.point, checkpoint.eta)
            assessed.append((checkpoint, reading, assess(
                reading, request.load_weight_lb)))

        path_points, path_miles = display_path
        return RouteDto(
            id=route_id,
            name=f"Route {route_id}",
            via=option.via_roads,
            distance_miles=round(option.distance_meters / METERS_PER_MILE, 1),
            duration_seconds=option.travel_time_seconds,
            traffic_delay_seconds=option.traffic_delay_seconds,
            departure_time=request.departure_time,
            arrival_time=request.departure_time +
            timedelta(seconds=option.travel_time_seconds),
            summary=assessment.summarize(assessed),
            segments=assessment.build_segments(
                path_points, path_miles, assessed),
            checkpoints=[assessment.to_checkpoint_dto(
                *item) for item in assessed],
        )
