"""The risk rules from the assessment, written exactly as the table reads.

Wind   Low <25 mph      Moderate 25–34   High 35–44     Severe 45–54   No Travel ≥55
Rain   Low <0.10 in/hr  Moderate 0.10–0.25  High 0.25–0.50  Severe 0.50–1.00  No Travel >1.00
Snow   Low <0.5 in/hr   Moderate 0.5–1.0    High 1.0–2.0    Severe 2.0–3.0    No Travel >3.0

Load rules: ≥55 mph is No Travel for any load (already in the wind table);
45–54 mph with more than 30,000 lb → No Travel; 35–44 mph with more than 40,000 lb → Severe.

A checkpoint's risk is the worst of its wind (after load rules), rain and snow levels.
"""

from ..domain import RiskAssessment, RiskLevel, WeatherReading

NO_TRAVEL_IN_SEVERE_WIND_ABOVE_LB = 30_000
SEVERE_IN_HIGH_WIND_ABOVE_LB = 40_000


def classify_wind(wind_mph: float) -> RiskLevel:
    if wind_mph >= 55:
        return RiskLevel.NO_TRAVEL
    if wind_mph >= 45:
        return RiskLevel.SEVERE
    if wind_mph >= 35:
        return RiskLevel.HIGH
    if wind_mph >= 25:
        return RiskLevel.MODERATE
    return RiskLevel.LOW


def classify_rain(rain_in_hr: float) -> RiskLevel:
    if rain_in_hr > 1.00:
        return RiskLevel.NO_TRAVEL
    if rain_in_hr >= 0.50:
        return RiskLevel.SEVERE
    if rain_in_hr >= 0.25:
        return RiskLevel.HIGH
    if rain_in_hr >= 0.10:
        return RiskLevel.MODERATE
    return RiskLevel.LOW


def classify_snow(snow_in_hr: float) -> RiskLevel:
    if snow_in_hr > 3.0:
        return RiskLevel.NO_TRAVEL
    if snow_in_hr >= 2.0:
        return RiskLevel.SEVERE
    if snow_in_hr >= 1.0:
        return RiskLevel.HIGH
    if snow_in_hr >= 0.5:
        return RiskLevel.MODERATE
    return RiskLevel.LOW


def apply_load_rules(wind_level: RiskLevel, load_weight_lb: int) -> RiskLevel:
    """Heavy loads are riskier in strong wind (the wind level already covers the ≥55 mph rule)."""
    if wind_level == RiskLevel.SEVERE and load_weight_lb > NO_TRAVEL_IN_SEVERE_WIND_ABOVE_LB:
        return RiskLevel.NO_TRAVEL
    if wind_level == RiskLevel.HIGH and load_weight_lb > SEVERE_IN_HIGH_WIND_ABOVE_LB:
        return RiskLevel.SEVERE
    return wind_level


def assess(weather: WeatherReading, load_weight_lb: int) -> RiskAssessment:
    wind_level = classify_wind(weather.wind_mph)
    loaded_wind_level = apply_load_rules(wind_level, load_weight_lb)
    rain_level = classify_rain(weather.rain_in_hr)
    snow_level = classify_snow(weather.snow_in_hr)

    reasons = []
    if wind_level > RiskLevel.LOW:
        reasons.append(f"Wind {weather.wind_mph:.0f} mph → {wind_level.label}")
    if loaded_wind_level != wind_level:
        reasons.append(
            f"{load_weight_lb:,} lb load in that wind → {loaded_wind_level.label}")
    if rain_level > RiskLevel.LOW:
        reasons.append(
            f"Rain {weather.rain_in_hr:.2f} in/hr → {rain_level.label}")
    if snow_level > RiskLevel.LOW:
        reasons.append(
            f"Snow {weather.snow_in_hr:.1f} in/hr → {snow_level.label}")

    return RiskAssessment(level=max(loaded_wind_level, rain_level, snow_level), reasons=reasons)
