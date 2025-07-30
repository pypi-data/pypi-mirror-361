"""
Code execution actions for running and processing code in sandboxed environments service functions.
Auto-generated - DO NOT EDIT.

Provides type-safe action definitions for codeexec service.
Actual execution happens in the Go backend after syncing.
"""

from typing import Any, Dict, Optional, Union

from pydantic import BaseModel

from erdo.template import TemplateString
from erdo.types import StepMetadata


class ExecuteParams(BaseModel):
    """Execute code in a sandboxed environment and return the results parameters"""

    name: str = "codeexec.execute"  # Action type for roundtrip compatibility
    entrypoint: Optional[Union[str, TemplateString]] = None  # entrypoint parameter
    code_files: Optional[Any] = None  # code_files parameter
    resources: Optional[Any] = None  # resources parameter
    encrypted_secrets: Optional[Union[str, TemplateString]] = (
        None  # encrypted_secrets parameter
    )
    parameters: Optional[Union[str, TemplateString]] = None  # parameters parameter


class ParseFileAsBotResourceParams(BaseModel):
    """Parse a file from code execution results into a bot resource with dataset and analysis parameters"""

    name: str = (
        "codeexec.parse_file_as_bot_resource"  # Action type for roundtrip compatibility
    )
    file: Optional[Any] = None  # file parameter
    files_analysis: Optional[Any] = None  # files_analysis parameter
    files_metadata: Optional[Any] = None  # files_metadata parameter


class ParseFileAsJsonParams(BaseModel):
    """Parse a file from code execution results as JSON data parameters"""

    name: str = "codeexec.parse_file_as_json"  # Action type for roundtrip compatibility
    file: Optional[Any] = None  # file parameter
    thread_id: Optional[Any] = None  # thread_id parameter


class ExecuteResult(BaseModel):
    """Execute code in a sandboxed environment and return the results result type

    Result schema for codeexec.execute action.
    """

    output: str
    error: Optional[str]
    exit_code: Optional[float]
    files: Optional[Any]


class ParseFileAsBotResourceResult(BaseModel):
    """Parse a file from code execution results into a bot resource with dataset and analysis result type

    Result schema for codeexec.parse_file_as_bot_resource action.
    """

    data: Optional[Dict[str, Any]]  # Action result data


class ParseFileAsJsonResult(BaseModel):
    """Parse a file from code execution results as JSON data result type

    Result schema for codeexec.parse_file_as_json action.
    """

    data: Any


def execute(
    entrypoint: Optional[Union[str, TemplateString]] = None,
    code_files: Optional[Any] = None,
    resources: Optional[Any] = None,
    encrypted_secrets: Optional[Union[str, TemplateString]] = None,
    parameters: Optional[Union[str, TemplateString]] = None,
    step_metadata: Optional[StepMetadata] = None,
    **params: Any,
) -> ExecuteParams:
    """Execute code in a sandboxed environment and return the results

    Args:
        entrypoint: entrypoint parameter
        code_files: code_files parameter
        resources: resources parameter
        encrypted_secrets: encrypted_secrets parameter
        parameters: parameters parameter

    Returns:
        ExecuteParams: Type-safe parameter object
    """
    param_dict = {
        "entrypoint": entrypoint,
        "code_files": code_files,
        "resources": resources,
        "encrypted_secrets": encrypted_secrets,
        "parameters": parameters,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)

    return ExecuteParams(**param_dict)


def parse_file_as_bot_resource(
    file: Optional[Any] = None,
    files_analysis: Optional[Any] = None,
    files_metadata: Optional[Any] = None,
    step_metadata: Optional[StepMetadata] = None,
    **params: Any,
) -> ParseFileAsBotResourceParams:
    """Parse a file from code execution results into a bot resource with dataset and analysis

    Args:
        file: file parameter
        files_analysis: files_analysis parameter
        files_metadata: files_metadata parameter

    Returns:
        ParseFileAsBotResourceParams: Type-safe parameter object
    """
    param_dict = {
        "file": file,
        "files_analysis": files_analysis,
        "files_metadata": files_metadata,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)

    return ParseFileAsBotResourceParams(**param_dict)


def parse_file_as_json(
    file: Optional[Any] = None,
    thread_id: Optional[Any] = None,
    step_metadata: Optional[StepMetadata] = None,
    **params: Any,
) -> ParseFileAsJsonParams:
    """Parse a file from code execution results as JSON data

    Args:
        file: file parameter
        thread_id: thread_id parameter

    Returns:
        ParseFileAsJsonParams: Type-safe parameter object
    """
    param_dict = {
        "file": file,
        "thread_id": thread_id,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)

    return ParseFileAsJsonParams(**param_dict)


# Associate parameter classes with their result types
ExecuteParams._result = ExecuteResult
ParseFileAsBotResourceParams._result = ParseFileAsBotResourceResult
ParseFileAsJsonParams._result = ParseFileAsJsonResult
