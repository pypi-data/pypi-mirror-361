"""
Analysis actions for creating and managing data analysis service functions.
Auto-generated - DO NOT EDIT.

Provides type-safe action definitions for analysis service.
Actual execution happens in the Go backend after syncing.
"""

from typing import Any, List, Optional, Union

from pydantic import BaseModel

from erdo.template import TemplateString
from erdo.types import StepMetadata


class CreateAnalysisParams(BaseModel):
    """Create an analysis for a dataset, resource, or dataset-resource combination parameters"""

    name: str = "analysis.create_analysis"  # Action type for roundtrip compatibility
    analysis: Optional[Any] = None  # analysis parameter
    dataset_id: Optional[Union[str, TemplateString]] = None  # dataset_id parameter
    resource_id: Optional[Union[str, TemplateString]] = None  # resource_id parameter


class CreateAnalysisResult(BaseModel):
    """Create an analysis for a dataset, resource, or dataset-resource combination result type

    Result schema for analysis.create_analysis action.
    """

    analysis: Any
    insights: Optional[List[str]]
    recommendations: Optional[List[str]]


def create_analysis(
    analysis: Optional[Any] = None,
    dataset_id: Optional[Union[str, TemplateString]] = None,
    resource_id: Optional[Union[str, TemplateString]] = None,
    step_metadata: Optional[StepMetadata] = None,
    **params: Any,
) -> CreateAnalysisParams:
    """Create an analysis for a dataset, resource, or dataset-resource combination

    Args:
        analysis: analysis parameter
        dataset_id: dataset_id parameter
        resource_id: resource_id parameter

    Returns:
        CreateAnalysisParams: Type-safe parameter object
    """
    param_dict = {
        "analysis": analysis,
        "dataset_id": dataset_id,
        "resource_id": resource_id,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)

    return CreateAnalysisParams(**param_dict)


# Associate parameter classes with their result types
CreateAnalysisParams._result = CreateAnalysisResult
