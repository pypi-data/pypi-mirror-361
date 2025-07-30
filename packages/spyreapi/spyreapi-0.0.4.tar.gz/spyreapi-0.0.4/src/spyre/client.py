import requests
from typing import TypeVar, Optional, Type, Generic, List, Union, Tuple, Dict, Any
from pydantic import BaseModel
import json
import urllib.parse
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException

T = TypeVar('T', bound=BaseModel)

class SpireClient():    
    """A lightweight client to interact with the Spire API using requests sessions for connection reuse and authenticated calls."""
    def __init__(self, host, company, username, password,):
        """
        :param host (str): Spire Server host
        :param company (str): Spire company
        :param username (str): Spire user username.
        :param password (str): Spire user password.
        
        """
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.headers.update({
            "accept": "application/json",
            "content-type": "application/json"
        })
        self.base_url = f"https://{host}/api/v2/companies/{company}"

        try: 
            response = self.session.get(self.base_url)
            if response.text == 'No such company intertes':
                raise ValueError(f"No company entries for {company}")
            if response.text == 'Unauthorized':
                raise ValueError(f"Invalid Authorization")

        except ConnectionError as conn_err:
            print(f"Connection error occurred for : {conn_err}")

        except Timeout as timeout_err:
            print(f"Request timed out: {timeout_err}")

        except RequestException as req_err:
            print(f"General error occurred: {req_err}")


    def _get(self, endpoint, params=None):

        """
        Send a GET request to the Spire API.

        This method constructs the full URL using the provided endpoint,
        sends an HTTP GET request with optional query parameters, and returns
        the parsed JSON response. Raises an HTTPError if the response contains
        an unsuccessful status code.

        Args:
            endpoint (str): The relative API endpoint (e.g., 'inventory/items/123').
            params (dict, optional): A dictionary of query parameters to include
                in the request (e.g., {'status': 'active'}). Defaults to None.

        Returns:
            dict: The JSON-decoded response from the API.

        Raises:
            requests.exceptions.HTTPError: If the response contains an HTTP error status.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.get(url , params=params)
        response.raise_for_status()
        return response.json()

    def _post(self, endpoint, data=None, json=None):
        """
        Send a POST request to the Spire API.

        Args:
            endpoint (str): The relative API endpoint (e.g., 'sales/orders').
            data (dict, optional): Data to send in the body of the request.
            json (dict, optional): JSON data to send in the body of the request.

        Returns:
            dict: A dictionary containing the response status code, URL, content, and headers.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.post(url, data=data, json=json)
        return self._handle_response(response)

    def _put(self, endpoint, data=None, json=None):
        """
        Send a PUT request to the Spire API.

        Args:
            endpoint (str): The relative API endpoint (e.g., 'inventory/items/123').
            data (dict, optional): Data to send in the body of the request.
            json (dict, optional): JSON data to send in the body of the request.

        Returns:
            dict: A dictionary containing the response status code, URL, content, and headers.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.put(url, data=data, json=json)
        return self._handle_response(response)

    def _delete(self, endpoint):
        """
        Send a DELETE request to the Spire API.

        Args:
            endpoint (str): The relative API endpoint to delete (e.g., 'inventory/items/123').

        Returns:
            bool: True if the deletion was successful (status code 200, 202, or 204), False otherwise.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.delete(url)
        return response.status_code in (200, 202, 204)
    
    def _handle_response(self, response):
        
        try:
            content = response.json()
        except ValueError:
            content = response.text
        return{
            "status_code": response.status_code,
            "url": response.url,
            "content": content,
            "headers" : response.headers
        }

    def _query(
        self,
        endpoint: str,
        resource_cls: Type["APIResource[T]"],
        *,
        all: bool = False,
        limit: int = 1000,
        start: int = 0,
        query: Optional[str] = None,
        filter: Optional[Dict[str, Any]] = None,
        sort: Optional[Dict[str, str]] = None,
        **extra_params
    ) -> List["APIResource[T]"]:
        """
        Query a list of resources from a Spire API endpoint with support for
        pagination, searching, filtering, and multi-level sorting.

        Args:
            endpoint (str): The API endpoint (e.g., 'sales/orders').
            resource_cls (Type[APIResource[T]]): The resource wrapper class (e.g., SalesOrderResource).
            all (bool, optional): If True, fetches all available pages of results.
            limit (int, optional): Number of results per page (max 1000). Default is 1000.
            start (int, optional): Starting offset for pagination. Default is 0.
            q (str, optional): Free-text search query.
            filter (dict, optional): Dictionary of filter criteria, which will be JSON-encoded.
            sort (dict, optional): Dictionary of sorting rules (e.g., {"orderDate": "desc", "orderNo": "asc"}).
            **extra_params: Any additional query parameters to pass to the API.

        Returns:
            List[APIResource[T]]: A list of wrapped resource instances.
        """
        collected = []
        current_start = start
        remaining = limit
        while True:

            current_limit = min(remaining, 1000)
            # Build the query params as a list of tuples to allow repeated keys like 'sort'
            params: List[Tuple[str, Any]] = [
                ("start", current_start),
                ("limit", current_limit)
            ]

            if query:
                params.append(("q", query))
                
            if filter:
                model_fields = resource_cls.Model.model_fields.keys()
                invalid_fields = [key for key in filter.keys() if key not in model_fields]
                if invalid_fields:
                    raise ValueError(f"Invalid filter field(s): {invalid_fields}. for {resource_cls.Model.__name__} ")

                encoded_filter = json.dumps(filter)
                params.append(("filter", encoded_filter))

            if sort:
                for field, direction in sort.items():
                    prefix = "-" if direction.lower() == "desc" else ""
                    params.append(("sort", f"{prefix}{field}"))

            # Add any additional custom parameters
            for k, v in extra_params.items():
                params.append((k, v))

            response = self._get(endpoint.rstrip("/"), params=params)
            items = response.get("records", [])
            count = response.get("count", 0)

            for item in items:
                collected.append(resource_cls.from_json(item, self))

            # Exit if:
            # - 'all' is False and we reached the requested 'limit'
            # - no more items are returned
            if not all:
                remaining -= len(items)
                if remaining <= 0 or len(items) == 0:
                    break

            # Exit if there are no more items available
            if (current_start + current_limit) >= count or len(items) == 0:
                break

            current_start += current_limit

        return collected


