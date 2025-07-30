"""
Resource definition actions for managing and searching data resources service functions.
Auto-generated - DO NOT EDIT.

Provides type-safe action definitions for resource_definitions service.
Actual execution happens in the Go backend after syncing.
"""

from typing import Any, List, Optional, Union

from pydantic import BaseModel

from erdo._generated.types import Resource
from erdo.template import TemplateString
from erdo.types import StepMetadata


class SearchParams(BaseModel):
    """Search for resource definitions using query and key filters parameters"""

    name: str = "resource_definitions.search"  # Action type for roundtrip compatibility
    query: Optional[Union[str, TemplateString]] = None  # query parameter
    or_keys: Optional[Any] = None  # or_keys parameter
    and_keys: Optional[Any] = None  # and_keys parameter
    dataset_id: Optional[Union[str, TemplateString]] = None  # dataset_id parameter
    integration_config_id: Optional[Union[str, TemplateString]] = (
        None  # integration_config_id parameter
    )
    limit: Optional[Union[int, TemplateString]] = None  # limit parameter


class ListParams(BaseModel):
    """List resource definitions with optional filtering by dataset, integration, or attach type parameters"""

    name: str = "resource_definitions.list"  # Action type for roundtrip compatibility
    dataset_id: Optional[Union[str, TemplateString]] = None  # dataset_id parameter
    integration_config_id: Optional[Union[str, TemplateString]] = (
        None  # integration_config_id parameter
    )
    attach_type: Optional[Union[str, TemplateString]] = None  # attach_type parameter
    limit: Optional[Union[int, TemplateString]] = None  # limit parameter


class ListByKeysParams(BaseModel):
    """List resource definitions filtered by specific keys with optional additional filters parameters"""

    name: str = (
        "resource_definitions.list_by_keys"  # Action type for roundtrip compatibility
    )
    keys: Optional[Any] = None  # keys parameter
    dataset_id: Optional[Union[str, TemplateString]] = None  # dataset_id parameter
    integration_config_id: Optional[Union[str, TemplateString]] = (
        None  # integration_config_id parameter
    )
    attach_type: Optional[Union[str, TemplateString]] = None  # attach_type parameter
    limit: Optional[Union[int, TemplateString]] = None  # limit parameter


class SearchResult(BaseModel):
    """Search for resource definitions using query and key filters result type

    Result schema for resource_definitions.search action.
    """

    resource_definitions: List[Resource]


class ListResult(BaseModel):
    """List resource definitions with optional filtering by dataset, integration, or attach type result type

    Result schema for resource_definitions.list action.
    """

    resource_definitions: List[Resource]


class ListByKeysResult(BaseModel):
    """List resource definitions filtered by specific keys with optional additional filters result type

    Result schema for resource_definitions.list_by_keys action.
    """

    resource_definitions: List[Resource]


def search(
    query: Optional[Union[str, TemplateString]] = None,
    or_keys: Optional[Any] = None,
    and_keys: Optional[Any] = None,
    dataset_id: Optional[Union[str, TemplateString]] = None,
    integration_config_id: Optional[Union[str, TemplateString]] = None,
    limit: Optional[Union[int, TemplateString]] = None,
    step_metadata: Optional[StepMetadata] = None,
    **params: Any,
) -> SearchParams:
    """Search for resource definitions using query and key filters

    Args:
        query: query parameter
        or_keys: or_keys parameter
        and_keys: and_keys parameter
        dataset_id: dataset_id parameter
        integration_config_id: integration_config_id parameter
        limit: limit parameter

    Returns:
        SearchParams: Type-safe parameter object
    """
    param_dict = {
        "query": query,
        "or_keys": or_keys,
        "and_keys": and_keys,
        "dataset_id": dataset_id,
        "integration_config_id": integration_config_id,
        "limit": limit,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)

    return SearchParams(**param_dict)


def list(
    dataset_id: Optional[Union[str, TemplateString]] = None,
    integration_config_id: Optional[Union[str, TemplateString]] = None,
    attach_type: Optional[Union[str, TemplateString]] = None,
    limit: Optional[Union[int, TemplateString]] = None,
    step_metadata: Optional[StepMetadata] = None,
    **params: Any,
) -> ListParams:
    """List resource definitions with optional filtering by dataset, integration, or attach type

    Args:
        dataset_id: dataset_id parameter
        integration_config_id: integration_config_id parameter
        attach_type: attach_type parameter
        limit: limit parameter

    Returns:
        ListParams: Type-safe parameter object
    """
    param_dict = {
        "dataset_id": dataset_id,
        "integration_config_id": integration_config_id,
        "attach_type": attach_type,
        "limit": limit,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)

    return ListParams(**param_dict)


def list_by_keys(
    keys: Optional[Any] = None,
    dataset_id: Optional[Union[str, TemplateString]] = None,
    integration_config_id: Optional[Union[str, TemplateString]] = None,
    attach_type: Optional[Union[str, TemplateString]] = None,
    limit: Optional[Union[int, TemplateString]] = None,
    step_metadata: Optional[StepMetadata] = None,
    **params: Any,
) -> ListByKeysParams:
    """List resource definitions filtered by specific keys with optional additional filters

    Args:
        keys: keys parameter
        dataset_id: dataset_id parameter
        integration_config_id: integration_config_id parameter
        attach_type: attach_type parameter
        limit: limit parameter

    Returns:
        ListByKeysParams: Type-safe parameter object
    """
    param_dict = {
        "keys": keys,
        "dataset_id": dataset_id,
        "integration_config_id": integration_config_id,
        "attach_type": attach_type,
        "limit": limit,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)

    return ListByKeysParams(**param_dict)


# Associate parameter classes with their result types
SearchParams._result = SearchResult
ListParams._result = ListResult
ListByKeysParams._result = ListByKeysResult
