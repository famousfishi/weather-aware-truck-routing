from django.urls import path

from .views import HealthView, PlaceSuggestView, TripPlanView

urlpatterns = [
    path("health", HealthView.as_view()),
    path("places/suggest", PlaceSuggestView.as_view()),
    path("trips/plan", TripPlanView.as_view()),
]
