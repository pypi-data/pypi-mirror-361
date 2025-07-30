# 🇨🇿 CzechFabric SDK

**Async Python SDK for accessing CzechFabric MCP server**

[![PyPI](https://img.shields.io/pypi/v/czechfabric-sdk.svg)](https://pypi.org/czechfabric/czechfabric-sdk/)
[![CI](https://github.com/yourusername/czechfabric-sdk/actions/workflows/publish.yml/badge.svg)](https://github.com/czechfabric/czechfabric-sdk/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## ✨ Overview

This SDK provides a robust, type-safe, async interface for interacting with a CzechFabric MCP server via [FastMCP](https://pypi.org/project/fastmcp/).

**Features:**
- ✅ Async operations
- ✅ Automatic retries with exponential backoff
- ✅ In-memory caching
- ✅ Structured logging
- ✅ Rich error handling

---

## 🏗 Installation

```bash
pip install czechfabric-sdk
````

Or install locally:

```bash
pip install .
```

---

## ⚡ Quickstart

```python
import asyncio
from czechfabric_sdk.client import CzechFabricClient

async def main():
    client = CzechFabricClient(
        api_key="YOUR_API_KEY",
        base_url="https://mcp-server.example.com/mcp"
    )

    trip = await client.plan_trip("Prague", "Brno")
    print("Trip Plan:\n", trip)

    departures = await client.get_departures("Florenc")
    print("Departures:\n", departures)

    geocode = await client.geocode("Karlovo náměstí")
    print("Geocode:\n", geocode)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🚀 API Reference

### `CzechFabricClient`

#### Initialization

```python
client = CzechFabricClient(
    api_key: str,
    base_url: str,
    timeout: float = 30.0
)
```

| Param     | Type  | Description                       |
| --------- | ----- | --------------------------------- |
| api\_key  | str   | Your API key for authentication   |
| base\_url | str   | MCP server base URL               |
| timeout   | float | Default timeout per request (sec) |

---

#### Methods

✅ **`plan_trip(from_place, to_place)`**

* Plan a trip between two places.

✅ **`get_departures(stop_name)`**

* Retrieve departures for a given stop.

✅ **`geocode(name, use_cache=True)`**

* Geocode a place name.

All methods are **async** and return `str`.

---

## ⚠️ Error Handling

This SDK raises clear, specific exceptions:

* `InvalidAPIKeyError` – invalid or missing API key
* `RateLimitExceededError` – rate limit exceeded
* `ToolExecutionError` – generic execution failure
* `NetworkError` – connectivity issues

Example:

```python
from czechfabric_sdk.exceptions import InvalidAPIKeyError

try:
    await client.plan_trip("A", "B")
except InvalidAPIKeyError:
    print("Your API key is invalid.")
```

---

## 🧠 Caching

By default, `geocode()` uses in-memory caching via `async_lru`.
To disable cache:

```python
await client.geocode("Prague", use_cache=False)
```

---

## 🧪 Testing

Install dev dependencies:

```bash
pip install pytest pytest-asyncio
```

Run tests:

```bash
pytest
```

---

## 🛠 Development

To build and publish:

```bash
python -m build
twine upload dist/*
```

Or trigger CI/CD by pushing a tag:

```bash
git tag v0.1.0
git push --tags
```

---

## 📄 License

MIT License © 2025 Czech Fabric

---

## 🤝 Contributing

Issues and PRs welcome!