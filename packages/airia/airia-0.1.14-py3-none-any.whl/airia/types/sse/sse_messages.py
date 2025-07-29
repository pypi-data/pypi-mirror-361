"""
Server-Sent Event (SSE) message types and models for the Airia API.

This module defines all possible SSE message types that can be received during
pipeline execution, including agent lifecycle events, processing steps, model
streaming, and tool execution messages.
"""

from datetime import datetime, time
from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, ConfigDict


class MessageType(str, Enum):
    """
    Enumeration of all possible SSE message types from the Airia API.

    These message types correspond to different events that occur during
    pipeline execution, agent processing, and streaming responses.
    """

    AGENT_PING = "AgentPingMessage"
    AGENT_START = "AgentStartMessage"
    AGENT_INPUT = "AgentInputMessage"
    AGENT_END = "AgentEndMessage"
    AGENT_STEP_START = "AgentStepStartMessage"
    AGENT_STEP_HALT = "AgentStepHaltMessage"
    AGENT_STEP_END = "AgentStepEndMessage"
    AGENT_OUTPUT = "AgentOutputMessage"
    AGENT_AGENT_CARD = "AgentAgentCardMessage"
    AGENT_DATASEARCH = "AgentDatasearchMessage"
    AGENT_INVOCATION = "AgentInvocationMessage"
    AGENT_MODEL = "AgentModelMessage"
    AGENT_PYTHON_CODE = "AgentPythonCodeMessage"
    AGENT_TOOL_ACTION = "AgentToolActionMessage"
    AGENT_MODEL_STREAM_START = "AgentModelStreamStartMessage"
    AGENT_MODEL_STREAM_END = "AgentModelStreamEndMessage"
    AGENT_MODEL_STREAM_ERROR = "AgentModelStreamErrorMessage"
    AGENT_MODEL_STREAM_USAGE = "AgentModelStreamUsageMessage"
    AGENT_MODEL_STREAM_FRAGMENT = "AgentModelStreamFragmentMessage"
    MODEL_STREAM_FRAGMENT = "ModelStreamFragment"
    AGENT_AGENT_CARD_STREAM_START = "AgentAgentCardStreamStartMessage"
    AGENT_AGENT_CARD_STREAM_ERROR = "AgentAgentCardStreamErrorMessage"
    AGENT_AGENT_CARD_STREAM_FRAGMENT = "AgentAgentCardStreamFragmentMessage"
    AGENT_AGENT_CARD_STREAM_END = "AgentAgentCardStreamEndMessage"
    AGENT_TOOL_REQUEST = "AgentToolRequestMessage"
    AGENT_TOOL_RESPONSE = "AgentToolResponseMessage"


class BaseSSEMessage(BaseModel):
    """
    Base class for all Server-Sent Event (SSE) messages from the Airia API.

    All SSE messages include a message_type field that identifies the specific
    type of event being reported.
    """

    model_config = ConfigDict(use_enum_values=True)
    message_type: MessageType


class AgentPingMessage(BaseSSEMessage):
    """
    Ping message sent periodically to maintain connection health.

    These messages help verify that the connection is still active during
    long-running pipeline executions.
    """

    message_type: MessageType = MessageType.AGENT_PING
    timestamp: datetime


### Agent Messages ###


class BaseAgentMessage(BaseSSEMessage):
    """
    Base class for messages related to agent execution.

    All agent messages include identifiers for the specific agent
    and execution session.
    """

    agent_id: str
    execution_id: str


class AgentStartMessage(BaseAgentMessage):
    """
    Message indicating that an agent has started processing.
    """

    message_type: MessageType = MessageType.AGENT_START


class AgentInputMessage(BaseAgentMessage):
    """
    Message indicating that an agent has received input to process.
    """

    message_type: MessageType = MessageType.AGENT_INPUT


class AgentEndMessage(BaseAgentMessage):
    """
    Message indicating that an agent has finished processing.
    """

    message_type: MessageType = MessageType.AGENT_END


### Step Messages ###


class BaseStepMessage(BaseAgentMessage):
    """
    Base class for messages related to individual processing steps within an agent.

    Steps represent discrete operations or tasks that an agent performs
    as part of its overall processing workflow.
    """

    step_id: str
    step_type: str
    step_title: Optional[str] = None


class AgentStepStartMessage(BaseStepMessage):
    """
    Message indicating that a processing step has started.
    """

    message_type: MessageType = MessageType.AGENT_STEP_START
    start_time: datetime


class AgentStepHaltMessage(BaseStepMessage):
    """
    Message indicating that a step has been halted pending approval.

    This occurs when human approval is required before proceeding
    with potentially sensitive or high-impact operations.
    """

    message_type: MessageType = MessageType.AGENT_STEP_HALT
    approval_id: str


class AgentStepEndMessage(BaseStepMessage):
    """
    Message indicating that a processing step has completed.

    Includes timing information and the final status of the step.
    """

    message_type: MessageType = MessageType.AGENT_STEP_END
    end_time: datetime
    duration: time
    status: str


