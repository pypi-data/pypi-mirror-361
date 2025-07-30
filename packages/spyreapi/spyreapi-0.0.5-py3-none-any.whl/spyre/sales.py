from .client import APIResource
from .Models.sales_models import SalesOrder, SalesOrderItem, Invoice
from .Models.shared_models import Note
from .utils import *
from .client import SpireClient
from urllib.parse import urlparse 
from .Exceptions import CreateRequestError
from typing import Any, Optional, List, Dict
from .crm import note, CRMClient

class OrdersClient():

    def __init__(self, client: SpireClient):
        self.client = client
        self.endpoint = "sales/orders"
    
    def get_sales_order(self, id: int = None, order_number: str = None) -> "salesOrder":
        """
        Retrieve a sales order by its ID or order number.

        Args:
            id (int, optional): The ID of the sales order to retrieve.
            order_number (str, optional): The order number of the sales order to retrieve.

        Returns:
            salesOrder: A `salesOrder` wrapper instance containing the retrieved data.

        Raises:
            ValueError: If neither id nor order_number is provided, or if no matching order is found.
        """
        if id is not None:
            response = self.client._get(f"/{self.endpoint}/{str(id)}")
            return salesOrder.from_json(response, self.client)
        elif order_number is not None:
            orders = self.query_sales_orders(query=order_number)
            for order in orders:
                if getattr(order, "orderNo", None) == order_number:
                    return order
            raise ValueError(f"No sales order found with order number: {order_number}")
        else:
            raise ValueError("Either 'id' or 'order_number' must be provided.")
    
    

    def create_sales_order(self, sales_order : 'SalesOrder') -> 'salesOrder':
        """
        Create a new sales order.

        Sends a POST request to the sales order endpoint .

        Args:
            sales_order (dict): A SalesOrder instance containing the sales order details.

        Returns:
            salesOrder: The created SalesOrder instance.

        Raises:
            CreateRequestError: If the creation fails or response is invalid.
        """

        response =  self.client._post(f"/{self.endpoint}", json=sales_order.model_dump(exclude_unset=True, exclude_none=True))
        if response.get('status_code') == 201:
            location = response.get('headers').get('location')
            parsed_url = urlparse(location)
            path_segments = parsed_url.path.rstrip("/").split("/")
            id = path_segments[-1]
            return self.get_sales_order(id)
        else:
            error_message = response.get('content')
            raise CreateRequestError(self.endpoint, status_code=response.get('status_code'), error_message=error_message)

    def update_sales_order(self, id: int, sales_order : 'SalesOrder') -> 'salesOrder':
        """
        Update an existing sales order by ID.

        Sends a PUT request to the sales order endpoint with the provided sales order data
        to update the existing record. Returns a wrapped `salesOrder` object containing
        the updated information.

        Args:
            id (int): The ID of the sales order to update.
            sales_order (SaleOrder): A SalesOrder instance with the sales order details.

        Returns:
            salesOrder: An instance of the salesOrder wrapper class initialized with 
                        the updated data and client session.
        """
        response = self.client._put(f"/{self.endpoint}/{str(id)}", json=sales_order.model_dump(exclude_none=True, exclude_unset=True))
        return salesOrder.from_json(response, self.client)

    def delete_sales_order(self, id: int) -> bool:
        """
        Delete a sales order by its ID.

        Sends a DELETE request to the sales order endpoint to remove the specified
        sales order from the system.

        Args:
            id (int): The ID of the sales order to delete.

        Returns:
            bool: True if the sales order was successfully deleted, False otherwise.
        """
        return self.client._delete(f"/{self.endpoint}/{str(id)}")

    def query_sales_orders(
        self,
        *,
        query: Optional[str] = None,
        sort: Optional[Dict[str, str]] = None,
        filter: Optional[Dict[str, Any]] = None,
        all: bool = False,
        limit: int = 1000,
        start: int = 0,
        **extra_params
    ) -> List["salesOrder"]:
        """
        Query sales orders with optional full-text search, filtering, multi-field sorting, and pagination.

        Args:
            q (str, optional): Full-text search string.
            sort (dict, optional): Dictionary of sorting rules (e.g., {"orderDate": "desc", "orderNo": "asc"}).
            filter (dict, optional): Dictionary of filters to apply (will be JSON-encoded and URL-safe).
            all (bool, optional): If True, retrieves all pages of results.
            limit (int, optional): Number of results per page (max 1000).
            start (int, optional): Starting offset for pagination.
            **extra_params: Any additional parameters to include in the query.

        Returns:
            List[salesOrder]: List of wrapped sales order resources.
        """
        return self.client._query(
            endpoint=self.endpoint,
            resource_cls=salesOrder,
            query=query,
            sort=sort,
            filter=filter,
            all=all,
            limit=limit,
            start=start,
            **extra_params
        )
    
    def create_sales_order_note(self, id: int , note_body : str, note_subject : str = "Note") -> note:
        """
        Create a new note on this sales order.

        Args:
            id (int): The id of the salesOrder to create a note on.
            note (str): The body of the note 
        Returns:
            note: The created note

        Raises:
            CreateRequestError: If the creation fails or response is invalid.
        """

        note_model = Note(body=note_body, subject=note_subject)
        response =  self.client._post(f"/{self.endpoint}/{id}/notes/", json=note_model.model_dump(exclude_unset=True, exclude_none=True))
        if response.get('status_code') == 201:
            location = response.get('headers').get('location')
            parsed_url = urlparse(location)
            path_segments = parsed_url.path.rstrip("/").split("/")
            id = path_segments[-1]
            return CRMClient(client=self.client).get_note(id)
        else:
            error_message = response.get('content')
            raise CreateRequestError(self.endpoint, status_code=response.get('status_code'), error_message=error_message)
    
