"""Small geometry helpers: distances, positions along a route, and trimming polylines."""

import math
from bisect import bisect_left, bisect_right

from .domain import GeoPoint

EARTH_RADIUS_MILES = 3958.8
METERS_PER_MILE = 1609.344


def distance_miles(a: GeoPoint, b: GeoPoint) -> float:
    """Straight-line distance over the Earth's surface (haversine formula)."""
    lat1, lat2 = math.radians(a.lat), math.radians(b.lat)
    d_lat = lat2 - lat1
    d_lng = math.radians(b.lng - a.lng)
    h = math.sin(d_lat / 2) ** 2 + math.cos(lat1) * \
        math.cos(lat2) * math.sin(d_lng / 2) ** 2
    return 2 * EARTH_RADIUS_MILES * math.asin(math.sqrt(h))


def cumulative_miles(points: list[GeoPoint]) -> list[float]:
    """Miles from the start of the path to each point."""
    totals = [0.0]
    for previous, current in zip(points, points[1:]):
        totals.append(totals[-1] + distance_miles(previous, current))
    return totals


def interpolate(x: float, xs: list[float], ys: list[float]) -> float:
    """Linear interpolation of y at x, given sorted xs. Values outside the range are clamped."""
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    index = bisect_right(xs, x)
    x0, x1, y0, y1 = xs[index - 1], xs[index], ys[index - 1], ys[index]
    if x1 == x0:
        return y1
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


def point_at_mile(points: list[GeoPoint], miles: list[float], mile: float) -> GeoPoint:
    """The position on the path `mile` miles from the start."""
    if mile <= miles[0]:
        return points[0]
    if mile >= miles[-1]:
        return points[-1]
    index = bisect_right(miles, mile)
    start, end = miles[index - 1], miles[index]
    fraction = (mile - start) / (end - start) if end > start else 1.0
    a, b = points[index - 1], points[index]
    return GeoPoint(a.lat + (b.lat - a.lat) * fraction, a.lng + (b.lng - a.lng) * fraction)


def thin_path(points: list[GeoPoint], miles: list[float], min_gap_miles: float) -> tuple[list[GeoPoint], list[float]]:
    """Drops points closer than `min_gap_miles` to the last kept one, so the map gets a lighter line."""
    kept_points, kept_miles = [points[0]], [miles[0]]
    for point, mile in zip(points[1:-1], miles[1:-1]):
        if mile - kept_miles[-1] >= min_gap_miles:
            kept_points.append(point)
            kept_miles.append(mile)
    if len(points) > 1:
        kept_points.append(points[-1])
        kept_miles.append(miles[-1])
    return kept_points, kept_miles


def slice_path(points: list[GeoPoint], miles: list[float], start_mile: float, end_mile: float) -> list[GeoPoint]:
    """The part of the path between two mile marks, with exact end points."""
    first_inside = bisect_right(miles, start_mile)
    first_after = bisect_left(miles, end_mile)
    return [
        point_at_mile(points, miles, start_mile),
        *points[first_inside:first_after],
        point_at_mile(points, miles, end_mile),
    ]
