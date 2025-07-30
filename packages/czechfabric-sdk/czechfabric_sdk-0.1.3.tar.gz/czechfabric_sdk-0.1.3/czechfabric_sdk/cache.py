from async_lru import alru_cache

@alru_cache(maxsize=256)
async def cache_tool_call(tool_name: str, params: tuple):
    """
    Decorator-compatible cache for tool calls.
    """
    # In practice, the SDK will call this indirectly
    pass