class InvoiceClient():
    
    def __init__(self, client : SpireClient):
        self.client = client
        self.endpoint = "sales/invoices"

    def get_invoice(self, id: int) -> 'invoice':
        """
        Retrieve a sales invoice by its ID.

        Sends a GET request to the invoices endpoint to fetch the invoice data.

        Args:
            id (int): The ID of the invoice to retrieve.

        Returns:
            invoice: An invoice instance created from the response data.
        """
        response = self.client._get(f"/{self.endpoint}/{id}")
        return invoice.from_json(response, self.client)

    def update_invoice(self, id: int, invoice : Invoice) -> 'invoice':
        """
        Update an existing invoice by ID.

        Sends a PUT request with updated invoice data to the invoices endpoint.

        Args:
            id (int): The ID of the invoice to update.
            invoice (Invoice): The Invoice model instance containing updated data.

        Returns:
            invoice: The updated invoice instance created from the response data.
        """
        response = self.client._put(f"/{self.endpoint}/{id}", json=invoice.model_dump(exclude_none=True, exclude_unset=True))
        return invoice.from_json(response, self.client)
    
    def query_invoices(
        self,
        *,
        query: Optional[str] = None,
        sort: Optional[Dict[str, str]] = None,
        filter: Optional[Dict[str, Any]] = None,
        all: bool = False,
        limit: int = 1000,
        start: int = 0,
        **extra_params
    ) -> List["salesOrder"]:
        """
        Query invoices with optional full-text search, filtering, multi-field sorting, and pagination.

        Args:
            q (str, optional): Full-text search string.
            sort (dict, optional): Dictionary of sorting rules (e.g., {"orderDate": "desc", "orderNo": "asc"}).
            filter (dict, optional): Dictionary of filters to apply (will be JSON-encoded and URL-safe).
            all (bool, optional): If True, retrieves all pages of results.
            limit (int, optional): Number of results per page (max 1000).
            start (int, optional): Starting offset for pagination.
            **extra_params: Any additional parameters to include in the query.

        Returns:
            List[invoice]: List of wrapped invoice resources.
        """
        return self.client._query(
            endpoint=self.endpoint,
            resource_cls=invoice,
            query=query,
            sort=sort,
            filter=filter,
            all=all,
            limit=limit,
            start=start,
            **extra_params
        )