class AgentOutputMessage(BaseStepMessage):
    """
    Message containing the output result from a completed step.
    """

    message_type: MessageType = MessageType.AGENT_OUTPUT
    step_result: str


### Status Messages ###


class BaseStatusMessage(BaseStepMessage):
    """
    Base class for status update messages within processing steps.

    Status messages provide real-time updates about what operations
    are being performed during step execution.
    """

    pass


class AgentAgentCardMessage(BaseStatusMessage):
    """
    Message indicating that an agent card step is being processed.

    Agent cards represent interactive UI components or displays
    that provide rich information to users during pipeline execution.
    """

    message_type: MessageType = MessageType.AGENT_AGENT_CARD
    step_name: str


class AgentDatasearchMessage(BaseStatusMessage):
    """
    Message indicating that data source search is being performed.

    This message is sent when an agent is querying or searching
    through configured data sources to retrieve relevant information.
    """

    message_type: MessageType = MessageType.AGENT_DATASEARCH
    datastore_id: str
    datastore_type: str
    datastore_name: str


class AgentInvocationMessage(BaseStatusMessage):
    """
    Message indicating that another agent is being invoked.

    This occurs when the current agent calls or delegates work
    to another specialized agent in the pipeline.
    """

    message_type: MessageType = MessageType.AGENT_INVOCATION
    agent_name: str


class AgentModelMessage(BaseStatusMessage):
    """
    Message indicating that a language model is being called.

    This message is sent when an agent begins interacting with
    a language model for text generation or processing.
    """

    message_type: MessageType = MessageType.AGENT_MODEL
    model_name: str


class AgentPythonCodeMessage(BaseStatusMessage):
    """
    Message indicating that Python code execution is taking place.

    This message is sent when an agent executes custom Python code
    blocks as part of its processing workflow.
    """

    message_type: MessageType = MessageType.AGENT_PYTHON_CODE
    step_name: str


class AgentToolActionMessage(BaseStatusMessage):
    """
    Message indicating that a tool or external service is being called.

    This message is sent when an agent invokes an external tool,
    API, or service to perform a specific action or retrieve data.
    """

    message_type: MessageType = MessageType.AGENT_TOOL_ACTION
    step_name: str
    tool_name: str


### Model Stream Messages ###


class BaseModelStreamMessage(BaseAgentMessage):
    """
    Base class for language model streaming messages.

    Model streaming allows real-time display of text generation
    as it occurs, providing better user experience for long responses.
    """

    step_id: str
    stream_id: str


class AgentModelStreamStartMessage(BaseModelStreamMessage):
    """
    Message indicating that model text streaming has begun.
    """

    message_type: MessageType = MessageType.AGENT_MODEL_STREAM_START
    model_name: str


class AgentModelStreamErrorMessage(BaseModelStreamMessage):
    """
    Message indicating that an error occurred during model streaming.
    """

    message_type: MessageType = MessageType.AGENT_MODEL_STREAM_ERROR
    error_message: str


class AgentModelStreamFragmentMessage(BaseModelStreamMessage):
    """
    Fragment of streaming text content from a language model.

    These messages contain individual chunks of text as they are generated
    by the model, allowing for real-time display of results.
    """

    message_type: MessageType = MessageType.AGENT_MODEL_STREAM_FRAGMENT
    index: int
    content: Optional[str] = None


class AgentModelStreamEndMessage(BaseModelStreamMessage):
    """
    Message indicating that model text streaming has completed.
    """

    message_type: MessageType = MessageType.AGENT_MODEL_STREAM_END
    content_id: str
    duration: Optional[float] = None


class AgentModelStreamUsageMessage(BaseModelStreamMessage):
    """
    Message containing token usage and cost information for model calls.
    """

    message_type: MessageType = MessageType.AGENT_MODEL_STREAM_USAGE
    token: Optional[int] = None
    tokens_cost: Optional[float] = None


### Agent Card Messages ###


class BaseAgentAgentCardStreamMessage(BaseAgentMessage):
    """
    Base class for agent card streaming messages.

    Agent card streaming allows real-time updates to interactive
    UI components during their generation or processing.
    """

    step_id: str
    stream_id: str


class AgentAgentCardStreamStartMessage(BaseAgentAgentCardStreamMessage):
    """
    Message indicating that agent card streaming has begun.
    """

    message_type: MessageType = MessageType.AGENT_AGENT_CARD_STREAM_START
    content: Optional[str] = None


class AgentAgentCardStreamErrorMessage(BaseAgentAgentCardStreamMessage):
    """
    Message indicating that an error occurred during agent card streaming.
    """

    message_type: MessageType = MessageType.AGENT_AGENT_CARD_STREAM_ERROR
    error_message: str


