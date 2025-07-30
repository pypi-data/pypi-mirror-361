"""
Tora Python SDK - ML Experiment Tracking

A Python SDK for the Tora ML experiment tracking platform.
Provides easy-to-use APIs for logging metrics, managing experiments,
and tracking machine learning workflows.

Example:
    >>> import tora
    >>>
    >>> # Create an experiment
    >>> client = tora.Tora.create_experiment(
    ...     name="my-experiment",
    ...     workspace_id="workspace-123"
    ... )
    >>>
    >>> # Log metrics
    >>> client.log("accuracy", 0.95, step=100)
    >>> client.log("loss", 0.05, step=100)
    >>>
    >>> # Ensure all metrics are sent
    >>> client.shutdown()
"""

from ._client import Tora, create_workspace
from ._exceptions import (
    ToraAPIError,
    ToraAuthenticationError,
    ToraConfigurationError,
    ToraError,
    ToraExperimentError,
    ToraMetricError,
    ToraNetworkError,
    ToraTimeoutError,
    ToraValidationError,
    ToraWorkspaceError,
)
from ._wrapper import (
    flush,
    get_experiment_id,
    get_experiment_url,
    is_initialized,
    setup,
    shutdown,
    tlog,
)

__version__ = "0.0.5"

__all__ = [
    # Main classes
    "Tora",
    "create_workspace",
    # Convenience functions
    "setup",
    "tlog",
    "flush",
    "shutdown",
    "is_initialized",
    "get_experiment_id",
    "get_experiment_url",
    # Exceptions
    "ToraError",
    "ToraAPIError",
    "ToraAuthenticationError",
    "ToraConfigurationError",
    "ToraExperimentError",
    "ToraMetricError",
    "ToraNetworkError",
    "ToraTimeoutError",
    "ToraValidationError",
    "ToraWorkspaceError",
]
