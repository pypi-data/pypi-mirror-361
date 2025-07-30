# Spire API Python Client

A robust and extensible Python client for interacting with the [Spire Business Software API](https://developer.spiresystems.com/reference). This client provides an object-oriented interface to get, create, update, delete, query, filter, sort, and manage various Spire modules such as Sales Orders, Invoices, Inventory Items, and more.

---

## ✨ Features

- ✅ Object-oriented resource wrappers for each module (e.g., `salesOrder`, `invoice`, `item`)
- 🔍 Full-text search via `q` parameter
- 🔁 Pagination with `start` and `limit` support
- 🧾 JSON-based advanced filtering (supports `$gt`, `$lt`, `$in`, `$or`, etc.)
- ↕️ Multi-field sorting with ascending/descending control
- 🔧 Clean abstraction layer for API endpoints
- 📦 Powered by `pydantic` models for validation

---

## 📦 Installation

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

- How to set up your spire client

### Find your Spire URL

The base URL for the Spire API is the same url provided by Spire that you use to access Spire server and uses port 10880 as default:
Replace {spire-url} with the url provided by Spire.

- https://{spire-url}:10880/api/v2/
  
Spire Cloud
If you are using Spire cloud you do not need to specify a port. The base URL for API for Spire Cloud customers would be:

- https://{spire-cloud-url}/api/v2/

### Set up your client with your credentials

```python
from spyre import Spire
# host is your spire url and the port if applicable
client = Spire(host = 'your-spire-host', company = 'comapany-name' , username = 'username' , password = 'password' )

```

## Example : Updating the status of an inventory item 
```python
item = client.inventory.items.get_item(1101)    # Gets item with id 1101
item.status = 1                                 # Use either item. or item.model. . item.model. will bring up all attributes
item.update()
```