class AgentAgentCardStreamFragmentMessage(BaseAgentAgentCardStreamMessage):
    """
    Fragment of streaming agent card content.

    These messages contain individual chunks of agent card data
    as they are generated, allowing for real-time UI updates.
    """

    message_type: MessageType = MessageType.AGENT_AGENT_CARD_STREAM_FRAGMENT
    index: int
    content: Optional[str]


class AgentAgentCardStreamEndMessage(BaseAgentAgentCardStreamMessage):
    """
    Message indicating that agent card streaming has completed.
    """

    message_type: MessageType = MessageType.AGENT_AGENT_CARD_STREAM_END
    content: Optional[str] = None


### Tool Messages ###


class BaseAgentToolMessage(BaseStepMessage):
    """
    Base class for tool execution messages.

    Tool messages track the lifecycle of external tool or service
    calls made by agents during pipeline execution.
    """

    id: str
    name: str


class AgentToolRequestMessage(BaseAgentToolMessage):
    """
    Message indicating that a tool request has been initiated.

    This message is sent when an agent begins calling an external
    tool or service to perform a specific operation.
    """

    message_type: MessageType = MessageType.AGENT_TOOL_REQUEST


class AgentToolResponseMessage(BaseAgentToolMessage):
    """
    Message indicating that a tool request has completed.

    This message contains the results and timing information
    from a completed tool or service call.
    """

    message_type: MessageType = MessageType.AGENT_TOOL_RESPONSE
    duration: time
    success: bool


# Union type for all possible messages
SSEMessage = Union[
    AgentPingMessage,
    AgentStartMessage,
    AgentInputMessage,
    AgentEndMessage,
    AgentStepStartMessage,
    AgentStepHaltMessage,
    AgentStepEndMessage,
    AgentOutputMessage,
    AgentAgentCardMessage,
    AgentDatasearchMessage,
    AgentInvocationMessage,
    AgentModelMessage,
    AgentPythonCodeMessage,
    AgentToolActionMessage,
    AgentModelStreamStartMessage,
    AgentModelStreamEndMessage,
    AgentModelStreamErrorMessage,
    AgentModelStreamUsageMessage,
    AgentModelStreamFragmentMessage,
    AgentAgentCardStreamStartMessage,
    AgentAgentCardStreamErrorMessage,
    AgentAgentCardStreamFragmentMessage,
    AgentAgentCardStreamEndMessage,
    AgentToolRequestMessage,
    AgentToolResponseMessage,
]
"""Union type representing all possible SSE message types from the Airia API."""

SSEDict = {
    MessageType.AGENT_PING.value: AgentPingMessage,
    MessageType.AGENT_START.value: AgentStartMessage,
    MessageType.AGENT_INPUT.value: AgentInputMessage,
    MessageType.AGENT_END.value: AgentEndMessage,
    MessageType.AGENT_STEP_START.value: AgentStepStartMessage,
    MessageType.AGENT_STEP_HALT.value: AgentStepHaltMessage,
    MessageType.AGENT_STEP_END.value: AgentStepEndMessage,
    MessageType.AGENT_OUTPUT.value: AgentOutputMessage,
    MessageType.AGENT_AGENT_CARD.value: AgentAgentCardMessage,
    MessageType.AGENT_DATASEARCH.value: AgentDatasearchMessage,
    MessageType.AGENT_INVOCATION.value: AgentInvocationMessage,
    MessageType.AGENT_MODEL.value: AgentModelMessage,
    MessageType.AGENT_PYTHON_CODE.value: AgentPythonCodeMessage,
    MessageType.AGENT_TOOL_ACTION.value: AgentToolActionMessage,
    MessageType.AGENT_MODEL_STREAM_START.value: AgentModelStreamStartMessage,
    MessageType.AGENT_MODEL_STREAM_END.value: AgentModelStreamEndMessage,
    MessageType.AGENT_MODEL_STREAM_ERROR.value: AgentModelStreamErrorMessage,
    MessageType.AGENT_MODEL_STREAM_USAGE.value: AgentModelStreamUsageMessage,
    MessageType.AGENT_MODEL_STREAM_FRAGMENT.value: AgentModelStreamFragmentMessage,
    MessageType.AGENT_AGENT_CARD_STREAM_START.value: AgentAgentCardStreamStartMessage,
    MessageType.AGENT_AGENT_CARD_STREAM_ERROR.value: AgentAgentCardStreamErrorMessage,
    MessageType.AGENT_AGENT_CARD_STREAM_FRAGMENT.value: AgentAgentCardStreamFragmentMessage,
    MessageType.AGENT_AGENT_CARD_STREAM_END.value: AgentAgentCardStreamEndMessage,
    MessageType.AGENT_TOOL_REQUEST.value: AgentToolRequestMessage,
    MessageType.AGENT_TOOL_RESPONSE.value: AgentToolResponseMessage,
}
"""
Mapping from message type strings to their corresponding Pydantic model classes.

This dictionary is used by the SSE parser to instantiate the correct message
type based on the 'event' field in incoming SSE data.
"""
