"""
Type definitions for the Tora SDK.

This module contains type aliases and protocol definitions used throughout
the Tora SDK for better type safety and documentation.
"""

from typing import Any, Dict, List, Optional, Protocol, Union

try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict

# Hyperparameter value types
HPValue = Union[str, float, int]

# Metric metadata type
MetricMetadata = Dict[str, Any]


# API response types
class ExperimentResponse(TypedDict, total=False):
    """Type definition for experiment API response."""

    id: str
    name: str
    description: Optional[str]
    hyperparams: List[Dict[str, Any]]
    tags: List[str]
    created_at: str
    updated_at: str
    available_metrics: List[str]
    workspace_id: Optional[str]


class MetricResponse(TypedDict):
    """Type definition for metric API response."""

    id: int
    experiment_id: str
    name: str
    value: float
    step: Optional[int]
    metadata: Optional[Dict[str, Any]]
    created_at: str


class WorkspaceResponse(TypedDict, total=False):
    """Type definition for workspace API response."""

    id: str
    name: str
    description: Optional[str]
    created_at: str
    updated_at: str


class APIResponse(TypedDict):
    """Generic API response wrapper."""

    status: int
    data: Any


# Configuration types
class ToraConfig(TypedDict, total=False):
    """Configuration options for Tora client."""

    api_key: Optional[str]
    base_url: Optional[str]
    timeout: Optional[int]
    max_retries: Optional[int]
    retry_delay: Optional[float]
    debug: Optional[bool]


# Protocol for HTTP client interface
class HTTPClient(Protocol):
    """Protocol for HTTP client implementations."""

    def get(self, path: str, headers: Optional[Dict[str, str]] = None) -> Any:
        """Send GET request."""
        ...

    def post(
        self,
        path: str,
        json: Optional[Any] = None,
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Any:
        """Send POST request."""
        ...

    def close(self) -> None:
        """Close the client."""
        ...


# Callback protocol for metric logging
class MetricCallback(Protocol):
    """Protocol for metric logging callbacks."""

    def __call__(
        self,
        name: str,
        value: Union[int, float],
        step: Optional[int] = None,
        metadata: Optional[MetricMetadata] = None,
    ) -> None:
        """Log a metric."""
        ...
