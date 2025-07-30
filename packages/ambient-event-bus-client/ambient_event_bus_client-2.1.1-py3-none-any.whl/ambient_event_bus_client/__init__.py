"""A library to interact with the Ambient Labs Event Bus.
"""

__version__ = "2.1.1"

from .client import Client
from .models.error import Error
from .models.event_api_models import (
    Message,
    MessageCreate,
    Session,
    Subscriber,
    Subscription,
)
from .models.options import ClientOptions
