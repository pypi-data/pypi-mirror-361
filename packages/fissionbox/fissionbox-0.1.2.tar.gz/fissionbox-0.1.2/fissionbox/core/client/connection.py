import requests

class Connection:
    """
    Represents a connection to a FissionBox server.
    This class is responsible for managing the connection and sending/receiving messages.
    """

    def __init__(self, host: str, auth_token: str):
        """
        Initialize the Connection with a host and authentication token.
        
        :param host: The host of the FissionBox server.
        :param auth_token: The authentication token for the connection.
        """
        self._host = host
        self._auth_token = auth_token
        self._connected = False

    def test(self) -> bool:
        """
        Test the connection to the FissionBox server.
        
        :return: True if the connection is successful, False otherwise.
        """
        # Here you would implement the logic to test the connection
        # For example, sending a ping request to the server
        # and checking if it responds correctly.
        return self._connected
    
    def request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Make a request to the FissionBox server.
        
        :param method: The HTTP method (GET, POST, etc.).
        :param endpoint: The API endpoint to call.
        :param kwargs: Additional arguments to pass to the request.
        :return: The response from the server.
        """
        url = f"{self._host}/{endpoint}" if not endpoint.startswith("/") else f"{self._host}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self._auth_token}",
            "Content-Type": "application/json"
        }
        response = requests.request(method, url, headers=headers, **kwargs)
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            print(f"HTTP Error: {e.response.status_code} - {e.response.content}")
            raise e
        return response