# cl01-ZGF0YXNpbms
## Overview

cl01-ZGF0YXNpbms is a Python client library generated from the OpenAPI specification. It allows easy interaction with the API endpoints and includes Pydantic models for data validation and serialization.

## Installation

To install the library, use pip:

```bash
pip install -r requirements.txt
```

## Usage

### Initialize the Client

```python
from data_sink_api_client.client import DatasinkAPIClient

client = DatasinkAPIClient(base_url="https://api.example.com")
```

### API Methods


#### read_root

`GET /`

**Parameters:**
_No parameters._

**Example:**

```python

response = client.read_root()
print(response)
```

#### health_check

`GET /health`

**Parameters:**
_No parameters._

**Example:**

```python

response = client.health_check()
print(response)
```

#### get_models

`GET /models`

**Parameters:**
_No parameters._

**Example:**

```python

response = client.get_models()
print(response)
```

#### create_model

`POST /models`

**Parameters:**
- `embedding_model`: models.EmbeddingModel

**Example:**

```python
# Add your request body here
embedding_model = models.EmbeddingModel(...)

response = client.create_model(embedding_model)
print(response)
```

#### create_embedding

`POST /embed`

**Parameters:**
- `embedding_request`: models.EmbeddingRequest

**Example:**

```python
# Add your request body here
embedding_request = models.EmbeddingRequest(...)

response = client.create_embedding(embedding_request)
print(response)
```

#### get_collections

`GET /collections`

**Parameters:**
_No parameters._

**Example:**

```python

response = client.get_collections()
print(response)
```

#### create_collection

`POST /collections`

**Parameters:**
- `collection_info`: models.CollectionInfo

**Example:**

```python
# Add your request body here
collection_info = models.CollectionInfo(...)

response = client.create_collection(collection_info)
print(response)
```

#### update_collection

`PATCH /collections/{collection_id}`

**Parameters:**
- `collection_id`: Any (optional)
- `partial_collection_info`: models.PartialCollectionInfo

**Example:**

```python
# Add your parameters here
collection_id = None
# Add your request body here
partial_collection_info = models.PartialCollectionInfo(...)

response = client.update_collection(collection_id, partial_collection_info)
print(response)
```

#### delete_collection

`DELETE /collections/{collection_id}`

**Parameters:**
- `collection_id`: Any (optional)

**Example:**

```python
# Add your parameters here
collection_id = None

response = client.delete_collection(collection_id)
print(response)
```

#### get_collection

`GET /collections/{collection_id}`

**Parameters:**
- `collection_id`: Any (optional)

**Example:**

```python
# Add your parameters here
collection_id = None

response = client.get_collection(collection_id)
print(response)
```

#### query

`POST /collections/{collection_id}/query`

**Parameters:**
- `collection_id`: Any (optional)
- `query_request`: models.QueryRequest

**Example:**

```python
# Add your parameters here
collection_id = None
# Add your request body here
query_request = models.QueryRequest(...)

response = client.query(collection_id, query_request)
print(response)
```

#### get_collection_entities_list

`GET /collections/{collection_id}/entities`

**Parameters:**
- `collection_id`: Any (optional)
- `{'name': 'limit', 'required': False, 'default': 100}`: Any (optional)
- `{'name': 'offset', 'required': False, 'default': 0}`: Any (optional)

**Example:**

```python
# Add your parameters here
collection_id = None
# Add your query parameters here
{'name': 'limit', 'required': False, 'default': 100} = None
{'name': 'offset', 'required': False, 'default': 0} = None

response = client.get_collection_entities_list(collection_id)
print(response)
```

#### create_collection_entity

`POST /collections/{collection_id}/entities`

**Parameters:**
- `collection_id`: Any (optional)
- `collection_entity`: models.CollectionEntity

**Example:**

```python
# Add your parameters here
collection_id = None
# Add your request body here
collection_entity = models.CollectionEntity(...)

response = client.create_collection_entity(collection_id, collection_entity)
print(response)
```

#### create_collection_entities

`POST /collections/{collection_id}/entities/batch`

**Parameters:**
- `collection_id`: Any (optional)
- `collection_entity`: list[models.CollectionEntity]

**Example:**

```python
# Add your parameters here
collection_id = None
# Add your request body here
collection_entity = list[models.CollectionEntity](...)

response = client.create_collection_entities(collection_id, collection_entity)
print(response)
```

#### get_collection_entity

`GET /collections/{collection_id}/entities/{entity_id}`

**Parameters:**
- `collection_id`: Any (optional)
- `entity_id`: Any (optional)

**Example:**

```python
# Add your parameters here
collection_id = None
entity_id = None

response = client.get_collection_entity(collection_id, entity_id)
print(response)
```

#### update_collection_entity

`PUT /collections/{collection_id}/entities/{entity_id}`

**Parameters:**
- `collection_id`: Any (optional)
- `entity_id`: Any (optional)
- `partial_collection_entity`: models.PartialCollectionEntity

**Example:**

```python
# Add your parameters here
collection_id = None
entity_id = None
# Add your request body here
partial_collection_entity = models.PartialCollectionEntity(...)

response = client.update_collection_entity(collection_id, entity_id, partial_collection_entity)
print(response)
```

#### delete_collection_entity

`DELETE /collections/{collection_id}/entities/{entity_id}`

**Parameters:**
- `collection_id`: Any (optional)
- `entity_id`: Any (optional)

**Example:**

```python
# Add your parameters here
collection_id = None
entity_id = None

response = client.delete_collection_entity(collection_id, entity_id)
print(response)
```

#### delete_collection_entities

`POST /collections/{collection_id}/entities/delete`

**Parameters:**
- `collection_id`: Any (optional)
- `u_u_i_d`: list[Union[UUID, int, str]]

**Example:**

```python
# Add your parameters here
collection_id = None
# Add your request body here
u_u_i_d = list[Union[UUID, int, str]](...)

response = client.delete_collection_entities(collection_id, u_u_i_d)
print(response)
```

#### add_data

`POST /collections/{collection_id}/data`

**Parameters:**
- `collection_id`: Any (optional)
- `data_point`: Union['DataPoint', List['DataPoint']]

**Example:**

```python
# Add your parameters here
collection_id = None
# Add your request body here
data_point = Union['DataPoint', List['DataPoint']](...)

response = client.add_data(collection_id, data_point)
print(response)
```

## License

**[TODO]**