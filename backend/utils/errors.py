"""Nexus error hierarchy."""
from datetime import datetime
from typing import Any, Optional

import structlog

logger = structlog.get_logger()


class NexusError(Exception):
    def __init__(
        self,
        message: str,
        agent_id: Optional[str] = None,
        recoverable: bool = True,
        **kwargs: Any,
    ):
        super().__init__(message)
        self.message = message
        self.agent_id = agent_id
        self.recoverable = recoverable
        self.timestamp = datetime.utcnow()
        self.extra = kwargs
        logger.warning("nexus_error", message=message, agent_id=agent_id, **kwargs)


class AgentError(NexusError):
    pass


class LLMError(AgentError):
    def __init__(self, message: str, model: str = "", retry_count: int = 0, **kwargs: Any):
        super().__init__(message, **kwargs)
        self.model = model
        self.retry_count = retry_count


class TimeoutError(AgentError):
    def __init__(self, message: str, elapsed_seconds: float = 0, **kwargs: Any):
        super().__init__(message, **kwargs)
        self.elapsed_seconds = elapsed_seconds


class SchemaError(AgentError):
    def __init__(self, message: str, field_errors: Optional[list] = None, **kwargs: Any):
        super().__init__(message, **kwargs)
        self.field_errors = field_errors or []


class ConnectorError(NexusError):
    pass


class AuthError(ConnectorError):
    def __init__(self, message: str, source_name: str = "", **kwargs: Any):
        super().__init__(message, **kwargs)
        self.source_name = source_name


class DataError(ConnectorError):
    def __init__(self, message: str, source_name: str = "", raw_error: str = "", **kwargs: Any):
        super().__init__(message, **kwargs)
        self.source_name = source_name
        self.raw_error = raw_error


class SchemaDriftError(ConnectorError):
    pass


class RateLimitError(ConnectorError):
    pass


class MemoryError(NexusError):
    pass


class StorageError(MemoryError):
    pass
