import logging

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from .exceptions import ExternalServiceError, LocationNotFoundError, RouteNotFoundError, WeatherNeededError

logger = logging.getLogger(__name__)


def api_exception_handler(exc, context):
    """One place that turns errors into a consistent {"detail": "..."} JSON response."""
    if isinstance(exc, (LocationNotFoundError, RouteNotFoundError)):
        return Response({"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    if isinstance(exc, WeatherNeededError):
        # 428 Precondition Required: "fetch these forecasts, then send the same request again with them".
        return Response(
            {"detail": str(exc), "weather_requests": exc.weather_requests},
            status=status.HTTP_428_PRECONDITION_REQUIRED,
        )

    if isinstance(exc, ExternalServiceError):
        logger.warning("External service failed: %s", exc)
        return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

    response = drf_exception_handler(exc, context)
    if response is not None and isinstance(exc, ValidationError):
        response.data = {"detail": first_error_message(
            response.data), "errors": response.data}
    return response


def first_error_message(errors, path: str = "") -> str:
    """Finds the first readable message inside DRF's nested validation errors."""
    if isinstance(errors, dict):
        for field_name, value in errors.items():
            child_path = path if field_name == "non_field_errors" else ".".join(
                filter(None, [path, field_name]))
            message = first_error_message(value, child_path)
            if message:
                return message
        return ""
    if isinstance(errors, list):
        for item in errors:
            message = first_error_message(item, path)
            if message:
                return message
        return ""
    return f"{path}: {errors}" if path else str(errors)