class APIResource(Generic[T]):
    """Active-record-like wrapper that knows a *session* and a *model*."""
    _model: T
    _client: SpireClient
    Model: type
    endpoint: str   

    def __init__(self, model: T, client: SpireClient, **kwargs):
        object.__setattr__(self, "_model", model)
        object.__setattr__(self, "_client", client)

        # Let child classes handle extra kwargs
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __getattr__(self, item):
        """  delegate unknown attributes to the Pydantic model. 
        if you try to access an attribute on your wrapper class that doesn't exist in that class.
        It will automatically forward the request to self._model """
        
        return getattr(self._model, item)
    
    def __setattr__(self, key, value):
        """
        Delegate attribute setting to the Pydantic model unless the attribute 
        starts with an underscore (which indicates internal fields like _model or _client).
        """
        if key.startswith("_"):
            object.__setattr__(self, key, value)
        else:
            setattr(self._model, key, value)
  
    def __str__(self):
        return self._model.model_dump_json(indent=2)
    
    @property
    def model(self) -> T:
        """
        Accessor for the underlying Pydantic model.

        Returns:
            T: The internal Pydantic model instance.
        """
        return self._model
    
    @classmethod
    def from_json(cls, json_data: dict, client: SpireClient, **kwargs) -> "APIResource":
        model_instance = cls.Model(**json_data)
        return cls(model_instance, client, **kwargs)
    
    def refresh(self):
        updated = self._client._get(f"{self.endpoint}/{self.id}")
        self._model = self.Model(**updated)
        return self

    def to_dict(self):
        return self._model.model_dump(exclude_unset=True, exclude_none=True)
    

    

