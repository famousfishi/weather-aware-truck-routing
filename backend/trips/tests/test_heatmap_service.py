from django.test import SimpleTestCase

from trips.domain import GeoPoint
from trips.geo import cumulative_miles, distance_miles
from trips.services.heatmap_service import MAX_CELLS, build_corridor


def path(start, end, steps=200):
    points = [GeoPoint(start.lat + (end.lat - start.lat) * i / steps, start.lng +
                       (end.lng - start.lng) * i / steps) for i in range(steps + 1)]
    return points, cumulative_miles(points)


class CorridorTests(SimpleTestCase):
    def test_short_trip_gets_fine_cells(self):
        grid = build_corridor(
            [path(GeoPoint(39.7, -105.0), GeoPoint(38.8, -104.8))])
        self.assertEqual(grid.cell_size_deg, 0.1)
        self.assertLessEqual(len(grid.cells), MAX_CELLS)

    def test_cross_country_trip_stays_under_the_cell_limit(self):
        grid = build_corridor(
            [path(GeoPoint(34.05, -118.24), GeoPoint(40.71, -74.0))])
        self.assertLessEqual(len(grid.cells), MAX_CELLS)
        self.assertGreater(grid.cell_size_deg, 0.1)

    def test_every_route_point_has_a_nearby_cell(self):
        points, miles = path(GeoPoint(39.7, -105.0), GeoPoint(41.9, -87.6))
        grid = build_corridor([(points, miles)])
        half_cell_diagonal_miles = grid.cell_size_deg * 69 * 0.75
        for point in points[::20]:
            nearest = min(distance_miles(point, cell) for cell in grid.cells)
            self.assertLessEqual(nearest, half_cell_diagonal_miles)
