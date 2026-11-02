"""Applies the risk rules to a whole route: per-checkpoint results, mile totals and colored map segments."""

from ..domain import Checkpoint, GeoPoint, RiskAssessment, RiskLevel, WeatherReading
from ..dtos import CheckpointDto, RiskSegmentDto, RouteSummaryDto, WeatherDto
from ..geo import slice_path

AssessedCheckpoint = tuple[Checkpoint, WeatherReading, RiskAssessment]


def to_checkpoint_dto(checkpoint: Checkpoint, weather: WeatherReading, risk: RiskAssessment) -> CheckpointDto:
    return CheckpointDto(
        mile=round(checkpoint.mile, 1),
        lat=round(checkpoint.point.lat, 5),
        lng=round(checkpoint.point.lng, 5),
        eta=checkpoint.eta,
        weather=WeatherDto(
            wind_mph=round(weather.wind_mph, 1),
            rain_in_hr=round(weather.rain_in_hr, 2),
            snow_in_hr=round(weather.snow_in_hr, 2),
        ),
        risk_level=int(risk.level),
        risk_label=risk.level.label,
        reasons=risk.reasons,
    )


def summarize(assessed: list[AssessedCheckpoint]) -> RouteSummaryDto:
    """Miles driven at each risk level, plus the mileage-weighted average risk (0 = Low … 4 = No Travel)."""
    miles_by_level = {level: 0.0 for level in RiskLevel}
    for checkpoint, _, risk in assessed:
        miles_by_level[risk.level] += checkpoint.covered_miles

    total_miles = sum(miles_by_level.values())
    weighted_risk = sum(int(level) * miles for level,
                        miles in miles_by_level.items())
    return RouteSummaryDto(
        low_miles=round(miles_by_level[RiskLevel.LOW], 1),
        moderate_miles=round(miles_by_level[RiskLevel.MODERATE], 1),
        high_miles=round(miles_by_level[RiskLevel.HIGH], 1),
        severe_miles=round(miles_by_level[RiskLevel.SEVERE], 1),
        no_travel_miles=round(miles_by_level[RiskLevel.NO_TRAVEL], 1),
        average_risk=round(weighted_risk / total_miles,
                           2) if total_miles else 0.0,
        worst_risk_level=int(
            max((risk.level for _, _, risk in assessed), default=RiskLevel.LOW)),
    )


def build_segments(path: list[GeoPoint], path_miles: list[float], assessed: list[AssessedCheckpoint]) -> list[RiskSegmentDto]:
    """Splits the route line into pieces colored by risk. Neighbouring checkpoints with the same
    level are merged, so a calm 300-mile stretch is one line instead of thirty.
    """
    stretches: list[list] = []  # [level, from_mile, to_mile]
    for checkpoint, _, risk in assessed:
        if stretches and stretches[-1][0] == risk.level:
            stretches[-1][2] = checkpoint.covers_to_mile
        else:
            stretches.append(
                [risk.level, checkpoint.covers_from_mile, checkpoint.covers_to_mile])

    return [
        RiskSegmentDto(
            risk_level=int(level),
            path=[[round(p.lat, 5), round(p.lng, 5)]
                  for p in slice_path(path, path_miles, start, end)],
        )
        for level, start, end in stretches
    ]
