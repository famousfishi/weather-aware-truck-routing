"""Builds the weather heatmap: a grid of cells covering the trip corridor, with risk for each hour 0–48."""

import math
from dataclasses import dataclass
from datetime import datetime, timedelta

from ..domain import GeoPoint
from ..dtos import HeatCellDto, HeatmapDto
from ..geo import distance_miles, point_at_mile
from .risk_service import assess
from .weather_service import WeatherLookup

HEATMAP_HOURS = 48
CORRIDOR_RADIUS_MILES = 30
ANCHOR_SPACING_MILES = 10
MAX_CELLS = 300
CELL_SIZES_DEG = (0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.75, 1.0)
MILES_PER_DEGREE_LAT = 69.0


@dataclass
class CorridorGrid:
    cell_size_deg: float
    cells: list[GeoPoint]


def build_corridor(paths: list[tuple[list[GeoPoint], list[float]]]) -> CorridorGrid:
    """Square cells within ~30 miles of any route. Short trips get small cells (more detail); long
    trips get bigger cells so the cell count stays under MAX_CELLS (keeps the API calls and the
    browser fast).
    """
    anchors = [
        point_at_mile(points, miles, mile)
        for points, miles in paths
        for mile in frange(0, miles[-1], ANCHOR_SPACING_MILES)
    ]
    cells: list[GeoPoint] = []
    for size in CELL_SIZES_DEG:
        cells = cells_near(anchors, size)
        if len(cells) <= MAX_CELLS:
            return CorridorGrid(size, cells)
    step = math.ceil(len(cells) / MAX_CELLS)
    return CorridorGrid(CELL_SIZES_DEG[-1], cells[::step])


def cells_near(anchors: list[GeoPoint], size: float) -> list[GeoPoint]:
    reach_miles = CORRIDOR_RADIUS_MILES + size * MILES_PER_DEGREE_LAT / 2
    reach_lat = reach_miles / MILES_PER_DEGREE_LAT
    found: set[tuple[int, int]] = set()

    for anchor in anchors:
        reach_lng = reach_lat / max(math.cos(math.radians(anchor.lat)), 0.2)
        for row in range(math.floor((anchor.lat - reach_lat) / size), math.floor((anchor.lat + reach_lat) / size) + 1):
            for col in range(math.floor((anchor.lng - reach_lng) / size), math.floor((anchor.lng + reach_lng) / size) + 1):
                if (row, col) not in found and distance_miles(cell_center(row, col, size), anchor) <= reach_miles:
                    found.add((row, col))

    return [cell_center(row, col, size) for row, col in sorted(fill_enclosed_gaps(found))]


def fill_enclosed_gaps(found: set[tuple[int, int]]) -> set[tuple[int, int]]:
    """Adds empty cells that have corridor cells on all four sides, so the land between two
    routes that split apart is covered too instead of showing blank holes.
    """
    row_spans: dict[int, tuple[int, int]] = {}
    col_spans: dict[int, tuple[int, int]] = {}
    for row, col in found:
        first, last = row_spans.get(row, (col, col))
        row_spans[row] = (min(first, col), max(last, col))
        first, last = col_spans.get(col, (row, row))
        col_spans[col] = (min(first, row), max(last, row))

    filled = set(found)
    for row, (first_col, last_col) in row_spans.items():
        for col in range(first_col, last_col + 1):
            first_row, last_row = col_spans.get(col, (row + 1, row - 1))
            if first_row <= row <= last_row:
                filled.add((row, col))
    return filled


def cell_center(row: int, col: int, size: float) -> GeoPoint:
    return GeoPoint(round((row + 0.5) * size, 4), round((col + 0.5) * size, 4))


def build_heatmap(grid: CorridorGrid, weather: WeatherLookup, start_time: datetime, load_weight_lb: int) -> HeatmapDto:
    hours = [start_time + timedelta(hours=offset)
             for offset in range(HEATMAP_HOURS + 1)]
    cells = []
    for center in grid.cells:
        readings = [weather.reading_at(center, hour) for hour in hours]
        cells.append(
            HeatCellDto(
                lat=center.lat,
                lng=center.lng,
                risk_level=[int(assess(reading, load_weight_lb).level)
                            for reading in readings],
                wind_mph=[round(reading.wind_mph) for reading in readings],
                rain_in_hr=[round(reading.rain_in_hr, 2)
                            for reading in readings],
                snow_in_hr=[round(reading.snow_in_hr, 1)
                            for reading in readings],
            )
        )
    return HeatmapDto(start_time=start_time, hours=HEATMAP_HOURS, cell_size_deg=grid.cell_size_deg, cells=cells)


def frange(start: float, stop: float, step: float) -> list[float]:
    values = []
    value = start
    while value <= stop:
        values.append(value)
        value += step
    return values
