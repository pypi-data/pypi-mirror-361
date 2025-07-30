import datetime
import functools
import json
import os
import re
import ssl
import tempfile
import typing
import warnings
import zoneinfo
from typing import Iterable

import fastmcp.tools
import httpx
import langchain_core.utils.function_calling
import mcp
import pydantic
import urllib3


def truncate_text(text: str, max_length: int, placeholder: str = "[...]") -> str:
    text = text[:max_length] + placeholder if len(text) > max_length else text
    return text


def json_dumps_for_ai(
    value: str | list | dict | pydantic.BaseModel,
    max_length: int | None = None,
    truncation_placeholder: str = "[CONTENT END] The rest of the content was truncated to fit into LLM context window.",
    **kwargs,
) -> str:
    if isinstance(value, str):
        return value

    if isinstance(value, pydantic.BaseModel):
        value = value.model_dump()

    value = json.dumps(value, ensure_ascii=False, **kwargs)
    if max_length:
        value = truncate_text(value, max_length, placeholder=truncation_placeholder)

    return value


def format_datetime_for_ai(
    date: datetime.datetime | str,
    timespec: str = "seconds",
    timezone: zoneinfo.ZoneInfo = zoneinfo.ZoneInfo("UTC"),
) -> str:
    date = datetime.datetime.fromisoformat(date) if isinstance(date, str) else date
    date = date.astimezone(timezone)
    date = date.isoformat(timespec=timespec, sep=" ")
    return date


def to_markdown_json(text: str) -> str:
    text = f"```json\n{text}\n```"
    return text


def format_json_for_ai(
    value: str | list | dict | pydantic.BaseModel, indent: int | None = 0
) -> str:
    text = json_dumps_for_ai(value, indent=indent)
    text = to_markdown_json(text)
    return text


def filter_dict_by_keys(dictionary: dict, keys: Iterable) -> dict:
    dictionary = {key: dictionary[key] for key in keys if key in dictionary}
    return dictionary


def recursively_collect_file_paths_in_directory(directory_path: str) -> list[str]:
    file_paths = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            full_path = os.path.join(root, file)
            if os.path.isfile(full_path):
                file_paths.append(full_path)

    return file_paths


def get_return_type_annotation(function):
    annotation = function.__annotations__.get("return")
    return annotation


def to_fastmcp_tool(
    function,
    tags: set[str] | None,
    annotations: mcp.types.ToolAnnotations | None,
    max_output_length: int | None = None,
) -> fastmcp.tools.FunctionTool:
    """Adds a custom serializer to ensure consistent and token-efficient conversion of tool output to text."""
    return_type = get_return_type_annotation(function)
    if return_type is list or typing.get_origin(return_type) is list:
        warnings.warn(
            "When tool returns list, each of its elements will be serialized separately "
            "using fastmcp.tools.tool._convert_to_content into MCPContent."
        )

    tool = fastmcp.tools.FunctionTool.from_function(
        function,
        tags=tags,
        annotations=annotations,
        serializer=functools.partial(json_dumps_for_ai, max_length=max_output_length),
    )
    # Normalize tool parameters schema to match OpenAI's.
    # For example, it dereferences JSON schema $refs, which are not supported by many AI API providers.
    openai_tool_schema = langchain_core.utils.function_calling.convert_to_openai_tool(function)
    tool.parameters = openai_tool_schema["function"]["parameters"]
    return tool


def request_as_dict(*args, **kwargs) -> dict:
    response = httpx.get(*args, **kwargs)
    response.raise_for_status()
    response_dict = response.json()
    return response_dict


def to_datetime(
    date: datetime.date | datetime.timedelta | str | int | float | None = None,
) -> datetime.datetime:
    match date:
        case datetime.datetime():
            pass
        case datetime.date():
            date = datetime.datetime.combine(date, datetime.time())
        case None:
            date = datetime.datetime.now()
        case datetime.timedelta():
            date += datetime.datetime.now()
        case str():
            date = datetime.datetime.fromisoformat(date)
        case int() | float():
            date = datetime.datetime.fromtimestamp(date)
        case _:
            raise ValueError(f"Unexpected date type: {type(date)}")

    date = date if date.tzinfo else date.astimezone()
    # or date = date.astimezone(datetime.timezone.utc)
    return date


