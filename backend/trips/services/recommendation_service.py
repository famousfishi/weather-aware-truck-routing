"""Ranks the routes and explains the choice in plain words.

Order of preference (from the assessment), with one addition at the top:
  0. Fewest No-Travel miles  (a route you legally/safely can't drive must never win)
  1. Fewest Severe miles
  2. Fewest High miles
  3. Lowest average risk
  4. Shortest travel time
"""

from ..dtos import RecommendationDto, RouteDto

CRITERIA = (
    ("no_travel_miles", "Fewer No-Travel miles", " mi"),
    ("severe_miles", "Fewer Severe miles", " mi"),
    ("high_miles", "Fewer High-risk miles", " mi"),
    ("average_risk", "Lower average risk", " (0 = Low, 4 = No Travel)"),
)


def rank_key(route: RouteDto) -> tuple:
    s = route.summary
    return (s.no_travel_miles, s.severe_miles, s.high_miles, s.average_risk, route.duration_seconds)


def rank_routes(routes: list[RouteDto]) -> list[RouteDto]:
    """Sorts best-first and marks each route's rank; the first one is the recommendation."""
    ranked = sorted(routes, key=rank_key)
    for position, route in enumerate(ranked, start=1):
        route.rank = position
        route.is_recommended = position == 1
    return ranked


def build_recommendation(ranked: list[RouteDto]) -> RecommendationDto:
    best = ranked[0]
    via = f" via {', '.join(best.via)}" if best.via else ""
    recommendation = RecommendationDto(
        route_id=best.id, headline=f"Take {best.name}{via}")

    if len(ranked) > 1:
        recommendation.reasons.append(deciding_reason(best, ranked[1]))
        fastest = min(ranked, key=lambda route: route.duration_seconds)
        if fastest.id == best.id:
            recommendation.reasons.append("It is also the fastest option.")
        else:
            extra_time = format_duration(
                best.duration_seconds - fastest.duration_seconds)
            recommendation.reasons.append(
                f"It takes {extra_time} longer than {fastest.name}, the fastest option, but avoids its worse weather."
            )

    recommendation.warnings = build_warnings(best, len(ranked))
    return recommendation


def deciding_reason(best: RouteDto, runner_up: RouteDto) -> str:
    """The first rule (in priority order) where the winner beats the runner-up."""
    for field, phrase, unit in CRITERIA:
        best_value = getattr(best.summary, field)
        other_value = getattr(runner_up.summary, field)
        if best_value < other_value:
            return f"{phrase} than {runner_up.name}: {format_number(best_value)} vs {format_number(other_value)}{unit}."

    if best.duration_seconds < runner_up.duration_seconds:
        return (
            f"Same weather risk as {runner_up.name}, so the quicker drive wins: "
            f"{format_duration(best.duration_seconds)} vs {format_duration(runner_up.duration_seconds)}."
        )
    return f"Weather risk and drive time are effectively the same as {runner_up.name}."


def build_warnings(best: RouteDto, route_count: int) -> list[str]:
    warnings = []
    if best.summary.no_travel_miles > 0:
        warnings.append(
            f"Every route hits No-Travel conditions at the times you would be driving "
            f"({format_number(best.summary.no_travel_miles)} mi on the best one). Consider a different departure time."
        )
    elif best.summary.severe_miles > 0:
        warnings.append(
            f"Even the best route has {format_number(best.summary.severe_miles)} Severe miles. "
            f"Check conditions before that stretch."
        )
    if route_count < 3:
        warnings.append(
            f"Only {route_count} distinct route(s) were found between these places.")
    return warnings


def format_number(value: float) -> str:
    return f"{value:,.1f}".removesuffix(".0")


def format_duration(seconds: int) -> str:
    hours, remainder = divmod(int(seconds), 3600)
    minutes = remainder // 60
    return f"{hours}h {minutes:02d}m" if hours else f"{minutes} min"
