from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    """
    Health check endpoint for the application.
    """

    def get(self, request):
        """
        Handle GET requests to the health check endpoint.

        Returns:
            Response: A JSON response indicating the health status of the application.
        """
        return Response({"status": "ok", "demo_mode": settings.USE_FAKE_PROVIDERS})
