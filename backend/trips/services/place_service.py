"""Turns what the user typed into coordinates, and powers the search-as-you-type box."""

import hashlib

from ..domain import GeoPoint, LocationInput, Place
from ..dtos import PlaceDto
from ..exceptions import LocationNotFoundError

CACHE_SECONDS = 24 * 60 * 60
MIN_SUGGEST_LENGTH = 3


class PlaceService:
    def __init__(self, geocoder, cache):
        self._geocoder = geocoder
        self._cache = cache

    def resolve(self, location: LocationInput) -> Place:
        if location.has_coordinates:
            return Place(location.query, GeoPoint(location.lat, location.lng))

        place = self._cached("geocode", location.query,
                             lambda: self._geocoder.geocode(location.query))
        if place is None:
            raise LocationNotFoundError(location.query)
        return place

    def suggest(self, query: str) -> list[PlaceDto]:
        query = query.strip()
        if len(query) < MIN_SUGGEST_LENGTH:
            return []
        places = self._cached(
            "suggest", query, lambda: self._geocoder.suggest(query))
        return [PlaceDto.from_place(place) for place in places]

    def _cached(self, kind: str, query: str, load):
        key = f"{kind}:{hashlib.sha1(query.lower().encode()).hexdigest()}"
        value = self._cache.get(key)
        if value is None:
            value = load()
            if value:
                self._cache.set(key, value, CACHE_SECONDS)
        return value
