"""
LLM service functions.
Auto-generated - DO NOT EDIT.

Provides type-safe action definitions for LLM service with bot-compatible parameters.
Actual execution happens in the Go backend after syncing.

NOTE: This module is hardcoded to provide bot-compatible parameter names
that match the exported bot code format.
"""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

from erdo.template import TemplateString
from erdo.types import StepMetadata

from ..types import Tool


class MessageParams(BaseModel):
    """LLM message parameters (bot-compatible)"""

    name: str = "llm.message"  # Action type for roundtrip compatibility

    # Bot definition parameters (high-level)
    system_prompt: Optional[Union[str, TemplateString]] = (
        None  # System prompt for the conversation
    )
    message_history: Optional[Union[List[Dict[str, Any]], TemplateString]] = (
        None  # Previous messages in the conversation
    )
    query: Optional[Union[str, TemplateString]] = None  # User query/message
    context: Optional[Union[str, TemplateString]] = None  # Additional context

    # LLM configuration parameters
    model: Optional[Union[str, TemplateString]] = None  # LLM model to use
    tools: Optional[List[Tool]] = None  # Available tools for the LLM
    response_format: Optional[Union[Dict[str, Any], TemplateString]] = (
        None  # Response format specification
    )
    max_tokens: Optional[Union[int, TemplateString]] = (
        None  # Maximum tokens in response
    )
    metadata: Optional[Union[Dict[str, Any], TemplateString]] = (
        None  # Additional metadata
    )
    disable_tools: Optional[Union[bool, TemplateString]] = (
        None  # Whether to disable tools for this message
    )


def message(
    system_prompt: Optional[Union[str, TemplateString]] = None,
    message_history: Optional[Union[List[Dict[str, Any]], TemplateString]] = None,
    query: Optional[Union[str, TemplateString]] = None,
    context: Optional[Union[str, TemplateString]] = None,
    model: Optional[Union[str, TemplateString]] = None,
    tools: Optional[List[Tool]] = None,
    response_format: Optional[Union[Dict[str, Any], TemplateString]] = None,
    max_tokens: Optional[Union[int, TemplateString]] = None,
    metadata: Optional[Union[Dict[str, Any], TemplateString]] = None,
    disable_tools: Optional[Union[bool, TemplateString]] = None,
    step_metadata: Optional[StepMetadata] = None,
) -> MessageParams:
    """Generate LLM message with bot-compatible parameters

    This function accepts the same parameters that bot definitions use,
    making it compatible with exported bot code.

    Args:
        system_prompt: System prompt for the conversation
        message_history: Previous messages in the conversation
        query: User query/message
        context: Additional context
        model: LLM model to use
        tools: Available tools for the LLM
        response_format: Response format specification
        max_tokens: Maximum tokens in response
        metadata: Additional metadata
        disable_tools: Whether to disable tools for this message

    Returns:
        MessageParams: Type-safe parameter object
    """
    params = {
        "system_prompt": system_prompt,
        "message_history": message_history,
        "query": query,
        "context": context,
        "model": model,
        "tools": tools,
        "response_format": response_format,
        "max_tokens": max_tokens,
        "metadata": metadata,
        "disable_tools": disable_tools,
    }

    # Remove None values for optional parameters
    params = {k: v for k, v in params.items() if v is not None}

    # Use normal constructor for proper validation
    return MessageParams(**params)
