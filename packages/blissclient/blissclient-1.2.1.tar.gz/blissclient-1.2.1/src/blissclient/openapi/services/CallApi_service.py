import json
from typing import *

import httpx

from ..api_config import APIConfig, HTTPException
from ..models import *


def _CallFunctionResourceV1_post_post(
    data: CallFunction, api_config_override: Optional[APIConfig] = None
) -> CallFunctionResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/call"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    try:
        with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
            response = client.request(
                "post",
                httpx.URL(path),
                headers=headers,
                params=query_params,
                json=data.dict(),
            )
    except httpx.ConnectError:
        import os

        from blissclient.exceptions import BlissRESTCantConnect

        raise BlissRESTCantConnect(f"Cant connect to Bliss REST API at `{base_path}`")

    if response.status_code != 200:
        from blissclient import parse_http_error_response

        parse_http_error_response(response)
        raise HTTPException(
            response.status_code, f" failed with status code: {response.status_code}"
        )

    return (
        CallFunctionResponse(**response.json())
        if response.json() is not None
        else CallFunctionResponse()
    )


def _CallFunctionStateResourceV1_get__call_id__get(
    call_id: str, api_config_override: Optional[APIConfig] = None
) -> CallFunctionAsyncState:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/call/{call_id}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    try:
        with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
            response = client.request(
                "get",
                httpx.URL(path),
                headers=headers,
                params=query_params,
            )
    except httpx.ConnectError:
        import os

        from blissclient.exceptions import BlissRESTCantConnect

        raise BlissRESTCantConnect(f"Cant connect to Bliss REST API at `{base_path}`")

    if response.status_code != 200:
        from blissclient import parse_http_error_response

        parse_http_error_response(response)
        raise HTTPException(
            response.status_code, f" failed with status code: {response.status_code}"
        )

    return (
        CallFunctionAsyncState(**response.json())
        if response.json() is not None
        else CallFunctionAsyncState()
    )


def _CallFunctionStateResourceV1_delete__call_id__delete(
    call_id: str, api_config_override: Optional[APIConfig] = None
) -> None:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/call/{call_id}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    try:
        with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
            response = client.request(
                "delete",
                httpx.URL(path),
                headers=headers,
                params=query_params,
            )
    except httpx.ConnectError:
        import os

        from blissclient.exceptions import BlissRESTCantConnect

        raise BlissRESTCantConnect(f"Cant connect to Bliss REST API at `{base_path}`")

    if response.status_code != 204:
        from blissclient import parse_http_error_response

        parse_http_error_response(response)
        raise HTTPException(
            response.status_code, f" failed with status code: {response.status_code}"
        )

    return None
