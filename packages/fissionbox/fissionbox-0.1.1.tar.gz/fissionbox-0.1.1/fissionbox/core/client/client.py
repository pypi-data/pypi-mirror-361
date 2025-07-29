from typing import Optional, Dict, Any, Union

from .sample import SampleClient
from .reactor import ReactorClient
from .connection import Connection


class Client:
    """
    Client class for FissionBox.
    This class is used to interact with the FissionBox platform API.
    """

    def __init__(
        self,
        connection: Optional[Connection] = None,
        host: str = "https://api.platform.fissionbox.ai",
        api_key: str = None,
    ):
        """
        Initialize the Client with an API key.

        :param api_key: The API
        """
        self._api_key = api_key
        self._connection = connection if connection else Connection(host, api_key)
        self._sample_client = SampleClient(connection)
        self._reactor_client = ReactorClient(connection)

    @property
    def reactor(self) -> ReactorClient:
        """
        Get the ReactorClient instance.

        :return: An instance of ReactorClient.
        """
        return self._reactor_client

    @property
    def sample(self) -> SampleClient:
        """
        Get the SampleClient instance.

        :return: An instance of SampleClient.
        """
        return self._sample_client