class salesOrder(APIResource[SalesOrder]):
    endpoint = "sales/orders/"
    Model = SalesOrder 

    def invoice(self):
        """
        Invoice the current sales order.

        Sends a POST request to create an invoice for this sales order.
        Note that quotes (salesOrder with type "Q") cannot be invoiced.

        Returns:
            invoice: The created invoice object if successful.
            dict: The full response if invoicing failed.
 
        """
        response = self._client._post(f"/{self.endpoint}/{str(self.id)}/invoice")
        if response.get('status_code') == 200:
            data = response.get('content').get('invoice')
            return salesOrder.from_json(json_data=data, client= self._client)
        else:
            error_message = response.get('content')
            raise CreateRequestError(self.endpoint, status_code=response.get('status_code'), error_message=error_message)
    
    def process(self) -> 'salesOrder':
        """
        Set the status of the salesOrder to 'Processed' (status = 'P').

        Sends a PUT request to update the status field of this Sales Oder.

        Returns:
            salesOrder: The updated salesOrder object reflecting the new status.
        """
        response = self._client._put(
            f"/{self.endpoint}/{str(self.id)}",
            json={"status": "P"}    
        )
        return salesOrder.from_json(response, self._client)
    
    def delete(self):
        """
        Cancels or deletes the sales order.

        Sends a DELETE request to the API to remove the sales order with the current ID.

        Returns:
            bool: True if the order was successfully deleted (HTTP 204 or 200), False otherwise.
        """
        
        return self._client._delete(f"/{self.endpoint}/{str(self.id)}")
    
    def update(self, order: "salesOrder" = None) -> 'salesOrder':
        """
        Update the sales order.

        If no order object is provided, updates the current instance on the server.
        If an order object is provided, updates the sales order using the given data.

        Args:
            order (salesOrder, optional): An optional salesOrder instance to use for the update.

        Returns:
            salesOrder: The updated salesOrder object reflecting the new status.
        """
        data = order.model_dump(exclude_unset=True, exclude_none=True) if order else self.model_dump(exclude_unset=True, exclude_none=True)
        response = self._client._put(f"/{self.endpoint}/{str(self.id)}", json=data)
        return salesOrder.from_json(response, self._client)    

    def add_note(self, note_body : "str" , note_subject : "str" = "Note") -> note:
        """
        Add a note to this sales order

        Args:
            note_body (str): the body of the note.
            note_subject (str, "Note"): the subject of the note. the defualt value is just "Note"

        Returns:
            note: The note created.
        """

        note_model = Note(body=note_body, subject=note_subject)
        response =  self._client._post(f"/{self.endpoint}/{str(self.id)}/notes/", json=note_model.model_dump(exclude_unset=True, exclude_none=True))
        if response.get('status_code') == 201:
            location = response.get('headers').get('location')
            parsed_url = urlparse(location)
            path_segments = parsed_url.path.rstrip("/").split("/")
            id = path_segments[-1]
            return CRMClient(client=self._client).get_note(id)
        else:
            error_message = response.get('content')
            raise CreateRequestError(f"/{self.endpoint}/{str(self.id)}/notes/", status_code=response.get('status_code'), error_message=error_message)

class invoice(APIResource[Invoice]):
    endpoint = "sales/invoices/"
    Model = Invoice

    def reverse(self):
        """
        Convert this invoice into a sales order.

        This method uses the internal model of the invoice to create a new sales order
        using the `create_sales_order_from_invoice` utility function. It then submits the
        order through the OrdersClient.

        Returns:
            salesOrder: The created sales order instance returned by the API.
        """
        order_converted = create_sales_order_from_invoice(self._model)
        return OrdersClient(self._client).create_sales_order(order_converted)

    def update(self , invoice_: "Invoice" = None) -> 'invoice':
        """
        Update this invoice.

        Sends a PUT request with updated invoice data to the invoices endpoint.
        If no order object is provided, updates the current instance on the server.

        Args:
            invoice (Invoice): The Invoice model instance containing updated data.

        Returns:
            invoice: The updated invoice instance created from the response data.
        """
        data = invoice_.model_dump(exclude_unset=True, exclude_none=True) if invoice_ else self.model_dump(exclude_unset=True, exclude_none=True)
        response = self._client._put(f"/{self.endpoint}/{str(self.id)}", json=data)
        return invoice.from_json(response, self._client)   
    

