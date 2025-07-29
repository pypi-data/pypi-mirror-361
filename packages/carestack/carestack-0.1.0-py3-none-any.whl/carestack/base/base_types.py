from typing import Any


class ClientConfig:
    def __init__(self, api_key: str, api_url: str, x_hpr_id) -> None:
        self.api_key = api_key
        self.api_url = api_url
        self.hprid_auth = x_hpr_id


class ApiResponse:
    def __init__(self, data: Any, status: int, message: str) -> None:
        self.data = data
        self.status = status
        self.message = message
