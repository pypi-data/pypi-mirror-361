from pydantic import BaseModel, Field
from typing import Optional, Any, Literal, Union, List
from uuid import UUID
from enum import Enum


class CollectionStatus(str, Enum):
  UNDEFINED: str = 'undefined'  # undefined
  CREATED: str = 'created'  # created
  READY: str = 'ready'  # ready
  DELETED: str = 'deleted'  # deleted
  ERROR: str = 'error'  # error
  PENDING: str = 'pending'  # pending


class CollectionType(str, Enum):
  QDRANT: str = 'qdrant'  # qdrant
  UNKNOWN: str = 'unknown'  # unknown


class DistanceMethod(str, Enum):
  COSINE: str = 'Cosine'  # Cosine
  EUCLIDEAN: str = 'Euclidean'  # Euclidean
  DOT: str = 'Dot'  # Dot
  MANHATTAN: str = 'Manhattan'  # Manhattan


class CollectionEntity(BaseModel):
  input: str = ...  # Input
  payload: dict = ...  # Payload
  id: Union[str, int, UUID] = ...  # Id
  variants: Union[List[str], Any] = None  # Variants


class CollectionEntityAlreadyExistsResponse(BaseModel):
  detail: str = 'Collection entity with this id already exists'  # Detail


class CollectionEntityListResponse(BaseModel):
  results: List['CollectionEntityResponse'] = ...  # Results
  count: int = ...  # Count


class CollectionEntityResponse(BaseModel):
  id: Union[str, int, UUID] = ...  # Id
  payload: dict = ...  # Payload


class CollectionInfo(BaseModel):
  id: Union[str, int, UUID, Any] = None  # Id
  name: str = ...  # Name
  embedding_model: 'EmbeddingModel' = ...
  internal_name: str = 'None'  # Internal Name
  collection_id: Union[UUID, Any] = None  # Collection Id
  metadata: Union[dict, 'QdrantCollectionMetadata'] = None  # Metadata
  owner: Union[str, Any] = None  # Owner
  collection_type: 'CollectionType' = 'qdrant'
  status: 'CollectionStatus' = 'undefined'


class CollectionNotFoundResponse(BaseModel):
  detail: str = 'Collection not found'  # Detail


class DataPoint(BaseModel):
  input: str = ...  # Input
  payload: dict = ...  # Payload
  id: Union[str, int, UUID] = None  # Id


class EmbeddingModel(BaseModel):
  id: Union[str, int, UUID] = None  # Id
  name: str = ...  # Name
  version: str = '0.0.1'  # Version
  library: str = 'transformers'  # Library
  loaded: bool = False  # Loaded
  eb_model: Any = 'None'  # Eb Model
  tokenizer: Any = 'None'  # Tokenizer
  target_location: Union[str, Any] = None  # Target Location


class EmbeddingRequest(BaseModel):
  text: Union[str, List[str]] = ...  # Text
  eb_model_name: str = ...  # Eb Model Name
  eb_model_version: Union[str, Any] = None  # Eb Model Version


class EmbeddingResponse(BaseModel):
  embeddings: 'Embeddings' = ...  # Embeddings
  eb_model_name: str = ...  # Eb Model Name
  eb_model_version: Union[str, Any] = None  # Eb Model Version


class ErrorResponse(BaseModel):
  detail: str = ...  # Detail


class HTTPValidationError(BaseModel):
  detail: List['ValidationError'] = None  # Detail


class HealthCheckResponse(BaseModel):
  status: str = 'ok'  # Status


class ModelNotFoundResponse(BaseModel):
  detail: str = 'Model not found'  # Detail


class PartialCollectionEntity(BaseModel):
  input: Union[str, Any] = None  # Input
  payload: Union[dict, Any] = None  # Payload
  id: Union[str, int, UUID, Any] = None  # Id
  variants: Union[List[str], Any] = None  # Variants


class PartialCollectionInfo(BaseModel):
  id: Union[str, int, UUID, Any] = None  # Id
  name: Union[str, Any] = None  # Name
  embedding_model: Union[Any, 'PartialEmbeddingModel'] = None
  internal_name: Union[str, Any] = None  # Internal Name
  collection_id: Union[UUID, Any] = None  # Collection Id
  metadata: Union[dict, 'QdrantCollectionMetadata', Any] = None  # Metadata
  owner: Union[str, Any] = None  # Owner
  collection_type: Union['CollectionType', Any] = None
  status: Union['CollectionStatus', Any] = None


class PartialEmbeddingModel(BaseModel):
  id: Union[str, int, UUID, Any] = None  # Id
  name: Union[str, Any] = None  # Name
  version: Union[str, Any] = None  # Version
  library: Union[str, Any] = None  # Library
  loaded: Union[bool, Any] = None  # Loaded
  eb_model: Any = 'None'  # Eb Model
  tokenizer: Any = 'None'  # Tokenizer
  target_location: Union[str, Any] = None  # Target Location


class QdrantCollectionInfo(BaseModel):
  id: Union[str, int, UUID, Any] = None  # Id
  name: str = ...  # Name
  embedding_model: 'EmbeddingModel' = ...
  internal_name: str = 'None'  # Internal Name
  collection_id: Union[UUID, Any] = None  # Collection Id
  metadata: 'QdrantCollectionMetadata' = ...
  owner: Union[str, Any] = None  # Owner
  collection_type: 'CollectionType' = 'qdrant'
  status: 'CollectionStatus' = 'undefined'


class QdrantCollectionMetadata(BaseModel):
  host: str = ...  # Host
  token: str = ...  # Token
  distance_method: 'DistanceMethod' = 'Dot'
  dimension: Union[int, Any] = None  # Dimension


class QueryRequest(BaseModel):
  query: str = ...  # Query
  top_k: Union[int, Any] = 10  # Top K
  point_ids: Union[List[int], Any] = None  # Point Ids


class ReadRootResponse(BaseModel):
  status: str = 'ok'  # Status


class UnauthorizedResponse(BaseModel):
  detail: str = 'Unauthorized'  # Detail


class UnsupportedCollectionTypeResponse(BaseModel):
  detail: str = 'Unsupported collection type'  # Detail


class ValidationError(BaseModel):
  loc: List[Union[str, int]] = ...  # Location
  msg: str = ...  # Message
  type: str = ...  # Error Type

