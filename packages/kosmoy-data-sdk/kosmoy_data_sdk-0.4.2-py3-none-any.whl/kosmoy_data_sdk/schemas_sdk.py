from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


# Base models for common fields
class BaseSdkModel(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    id: int


class NameDescriptionModel(BaseSdkModel):
    name: str
    description: Optional[str] = None


# User Status
class UserStatusModel(BaseSdkModel):
    name: str


# Assistant Types
class AssistantTypesModel(NameDescriptionModel):
    pass


# Assistant Scopes
class AssistantScopesModel(BaseSdkModel):
    name: str


# Service Types
class ServiceTypesModel(NameDescriptionModel):
    pass


# Services
class ServicesModel(NameDescriptionModel):
    provider: int = Field(..., alias="provider")
    provider_name: Optional[str] = None
    service_type: int = Field(..., alias="service_type")
    service_type_name: Optional[str] = None
    req_config_params: Optional[Dict[str, Any]] = None


# Data Source Types
class DataSourceTypesModel(NameDescriptionModel):
    pass


# Data Sources
class DataSourcesModel(NameDescriptionModel):
    provider: int = Field(..., alias="provider")
    provider_name: Optional[str] = None
    data_source_type: int = Field(..., alias="data_source_type")
    data_source_type_name: Optional[str] = None
    req_config_params: Optional[Dict[str, Any]] = None


# Channels
class ChannelsModel(NameDescriptionModel):
    assistant_scope: int = Field(..., alias="assistant_scope")
    assistant_scope_name: Optional[str] = None
    provider: int = Field(..., alias="provider")
    provider_name: Optional[str] = None
    req_config_params: Optional[Dict[str, Any]] = None


# Assistant Types Service Types
class AssistantTypesServiceTypesModel(BaseSdkModel):
    assistant_type: int = Field(..., alias="assistant_type")
    assistant_type_name: Optional[str] = None
    service_type: int = Field(..., alias="service_type")
    service_type_name: Optional[str] = None


# Session Types
class SessionTypesModel(BaseSdkModel):
    name: str


# Connection Types
class ConnectionTypesModel(NameDescriptionModel):
    pass


# Connection Providers
class ConnectionProvidersModel(NameDescriptionModel):
    connection_type: int = Field(..., alias="connection_type")
    connection_type_name: Optional[str] = None
    req_connection_params: Dict[str, Any]
    req_collection_params: Optional[Dict[str, Any]] = None


# Vector Distance Strategies
class VectorDistanceStrategiesModel(NameDescriptionModel):
    pass


# Connection Providers Vector Distance Strategies
class ConnectionProvidersVectorDistanceStrategiesModel(BaseSdkModel):
    connection_provider: int = Field(..., alias="connection_provider")
    connection_provider_name: Optional[str] = None
    vector_distance_strategy: int = Field(..., alias="vector_distance_strategy")
    vector_distance_strategy_name: Optional[str] = None


# Retriever Types
class RetrieverTypesModel(NameDescriptionModel):
    pass


# Retriever Strategies
class RetrieverStrategiesModel(NameDescriptionModel):
    req_retriever_params: Dict[str, Any]


# Vector Channel Strategies
class VectorChannelStrategiesModel(NameDescriptionModel):
    req_vector_channel_params: Optional[Dict[str, Any]] = None


# Run Statuses
class RunStatusesModel(BaseSdkModel):
    name: str


# Avatars
class AvatarsModel(BaseSdkModel):
    avatar_path: str
    is_default: bool = True


# Guardrail Types
class GuardrailTypesModel(NameDescriptionModel):
    allowed_scopes: List[str]
    allowed_subtypes: Optional[List[str]] = None
    is_built_in: bool = False


# Original fixed data models (keeping for backward compatibility)

class AvailableModelTagModel(BaseModel):
    id: int
    name: str
    description: Optional[str] = None



class ProviderModel(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    id: int
    name: str
    description: Optional[str] = None
    logo: Optional[str] = None
    req_config_params: Optional[Dict[str, Any]] = None
    # stage_name: str = "develop"


class ModelCreatorModel(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    id: int
    name: str
    description: Optional[str] = None
    logo: Optional[str] = None
    stage_name: str = "develop"


class AvailableModelModel(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    id: int
    provider: ProviderModel
    creator: ModelCreatorModel
    name: str
    model_call_name: str
    req_config_params: Optional[Dict[str, Any]] = None
    cost_input_token: float
    cost_output_token: float
    embedding_dimension: Optional[int] = None
    is_verified: bool
    is_legacy: bool = False
    model_source_url: Optional[str] = None
    model_input: List[str]
    tags: List[AvailableModelTagModel]
    model_output: List[str]
    stage_name: str = "develop"