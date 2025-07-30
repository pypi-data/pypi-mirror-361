import pytest

import httpx
from unittest.mock import AsyncMock, patch

from czechfabric_sdk.client import CzechFabricClient
from czechfabric_sdk.exceptions import InvalidAPIKeyError, RateLimitExceededError


@pytest.mark.asyncio
async def test_plan_trip_success():
    client = CzechFabricClient(api_key="dummy", base_url="https://fake-server/mcp")

    # Patch _call_tool to return dummy response
    client._call_tool = AsyncMock(return_value="Trip planned successfully.")

    result = await client.plan_trip("A", "B")
    assert result == "Trip planned successfully."


@pytest.mark.asyncio
async def test_geocode_with_cache():
    client = CzechFabricClient(api_key="dummy", base_url="https://fake-server/mcp")

    client._call_tool = AsyncMock(return_value="Geocode result")

    result = await client.geocode("Test Place", use_cache=True)
    assert "Geocode result" in result


@pytest.mark.asyncio
async def test_invalid_api_key_error():
    client = CzechFabricClient(api_key="invalid", base_url="https://fake-server/mcp")

    # Patch _call_tool to raise InvalidAPIKeyError
    client._call_tool = AsyncMock(side_effect=InvalidAPIKeyError("Invalid API key"))

    with pytest.raises(InvalidAPIKeyError):
        await client.plan_trip("A", "B")


@pytest.mark.asyncio
async def test_rate_limit_error():
    client = CzechFabricClient(api_key="dummy", base_url="https://fake-server/mcp")

    client._call_tool = AsyncMock(side_effect=RateLimitExceededError("Rate limit exceeded"))

    with pytest.raises(RateLimitExceededError):
        await client.get_departures("Florenc")
