from dataclasses import asdict, is_dataclass

from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from . import container
from .serializers import PlaceSuggestQuerySerializer, TripPlanRequestSerializer


def to_json(result):
    if isinstance(result, list):
        return [to_json(item) for item in result]
    return asdict(result) if is_dataclass(result) else result


class HealthView(APIView):
    def get(self, request):
        return Response({"status": "ok", "demo_mode": settings.USE_FAKE_PROVIDERS})


class PlaceSuggestView(APIView):
    def get(self, request):
        query = PlaceSuggestQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        return Response(to_json(container.place_service().suggest(query.validated_data["q"])))


class TripPlanView(APIView):
    def post(self, request):
        trip = TripPlanRequestSerializer(data=request.data)
        trip.is_valid(raise_exception=True)
        return Response(to_json(container.trip_planner().plan_trip(trip.to_trip_request())))
