"""
Basic utility actions for data manipulation and control flow service functions.
Auto-generated - DO NOT EDIT.

Provides type-safe action definitions for utils service.
Actual execution happens in the Go backend after syncing.
"""

from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field

from erdo.template import TemplateString
from erdo.types import StepMetadata


class EchoParams(BaseModel):
    """Echo parameters back as output parameters"""

    name: str = "utils.echo"  # Action type for roundtrip compatibility
    data: Optional[Any] = None  # data parameter


class ParseJsonParams(BaseModel):
    """Parse JSON string and validate required keys parameters"""

    model_config = {"populate_by_name": True}  # Allow both field names and aliases

    name: str = "utils.parse_json"  # Action type for roundtrip compatibility
    json_data: Optional[Union[str, TemplateString]] = Field(
        default=None, alias="json"
    )  # json parameter
    required_keys: Optional[Any] = None  # required_keys parameter


class ConcatParams(BaseModel):
    """Concatenate arrays or strings from specified keys parameters"""

    name: str = "utils.concat"  # Action type for roundtrip compatibility
    concat: Optional[Any] = None  # concat parameter
    data: Optional[Any] = None  # data parameter


class CastParams(BaseModel):
    """Cast string values to different types (string, integer, float, bool) parameters"""

    model_config = {"populate_by_name": True}  # Allow both field names and aliases

    name: str = "utils.cast"  # Action type for roundtrip compatibility
    value: Optional[Union[str, TemplateString]] = None  # value parameter
    type_name: Optional[Union[str, TemplateString]] = Field(
        default=None, alias="type"
    )  # type parameter


class RaiseParams(BaseModel):
    """Raise a status with message and parameters parameters"""

    name: str = "utils.raise"  # Action type for roundtrip compatibility
    status: Optional[Union[str, TemplateString]] = None  # status parameter
    message: Optional[Union[str, TemplateString]] = None  # message parameter
    parameters: Optional[Any] = None  # parameters parameter


class CaptureExceptionParams(BaseModel):
    """Capture an exception to Sentry and return an error result parameters"""

    name: str = "utils.capture_exception"  # Action type for roundtrip compatibility
    exception: Optional[Union[str, TemplateString]] = None  # exception parameter
    message: Optional[Union[str, TemplateString]] = None  # message parameter
    error_type: Optional[Union[str, TemplateString]] = None  # error_type parameter


class SendStatusParams(BaseModel):
    """Send a status event to the client parameters"""

    name: str = "utils.send_status"  # Action type for roundtrip compatibility
    status: Optional[Union[str, TemplateString]] = None  # status parameter
    message: Optional[Union[str, TemplateString]] = None  # message parameter
    details: Optional[Any] = None  # details parameter


class WriteParams(BaseModel):
    """Write output message with specified content types parameters"""

    name: str = "utils.write"  # Action type for roundtrip compatibility
    message: Optional[Union[str, TemplateString]] = None  # message parameter
    content_type: Optional[Union[str, TemplateString]] = None  # content_type parameter
    history_content_type: Optional[Union[str, TemplateString]] = (
        None  # history_content_type parameter
    )
    ui_content_type: Optional[Union[str, TemplateString]] = (
        None  # ui_content_type parameter
    )


class EchoResult(BaseModel):
    """Echo parameters back as output result type

    Result schema for utils.echo action.
    """

    data: Optional[Dict[str, Any]]  # Action result data


class ParseJsonResult(BaseModel):
    """Parse JSON string and validate required keys result type

    Result schema for utils.parse_json action.
    """

    data: Optional[Dict[str, Any]]  # Action result data


class ConcatResult(BaseModel):
    """Concatenate arrays or strings from specified keys result type

    Result schema for utils.concat action.
    """

    data: Optional[Dict[str, Any]]  # Action result data


class CastResult(BaseModel):
    """Cast string values to different types (string, integer, float, bool) result type

    Result schema for utils.cast action.
    """

    data: Optional[Dict[str, Any]]  # Action result data


class RaiseResult(BaseModel):
    """Raise a status with message and parameters result type

    Result schema for utils.raise action.
    """

    data: Optional[Dict[str, Any]]  # Action result data


class CaptureExceptionResult(BaseModel):
    """Capture an exception to Sentry and return an error result result type

    Result schema for utils.capture_exception action.
    """

    data: Optional[Dict[str, Any]]  # Action result data


class SendStatusResult(BaseModel):
    """Send a status event to the client result type

    Result schema for utils.send_status action.
    """

    data: Optional[Dict[str, Any]]  # Action result data


class WriteResult(BaseModel):
    """Write output message with specified content types result type

    Result schema for utils.write action.
    """

    data: Optional[Dict[str, Any]]  # Action result data


