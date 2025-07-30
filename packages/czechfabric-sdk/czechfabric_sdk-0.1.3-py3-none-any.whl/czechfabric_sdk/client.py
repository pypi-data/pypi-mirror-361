import asyncio
from typing import Optional
from functools import wraps

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.exceptions import ToolError

import httpx


from czechfabric_sdk.exceptions import NetworkError, InvalidAPIKeyError, RateLimitExceededError, ToolExecutionError
from czechfabric_sdk.logging_config import logger
from czechfabric_sdk.models import TripRequest, DeparturesRequest, GeocodeRequest


def retry(max_attempts=3, backoff_factor=0.5):
    """
    Decorator for retrying async functions with exponential backoff.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            delay = backoff_factor
            attempt = 1
            while True:
                try:
                    return await func(*args, **kwargs)
                except (httpx.HTTPError, ToolError) as e:
                    if attempt >= max_attempts:
                        logger.error(f"Exceeded max retries ({max_attempts}).")
                        raise NetworkError(f"Operation failed after {max_attempts} attempts.") from e
                    logger.warning(f"Attempt {attempt} failed ({e}); retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    delay *= 2
                    attempt += 1

        return wrapper

    return decorator


class CzechFabricClient:
    """
    Async client for CzechFabric MCP.
    """

    def __init__(self, api_key: str, base_url: str, timeout: float = 30.0) -> None:
        if not api_key:
            raise ValueError("API key required.")
        if not base_url:
            raise ValueError("Base URL required.")

        self._transport = StreamableHttpTransport(
            url=base_url,
            headers={"x-api-key": api_key},
        )
        self._client = Client(self._transport, timeout=timeout)

    @retry(max_attempts=3, backoff_factor=0.75)
    async def _call_tool(self, name: str, params: dict, cache: bool = False) -> str:
        """
        Call tool with optional caching.
        """
        if cache:
            from czechfabric_sdk.cache import cache_tool_call
            return await cache_tool_call(name, tuple(sorted(params.items())))

        async with self._client:
            try:
                logger.info(f"Calling tool '{name}' with {params}")
                result = await self._client.call_tool(name, params)
                logger.debug(f"Tool '{name}' response: {result.data}")
                return str(result.data)
            except ToolError as e:
                msg = str(e).lower()
                if "unauthorized" in msg or "forbidden" in msg:
                    raise InvalidAPIKeyError("Invalid API key.") from e
                if "rate limit" in msg or "too many requests" in msg:
                    raise RateLimitExceededError("Rate limit exceeded.") from e
                raise ToolExecutionError(f"Tool '{name}' failed: {e}") from e

    async def plan_trip(self, from_place: str, to_place: str) -> str:
        request = TripRequest(from_place=from_place, to_place=to_place)
        return await self._call_tool("plan_trip_between", request.model_dump())

    async def get_departures(self, stop_name: str) -> str:
        request = DeparturesRequest(stop_name=stop_name)
        return await self._call_tool("get_departures", request.model_dump())

    async def geocode(self, name: str, use_cache: bool = True) -> str:
        request = GeocodeRequest(name=name)
        return await self._call_tool("geocode", request.model_dump(), cache=use_cache)
