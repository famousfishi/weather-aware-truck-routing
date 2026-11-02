from datetime import datetime, timezone

from django.test import SimpleTestCase

from trips.dtos import RouteDto, RouteSummaryDto
from trips.services.recommendation_service import build_recommendation, rank_routes

NOW = datetime(2026, 11, 1, 12, tzinfo=timezone.utc)


def make_route(route_id, hours, no_travel=0.0, severe=0.0, high=0.0, average=0.0):
    summary = RouteSummaryDto(
        low_miles=500, moderate_miles=0, high_miles=high, severe_miles=severe,
        no_travel_miles=no_travel, average_risk=average, worst_risk_level=0,
    )
    return RouteDto(
        id=route_id, name=f"Route {route_id}", via=[], distance_miles=500, duration_seconds=int(hours * 3600),
        traffic_delay_seconds=0, departure_time=NOW, arrival_time=NOW, summary=summary, segments=[], checkpoints=[],
    )


class RankingTests(SimpleTestCase):
    def winner(self, *routes):
        return rank_routes(list(routes))[0].id

    def test_fewest_severe_miles_beats_faster_route(self):
        self.assertEqual(self.winner(make_route(
            "A", 8, severe=40), make_route("B", 10, severe=0)), "B")

    def test_no_travel_miles_rank_above_severe_miles(self):
        self.assertEqual(self.winner(make_route(
            "A", 8, no_travel=5), make_route("B", 9, severe=60)), "B")

    def test_high_miles_break_a_severe_tie(self):
        self.assertEqual(self.winner(make_route(
            "A", 8, high=30), make_route("B", 9, high=10)), "B")

    def test_average_risk_breaks_a_high_tie(self):
        self.assertEqual(self.winner(make_route(
            "A", 8, average=0.9), make_route("B", 9, average=0.3)), "B")

    def test_travel_time_is_the_last_tie_breaker(self):
        self.assertEqual(self.winner(
            make_route("A", 9), make_route("B", 8)), "B")

    def test_ranks_are_assigned(self):
        ranked = rank_routes([make_route("A", 8, severe=5), make_route(
            "B", 9), make_route("C", 7, severe=50)])
        self.assertEqual([(r.id, r.rank, r.is_recommended) for r in ranked],
                         [("B", 1, True), ("A", 2, False), ("C", 3, False)])


class ExplanationTests(SimpleTestCase):
    def test_explains_deciding_rule_and_time_trade_off(self):
        ranked = rank_routes(
            [make_route("A", 8, severe=42), make_route("B", 8.5)])
        recommendation = build_recommendation(ranked)
        self.assertEqual(recommendation.route_id, "B")
        self.assertEqual(
            recommendation.reasons[0], "Fewer Severe miles than Route A: 0 vs 42 mi.")
        self.assertIn("30 min longer than Route A", recommendation.reasons[1])

    def test_warns_when_every_route_has_no_travel_miles(self):
        ranked = rank_routes(
            [make_route("A", 8, no_travel=12), make_route("B", 9, no_travel=20)])
        self.assertIn("No-Travel", build_recommendation(ranked).warnings[0])
