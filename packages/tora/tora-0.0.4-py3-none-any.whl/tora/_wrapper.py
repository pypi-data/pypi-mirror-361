import logging
from typing import Union

from ._client import Tora

__all__ = ["setup", "tlog"]


logger = logging.getLogger("tora")
_CLIENT = None


def _get_client() -> Tora:
    if _CLIENT is None:
        raise ValueError("Tora client not initialized")
    return _CLIENT


def setup(
    name: str,
    workspace_id: str | None = None,
    description: str | None = None,
    hyperparams: dict | None = None,
    tags: list[str] | None = None,
    api_key: str | None = None,
):
    global _CLIENT
    _CLIENT = Tora.create_experiment(
        name,
        workspace_id,
        description,
        hyperparams,
        tags,
        api_key=api_key,
        max_buffer_len=1,
    )
    print(
        "https://tora-web-1030250455947.us-central1.run.app/experiments/"
        + _CLIENT._experiment_id
    )


def tlog(
    name: str, value: Union[str, float, int], step: int, metadata: dict | None = None
):
    _get_client().log(name, value, step, metadata)
