"""
Bot service functions.
Auto-generated - DO NOT EDIT.

Provides type-safe action definitions for Bot service with correct parameter names.
Actual execution happens in the Go backend after syncing.

NOTE: This module is hardcoded because bot.invoke requires bot_name parameter
but the Go struct uses bot_id. The backend converts bot_name -> bot_id internally.
"""

from typing import Any, Dict, Optional, Union

from pydantic import BaseModel

from erdo.template import TemplateString
from erdo.types import StepMetadata


class InvokeParams(BaseModel):
    """Invoke a bot with specified parameters and return the result parameters"""

    name: str = "bot.invoke"  # Action type for roundtrip compatibility
    bot_name: Optional[Union[str, TemplateString]] = (
        None  # bot_name parameter (backend expects this, not bot_id)
    )
    parameters: Optional[Union[Dict[str, Any], TemplateString]] = (
        None  # parameters parameter
    )
    bot_output_visibility_behaviour: Optional[Union[str, TemplateString]] = (
        None  # Output visibility behaviour
    )
    transparent: Optional[Union[bool, TemplateString]] = (
        None  # Whether the invocation is transparent
    )
    disable_tools: Optional[Union[bool, TemplateString]] = (
        None  # Whether to disable tools for this invocation
    )


class AskParams(BaseModel):
    """Ask a bot a question and get a response parameters"""

    name: str = "bot.ask"  # Action type for roundtrip compatibility
    query: Optional[Union[str, TemplateString]] = None  # query parameter
    bot_name: Optional[Union[str, TemplateString]] = None  # bot_name parameter
    bot_id: Optional[Union[str, TemplateString]] = None  # bot_id parameter
    invocation_id: Optional[Union[str, TemplateString]] = (
        None  # invocation_id parameter
    )


def invoke(
    bot_name: Optional[Union[str, TemplateString]] = None,
    parameters: Optional[Union[Dict[str, Any], TemplateString]] = None,
    bot_output_visibility_behaviour: Optional[Union[str, TemplateString]] = None,
    transparent: Optional[Union[bool, TemplateString]] = None,
    disable_tools: Optional[Union[bool, TemplateString]] = None,
    step_metadata: Optional[StepMetadata] = None,
    **params: Any,
) -> InvokeParams:
    """Invoke a bot with specified parameters and return the result

    The bot.invoke action expects bot_name (not bot_id) as the parameter.
    The backend will look up the bot by name and convert to bot_id internally.

    Args:
        bot_name: Name of the bot to invoke
        parameters: Parameters to pass to the bot
        bot_output_visibility_behaviour: Output visibility behaviour
        transparent: Whether the invocation is transparent
        disable_tools: Whether to disable tools for this invocation

    Returns:
        InvokeParams: Type-safe parameter object
    """
    params_dict = {
        "bot_name": bot_name,
        "parameters": parameters,
        "bot_output_visibility_behaviour": bot_output_visibility_behaviour,
        "transparent": transparent,
        "disable_tools": disable_tools,
    }

    # Remove None values for optional parameters
    params_dict = {k: v for k, v in params_dict.items() if v is not None}
    params_dict.update(params)

    # Use normal constructor for proper validation
    return InvokeParams(**params_dict)


def ask(
    query: Optional[Union[str, TemplateString]] = None,
    bot_name: Optional[Union[str, TemplateString]] = None,
    bot_id: Optional[Union[str, TemplateString]] = None,
    invocation_id: Optional[Union[str, TemplateString]] = None,
    step_metadata: Optional[StepMetadata] = None,
    **params: Any,
) -> AskParams:
    """Ask a bot a question and get a response

    Args:
        query: Question to ask the bot
        bot_name: Name of the bot to ask
        bot_id: ID of the bot to ask (alternative to bot_name)
        invocation_id: Invocation ID for tracking

    Returns:
        AskParams: Type-safe parameter object
    """
    params_dict = {
        "query": query,
        "bot_name": bot_name,
        "bot_id": bot_id,
        "invocation_id": invocation_id,
    }

    # Remove None values for optional parameters
    params_dict = {k: v for k, v in params_dict.items() if v is not None}
    params_dict.update(params)

    # Use normal constructor for proper validation
    return AskParams(**params_dict)
