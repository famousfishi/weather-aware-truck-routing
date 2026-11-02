"""Places weather checkpoints every N miles along a route and works out when the truck reaches each one."""

from datetime import datetime, timedelta

from ..domain import Checkpoint, RouteOption
from ..geo import interpolate, point_at_mile

MERGE_LAST_GAP_UNDER_MILES = 1.0


def place_checkpoints(route: RouteOption, route_miles: list[float], interval_miles: int, departure_time: datetime) -> list[Checkpoint]:
    """Checkpoints at mile 0, N, 2N, ... and at the destination.

    Each checkpoint "covers" the road halfway back to the previous checkpoint and halfway forward to the
    next one, so adding up covered miles gives exactly the route length (used for Severe/High miles).
    """
    total_miles = route_miles[-1]
    marks = checkpoint_marks(total_miles, interval_miles)

    checkpoints = []
    for index, mile in enumerate(marks):
        covers_from = 0.0 if index == 0 else (marks[index - 1] + mile) / 2
        covers_to = total_miles if index == len(
            marks) - 1 else (mile + marks[index + 1]) / 2
        checkpoints.append(
            Checkpoint(
                mile=mile,
                point=point_at_mile(route.points, route_miles, mile),
                eta=estimate_arrival(
                    route, mile / total_miles if total_miles else 0.0, departure_time),
                covers_from_mile=covers_from,
                covers_to_mile=covers_to,
            )
        )
    return checkpoints


def checkpoint_marks(total_miles: float, interval_miles: int) -> list[float]:
    marks = []
    mile = 0.0
    while mile < total_miles:
        marks.append(mile)
        mile += interval_miles

    if len(marks) > 1 and total_miles - marks[-1] < MERGE_LAST_GAP_UNDER_MILES:
        marks.pop()
    marks.append(total_miles)
    return marks


def estimate_arrival(route: RouteOption, fraction_of_route: float, departure_time: datetime) -> datetime:
    """Uses the provider's (distance, time) profile, so slow city stretches and fast highways are respected."""
    meters = fraction_of_route * route.distance_meters
    distances = [meters_from_start for meters_from_start,
                 _ in route.time_profile]
    seconds = [seconds_from_start for _,
               seconds_from_start in route.time_profile]
    return departure_time + timedelta(seconds=interpolate(meters, distances, seconds))