def echo(
    data: Optional[Any] = None,
    step_metadata: Optional[StepMetadata] = None,
    **params: Any,
) -> EchoParams:
    """Echo parameters back as output

    Args:
        data: data parameter

    Returns:
        EchoParams: Type-safe parameter object
    """
    param_dict = {
        "data": data,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)

    return EchoParams(**param_dict)


def parse_json(
    json_data: Optional[Union[str, TemplateString]] = None,
    required_keys: Optional[Any] = None,
    step_metadata: Optional[StepMetadata] = None,
    **params: Any,
) -> ParseJsonParams:
    """Parse JSON string and validate required keys

    Args:
        json_data: json parameter
        required_keys: required_keys parameter

    Returns:
        ParseJsonParams: Type-safe parameter object
    """
    param_dict = {
        "json": json_data,
        "required_keys": required_keys,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)

    return ParseJsonParams(**param_dict)


def concat(
    concat: Optional[Any] = None,
    data: Optional[Any] = None,
    step_metadata: Optional[StepMetadata] = None,
    **params: Any,
) -> ConcatParams:
    """Concatenate arrays or strings from specified keys

    Args:
        concat: concat parameter
        data: data parameter

    Returns:
        ConcatParams: Type-safe parameter object
    """
    param_dict = {
        "concat": concat,
        "data": data,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)

    return ConcatParams(**param_dict)


def cast(
    value: Optional[Union[str, TemplateString]] = None,
    type_name: Optional[Union[str, TemplateString]] = None,
    step_metadata: Optional[StepMetadata] = None,
    **params: Any,
) -> CastParams:
    """Cast string values to different types (string, integer, float, bool)

    Args:
        value: value parameter
        type_name: type parameter

    Returns:
        CastParams: Type-safe parameter object
    """
    param_dict = {
        "value": value,
        "type": type_name,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)

    return CastParams(**param_dict)


def raise_error(
    status: Optional[Union[str, TemplateString]] = None,
    message: Optional[Union[str, TemplateString]] = None,
    parameters: Optional[Any] = None,
    step_metadata: Optional[StepMetadata] = None,
    **params: Any,
) -> RaiseParams:
    """Raise a status with message and parameters

    Args:
        status: status parameter
        message: message parameter
        parameters: parameters parameter

    Returns:
        RaiseParams: Type-safe parameter object
    """
    param_dict = {
        "status": status,
        "message": message,
        "parameters": parameters,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)

    return RaiseParams(**param_dict)


def capture_exception(
    exception: Optional[Union[str, TemplateString]] = None,
    message: Optional[Union[str, TemplateString]] = None,
    error_type: Optional[Union[str, TemplateString]] = None,
    step_metadata: Optional[StepMetadata] = None,
    **params: Any,
) -> CaptureExceptionParams:
    """Capture an exception to Sentry and return an error result

    Args:
        exception: exception parameter
        message: message parameter
        error_type: error_type parameter

    Returns:
        CaptureExceptionParams: Type-safe parameter object
    """
    param_dict = {
        "exception": exception,
        "message": message,
        "error_type": error_type,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)

    return CaptureExceptionParams(**param_dict)


def send_status(
    status: Optional[Union[str, TemplateString]] = None,
    message: Optional[Union[str, TemplateString]] = None,
    details: Optional[Any] = None,
    step_metadata: Optional[StepMetadata] = None,
    **params: Any,
) -> SendStatusParams:
    """Send a status event to the client

    Args:
        status: status parameter
        message: message parameter
        details: details parameter

    Returns:
        SendStatusParams: Type-safe parameter object
    """
    param_dict = {
        "status": status,
        "message": message,
        "details": details,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)

    return SendStatusParams(**param_dict)


def write(
    message: Optional[Union[str, TemplateString]] = None,
    content_type: Optional[Union[str, TemplateString]] = None,
    history_content_type: Optional[Union[str, TemplateString]] = None,
    ui_content_type: Optional[Union[str, TemplateString]] = None,
    step_metadata: Optional[StepMetadata] = None,
    **params: Any,
) -> WriteParams:
    """Write output message with specified content types

    Args:
        message: message parameter
        content_type: content_type parameter
        history_content_type: history_content_type parameter
        ui_content_type: ui_content_type parameter

    Returns:
        WriteParams: Type-safe parameter object
    """
    param_dict = {
        "message": message,
        "content_type": content_type,
        "history_content_type": history_content_type,
        "ui_content_type": ui_content_type,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)

    return WriteParams(**param_dict)


# Associate parameter classes with their result types
EchoParams._result = EchoResult
ParseJsonParams._result = ParseJsonResult
ConcatParams._result = ConcatResult
CastParams._result = CastResult
RaiseParams._result = RaiseResult
CaptureExceptionParams._result = CaptureExceptionResult
SendStatusParams._result = SendStatusResult
WriteParams._result = WriteResult
