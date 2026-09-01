"""Process-local egress denial for the bounded Demucs HOST probe.

Install this guard before importing Demucs. Environment flags remain useful,
but the patched connection and downloader surfaces are the enforcement layer.
"""

from __future__ import annotations

import importlib
import os
import socket
import urllib.request
from contextlib import ExitStack, contextmanager
from typing import Callable, Iterator
from unittest.mock import patch

ERROR_CODE = "DEMUCS_NETWORK_FORBIDDEN"


class DemucsNetworkForbidden(RuntimeError):
    """Raised before a guarded network or downloader call can leave the process."""


def _deny(surface: str) -> Callable[..., None]:
    def denied(*_args, **_kwargs) -> None:
        raise DemucsNetworkForbidden(f"{ERROR_CODE}: {surface}")

    return denied


def _patch_if_present(stack: ExitStack, target: object, name: str, surface: str) -> None:
    if hasattr(target, name):
        stack.enter_context(patch.object(target, name, _deny(surface)))


def _optional_module(name: str):
    try:
        return importlib.import_module(name)
    except ImportError:
        return None


@contextmanager
def demucs_network_forbidden() -> Iterator[None]:
    """Deny sockets and known downloader entry points until the context exits."""
    offline_values = {
        "HF_HUB_OFFLINE": "1",
        "TRANSFORMERS_OFFLINE": "1",
        "PIP_NO_INDEX": "1",
    }
    previous = {name: os.environ.get(name) for name in offline_values}
    os.environ.update(offline_values)

    try:
        with ExitStack() as stack:
            # Patch sockets first. Optional downloader imports happen only after
            # arbitrary connection attempts are already impossible.
            stack.enter_context(
                patch.object(socket.socket, "connect", _deny("socket.socket.connect"))
            )
            stack.enter_context(
                patch.object(socket.socket, "connect_ex", _deny("socket.socket.connect_ex"))
            )
            stack.enter_context(
                patch.object(socket, "create_connection", _deny("socket.create_connection"))
            )
            for name in ("send", "sendall", "sendto", "sendmsg"):
                _patch_if_present(stack, socket.socket, name, f"socket.socket.{name}")
            stack.enter_context(
                patch.object(urllib.request, "urlopen", _deny("urllib.request.urlopen"))
            )
            stack.enter_context(
                patch.object(
                    urllib.request, "urlretrieve", _deny("urllib.request.urlretrieve")
                )
            )
            stack.enter_context(
                patch.object(
                    urllib.request.OpenerDirector,
                    "open",
                    _deny("urllib.request.OpenerDirector.open"),
                )
            )

            requests = _optional_module("requests")
            if requests is not None:
                for name in ("request", "get", "post", "put", "patch", "delete", "head"):
                    _patch_if_present(stack, requests, name, f"requests.{name}")
                sessions = getattr(requests, "sessions", None)
                session_class = getattr(sessions, "Session", None)
                if session_class is not None:
                    _patch_if_present(
                        stack, session_class, "request", "requests.Session.request"
                    )

            hub = _optional_module("huggingface_hub")
            if hub is not None:
                for name in ("hf_hub_download", "snapshot_download"):
                    _patch_if_present(stack, hub, name, f"huggingface_hub.{name}")
            hub_file_download = _optional_module("huggingface_hub.file_download")
            if hub_file_download is not None:
                for name in ("hf_hub_download", "get_hf_file_metadata"):
                    _patch_if_present(
                        stack,
                        hub_file_download,
                        name,
                        f"huggingface_hub.file_download.{name}",
                    )

            torch_hub = _optional_module("torch.hub")
            if torch_hub is not None:
                for name in ("load", "load_state_dict_from_url", "download_url_to_file"):
                    _patch_if_present(stack, torch_hub, name, f"torch.hub.{name}")

            yield
    finally:
        for name, value in previous.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
