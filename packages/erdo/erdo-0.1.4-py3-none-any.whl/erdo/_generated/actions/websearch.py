"""
Web search actions for finding information on the internet service functions.
Auto-generated - DO NOT EDIT.

Provides type-safe action definitions for websearch service.
Actual execution happens in the Go backend after syncing.
"""

from typing import Any, List, Optional, Union

from pydantic import BaseModel

from erdo.template import TemplateString
from erdo.types import StepMetadata


class SearchParams(BaseModel):
    """Search the web using Jina's search API and return relevant results parameters"""

    name: str = "websearch.search"  # Action type for roundtrip compatibility
    query: Optional[Union[str, TemplateString]] = None  # query parameter
    language: Optional[Union[str, TemplateString]] = None  # language parameter
    country: Optional[Union[str, TemplateString]] = None  # country parameter
    location: Optional[Union[str, TemplateString]] = None  # location parameter
    num_results: Optional[Union[int, TemplateString]] = None  # num_results parameter


class SearchResult(BaseModel):
    """Search the web using Jina's search API and return relevant results result type

    Result schema for websearch.search action.
    """

    results: List[Any]
    total_results: Optional[float]
    query: Optional[str]


def search(
    query: Optional[Union[str, TemplateString]] = None,
    language: Optional[Union[str, TemplateString]] = None,
    country: Optional[Union[str, TemplateString]] = None,
    location: Optional[Union[str, TemplateString]] = None,
    num_results: Optional[Union[int, TemplateString]] = None,
    step_metadata: Optional[StepMetadata] = None,
    **params: Any,
) -> SearchParams:
    """Search the web using Jina's search API and return relevant results

    Args:
        query: query parameter
        language: language parameter
        country: country parameter
        location: location parameter
        num_results: num_results parameter

    Returns:
        SearchParams: Type-safe parameter object
    """
    param_dict = {
        "query": query,
        "language": language,
        "country": country,
        "location": location,
        "num_results": num_results,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)

    return SearchParams(**param_dict)


# Associate parameter classes with their result types
SearchParams._result = SearchResult