def join_url_components(*url_components: str) -> str:
    url = "/".join(str(i).strip("/") for i in url_components)
    return url


def try_format_json_with_indent(text: str, indent: int = 2) -> str:
    try:
        text = json.dumps(json.loads(text), indent=indent)
    except json.JSONDecodeError:
        pass

    return text


def raise_for_status(response: httpx.Response, max_text_length: int = 1000) -> None:
    if not response.is_error:
        return

    response_text = try_format_json_with_indent(response.text)
    request_text = try_format_json_with_indent(response.request.content.decode())
    if max_text_length:
        request_text = truncate_text(request_text, max_text_length)
        response_text = truncate_text(response_text, max_text_length)

    error_message = (
        f"Error in HTTP response while requesting {response.url}\n"
        f"Status code: {response.status_code}\n"
        f"Reason: {response.reason_phrase}\n"
        f"Request body: {request_text}\n"
        f"Response body: {response_text}\n"
    )
    error = httpx.HTTPStatusError(error_message, request=response.request, response=response)
    raise error


async def araise_for_status(response: httpx.Response, max_response_text_length: int = 1000) -> None:
    if not response.is_error:
        return

    await response.aread()
    raise_for_status(response, max_text_length=max_response_text_length)


def try_match_regex(pattern: str, string: str, **kwargs):
    match = re.match(pattern, string, **kwargs)
    if not match:
        raise ValueError(f"String '{string}' does not fit expected pattern '{pattern}'")

    return match


def value_to_key(items: list, key: str) -> dict:
    dictionary = {i.pop(key): i for i in items}
    return dictionary


def to_maybe_ssl_context(ssl_verify: bool | str) -> bool | ssl.SSLContext:
    if isinstance(ssl_verify, str):
        ssl_verify = ssl.create_default_context(cafile=ssl_verify)

    return ssl_verify


def add_mcp_server_components(
    server: fastmcp.FastMCP | None = None,
    tools: Iterable[fastmcp.tools.FunctionTool] = (),
    resources: Iterable[fastmcp.resources.Resource] = (),
    prompts: Iterable[fastmcp.prompts.Prompt] = (),
) -> fastmcp.FastMCP:
    server = server or fastmcp.FastMCP()
    for tool in tools:
        server.add_tool(tool)

    for resource in resources:
        server.add_resource(resource)

    for prompt in prompts:
        server.add_prompt(prompt)

    return server


def wrap_with_xml_tag(tag: str, value: str, with_new_lines: bool = False) -> str:
    value = f"\n{value}\n" if with_new_lines else value
    wrapped_value = f"<{tag}>{value}</{tag}>"
    wrapped_value += "\n" if with_new_lines else ""
    return wrapped_value


def assign_default_tool_annotation_hints(
    annotation: mcp.types.ToolAnnotations | None = None,
) -> mcp.types.ToolAnnotations:
    annotation = annotation or mcp.types.ToolAnnotations()
    if annotation.readOnlyHint and annotation.destructiveHint:
        raise ValueError("Tool cannot be both readonly and destructive.")

    if annotation.readOnlyHint and annotation.idempotentHint is False:
        raise ValueError("Tool cannot be both readonly and non-idempotent.")

    default = mcp.types.ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=False,
        openWorldHint=True,
    )
    for hint, value in default.model_dump().items():
        if getattr(annotation, hint) is None:
            setattr(annotation, hint, value)

    return annotation


def disable_urllib_insecure_request_warning():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def set_ssl_cert_file_from_cadata(cadata: str, set_ssl_cert_file_env_var: bool = True) -> str:
    with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".pem") as temp_ca_file:
        temp_ca_file.write(cadata)
        ca_file_path = temp_ca_file.name

    if set_ssl_cert_file_env_var:
        os.environ["SSL_CERT_FILE"] = ca_file_path

    return ca_file_path


def split_schema_table(schema_table: str) -> tuple[str | None, str]:
    schema, table = schema_table.split(".") if "." in schema_table else (None, schema_table)
    return schema, table
