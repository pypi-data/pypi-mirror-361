"""
Memory management actions for storing, searching, and managing memories service functions.
Auto-generated - DO NOT EDIT.

Provides type-safe action definitions for memory service.
Actual execution happens in the Go backend after syncing.
"""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

from erdo._generated.types import Memory
from erdo.template import TemplateString
from erdo.types import StepMetadata


class SearchParams(BaseModel):
    """Search memories using semantic search with optional filters parameters"""

    name: str = "memory.search"  # Action type for roundtrip compatibility
    query: Optional[Union[str, TemplateString]] = None  # query parameter
    organization_scope: Optional[Union[str, TemplateString]] = (
        None  # organization_scope parameter
    )
    user_scope: Optional[Union[str, TemplateString]] = None  # user_scope parameter
    thread_id: Optional[Union[str, TemplateString]] = None  # thread_id parameter
    dataset_id: Optional[Union[str, TemplateString]] = None  # dataset_id parameter
    integration_config_id: Optional[Union[str, TemplateString]] = (
        None  # integration_config_id parameter
    )
    approval_status: Optional[Union[str, TemplateString]] = (
        None  # approval_status parameter
    )
    limit: Optional[Union[int, TemplateString]] = None  # limit parameter
    max_distance: Optional[Any] = None  # max_distance parameter


class SearchFromQueriesParams(BaseModel):
    """Search memories using multiple queries including integration-specific queries parameters"""

    name: str = "memory.search_from_queries"  # Action type for roundtrip compatibility
    queries: Optional[Any] = None  # queries parameter
    integration_queries: Optional[Any] = None  # integration_queries parameter
    organization_scope: Optional[Union[str, TemplateString]] = (
        None  # organization_scope parameter
    )
    user_scope: Optional[Union[str, TemplateString]] = None  # user_scope parameter
    thread_id: Optional[Union[str, TemplateString]] = None  # thread_id parameter
    limit: Optional[Union[int, TemplateString]] = None  # limit parameter
    max_distance: Optional[Any] = None  # max_distance parameter


class ProcessIntegrationQueriesParams(BaseModel):
    """Process integration queries to create resource-specific search queries parameters"""

    name: str = (
        "memory.process_integration_queries"  # Action type for roundtrip compatibility
    )
    query: Optional[Union[str, TemplateString]] = None  # query parameter
    resource: Optional[Any] = None  # resource parameter
    queries: Optional[Any] = None  # queries parameter


class StoreParams(BaseModel):
    """Store or update a memory with content, metadata, and scope settings parameters"""

    name: str = "memory.store"  # Action type for roundtrip compatibility
    memory: Optional[Any] = None  # memory parameter


class SearchResult(BaseModel):
    """Search memories using semantic search with optional filters result type

    Result schema for memory.search action.
    """

    memories: List[Memory]


class SearchFromQueriesResult(BaseModel):
    """Search memories using multiple queries including integration-specific queries result type

    Result schema for memory.search_from_queries action.
    """

    data: Optional[Dict[str, Any]]  # Action result data


class ProcessIntegrationQueriesResult(BaseModel):
    """Process integration queries to create resource-specific search queries result type

    Result schema for memory.process_integration_queries action.
    """

    data: Optional[Dict[str, Any]]  # Action result data


class StoreResult(BaseModel):
    """Store or update a memory with content, metadata, and scope settings result type

    Result schema for memory.store action.
    """

    memory: Any


def search(
    query: Optional[Union[str, TemplateString]] = None,
    organization_scope: Optional[Union[str, TemplateString]] = None,
    user_scope: Optional[Union[str, TemplateString]] = None,
    thread_id: Optional[Union[str, TemplateString]] = None,
    dataset_id: Optional[Union[str, TemplateString]] = None,
    integration_config_id: Optional[Union[str, TemplateString]] = None,
    approval_status: Optional[Union[str, TemplateString]] = None,
    limit: Optional[Union[int, TemplateString]] = None,
    max_distance: Optional[Any] = None,
    step_metadata: Optional[StepMetadata] = None,
    **params: Any,
) -> SearchParams:
    """Search memories using semantic search with optional filters

    Args:
        query: query parameter
        organization_scope: organization_scope parameter
        user_scope: user_scope parameter
        thread_id: thread_id parameter
        dataset_id: dataset_id parameter
        integration_config_id: integration_config_id parameter
        approval_status: approval_status parameter
        limit: limit parameter
        max_distance: max_distance parameter

    Returns:
        SearchParams: Type-safe parameter object
    """
    param_dict = {
        "query": query,
        "organization_scope": organization_scope,
        "user_scope": user_scope,
        "thread_id": thread_id,
        "dataset_id": dataset_id,
        "integration_config_id": integration_config_id,
        "approval_status": approval_status,
        "limit": limit,
        "max_distance": max_distance,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)

    return SearchParams(**param_dict)


def search_from_queries(
    queries: Optional[Any] = None,
    integration_queries: Optional[Any] = None,
    organization_scope: Optional[Union[str, TemplateString]] = None,
    user_scope: Optional[Union[str, TemplateString]] = None,
    thread_id: Optional[Union[str, TemplateString]] = None,
    limit: Optional[Union[int, TemplateString]] = None,
    max_distance: Optional[Any] = None,
    step_metadata: Optional[StepMetadata] = None,
    **params: Any,
) -> SearchFromQueriesParams:
    """Search memories using multiple queries including integration-specific queries

    Args:
        queries: queries parameter
        integration_queries: integration_queries parameter
        organization_scope: organization_scope parameter
        user_scope: user_scope parameter
        thread_id: thread_id parameter
        limit: limit parameter
        max_distance: max_distance parameter

    Returns:
        SearchFromQueriesParams: Type-safe parameter object
    """
    param_dict = {
        "queries": queries,
        "integration_queries": integration_queries,
        "organization_scope": organization_scope,
        "user_scope": user_scope,
        "thread_id": thread_id,
        "limit": limit,
        "max_distance": max_distance,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)

    return SearchFromQueriesParams(**param_dict)


def process_integration_queries(
    query: Optional[Union[str, TemplateString]] = None,
    resource: Optional[Any] = None,
    queries: Optional[Any] = None,
    step_metadata: Optional[StepMetadata] = None,
    **params: Any,
) -> ProcessIntegrationQueriesParams:
    """Process integration queries to create resource-specific search queries

    Args:
        query: query parameter
        resource: resource parameter
        queries: queries parameter

    Returns:
        ProcessIntegrationQueriesParams: Type-safe parameter object
    """
    param_dict = {
        "query": query,
        "resource": resource,
        "queries": queries,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)

    return ProcessIntegrationQueriesParams(**param_dict)


def store(
    memory: Optional[Any] = None,
    step_metadata: Optional[StepMetadata] = None,
    **params: Any,
) -> StoreParams:
    """Store or update a memory with content, metadata, and scope settings

    Args:
        memory: memory parameter

    Returns:
        StoreParams: Type-safe parameter object
    """
    param_dict = {
        "memory": memory,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)

    return StoreParams(**param_dict)


# Associate parameter classes with their result types
SearchParams._result = SearchResult
SearchFromQueriesParams._result = SearchFromQueriesResult
ProcessIntegrationQueriesParams._result = ProcessIntegrationQueriesResult
StoreParams._result = StoreResult
