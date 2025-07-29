from typing import Optional, Dict, Any, Union
import os
import requests
import mimetypes
from tqdm import tqdm

from fissionbox.core.sample import Sample
from fissionbox.core.reactor import Reactor
from .connection import Connection


class ReactorClient:
    def __init__(self, connection: Connection):
        self._connection = connection

    def create(self, reactor: Reactor) -> dict:
        """
        Create a new reactor on the FissionBox platform.

        Args:
            reactor (Reactor): The reactor object to create.
        
        Returns:
            Reactor: The created reactor object.
        """
        body = {
            "data": reactor.model_dump(),
        }
        response = self._connection.request("POST", "/reactors", json=body)
        data = response.json()
        return data
    
    def list(self) -> Dict[str, Reactor]:
        """
        List all reactors on the FissionBox platform.

        Returns:
            Dict[str, Reactor]: A dictionary mapping reactor names to Reactor objects.
        """
        response = self._connection.request("GET", "/reactors")
        data = response.json()
        reactors = {}
        for reactor_data in data:
            reactor = Reactor.bootstrap(reactor_data)
            reactors[reactor.id] = reactor
        return reactors
    
    def delete(self, reactor_id: str) -> dict:
        """
        Delete a reactor by its ID.

        Args:
            reactor_id (str): The ID of the reactor to delete.
        
        Returns:
            None
        """
        response = self._connection.request("DELETE", f"/reactors/{reactor_id}")
        return response