"""TomTom: geocoding, place suggestions and truck routing (https://developer.tomtom.com)."""

from urllib.parse import quote

import requests

from ..domain import GeoPoint, Place
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

    def _get(self, path: str, params: list[tuple], service: str) -> dict:
        if not self._api_key:
            raise ExternalServiceError(
                service, "TOMTOM_API_KEY is not set on the server")
        return get_json(self._session, self.BASE_URL + path, [*params, ("key", self._api_key)], service, self._timeout)


def to_place(result: dict) -> Place:
    position = result["position"]
    point = GeoPoint(position["lat"], position["lon"])
    address = (result.get("address") or {}).get(
        "freeformAddress") or f"{point.lat:.4f}, {point.lng:.4f}"
    poi_name = (result.get("poi") or {}).get("name")
    return Place(label=f"{poi_name}, {address}" if poi_name else address, point=point)
