from django.test import SimpleTestCase

from trips.domain import RiskLevel, WeatherReading
from trips.services.risk_service import assess, classify_rain, classify_snow, classify_wind

LOW, MODERATE, HIGH, SEVERE, NO_TRAVEL = RiskLevel


class ThresholdTests(SimpleTestCase):
    def test_wind_bands(self):
        cases = [(0, LOW), (24.9, LOW), (25, MODERATE), (34.9, MODERATE), (35, HIGH), (44.9, HIGH),
                 (45, SEVERE), (54.9, SEVERE), (55, NO_TRAVEL), (80, NO_TRAVEL)]
        for wind, expected in cases:
            with self.subTest(wind=wind):
                self.assertEqual(classify_wind(wind), expected)

    def test_rain_bands(self):
        cases = [(0, LOW), (0.09, LOW), (0.10, MODERATE), (0.24, MODERATE), (0.25, HIGH), (0.49, HIGH),
                 (0.50, SEVERE), (1.00, SEVERE), (1.01, NO_TRAVEL)]
        for rain, expected in cases:
            with self.subTest(rain=rain):
                self.assertEqual(classify_rain(rain), expected)

    def test_snow_bands(self):
        cases = [(0, LOW), (0.4, LOW), (0.5, MODERATE), (0.9, MODERATE), (1.0, HIGH), (1.9, HIGH),
                 (2.0, SEVERE), (3.0, SEVERE), (3.1, NO_TRAVEL)]
        for snow, expected in cases:
            with self.subTest(snow=snow):
                self.assertEqual(classify_snow(snow), expected)


class LoadRuleTests(SimpleTestCase):
    def level(self, wind_mph, load_lb):
        return assess(WeatherReading(wind_mph, 0, 0), load_lb).level

    def test_55_mph_is_no_travel_for_any_load(self):
        self.assertEqual(self.level(55, 1_000), NO_TRAVEL)

    def test_severe_wind_with_heavy_load_is_no_travel(self):
        self.assertEqual(self.level(50, 30_001), NO_TRAVEL)
        self.assertEqual(self.level(50, 30_000), SEVERE)

    def test_high_wind_with_very_heavy_load_is_severe(self):
        self.assertEqual(self.level(40, 40_001), SEVERE)
        self.assertEqual(self.level(40, 40_000), HIGH)

    def test_moderate_wind_is_not_affected_by_load(self):
        self.assertEqual(self.level(30, 79_000), MODERATE)


class CombinedTests(SimpleTestCase):
    def test_worst_condition_wins(self):
        result = assess(WeatherReading(
            wind_mph=28, rain_in_hr=0.6, snow_in_hr=0.2), 20_000)
        self.assertEqual(result.level, SEVERE)

    def test_reasons_explain_each_non_low_condition(self):
        result = assess(WeatherReading(
            wind_mph=40, rain_in_hr=0.12, snow_in_hr=0), 42_000)
        self.assertEqual(
            result.reasons,
            ["Wind 40 mph → High", "42,000 lb load in that wind → Severe",
                "Rain 0.12 in/hr → Moderate"],
        )

    def test_calm_weather_has_no_reasons(self):
        self.assertEqual(assess(WeatherReading(5, 0, 0), 42_000).reasons, [])
