import requests
from typing import List, Optional
from pydantic import TypeAdapter
from .schemas_sdk import (
    UserStatusModel, AssistantTypesModel, AssistantScopesModel, ServiceTypesModel,
    ServicesModel, DataSourceTypesModel, DataSourcesModel, ChannelsModel,
    AssistantTypesServiceTypesModel, SessionTypesModel, ModelCreatorModel,
    ConnectionTypesModel, ConnectionProvidersModel, VectorDistanceStrategiesModel,
    ConnectionProvidersVectorDistanceStrategiesModel, RetrieverTypesModel,
    RetrieverStrategiesModel, VectorChannelStrategiesModel, RunStatusesModel,
    AvatarsModel, GuardrailTypesModel, AvailableModelModel, ProviderModel
)



class FixedModelsAPI:
    """
    Provides access to fixed model data through API requests.
    This class offers the same interface as ModelsAPI but uses a different endpoint.
    """

    def __init__(self, base_url: str):
        self.base_url = base_url

    # New fixed data methods

    # User Status
    def get_user_statuses(self) -> List[UserStatusModel]:
        """Get a list of all user statuses."""
        response = requests.get(f"{self.base_url}/user-statuses/")
        response.raise_for_status()
        adapter = TypeAdapter(List[UserStatusModel])
        return adapter.validate_python(response.json())

    def get_user_status(self, status_id: int) -> Optional[UserStatusModel]:
        """Get details for a specific user status by ID."""
        try:
            response = requests.get(f"{self.base_url}/user-statuses/{status_id}")
            response.raise_for_status()
            adapter = TypeAdapter(UserStatusModel)
            return adapter.validate_python(response.json())
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    # Assistant Types
    def get_assistant_types(self) -> List[AssistantTypesModel]:
        """Get a list of all assistant types."""
        response = requests.get(f"{self.base_url}/assistant-types/")
        response.raise_for_status()
        adapter = TypeAdapter(List[AssistantTypesModel])
        return adapter.validate_python(response.json())

    def get_assistant_type(self, type_id: int) -> Optional[AssistantTypesModel]:
        """Get details for a specific assistant type by ID."""
        try:
            response = requests.get(f"{self.base_url}/assistant-types/{type_id}")
            response.raise_for_status()
            adapter = TypeAdapter(AssistantTypesModel)
            return adapter.validate_python(response.json())
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    # Assistant Scopes
    def get_assistant_scopes(self) -> List[AssistantScopesModel]:
        """Get a list of all assistant scopes."""
        response = requests.get(f"{self.base_url}/assistant-scopes/")
        response.raise_for_status()
        adapter = TypeAdapter(List[AssistantScopesModel])
        return adapter.validate_python(response.json())

    def get_assistant_scope(self, scope_id: int) -> Optional[AssistantScopesModel]:
        """Get details for a specific assistant scope by ID."""
        try:
            response = requests.get(f"{self.base_url}/assistant-scopes/{scope_id}")
            response.raise_for_status()
            adapter = TypeAdapter(AssistantScopesModel)
            return adapter.validate_python(response.json())
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    # Service Types
    def get_service_types(self) -> List[ServiceTypesModel]:
        """Get a list of all service types."""
        response = requests.get(f"{self.base_url}/service-types/")
        response.raise_for_status()
        adapter = TypeAdapter(List[ServiceTypesModel])
        return adapter.validate_python(response.json())

    def get_service_type(self, type_id: int) -> Optional[ServiceTypesModel]:
        """Get details for a specific service type by ID."""
        try:
            response = requests.get(f"{self.base_url}/service-types/{type_id}")
            response.raise_for_status()
            adapter = TypeAdapter(ServiceTypesModel)
            return adapter.validate_python(response.json())
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    # Services
    def get_services(self) -> List[ServicesModel]:
        """Get a list of all services."""
        response = requests.get(f"{self.base_url}/services/")
        response.raise_for_status()
        adapter = TypeAdapter(List[ServicesModel])
        return adapter.validate_python(response.json())

    def get_service(self, service_id: int) -> Optional[ServicesModel]:
        """Get details for a specific service by ID."""
        try:
            response = requests.get(f"{self.base_url}/services/{service_id}")
            response.raise_for_status()
            adapter = TypeAdapter(ServicesModel)
            return adapter.validate_python(response.json())
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    # Data Source Types
    def get_data_source_types(self) -> List[DataSourceTypesModel]:
        """Get a list of all data source types."""
        response = requests.get(f"{self.base_url}/data-source-types/")
        response.raise_for_status()
        adapter = TypeAdapter(List[DataSourceTypesModel])
        return adapter.validate_python(response.json())

    def get_data_source_type(self, type_id: int) -> Optional[DataSourceTypesModel]:
        """Get details for a specific data source type by ID."""
        try:
            response = requests.get(f"{self.base_url}/data-source-types/{type_id}")
            response.raise_for_status()
            adapter = TypeAdapter(DataSourceTypesModel)
            return adapter.validate_python(response.json())
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    # Data Sources
    def get_data_sources(self) -> List[DataSourcesModel]:
        """Get a list of all data sources."""
        response = requests.get(f"{self.base_url}/data-sources/")
        response.raise_for_status()
        adapter = TypeAdapter(List[DataSourcesModel])
        return adapter.validate_python(response.json())

    def get_data_source(self, source_id: int) -> Optional[DataSourcesModel]:
        """Get details for a specific data source by ID."""
        try:
            response = requests.get(f"{self.base_url}/data-sources/{source_id}")
            response.raise_for_status()
            adapter = TypeAdapter(DataSourcesModel)
            return adapter.validate_python(response.json())
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    # Channels
    def get_channels(self) -> List[ChannelsModel]:
        """Get a list of all channels."""
        response = requests.get(f"{self.base_url}/channels/")
        response.raise_for_status()
        adapter = TypeAdapter(List[ChannelsModel])
        return adapter.validate_python(response.json())

    def get_channel(self, channel_id: int) -> Optional[ChannelsModel]:
        """Get details for a specific channel by ID."""
        try:
            response = requests.get(f"{self.base_url}/channels/{channel_id}")
            response.raise_for_status()
            adapter = TypeAdapter(ChannelsModel)
            return adapter.validate_python(response.json())
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    # Assistant Types Service Types
    def get_assistant_types_service_types(self) -> List[AssistantTypesServiceTypesModel]:
        """Get a list of all assistant types service types."""
        response = requests.get(f"{self.base_url}/assistant-types-service-types/")
        response.raise_for_status()
        adapter = TypeAdapter(List[AssistantTypesServiceTypesModel])
        return adapter.validate_python(response.json())

    def get_assistant_types_service_type(self, id: int) -> Optional[AssistantTypesServiceTypesModel]:
        """Get details for a specific assistant types service type by ID."""
        try:
            response = requests.get(f"{self.base_url}/assistant-types-service-types/{id}")
            response.raise_for_status()
            adapter = TypeAdapter(AssistantTypesServiceTypesModel)
            return adapter.validate_python(response.json())
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    # Session Types
    def get_session_types(self) -> List[SessionTypesModel]:
        """Get a list of all session types."""
        response = requests.get(f"{self.base_url}/session-types/")
        response.raise_for_status()
        adapter = TypeAdapter(List[SessionTypesModel])
        return adapter.validate_python(response.json())

    def get_session_type(self, type_id: int) -> Optional[SessionTypesModel]:
        """Get details for a specific session type by ID."""
        try:
            response = requests.get(f"{self.base_url}/session-types/{type_id}")
            response.raise_for_status()
            adapter = TypeAdapter(SessionTypesModel)
            return adapter.validate_python(response.json())
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    # Connection Types
    def get_connection_types(self) -> List[ConnectionTypesModel]:
        """Get a list of all connection types."""
        response = requests.get(f"{self.base_url}/connection-types/")
        response.raise_for_status()
        adapter = TypeAdapter(List[ConnectionTypesModel])
        return adapter.validate_python(response.json())

    def get_connection_type(self, type_id: int) -> Optional[ConnectionTypesModel]:
        """Get details for a specific connection type by ID."""
        try:
            response = requests.get(f"{self.base_url}/connection-types/{type_id}")
            response.raise_for_status()
            adapter = TypeAdapter(ConnectionTypesModel)
            return adapter.validate_python(response.json())
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    # Connection Providers
    def get_connection_providers(self) -> List[ConnectionProvidersModel]:
        """Get a list of all connection providers."""
        response = requests.get(f"{self.base_url}/connection-providers/")
        response.raise_for_status()
        adapter = TypeAdapter(List[ConnectionProvidersModel])
        return adapter.validate_python(response.json())

    def get_connection_provider(self, provider_id: int) -> Optional[ConnectionProvidersModel]:
        """Get details for a specific connection provider by ID."""
        try:
            response = requests.get(f"{self.base_url}/connection-providers/{provider_id}")
            response.raise_for_status()
            adapter = TypeAdapter(ConnectionProvidersModel)
            return adapter.validate_python(response.json())
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    # Vector Distance Strategies
    def get_vector_distance_strategies(self) -> List[VectorDistanceStrategiesModel]:
        """Get a list of all vector distance strategies."""
        response = requests.get(f"{self.base_url}/vector-distance-strategies/")
        response.raise_for_status()
        adapter = TypeAdapter(List[VectorDistanceStrategiesModel])
        return adapter.validate_python(response.json())

    def get_vector_distance_strategy(self, strategy_id: int) -> Optional[VectorDistanceStrategiesModel]:
        """Get details for a specific vector distance strategy by ID."""
        try:
            response = requests.get(f"{self.base_url}/vector-distance-strategies/{strategy_id}")
            response.raise_for_status()
            adapter = TypeAdapter(VectorDistanceStrategiesModel)
            return adapter.validate_python(response.json())
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    # Connection Providers Vector Distance Strategies
    def get_connection_providers_vector_distance_strategies(self) -> List[ConnectionProvidersVectorDistanceStrategiesModel]:
        """Get a list of all connection providers vector distance strategies."""
        response = requests.get(f"{self.base_url}/connection-providers-vector-distance-strategies/")
        response.raise_for_status()
        adapter = TypeAdapter(List[ConnectionProvidersVectorDistanceStrategiesModel])
        return adapter.validate_python(response.json())

    def get_connection_providers_vector_distance_strategy(self, id: int) -> Optional[ConnectionProvidersVectorDistanceStrategiesModel]:
        """Get details for a specific connection providers vector distance strategy by ID."""
        try:
            response = requests.get(f"{self.base_url}/connection-providers-vector-distance-strategies/{id}")
            response.raise_for_status()
            adapter = TypeAdapter(ConnectionProvidersVectorDistanceStrategiesModel)
            return adapter.validate_python(response.json())
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    # Retriever Types
    def get_retriever_types(self) -> List[RetrieverTypesModel]:
        """Get a list of all retriever types."""
        response = requests.get(f"{self.base_url}/retriever-types/")
        response.raise_for_status()
        adapter = TypeAdapter(List[RetrieverTypesModel])
        return adapter.validate_python(response.json())

    def get_retriever_type(self, type_id: int) -> Optional[RetrieverTypesModel]:
        """Get details for a specific retriever type by ID."""
        try:
            response = requests.get(f"{self.base_url}/retriever-types/{type_id}")
            response.raise_for_status()
            adapter = TypeAdapter(RetrieverTypesModel)
            return adapter.validate_python(response.json())
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    # Retriever Strategies
    def get_retriever_strategies(self) -> List[RetrieverStrategiesModel]:
        """Get a list of all retriever strategies."""
        response = requests.get(f"{self.base_url}/retriever-strategies/")
        response.raise_for_status()
        adapter = TypeAdapter(List[RetrieverStrategiesModel])
        return adapter.validate_python(response.json())

    def get_retriever_strategy(self, strategy_id: int) -> Optional[RetrieverStrategiesModel]:
        """Get details for a specific retriever strategy by ID."""
        try:
            response = requests.get(f"{self.base_url}/retriever-strategies/{strategy_id}")
            response.raise_for_status()
            adapter = TypeAdapter(RetrieverStrategiesModel)
            return adapter.validate_python(response.json())
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    # Vector Channel Strategies
    def get_vector_channel_strategies(self) -> List[VectorChannelStrategiesModel]:
        """Get a list of all vector channel strategies."""
        response = requests.get(f"{self.base_url}/vector-channel-strategies/")
        response.raise_for_status()
        adapter = TypeAdapter(List[VectorChannelStrategiesModel])
        return adapter.validate_python(response.json())

    def get_vector_channel_strategy(self, strategy_id: int) -> Optional[VectorChannelStrategiesModel]:
        """Get details for a specific vector channel strategy by ID."""
        try:
            response = requests.get(f"{self.base_url}/vector-channel-strategies/{strategy_id}")
            response.raise_for_status()
            adapter = TypeAdapter(VectorChannelStrategiesModel)
            return adapter.validate_python(response.json())
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    # Run Statuses
    def get_run_statuses(self) -> List[RunStatusesModel]:
        """Get a list of all run statuses."""
        response = requests.get(f"{self.base_url}/run-statuses/")
        response.raise_for_status()
        adapter = TypeAdapter(List[RunStatusesModel])
        return adapter.validate_python(response.json())

    def get_run_status(self, status_id: int) -> Optional[RunStatusesModel]:
        """Get details for a specific run status by ID."""
        try:
            response = requests.get(f"{self.base_url}/run-statuses/{status_id}")
            response.raise_for_status()
            adapter = TypeAdapter(RunStatusesModel)
            return adapter.validate_python(response.json())
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    # Avatars
    def get_avatars(self) -> List[AvatarsModel]:
        """Get a list of all avatars."""
        response = requests.get(f"{self.base_url}/avatars/")
        response.raise_for_status()
        adapter = TypeAdapter(List[AvatarsModel])
        return adapter.validate_python(response.json())

    def get_avatar(self, avatar_id: int) -> Optional[AvatarsModel]:
        """Get details for a specific avatar by ID."""
        try:
            response = requests.get(f"{self.base_url}/avatars/{avatar_id}")
            response.raise_for_status()
            adapter = TypeAdapter(AvatarsModel)
            return adapter.validate_python(response.json())
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    # Guardrail Types
    def get_guardrail_types(self) -> List[GuardrailTypesModel]:
        """Get a list of all guardrail types."""
        response = requests.get(f"{self.base_url}/guardrail-types/")
        response.raise_for_status()
        adapter = TypeAdapter(List[GuardrailTypesModel])
        return adapter.validate_python(response.json())

    def get_guardrail_type(self, type_id: int) -> Optional[GuardrailTypesModel]:
        """Get details for a specific guardrail type by ID."""
        try:
            response = requests.get(f"{self.base_url}/guardrail-types/{type_id}")
            response.raise_for_status()
            adapter = TypeAdapter(GuardrailTypesModel)
            return adapter.validate_python(response.json())
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise




