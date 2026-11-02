import requests

from ..exceptions import ExternalServiceError


def get_json(session: requests.Session, url: str, params, service: str, timeout: float):
    """GET a JSON endpoint and turn any network/HTTP problem into ExternalServiceError."""
    try:
        response = session.get(url, params=params, timeout=timeout)
    except requests.RequestException as error:
        raise ExternalServiceError(
            service, "the service could not be reached") from error

    if response.status_code != 200:
        raise ExternalServiceError(service, read_error_detail(response))
    return response.json()


def read_error_detail(response: requests.Response) -> str:
    try:
        body = response.json()
    except ValueError:
        return f"HTTP {response.status_code}"

    if isinstance(body, dict):
        detailed = body.get("detailedError")
        if isinstance(detailed, dict) and detailed.get("message"):
            return detailed["message"]
        error = body.get("error")
        if isinstance(error, dict) and error.get("description"):
            return error["description"]
        if body.get("reason"):
            return body["reason"]
    return f"HTTP {response.status_code}"
