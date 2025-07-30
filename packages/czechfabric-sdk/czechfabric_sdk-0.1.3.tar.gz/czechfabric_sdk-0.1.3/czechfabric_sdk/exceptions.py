class CzechFabricError(Exception):
    """Base exception for all SDK errors."""


class InvalidAPIKeyError(CzechFabricError):
    """Invalid or unauthorized API key."""


class RateLimitExceededError(CzechFabricError):
    """Rate limit exceeded."""


class ToolExecutionError(CzechFabricError):
    """Generic tool execution failure."""


class NetworkError(CzechFabricError):
    """Networking-related error."""
