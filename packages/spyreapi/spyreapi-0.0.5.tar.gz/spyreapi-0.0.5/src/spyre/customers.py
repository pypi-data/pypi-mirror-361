from .client import SpireClient, APIResource
from .Models.customers_models import Customer
from .Exceptions import CreateRequestError
from urllib.parse import urlparse
from typing import Optional, Dict, Any, List

class CustomerClient():

    def __init__(self, client : SpireClient):
        self.client = client
        self.endpoint = "customers"

    def get_customer(self, id: int) -> "customer":
        """
        Retrieve a customer by ID.

        Sends a GET request to the customer endpoint to fetch details of a specific customer.

        Args:
            id (int): The ID of the customer to retrieve.

        Returns:
            Customer: A Customer object populated with the retrieved data.
        """

        response = self.client._get(f"{self.endpoint}/{str(id)}")
        return customer.from_json(json_data=response, client=self.client)
    
    def create_customer(self, customer : 'Customer') -> "customer":
        """
        Create a new customer.

        Sends a POST request to the customer endpoint with the customer data
        to create a new customer record.

        Args:
            customer (Customer): The Customer object containing the data to be created.

        Returns:
            Customer: The newly created Customer object returned by the API.
        """

        response =  self.client._post(f"/{self.endpoint}", json=customer.model_dump(exclude_unset=True, exclude_none=True))
        if response.get('status_code') == 201:
            location = response.get('headers').get('location')
            parsed_url = urlparse(location)
            path_segments = parsed_url.path.rstrip("/").split("/")
            id = path_segments[-1]
            return self.get_customer(id)
        else:
            error_message = response.get('content')
            raise CreateRequestError(self.endpoint, status_code=response.get('status_code'), error_message=error_message)
        
    def update_customer(self, id : int, customer : 'Customer') -> "customer":
        """
        Update an existing customer by ID.

        Sends a PUT request to update a customer record using the provided customer data.

        Args:
            id (int): The ID of the customer to update.
            customer (Customer): A Pydantic model representing the updated customer data.

        Returns:
            customer: A new Customer instance built from the updated response data.
        """
        response = self.client._put(f"/{self.endpoint}/{str(id)}", json=customer.model_dump(exclude_none=True, exclude_unset=True))
        return customer.from_json(response, self.client)
    
    def delete_customer(self, id : int) -> bool:
        """
        Delete a customer by ID.

        Sends a DELETE request to the customer endpoint. Returns True if deletion was successful (HTTP 200/204),
        otherwise returns False.

        Args:
            id (int): The ID of the customer to delete.

        Returns:
            bool: True if the customer was successfully deleted, False otherwise.
        """
        return self.client._delete(f"/{self.endpoint}/{str(id)}")
    

    def query_customers (
        self,
        *,
        query: Optional[str] = None,
        sort: Optional[Dict[str, str]] = None,
        filter: Optional[Dict[str, Any]] = None,
        all: bool = False,
        limit: int = 1000,
        start: int = 0,
        **extra_params
    ) -> List["customer"]:
        """
        Query customer with optional full-text search, filtering, multi-field sorting, and pagination.

        Args:
            q (str, optional): Full-text search string.
            sort (dict, optional): Dictionary of sorting rules (e.g., {"orderDate": "desc", "orderNo": "asc"}).
            filter (dict, optional): Dictionary of filters to apply (will be JSON-encoded and URL-safe).
            all (bool, optional): If True, retrieves all pages of results.
            limit (int, optional): Number of results per page (max 1000).
            start (int, optional): Starting offset for pagination.
            **extra_params: Any additional parameters to include in the query.

        Returns:
            List[customer]: List of wrapped customer resources.
        """
        return self.client._query(
            endpoint=self.endpoint,
            resource_cls=customer,
            query=query,
            sort=sort,
            filter=filter,
            all=all,
            limit=limit,
            start=start,
            **extra_params
        )
    

class customer(APIResource[Customer]):
    endpoint = "customers"
    Model = Customer


    def delete(self):
        """
        Deletes the Customer from Spire.

        Sends a DELETE request to the API to remove the customer with the current ID.

        Returns:
            bool: True if the order was successfully deleted (HTTP 204 or 200), False otherwise.
        """
        return self._client._delete(f"/{self.endpoint}/{str(self.id)}")

    def update(self, customer: "customer" = None) -> 'customer':
        """
        Update the customer.

        If no order object is provided, updates the current instance on the server.
        If an order object is provided, updates the customer using the given data.

        Args:
            customer (customer, optional): An optional customer instance to use for the update.

        Returns:
            customer: The updated customer object reflecting the new status.
        """
        data = customer.model_dump(exclude_unset=True, exclude_none=True) if customer else self.model_dump(exclude_unset=True, exclude_none=True)
        response = self._client._put(f"/{self.endpoint}/{str(self.id)}", json=data)
        return customer.from_json(response, self._client)
