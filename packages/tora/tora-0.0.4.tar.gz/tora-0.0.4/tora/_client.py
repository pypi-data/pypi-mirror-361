import logging
from typing import Any, Mapping, Optional

from ._config import TORA_API_KEY, TORA_BASE_URL
from ._http import HttpClient, HTTPStatusError
from ._types import HPValue

__all__ = ["Tora", "create_workspace"]

logger = logging.getLogger("tora")


def _to_tora_hp(hp: Mapping[str, HPValue]) -> list[dict[str, HPValue]]:
    return [{"key": k, "value": v} for k, v in hp.items()]


def _from_tora_hp(tora_hp: list[dict[str, Any]]) -> dict[str, HPValue]:
    return {item["key"]: item["value"] for item in tora_hp}


def create_workspace(
    name: str,
    description: Optional[str] = None,
    api_key: Optional[str] = None,
    server_url: str | None = None,
) -> dict[str, Any]:
    """
    Creates a new Tora workspace. Requires an API key.

    Args:
        name: The name for the new workspace.
        description: An optional description for the workspace.
        server_url: The base URL of the Tora server.

    Returns:
        The full JSON response for the newly created workspace.

    Raises:
        HTTPStatusError: If the API request fails.
    """
    server_url = server_url or TORA_BASE_URL
    resolved_api_key = api_key or TORA_API_KEY
    if not resolved_api_key:
        raise RuntimeWarning("API key is required to create a workspace")

    headers = {
        "x-api-key": resolved_api_key,
        "Content-Type": "application/json",
    }
    with HttpClient(base_url=server_url, headers=headers) as client:
        req = client.post(
            "/workspaces", json={"name": name, "description": description}
        )
        try:
            req.raise_for_status()
            return req.json()["data"]
        except Exception as e:
            print(req.status_code)
            logger.exception(e)
            raise e


class Tora:
    def __init__(
        self,
        experiment_id: str,
        description: str | None = None,
        hyperparams: Mapping[str, HPValue] | None = None,
        tags: list[str] | None = None,
        max_buffer_len: int = 25,
        api_key: str | None = None,
        server_url: str | None = None,
    ):
        self._experiment_id = experiment_id
        self._description = description
        self._hyperparams = hyperparams
        self.tags = tags
        self._max_buffer_len = max_buffer_len
        self._buffer = []
        self._api_key = api_key or TORA_API_KEY

        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["x-api-key"] = self._api_key

        server_url = server_url or TORA_BASE_URL
        self._http_client = HttpClient(
            base_url=server_url or TORA_BASE_URL, headers=headers
        )

    @staticmethod
    def _get_api_key(api_key: str | None) -> str | None:
        """Helper to resolve API key from param or environment."""
        key = api_key or TORA_API_KEY
        if key is None:
            logger.warning("Tora API key not provided. Operating in anonymous mode.")
        return key

    @classmethod
    def create_experiment(
        cls,
        name: str,
        workspace_id: str | None = None,
        description: str | None = None,
        hyperparams: Mapping[str, HPValue] | None = None,
        tags: list[str] | None = None,
        max_buffer_len: int = 25,
        api_key: str | None = None,
        server_url: str | None = None,
    ) -> "Tora":
        """
        An API key is required to create an experiment in a specific workspace
        """
        resolved_api_key = Tora._get_api_key(api_key)
        data = cls._create_payload(name, workspace_id, description, hyperparams, tags)
        server_url = server_url or TORA_BASE_URL
        url_path = "/experiments"
        headers = {"Content-Type": "application/json"}
        if resolved_api_key:
            headers["x-api-key"] = resolved_api_key

        with HttpClient(base_url=server_url, headers=headers) as client:
            print(data)
            req = client.post(url_path, json=data)
            req.raise_for_status()
            res = req.json()
            experiment_id = res["data"]["id"]

        return cls(
            experiment_id=experiment_id,
            description=description,
            hyperparams=hyperparams,
            tags=tags,
            server_url=server_url,
            max_buffer_len=max_buffer_len,
            api_key=resolved_api_key,
        )

    @classmethod
    def _create_payload(
        cls,
        name: str,
        workspace_id: str | None,
        description: str | None,
        hyperparams: Mapping[str, HPValue] | None,
        tags: list[str] | None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {"name": name}
        if workspace_id:
            data["workspace_id"] = workspace_id
        if description:
            data["description"] = description
        if hyperparams:
            data["hyperparams"] = _to_tora_hp(hyperparams)
        if tags:
            data["tags"] = tags
        return data

    @classmethod
    def load_experiment(
        cls,
        experiment_id: str,
        max_buffer_len: int = 25,
        api_key: str | None = None,
        server_url: str | None = None,
    ) -> "Tora":
        """
        Loads an existing experiment and returns a Tora instance to interact with it.
        """
        server_url = server_url or TORA_BASE_URL
        resolved_api_key = Tora._get_api_key(api_key)

        headers = {}
        if resolved_api_key:
            headers["x-api-key"] = resolved_api_key

        with HttpClient(base_url=server_url, headers=headers) as client:
            req = client.get(f"/experiments/{experiment_id}")
            req.raise_for_status()
            data = req.json()

        hyperparams = (
            _from_tora_hp(data["hyperparams"]) if data.get("hyperparams") else None
        )

        return cls(
            experiment_id=data["id"],
            description=data.get("description"),
            hyperparams=hyperparams,
            tags=data.get("tags"),
            max_buffer_len=max_buffer_len,
            api_key=resolved_api_key,
            server_url=server_url,
        )

    def log(
        self,
        name: str,
        value: Any,
        step: int | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        """
        Logs a metric. Metrics are buffered and sent in batches. Specified by max_buffer_len.
        """
        log_entry = {"name": name, "value": value, "step": step, "metadata": metadata}
        self._buffer.append(log_entry)

        if len(self._buffer) >= self._max_buffer_len:
            self._write_logs()

    def _write_logs(self) -> None:
        if not self._buffer:
            return

        try:
            print(self._experiment_id)

            req = self._http_client.post(
                f"/experiments/{self._experiment_id}/metrics/batch",
                json={"metrics": self._buffer},
                timeout=120,
            )
            req.raise_for_status()
            self._buffer = []
        except HTTPStatusError as e:
            logger.error(
                f"Failed to write Tora logs. Status: {e.response.status_code}. Response: {e.response.text}"
            )
        except Exception as e:
            logger.error(f"An unexpected error occurred while writing Tora logs: {e}")

    def shutdown(self) -> None:
        """
        Ensures all buffered logs are sent before the program exits.
        """
        if self._buffer:
            logger.info(
                f"Tora shutting down. Sending {len(self._buffer)} remaining logs..."
            )
            self._write_logs()
        self._http_client.close()

    @property
    def max_buffer_len(self) -> int:
        return self._max_buffer_len

    @max_buffer_len.setter
    def max_buffer_len(self, value: int):
        self._max_buffer_len = int(value)

    def __enter__(self):
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager, ensuring logs are flushed."""
        self.shutdown()
