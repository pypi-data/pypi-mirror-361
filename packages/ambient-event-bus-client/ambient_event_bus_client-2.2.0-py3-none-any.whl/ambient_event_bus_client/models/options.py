from typing import Callable, Optional

from pydantic import BaseModel


class ClientOptions(BaseModel):
    """
    Options for the client.
    """

    event_api_url: str
    connection_service_url: str
    api_token: str
    log_level: str = "ERROR"

    fetch_new_token_callback: Optional[Callable] = None
