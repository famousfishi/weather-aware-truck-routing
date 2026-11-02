from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from .domain import LocationInput, TripRequest

MAX_DAYS_AHEAD = 7
PAST_GRACE_MINUTES = 60


class LocationInputSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=200)
    lat = serializers.FloatField(required=False, min_value=-90, max_value=90)
    lng = serializers.FloatField(required=False, min_value=-180, max_value=180)

    def validate(self, data):
        if ("lat" in data) != ("lng" in data):
            raise serializers.ValidationError(
                "Send both lat and lng, or neither.")
        return data


class TripPlanRequestSerializer(serializers.Serializer):
    origin = LocationInputSerializer()
    destination = LocationInputSerializer()
    departure_time = serializers.DateTimeField()
    load_weight_lb = serializers.IntegerField(
        min_value=1,
        max_value=80_000,
        error_messages={
            "min_value": "Load weight must be at least 1 lb.",
            "max_value": "Load weight can't be more than 80,000 lb.",
        },
    )
    sample_interval_miles = serializers.ChoiceField(
        choices=[10, 25, 50], default=25)

    def validate_departure_time(self, value):
        now = timezone.now()
        if value < now - timedelta(minutes=PAST_GRACE_MINUTES):
            raise serializers.ValidationError("Departure time is in the past.")
        if value > now + timedelta(days=MAX_DAYS_AHEAD):
            raise serializers.ValidationError(
                f"Pick a departure within the next {MAX_DAYS_AHEAD} days (forecast limit).")
        return value

    def to_trip_request(self) -> TripRequest:
        data = self.validated_data
        return TripRequest(
            origin=LocationInput(**data["origin"]),
            destination=LocationInput(**data["destination"]),
            departure_time=data["departure_time"],
            load_weight_lb=data["load_weight_lb"],
            sample_interval_miles=data["sample_interval_miles"],
        )


class PlaceSuggestQuerySerializer(serializers.Serializer):
    q = serializers.CharField(max_length=200)
