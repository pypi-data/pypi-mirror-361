import asyncio
import json
import logging
import urllib.parse
from typing import AsyncIterator, Optional

import aiohttp
import websockets
from result import Err, Ok, Result

from ambient_event_bus_client.models.error import Error
from ambient_event_bus_client.models.event_api_models import (
    Message,
    MessageCreate,
    Session,
    Subscriber,
    Subscription,
)
from ambient_event_bus_client.models.options import ClientOptions


class Client:
    """
    A client to interact with the Ambient Labs Event Bus.

    Parameters:
        - options: ClientOptions - The options for the client.

    Attributes:
        - session: Session - The session of the client.
        - client_options: ClientOptions - The options for the client.
        - uri: str - The URI to connect to the event bus.
        - token: str - The API token for the client.

    Typical usage example:

    ```python
    options = ClientOptions(
        event_api_url="http://localhost:8000",
        connection_service_url="http://localhost:8001",
        api_token = "my_token"
    )
    client = Client(options)
    await client.init_client() # ensure you are in an async context

    # add subscriptions
    await client.add_subscription(topic="test")

    # add subscription with aggregate filtering
    await client.add_subscription(topic="node", aggregate_type="node", aggregate_id=123)

    # add subscription with regex topic matching
    await client.add_subscription(topic="user\\.*", is_regex=True)

    # read messages from subscriptions
    async for message in client.subscribe():
        print(message)

    # publish a message
    message = MessageCreate(topic="my_topic", content="my_message")
    await client.publish(message)

    # publish a message with aggregate info
    message = MessageCreate(
        topic="node_update",
        content="Node updated",
        aggregate_type="node",
        aggregate_id=123
    )
    await client.publish(message)
    ```

    """

    def __init__(self, options: ClientOptions) -> None:
        self._client_options = options
        self._session: Optional[None] = None
        logging.basicConfig()
        self.logger = logging.getLogger("event_bus_client")
        self.logger.setLevel(self._client_options.log_level)

        self.looping_limit = 10

    async def init_client(self) -> None:
        """This async method initializes the client.

        Raises:
            Exception: if the client fails to initialize.
            Exception: if the API token is invalid.
        """
        try:
            self.subscriber = await self._register_subscriber()
            self.logger.debug(
                "registered subscriber: %s", self.subscriber.model_dump_json(indent=4)
            )
            self.session = await self._request_session()
            self.logger.debug(
                "registered session: %s", self.session.model_dump_json(indent=4)
            )
        except aiohttp.ClientResponseError as e:
            if hasattr(e, "request_info") and hasattr(e.request_info, "url"):
                url_info = str(e.request_info.url)
            else:
                url_info = "Unknown"
            error_context = f"URL: {url_info}"
            self.logger.error(
                "Failed to initialize client: %s (%s)", str(e), error_context
            )
            if e.status == 401:
                err_msg = (
                    f"401 Unauthorized: Invalid API token provided in "
                    f"ClientOptions. Verify your token is valid and has not "
                    f"expired. {error_context}"
                )
                self.logger.warning(err_msg)
                if self._client_options.fetch_new_token_callback is not None:
                    self.logger.info("Fetching new token ...")
                    await asyncio.sleep(1)
                    new_token = await self._client_options.fetch_new_token_callback()
                    self._client_options.api_token = new_token
                    self.logger.info("New token fetched.")
                    self.looping_limit -= 1
                    if self.looping_limit > 0:
                        return await self.init_client()
                    else:
                        raise Exception(
                            "Looping limit reached while trying to refresh token."
                        )
                raise Exception(err_msg)
            elif e.status == 403:
                err_msg = (
                    f"403 Forbidden: Token lacks required permissions. "
                    f"{error_context}"
                )
                self.logger.error(err_msg)
                raise Exception(err_msg)
            elif e.status == 404:
                err_msg = (
                    f"404 Not Found: API endpoint not found. Check "
                    f"event_api_url: {self._client_options.event_api_url}. "
                    f"{error_context}"
                )
                self.logger.error(err_msg)
                raise Exception(err_msg)
            elif e.status >= 500:
                err_msg = (
                    f"Server Error ({e.status}): The event bus service is "
                    f"experiencing issues. {error_context}"
                )
                self.logger.error(err_msg)
                raise Exception(err_msg)
            else:
                err_msg = f"HTTP Error ({e.status}): {e.message}. {error_context}"
                self.logger.error(err_msg)
                raise Exception(err_msg)
        except aiohttp.ClientConnectorError as e:
            err_msg = (
                f"Connection Error: Cannot connect to event bus at "
                f"{self._client_options.event_api_url}. Check your network "
                f"connection and URL. Details: {str(e)}"
            )
            self.logger.error(err_msg)
            raise Exception(err_msg)
        except asyncio.TimeoutError:
            err_msg = (
                f"Timeout Error: Request to {self._client_options.event_api_url} "
                f"timed out. Check your network connection and server "
                f"availability."
            )
            self.logger.error(err_msg)
            raise Exception(err_msg)
        except Exception as e:
            err_msg = f"Unexpected error during client initialization: {str(e)}"
            self.logger.error(err_msg)
            raise Exception(err_msg)

    async def _register_subscriber(self) -> Subscriber:
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self._client_options.event_api_url}/subscribers/"
                headers = {"Authorization": f"Bearer {self._client_options.api_token}"}
                self.logger.debug("Registering subscriber at: %s", url)

                async with session.post(url, headers=headers) as response:
                    response.raise_for_status()
                    return Subscriber.model_validate(await response.json())
        except aiohttp.ClientResponseError as e:
            err_msg = (
                f"Failed to register subscriber: HTTP {e.status} at "
                f"{self._client_options.event_api_url}/subscribers/. "
                f"Response: {e.message}"
            )
            self.logger.error(err_msg)
            raise
        except aiohttp.ClientConnectorError as e:
            err_msg = (
                f"Connection failed when registering subscriber at "
                f"{self._client_options.event_api_url}/subscribers/. "
                f"Check URL and network: {str(e)}"
            )
            self.logger.error(err_msg)
            raise
        except Exception as e:
            err_msg = f"Unexpected error registering subscriber: {str(e)}"
            self.logger.error(err_msg)
            raise

    async def _request_session(self) -> Session:
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self._client_options.event_api_url}/sessions/"
                payload = {"subscriber_id": self.subscriber.id}
                headers = {
                    "Authorization": f"Bearer {self._client_options.api_token}",
                    "Content-Type": "application/json",
                }
                self.logger.debug(
                    "Creating session at: %s with subscriber_id: %s",
                    url,
                    self.subscriber.id,
                )

                async with session.post(url, headers=headers, json=payload) as response:
                    response.raise_for_status()
                    resp_body = await response.json()
                    return Session.model_validate(resp_body)
        except aiohttp.ClientResponseError as e:
            err_msg = (
                f"Failed to create session: HTTP {e.status} at "
                f"{self._client_options.event_api_url}/sessions/. "
                f"Response: {e.message}. Subscriber ID: {self.subscriber.id}"
            )
            self.logger.error(err_msg)
            raise
        except aiohttp.ClientConnectorError as e:
            err_msg = (
                f"Connection failed when creating session at "
                f"{self._client_options.event_api_url}/sessions/. "
                f"Check URL and network: {str(e)}"
            )
            self.logger.error(err_msg)
            raise
        except Exception as e:
            err_msg = f"Unexpected error creating session: {str(e)}"
            self.logger.error(err_msg)
            raise

    async def subscribe(self) -> AsyncIterator[Result[Message, Error]]:
        while True:
            try:
                self.logger.debug("Connecting to WebSocket at: %s", self.uri)
                async with websockets.connect(self.uri) as websocket:
                    self.logger.debug("WebSocket connected successfully")
                    async for message in websocket:
                        try:
                            msg_data = json.loads(message)
                            yield Ok(Message.model_validate(msg_data))
                        except json.JSONDecodeError as e:
                            err_msg = (
                                f"Invalid JSON received from WebSocket: {str(e)}. "
                                f"Raw message: {message}"
                            )
                            self.logger.error(err_msg)
                            error = Error(
                                error=err_msg,
                                message="Failed to parse message JSON from WebSocket.",
                                code=400,
                            )
                            yield Err(error)
                        except Exception as e:
                            msg_data_info = (
                                msg_data if "msg_data" in locals() else message
                            )
                            err_msg = (
                                f"Failed to validate message model: {str(e)}. "
                                f"Raw data: {msg_data_info}"
                            )
                            self.logger.error(err_msg)
                            error = Error(
                                error=err_msg,
                                message="Failed to validate message structure.",
                                code=422,
                            )
                            yield Err(error)
            except websockets.exceptions.ConnectionClosedError as e:
                err_msg = (
                    f"WebSocket connection closed unexpectedly "
                    f"(code: {e.code}, reason: {e.reason}). "
                    f"WebSocket URL: {self.uri}. Retrying in 5 seconds..."
                )
                self.logger.warning(err_msg)
                await asyncio.sleep(5)
            except websockets.exceptions.InvalidURI as e:
                err_msg = (
                    f"Invalid WebSocket URI: {self.uri}. "
                    f"Check connection_service_url: "
                    f"{self._client_options.connection_service_url}. "
                    f"Error: {str(e)}"
                )
                self.logger.error(err_msg)
                error = Error(
                    error=err_msg,
                    message="Invalid WebSocket URI configuration.",
                    code=400,
                )
                yield Err(error)
                break  # Don't retry for invalid URI
            except Exception as e:
                err_msg = (
                    f"Unexpected error in WebSocket connection to {self.uri}: "
                    f"{str(e)}. Retrying in 5 seconds..."
                )
                self.logger.warning(err_msg)
                error = Error(
                    error=err_msg,
                    message="Error occurred while handling WebSocket connection.",
                    code=500,
                )
                yield Err(error)
                await asyncio.sleep(5)

    async def publish(self, message: MessageCreate) -> None:
        self.logger.debug("Publishing message:\n%s", message.model_dump_json(indent=4))
        try:
            self.logger.debug("Connecting to WebSocket at %s", self.uri)
            async with websockets.connect(self.uri) as websocket:
                message_json = message.model_dump_json()
                await websocket.send(message_json)
                self.logger.debug("Message published successfully")
        except websockets.exceptions.ConnectionClosedError as e:
            err_msg = (
                f"WebSocket connection closed while publishing "
                f"(code: {e.code}, reason: {e.reason}). "
                f"WebSocket URL: {self.uri}"
            )
            self.logger.error(err_msg)
            raise Exception(err_msg)
        except websockets.exceptions.InvalidURI as e:
            err_msg = (
                f"Invalid WebSocket URI for publishing: {self.uri}. "
                f"Check connection_service_url: "
                f"{self._client_options.connection_service_url}. "
                f"Error: {str(e)}"
            )
            self.logger.error(err_msg)
            raise Exception(err_msg)
        except websockets.exceptions.WebSocketException as e:
            if "HTTP 404" in str(e):
                err_msg = (
                    f"WebSocket endpoint not found (404) at {self.uri}. "
                    f"This might mean: 1) WebSocket service not running, "
                    f"2) Incorrect path (check connection_service_url: "
                    f"{self._client_options.connection_service_url}), "
                    f"or 3) Authentication required. Error: {str(e)}"
                )
            elif "HTTP 401" in str(e) or "HTTP 403" in str(e):
                err_msg = (
                    f"WebSocket authentication failed at {self.uri}. "
                    f"Check if session token is valid or if WebSocket "
                    f"requires different authentication. Error: {str(e)}"
                )
            else:
                err_msg = f"WebSocket error while publishing to {self.uri}: {str(e)}"
            self.logger.error(err_msg)
            raise Exception(err_msg)
        except Exception as e:
            err_msg = (
                f"Unexpected error while publishing message to {self.uri}: " f"{str(e)}"
            )
            self.logger.error(err_msg)
            raise Exception(err_msg)

    async def add_subscription(
        self,
        topic: str,
        aggregate_type: Optional[str] = None,
        aggregate_id: Optional[int] = None,
        is_regex: bool = False,
    ) -> Subscription:
        # Validate input parameters
        if not topic or not topic.strip():
            raise ValueError("Topic cannot be empty or whitespace")

        # Validate aggregate fields
        if aggregate_id is not None and aggregate_type is None:
            raise ValueError("aggregate_type is required when aggregate_id is provided")

        try:
            async with aiohttp.ClientSession() as session:
                base_url = urllib.parse.urljoin(
                    self._client_options.event_api_url + "/", "subscriptions/"
                )
                payload = {
                    "topic": topic,
                    "subscriber_id": self.subscriber.id,
                    "is_regex": is_regex,
                }
                if aggregate_type is not None:
                    payload["aggregate_type"] = aggregate_type
                if aggregate_id is not None:
                    payload["aggregate_id"] = aggregate_id

                self.logger.debug(
                    "Creating subscription at: %s with payload: %s", base_url, payload
                )

                async with session.post(
                    base_url,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self._client_options.api_token}",
                        "Content-Type": "application/json",
                    },
                ) as response:
                    response.raise_for_status()
                    resp_json = await response.json()
                    self.logger.debug(
                        "Subscription created successfully: %s", resp_json
                    )
                    return Subscription.model_validate(resp_json)
        except aiohttp.ClientResponseError as e:
            if e.status == 400:
                err_msg = (
                    f"Bad Request (400): Invalid subscription parameters. "
                    f"Topic: '{topic}', aggregate_type: {aggregate_type}, "
                    f"aggregate_id: {aggregate_id}, is_regex: {is_regex}. "
                    f"Response: {e.message}"
                )
            elif e.status == 409:
                err_msg = (
                    f"Conflict (409): Subscription already exists for "
                    f"topic '{topic}' with these parameters. "
                    f"Response: {e.message}"
                )
            else:
                err_msg = (
                    f"Failed to create subscription: HTTP {e.status} at "
                    f"{base_url}. Response: {e.message}. Topic: '{topic}'"
                )
            self.logger.error(err_msg)
            raise Exception(err_msg)
        except aiohttp.ClientConnectorError as e:
            err_msg = (
                f"Connection failed when creating subscription at {base_url}. "
                f"Check URL and network: {str(e)}"
            )
            self.logger.error(err_msg)
            raise Exception(err_msg)
        except Exception as e:
            err_msg = (
                f"Unexpected error creating subscription for topic '{topic}': "
                f"{str(e)}"
            )
            self.logger.error(err_msg)
            raise Exception(err_msg)

    @property
    def session(self) -> Session:
        return self._session

    @session.setter
    def session(self, value: Session) -> None:
        self._session = value

    @property
    def subscriber(self) -> Subscriber:
        return self._subscriber

    @subscriber.setter
    def subscriber(self, value: Subscriber) -> None:
        self._subscriber = value

    @property
    def uri(self) -> str:
        # Convert HTTP(S) scheme to WebSocket scheme for WebSocket connections
        ws_url = self._client_options.connection_service_url
        if ws_url.startswith("https://"):
            ws_url = ws_url.replace("https://", "wss://", 1)
        elif ws_url.startswith("http://"):
            ws_url = ws_url.replace("http://", "ws://", 1)

        # If the URL already ends with /ws, don't duplicate it
        if ws_url.endswith("/ws"):
            return f"{ws_url}/{self.session.id}"
        else:
            return f"{ws_url}/ws/{self.session.id}"

    @property
    def client_options(self) -> ClientOptions:
        return self._client_options

    @property
    def token(self) -> str:
        return self._client_options.api_token

    @token.setter
    def token(self, value: str) -> None:
        self._client_options.api_token = value
