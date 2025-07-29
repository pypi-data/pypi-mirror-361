"""
Pydantic models for pipeline configuration API responses.

This module defines comprehensive data structures for pipeline configuration exports,
including all components like agents, models, tools, data sources, and deployment settings.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Metadata(BaseModel):
    """Pipeline metadata and export configuration.

    Contains version information, export settings, and descriptive metadata
    about the pipeline configuration.

    Attributes:
        id: Unique identifier for the pipeline metadata
        export_version: Version of the export format
        tagline: Optional tagline describing the pipeline
        agent_description: Optional description of the agent
        industry: Optional industry classification
        tasks: Optional description of tasks the pipeline performs
        credential_export_option: Export option for credentials
        data_source_export_option: Export option for data sources
        version_information: Information about the pipeline version
        state: Current state of the pipeline
    """

    id: str
    export_version: str = Field(alias="exportVersion")
    tagline: Optional[str] = None
    agent_description: Optional[str] = Field(alias="agentDescription", default=None)
    industry: Optional[str] = None
    tasks: Optional[str] = None
    credential_export_option: str = Field(alias="credentialExportOption")
    data_source_export_option: str = Field(alias="dataSourceExportOption")
    version_information: str = Field(alias="versionInformation")
    state: str


class Agent(BaseModel):
    """AI agent configuration and workflow definition.

    Represents the core agent that executes the pipeline, including its
    identity, industry specialization, and step-by-step workflow configuration.

    Attributes:
        name: Display name of the agent
        execution_name: Name used during execution
        agent_description: Optional description of the agent's capabilities
        video_link: Optional link to demonstration video
        industry: Optional industry the agent specializes in
        sub_industries: List of sub-industry specializations
        agent_details: Dictionary containing additional agent configuration
        id: Unique identifier for the agent
        agent_icon: Optional icon identifier or URL
        steps: List of workflow steps the agent executes
    """

    name: str
    execution_name: str = Field(alias="executionName")
    agent_description: Optional[str] = Field(alias="agentDescription", default=None)
    video_link: Optional[str] = Field(alias="videoLink", default=None)
    industry: Optional[str] = None
    sub_industries: List[str] = Field(alias="subIndustries", default_factory=list)
    agent_details: Dict[str, Any] = Field(alias="agentDetails", default_factory=dict)
    id: str
    agent_icon: Optional[str] = Field(alias="agentIcon", default=None)
    steps: List[Dict[str, Any]]


class PromptMessage(BaseModel):
    """Individual message within a prompt template.

    Attributes:
        text: The message content
        order: Order of the message in the prompt sequence
    """

    text: str
    order: int


class Prompt(BaseModel):
    """Prompt template configuration.

    Attributes:
        name: Name of the prompt template
        version_change_description: Description of changes in this version
        prompt_message_list: List of messages in the prompt
        id: Unique identifier for the prompt
    """

    name: str
    version_change_description: str = Field(alias="versionChangeDescription")
    prompt_message_list: List[PromptMessage] = Field(alias="promptMessageList")
    id: str


class CredentialData(BaseModel):
    """Individual credential key-value pair.

    Attributes:
        key: The credential key name
        value: The credential value
    """

    key: str
    value: str


class CredentialsDefinition(BaseModel):
    """Credentials configuration and authentication settings.

    Attributes:
        name: Name of the credentials definition
        credential_type: Type of credentials (API key, OAuth, etc.)
        source_type: Source where credentials are stored
        credential_data_list: List of credential key-value pairs
        id: Unique identifier for the credentials definition
    """

    name: str
    credential_type: str = Field(alias="credentialType")
    source_type: str = Field(alias="sourceType")
    credential_data_list: List[CredentialData] = Field(alias="credentialDataList")
    id: str


class HeaderDefinition(BaseModel):
    """HTTP header definition for API requests.

    Attributes:
        key: Header name
        value: Header value
    """

    key: str
    value: str


class ParameterDefinition(BaseModel):
    """Parameter definition for tool configuration.

    Attributes:
        name: Name of the parameter
        parameter_type: Type of the parameter (string, integer, etc.)
        parameter_description: Description of the parameter's purpose
        default: Default value for the parameter
        valid_options: List of valid options for the parameter
        id: Unique identifier for the parameter definition
    """

    name: str
    parameter_type: str = Field(alias="parameterType")
    parameter_description: str = Field(alias="parameterDescription")
    default: str
    valid_options: List[str] = Field(alias="validOptions", default_factory=list)
    id: str


class Tool(BaseModel):
    """Tool configuration for external API integrations.

    Attributes:
        tool_type: Type of tool (API, function, etc.)
        name: Display name of the tool
        standardized_name: Standardized name for the tool
        tool_description: Description of the tool's functionality
        purpose: Purpose or use case for the tool
        api_endpoint: API endpoint URL
        credentials_definition: Optional credentials required for the tool
        headers_definition: List of HTTP headers for API requests
        body: Request body template
        parameters_definition: List of parameter definitions
        method_type: HTTP method type (GET, POST, etc.)
        route_through_acc: Whether to route through ACC
        use_user_credentials: Whether to use user credentials
        use_user_credentials_type: Type of user credentials to use
        id: Unique identifier for the tool
    """

    tool_type: str = Field(alias="toolType")
    name: str
    standardized_name: str = Field(alias="standardizedName")
    tool_description: str = Field(alias="toolDescription")
    purpose: str
    api_endpoint: str = Field(alias="apiEndpoint")
    credentials_definition: Optional[CredentialsDefinition] = Field(
        alias="credentialsDefinition"
    )
    headers_definition: List[HeaderDefinition] = Field(alias="headersDefinition")
    body: str
    parameters_definition: List[ParameterDefinition] = Field(
        alias="parametersDefinition"
    )
    method_type: str = Field(alias="methodType")
    route_through_acc: bool = Field(alias="routeThroughACC")
    use_user_credentials: bool = Field(alias="useUserCredentials")
    use_user_credentials_type: str = Field(alias="useUserCredentialsType")
    id: str


class Model(BaseModel):
    """Language model configuration and deployment settings.

    Defines an AI model used in the pipeline, including its deployment details,
    pricing configuration, authentication settings, and capabilities.

    Attributes:
        id: Unique identifier for the model
        display_name: Display name of the model
        model_name: Technical name of the model
        prompt_id: Optional ID of associated prompt template
        system_prompt_definition: Optional system prompt configuration
        url: Model endpoint URL
        input_type: Type of input the model accepts
        provider: Model provider (OpenAI, Anthropic, etc.)
        credentials_definition: Optional credentials for model access
        deployment_type: Type of deployment (cloud, on-premise, etc.)
        source_type: Source type of the model
        connection_string: Optional connection string for deployment
        container_name: Optional container name for deployment
        deployed_key: Optional key for deployed model
        deployed_url: Optional URL for deployed model
        state: Optional current state of the model
        uploaded_container_id: Optional ID of uploaded container
        library_model_id: Optional ID from model library
        input_token_price: Price per input token
        output_token_price: Price per output token
        token_units: Number of token units
        has_tool_support: Whether the model supports tool calling
        allow_airia_credentials: Whether Airia credentials are allowed
        allow_byok_credentials: Whether bring-your-own-key credentials are allowed
        author: Optional author of the model
        price_type: Type of pricing model
    """

    id: str
    display_name: str = Field(alias="displayName")
    model_name: str = Field(alias="modelName")
    prompt_id: Optional[str] = Field(alias="promptId", default=None)
    system_prompt_definition: Optional[Any] = Field(
        alias="systemPromptDefinition", default=None
    )
    url: str
    input_type: str = Field(alias="inputType")
    provider: str
    credentials_definition: Optional[CredentialsDefinition] = Field(
        alias="credentialsDefinition"
    )
    deployment_type: str = Field(alias="deploymentType")
    source_type: str = Field(alias="sourceType")
    connection_string: Optional[str] = Field(alias="connectionString", default=None)
    container_name: Optional[str] = Field(alias="containerName", default=None)
    deployed_key: Optional[str] = Field(alias="deployedKey", default=None)
    deployed_url: Optional[str] = Field(alias="deployedUrl", default=None)
    state: Optional[str] = None
    uploaded_container_id: Optional[str] = Field(
        alias="uploadedContainerId", default=None
    )
    library_model_id: Optional[str] = Field(alias="libraryModelId")
    input_token_price: str = Field(alias="inputTokenPrice")
    output_token_price: str = Field(alias="outputTokenPrice")
    token_units: int = Field(alias="tokenUnits")
    has_tool_support: bool = Field(alias="hasToolSupport")
    allow_airia_credentials: bool = Field(alias="allowAiriaCredentials")
    allow_byok_credentials: bool = Field(alias="allowBYOKCredentials")
    author: Optional[str]
    price_type: str = Field(alias="priceType")


class PythonCodeBlock(BaseModel):
    """Python code block for custom functionality.

    Attributes:
        id: Unique identifier for the code block
        code: Python code content
    """

    id: str
    code: str


class Router(BaseModel):
    """Router configuration for model selection and routing.

    Attributes:
        id: Unique identifier for the router
        model_id: ID of the associated model
        model: Optional model object
        router_config: Dictionary containing router configuration
    """

    id: str
    model_id: str = Field(alias="modelId")
    model: Optional[Any] = None
    router_config: Dict[str, Dict[str, Any]] = Field(alias="routerConfig")


class ChunkingConfig(BaseModel):
    """Configuration for text chunking in data processing.

    Attributes:
        id: Unique identifier for the chunking configuration
        chunk_size: Size of each text chunk
        chunk_overlap: Number of characters to overlap between chunks
        strategy_type: Type of chunking strategy to use
    """

    id: str
    chunk_size: int = Field(alias="chunkSize")
    chunk_overlap: int = Field(alias="chunkOverlap")
    strategy_type: str = Field(alias="strategyType")


class DataSourceFile(BaseModel):
    """File reference within a data source.

    Attributes:
        data_source_id: ID of the data source containing this file
        file_path: Optional path to the file
        input_token: Optional input token for file access
        file_count: Optional count of files
    """

    data_source_id: str = Field(alias="dataSourceId")
    file_path: Optional[str] = Field(None, alias="filePath")
    input_token: Optional[str] = Field(None, alias="inputToken")
    file_count: Optional[int] = Field(None, alias="fileCount")


class DataSource(BaseModel):
    """Data source configuration for pipeline data input.

    Attributes:
        id: Unique identifier for the data source
        name: Optional name of the data source
        execution_name: Optional name used during execution
        chunking_config: Configuration for text chunking
        data_source_type: Type of data source (file, database, etc.)
        database_type: Type of database if applicable
        embedding_provider: Provider for text embeddings
        is_user_specific: Whether the data source is user-specific
        files: Optional list of files in the data source
        configuration_json: Optional JSON configuration string
        credentials: Optional credentials for data source access
        is_image_processing_enabled: Whether image processing is enabled
    """

    id: str = Field(alias="id")
    name: Optional[str] = None
    execution_name: Optional[str] = Field(None, alias="executionName")
    chunking_config: ChunkingConfig = Field(alias="chunkingConfig")
    data_source_type: str = Field(alias="dataSourceType")
    database_type: str = Field(alias="databaseType")
    embedding_provider: str = Field(alias="embeddingProvider")
    is_user_specific: bool = Field(alias="isUserSpecific")
    files: Optional[List[DataSourceFile]] = None
    configuration_json: Optional[str] = Field(None, alias="configurationJson")
    credentials: Optional[CredentialsDefinition]
    is_image_processing_enabled: bool = Field(alias="isImageProcessingEnabled")


class GetPipelineConfigResponse(BaseModel):
    """Complete pipeline configuration export response.

    This is the root response model containing all components of a pipeline
    configuration, including the agent definition, associated resources,
    and deployment settings.

    Attributes:
        metadata: Pipeline metadata and export configuration
        agent: AI agent configuration and workflow definition
        data_sources: Optional list of data sources for the pipeline
        prompts: Optional list of prompt templates
        tools: Optional list of external tools and integrations
        models: Optional list of AI models used in the pipeline
        memories: Optional memory/context storage configurations
        python_code_blocks: Optional list of custom Python code blocks
        routers: Optional list of model routing configurations
        deployment: Optional deployment configuration
    """

    metadata: Metadata
    agent: Agent
    data_sources: Optional[List[DataSource]] = Field(
        alias="dataSources", default_factory=list
    )
    prompts: Optional[List[Prompt]] = Field(default_factory=list)
    tools: Optional[List[Tool]] = Field(default_factory=list)
    models: Optional[List[Model]] = Field(default_factory=list)
    memories: Optional[Any] = None
    python_code_blocks: Optional[List[PythonCodeBlock]] = Field(
        alias="pythonCodeBlocks", default_factory=list
    )
    routers: Optional[List[Router]] = Field(default_factory=list)
    deployment: Optional[Any] = None
