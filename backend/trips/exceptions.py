class LocationNotFoundError(Exception):
    def __init__(self, query: str):
        super().__init__(
            f"We couldn't find \"{query}\". Try a city and state, e.g. \"Denver, CO\".")


class RouteNotFoundError(Exception):
    def __init__(self):
        super().__init__("No drivable truck route was found between these places.")


class ExternalServiceError(Exception):
    def __init__(self, service: str, detail: str):
        super().__init__(f"{service} request failed: {detail}")
