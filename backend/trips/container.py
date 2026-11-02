"""Each function here builds its object once and reuses it. Set USE_FAKE_PROVIDERS=true to swap
the real APIs for the offline demo clients without touching any service code.
"""

from functools import lru_cache

from django.conf import settings
from django.core.cache import cache

from .clients.fake_clients import FakeOpenMeteoClient, FakeTomTomClient
from .clients.open_meteo_client import OpenMeteoClient
from .clients.tomtom_client import TomTomClient
from .services.place_service import PlaceService
from .services.route_service import RouteService
from .services.trip_planner_service import TripPlannerService
from .services.weather_service import WeatherService


@lru_cache(maxsize=1)
def tomtom_client():
    if settings.USE_FAKE_PROVIDERS:
        return FakeTomTomClient()
    return TomTomClient(settings.TOMTOM_API_KEY, settings.GEOCODE_COUNTRY_SET)


@lru_cache(maxsize=1)
def weather_client():
    return FakeOpenMeteoClient() if settings.USE_FAKE_PROVIDERS else OpenMeteoClient(settings.OPEN_METEO_API_KEY)


@lru_cache(maxsize=1)
def place_service() -> PlaceService:
    return PlaceService(tomtom_client(), cache)


@lru_cache(maxsize=1)
def trip_planner() -> TripPlannerService:
    return TripPlannerService(
        places=place_service(),
        routes=RouteService(tomtom_client()),
        weather=WeatherService(weather_client(), cache),
    )


def reset():
    for factory in (tomtom_client, weather_client, place_service, trip_planner):
        factory.cache_clear()
