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
            self.logger.error("Failed to initialize client: %s", str(e))
            if e.code == 401:
                err_msg = "401 Unauthorized: Invalid API token."
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
                        raise Exception("Looping limit reached.")
            raise Exception(f"Failed to initialize client: {e}")

    async def _register_subscriber(self) -> Subscriber:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self._client_options.event_api_url}/subscribers/",
                headers={"Authorization": f"Bearer {self._client_options.api_token}"},
            ) as response:
                response.raise_for_status()
                return Subscriber.model_validate(await response.json())

    async def _request_session(self) -> Session:
        async with aiohttp.ClientSession() as session:
            # Create session with subscriber_id in JSON body
            payload = {"subscriber_id": self.subscriber.id}
            async with session.post(
                f"{self._client_options.event_api_url}/sessions/",
                headers={
                    "Authorization": f"Bearer {self._client_options.api_token}",
                    "Content-Type": "application/json",
                },
                json=payload,
            ) as response:
                response.raise_for_status()
                resp_body = await response.json()
                return Session.model_validate(resp_body)

    async def subscribe(self) -> AsyncIterator[Result[Message, Error]]:
        while True:
            try:
                async with websockets.connect(self.uri) as websocket:
                    self.logger.debug("Connected")
                    async for message in websocket:
                        msg_data = json.loads(message)
                        yield Ok(Message.model_validate(msg_data))
            except websockets.exceptions.ConnectionClosedError:
                err_msg = "Connection closed unexpectedly.\nRetrying in 5 seconds ..."
                self.logger.info(err_msg)
                await asyncio.sleep(5)
            except Exception as e:
                self.logger.warning(f"An error occurred: {e}; retrying in 5 seconds.")
                error = Error(
                    error=str(e),
                    message="Error occurred while handling message.",
                    code=500,
                )
                yield Err(error)
                await asyncio.sleep(5)

    async def publish(self, message: MessageCreate) -> None:
        self.logger.debug("publishing message:\n%s", message.model_dump_json(indent=4))
        try:
            self.logger.debug("Connecting to WebSocket at %s", self.uri)
            async with websockets.connect(self.uri) as websocket:
                await websocket.send(message.model_dump_json())
        except Exception as e:
            if isinstance(e, websockets.exceptions.ConnectionClosedError):
                self.logger.debug("Connection closed: %s", str(e))
            else:
                self.logger.error("Failed to publish message: %s", str(e))
                raise e

    async def add_subscription(
        self,
        topic: str,
        aggregate_type: Optional[str] = None,
        aggregate_id: Optional[int] = None,
        is_regex: bool = False,
    ) -> Subscription:
        # Validate aggregate fields
        if aggregate_id is not None and aggregate_type is None:
            raise ValueError("aggregate_type is required when aggregate_id is provided")

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

            self.logger.debug("subscription payload: %s", payload)
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
                self.logger.debug("response data: %s", resp_json)
                return Subscription.model_validate(resp_json)

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
        return f"{self._client_options.connection_service_url}/ws/{self.session.id}"

    @property
    def client_options(self) -> ClientOptions:
        return self._client_options

    @property
    def token(self) -> str:
        return self._client_options.api_token

    @token.setter
    def token(self, value: str) -> None:
        self._client_options.api_token = value
