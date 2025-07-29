import json
from typing import *

import httpx

from ..api_config import APIConfig, HTTPException
from ..models import *


async def _HardwaresResourceV1_get_get(
    type: Optional[Union[str, None]] = None,
    api_config_override: Optional[APIConfig] = None,
) -> Paginated_ObjectSchema_:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/object"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {"type": type}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    try:
        async with httpx.AsyncClient(
            base_url=base_path, verify=api_config.verify
        ) as client:
            response = await client.request(
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
        Paginated_ObjectSchema_(**response.json())
        if response.json() is not None
        else Paginated_ObjectSchema_()
    )


async def _HardwaresResourceV1_post_post(
    data: RegisterHardwareSchema, api_config_override: Optional[APIConfig] = None
) -> RegisterHardwareSchema:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/object"
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
        async with httpx.AsyncClient(
            base_url=base_path, verify=api_config.verify
        ) as client:
            response = await client.request(
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
        RegisterHardwareSchema(**response.json())
        if response.json() is not None
        else RegisterHardwareSchema()
    )


async def _HardwareResourceV1_get__string_name__get(
    name: str, api_config_override: Optional[APIConfig] = None
) -> ObjectSchema:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/object/{name}"
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
        async with httpx.AsyncClient(
            base_url=base_path, verify=api_config.verify
        ) as client:
            response = await client.request(
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
        ObjectSchema(**response.json())
        if response.json() is not None
        else ObjectSchema()
    )


async def _HardwareResourceV1_put__string_name__put(
    name: str, data: SetObjectProperty, api_config_override: Optional[APIConfig] = None
) -> SetObjectProperty:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/object/{name}"
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
        async with httpx.AsyncClient(
            base_url=base_path, verify=api_config.verify
        ) as client:
            response = await client.request(
                "put",
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
        SetObjectProperty(**response.json())
        if response.json() is not None
        else SetObjectProperty()
    )


async def _HardwareResourceV1_delete__string_name__delete(
    name: str, api_config_override: Optional[APIConfig] = None
) -> None:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/object/{name}"
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
        async with httpx.AsyncClient(
            base_url=base_path, verify=api_config.verify
        ) as client:
            response = await client.request(
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