class ModelsAPI:
    fixed: FixedModelsAPI
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_available_models(
            self, stage_name: str, provider_name: Optional[str] = None,
            is_verified: Optional[bool] = None, provider_id: Optional[int] = None,
            creator_id: Optional[int] = None, is_primary: Optional[bool] = None,
            name: Optional[str] = None, model_input: Optional[List[str]] = None,
            model_call_name: Optional[str] = None,
            model_output: Optional[List[str]] = None, tags: Optional[List[str]] = None, include_all_tags=True
    ) -> List[AvailableModelModel]:
        params = {'stage_name': stage_name, 'include_all_tags': str(include_all_tags).lower()}
        if provider_name:
            params['provider_name'] = provider_name
        if is_verified is not None:
            params['is_verified'] = str(is_verified).lower()
        if is_primary is not None:
            params['is_primary'] = str(is_primary).lower()
        if provider_id:
            params['provider_id'] = provider_id
        if creator_id:
            params['creator_id'] = creator_id
        if name:
            params['name'] = name
        if model_call_name:
            params['model_call_name'] = model_call_name
        if model_input:
            params['model_input'] = ','.join(model_input)
        if model_output:
            params['model_output'] = ','.join(model_output)
        if tags:
            params['tags'] = ','.join(tags)
        response = requests.get(f"{self.base_url}/available-models/", params=params)
        response.raise_for_status()
        adapter = TypeAdapter(List[AvailableModelModel])
        return adapter.validate_python(response.json())

    def get_available_model(self, available_model_id: int) -> AvailableModelModel:
        response = requests.get(f"{self.base_url}/available-models/{available_model_id}")
        response.raise_for_status()
        adapter = TypeAdapter(AvailableModelModel)
        return adapter.validate_python(response.json())

    def get_providers(
            self, stage_name: str, model_input: Optional[List[str]] = None,
            model_output: Optional[List[str]] = None, tags: Optional[List[str]] = None, include_all_tags=True
    ) -> List[ProviderModel]:
        params = {'stage_name': stage_name, 'include_all_tags': str(include_all_tags).lower()}
        if model_input:
            params['model_input'] = ','.join(model_input)
        if model_output:
            params['model_output'] = ','.join(model_output)
        if tags:
            params['tags'] = ','.join(tags)
        response = requests.get(f"{self.base_url}/providers/", params=params)
        response.raise_for_status()
        adapter = TypeAdapter(List[ProviderModel])
        return adapter.validate_python(response.json())

    def get_model_creators(
            self, stage_name: str, model_input: Optional[List[str]] = None,
            model_output: Optional[List[str]] = None, tags: Optional[List[str]] = None, include_all_tags=True
    ) -> List[ModelCreatorModel]:
        params = {'stage_name': stage_name, 'include_all_tags': str(include_all_tags).lower()}
        if model_input:
            params['model_input'] = ','.join(model_input)
        if model_output:
            params['model_output'] = ','.join(model_output)
        if tags:
            params['tags'] = ','.join(tags)
        response = requests.get(f"{self.base_url}/model-creators/", params=params)
        response.raise_for_status()
        adapter = TypeAdapter(List[ModelCreatorModel])
        return adapter.validate_python(response.json())

    def get_model_creator(self, creator_id: int) -> ModelCreatorModel:
        response = requests.get(f"{self.base_url}/model-creators/{creator_id}")
        response.raise_for_status()
        adapter = TypeAdapter(ModelCreatorModel)
        return adapter.validate_python(response.json())


kosmoy_data = ModelsAPI('https://backoffice.kosmoy.io')
kosmoy_data.fixed = FixedModelsAPI('https://backoffice.kosmoy.io')
