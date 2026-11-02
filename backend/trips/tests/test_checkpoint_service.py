from datetime import datetime, timedelta, timezone

from django.test import SimpleTestCase

from trips.domain import GeoPoint, RouteOption
from trips.geo import METERS_PER_MILE, cumulative_miles
from trips.services.checkpoint_service import checkpoint_marks, place_checkpoints

DEPARTURE = datetime(2026, 11, 1, 8, tzinfo=timezone.utc)


def straight_route(points_count=500):
    """A route due east along the equator (1° of longitude ≈ 69.1 miles there)."""
    points = [GeoPoint(0.0, i * 0.01) for i in range(points_count + 1)]
    miles = cumulative_miles(points)
    meters = miles[-1] * METERS_PER_MILE
    # The first half is slow (30 mph), the second half fast (60 mph).
    half_seconds = (miles[-1] / 2) / 30 * 3600
    total_seconds = half_seconds + (miles[-1] / 2) / 60 * 3600
    profile = [(0.0, 0.0), (meters / 2, half_seconds), (meters, total_seconds)]
    return RouteOption(points, meters, int(total_seconds), 0, profile, []), miles


class CheckpointMarkTests(SimpleTestCase):
    def test_marks_every_interval_and_at_destination(self):
        self.assertEqual(checkpoint_marks(60, 25), [0, 25, 50, 60])

    def test_tiny_last_gap_is_merged_into_destination(self):
        self.assertEqual(checkpoint_marks(50.4, 25), [0, 25, 50.4])


class PlaceCheckpointTests(SimpleTestCase):
    def test_covered_miles_add_up_to_route_length(self):
        route, miles = straight_route()
        checkpoints = place_checkpoints(route, miles, 10, DEPARTURE)
        self.assertAlmostEqual(
            sum(c.covered_miles for c in checkpoints), miles[-1], places=6)

    def test_eta_follows_the_speed_profile(self):
        route, miles = straight_route()
        checkpoints = place_checkpoints(route, miles, 10, DEPARTURE)
        halfway = miles[-1] / 2
        quarter = next(c for c in checkpoints if abs(c.mile - 100) < 1e-6)
        # 100 miles at 30 mph = 3h20m (still in the slow first half of a ~345 mile route).
        self.assertLess(100, halfway)
        self.assertAlmostEqual(
            (quarter.eta - DEPARTURE).total_seconds(), 100 / 30 * 3600, delta=1)
        self.assertEqual(checkpoints[0].eta, DEPARTURE)
        expected_arrival = DEPARTURE + \
            timedelta(seconds=route.travel_time_seconds)
        self.assertAlmostEqual(
            checkpoints[-1].eta, expected_arrival, delta=timedelta(seconds=1))

    def test_checkpoint_positions_lie_on_the_route(self):
        route, miles = straight_route()
        for checkpoint in place_checkpoints(route, miles, 50, DEPARTURE):
            self.assertAlmostEqual(checkpoint.point.lat, 0.0)
