from datetime import timedelta

from django.core.cache import cache
from django.test import SimpleTestCase, override_settings
from django.utils import timezone

from trips import container


@override_settings(USE_FAKE_PROVIDERS=True)
class TripPlanApiTests(SimpleTestCase):
    def setUp(self):
        container.reset()
        cache.clear()

    def tearDown(self):
        container.reset()

    def plan(self, **overrides):
        body = {
            "origin": {"query": "Denver, CO"},
            "destination": {"query": "Chicago, IL"},
            "departure_time": (timezone.now() + timedelta(hours=2)).isoformat(),
            "load_weight_lb": 42_000,
            "sample_interval_miles": 25,
            **overrides,
        }
        return self.client.post("/api/trips/plan", body, content_type="application/json")

    def test_returns_three_routes_with_checkpoints_and_a_recommendation(self):
        response = self.plan()
        self.assertEqual(response.status_code, 200, response.content)
        plan = response.json()

        self.assertEqual([route["id"]
                         for route in plan["routes"]], ["A", "B", "C"])
        self.assertIn(plan["recommendation"]["route_id"], {"A", "B", "C"})
        self.assertEqual(sum(route["is_recommended"]
                         for route in plan["routes"]), 1)

        route = plan["routes"][0]
        self.assertGreater(len(route["checkpoints"]), 10)
        self.assertEqual(route["checkpoints"][0]["mile"], 0)
        self.assertTrue(route["segments"])
        summary = route["summary"]
        total = sum(summary[k] for k in (
            "low_miles", "moderate_miles", "high_miles", "severe_miles", "no_travel_miles"))
        self.assertAlmostEqual(
            total, route["checkpoints"][-1]["mile"], delta=0.5)

    def test_heatmap_has_49_hourly_values_per_cell(self):
        heatmap = self.plan().json()["heatmap"]
        self.assertEqual(heatmap["hours"], 48)
        self.assertTrue(heatmap["cells"])
        for key in ("risk_level", "wind_mph", "rain_in_hr", "snow_in_hr"):
            self.assertEqual(len(heatmap["cells"][0][key]), 49)

    def test_coordinates_skip_geocoding(self):
        response = self.plan(
            origin={"query": "My depot", "lat": 39.74, "lng": -104.99})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["origin"]["label"], "My depot")

    def test_unknown_place_returns_422_with_a_message(self):
        response = self.plan(destination={"query": "Atlantis"})
        self.assertEqual(response.status_code, 422)
        self.assertIn("Atlantis", response.json()["detail"])

    def test_validation_errors_have_a_readable_detail(self):
        response = self.plan(load_weight_lb=0)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()[
                         "detail"], "load_weight_lb: Load weight must be at least 1 lb.")

    def test_rejects_unsupported_sample_interval(self):
        self.assertEqual(self.plan(sample_interval_miles=15).status_code, 400)

    def test_rejects_departure_far_in_the_future(self):
        response = self.plan(departure_time=(
            timezone.now() + timedelta(days=9)).isoformat())
        self.assertEqual(response.status_code, 400)

    def test_place_suggestions(self):
        response = self.client.get("/api/places/suggest", {"q": "den"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["label"], "Denver, CO")
