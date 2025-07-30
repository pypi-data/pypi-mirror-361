import atexit
import logging

from ._client import Tora
from ._exceptions import ToraError
from ._types import HPValue, MetricMetadata

__all__ = [
    "flush",
    "get_experiment_id",
    "get_experiment_url",
    "is_initialized",
    "setup",
    "shutdown",
    "tlog",
]

logger = logging.getLogger("tora")
_CLIENT: Tora | None = None


def _get_client() -> Tora:
    """Get the global client instance."""
    if _CLIENT is None:
        raise ToraError("Tora client not initialized. Call tora.setup() first.")
    return _CLIENT


def setup(
    name: str,
    workspace_id: str | None = None,
    description: str | None = None,
    hyperparams: dict[str, HPValue] | None = None,
    tags: list[str] | None = None,
    api_key: str | None = None,
    server_url: str | None = None,
    max_buffer_len: int = 1,
) -> str:
    """Set up the global Tora client with a new experiment.

    This creates a new experiment and initializes the global client.
    After calling this function, you can use tlog() to log metrics.

    Args:
        name: Name of the experiment
        workspace_id: ID of the workspace to create the experiment in
        description: Optional description of the experiment
        hyperparams: Optional hyperparameters for the experiment
        tags: Optional list of tags for the experiment
        api_key: API key for authentication. Uses TORA_API_KEY env var if not
            provided
        server_url: Base URL for the Tora API. Uses TORA_BASE_URL env var if not
            provided
        max_buffer_len: Maximum number of metrics to buffer before sending
            (default: 1 for immediate sending)

    Returns:
        The experiment ID of the created experiment

    Raises:
        ToraError: If setup fails or client is already initialized
        ToraValidationError: If input validation fails
        ToraAuthenticationError: If authentication fails
        ToraAPIError: If the API request fails
        ToraNetworkError: If there's a network error

    """
    global _CLIENT
    if _CLIENT is not None:
        raise ToraError("Tora client already initialized. Call shutdown() first to reinitialize.")

    try:
        _CLIENT = Tora.create_experiment(
            name=name,
            workspace_id=workspace_id,
            description=description,
            hyperparams=hyperparams,
            tags=tags,
            api_key=api_key,
            server_url=server_url,
            max_buffer_len=max_buffer_len,
        )
        atexit.register(shutdown)
        experiment_url = f"https://tora-web-1030250455947.us-central1.run.app/experiments/{_CLIENT.experiment_id}"
        logger.info(f"Tora experiment created: {experiment_url}")
        print(f"Tora experiment: {experiment_url}")
        return _CLIENT.experiment_id

    except Exception:
        _CLIENT = None
        raise


def tlog(
    name: str,
    value: int | float,
    step: int | None = None,
    metadata: MetricMetadata | None = None,
) -> None:
    """Log a metric using the global Tora client.

    Args:
        name: Name of the metric
        value: Numeric value of the metric
        step: Optional step number for the metric
        metadata: Optional metadata dictionary for the metric

    Raises:
        ToraError: If the global client is not initialized
        ToraValidationError: If input validation fails
        ToraMetricError: If logging fails

    """
    client = _get_client()
    client.log(name, value, step, metadata)


def flush() -> None:
    """Flush all buffered metrics using the global client.

    Raises:
        ToraError: If the global client is not initialized

    """
    if _CLIENT is not None:
        _CLIENT.flush()


def shutdown() -> None:
    """Shutdown the global Tora client and flush all metrics.

    After calling this function, you need to call setup() again
    to reinitialize the client.
    """
    global _CLIENT
    if _CLIENT is not None:
        try:
            _CLIENT.shutdown()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        finally:
            _CLIENT = None


def is_initialized() -> bool:
    """Check if the global Tora client is initialized.

    Returns:
        True if the client is initialized, False otherwise

    """
    return _CLIENT is not None and not _CLIENT.is_closed


def get_experiment_id() -> str | None:
    """Get the experiment ID of the global client.

    Returns:
        The experiment ID if initialized, None otherwise

    """
    if _CLIENT is not None and not _CLIENT.is_closed:
        return _CLIENT.experiment_id
    return None


def get_experiment_url() -> str | None:
    """Get the web URL for the current experiment.

    Returns:
        The experiment URL if initialized, None otherwise

    """
    experiment_id = get_experiment_id()
    if experiment_id:
        return f"https://tora-web-1030250455947.us-central1.run.app/experiments/{experiment_id}"
    return None
