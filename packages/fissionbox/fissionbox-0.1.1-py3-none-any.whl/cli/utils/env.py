
import os
from fissionbox.core.client.connection import Connection
from fissionbox.core.client.client import Client
from fissionbox.cli.config import FISSIONBOX_HOST, FISSIONBOX_API_KEY


def get_connection() -> Connection:
    return Connection(
        host=FISSIONBOX_HOST,
        auth_token=FISSIONBOX_API_KEY
    )

def get_client() -> Client:
    return Client(
        connection=get_connection(),
        host=FISSIONBOX_HOST,
        api_key=FISSIONBOX_API_KEY
    )