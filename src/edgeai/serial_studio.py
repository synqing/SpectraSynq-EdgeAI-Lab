"""Read-only Serial Studio integration for Edge-AI laboratory tooling.

This module deliberately exposes no device-write operation. Serial Studio is an
observability sidecar here; an authoritative command/reply probe must first take
exclusive ownership of the target USB-CDC interface.
"""

from __future__ import annotations

import json
import socket
import time
from dataclasses import dataclass
from typing import Any


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 7777

_READ_COMMANDS = frozenset(
    {
        "project.source.list",
        "project.source.getConfig",
        "dashboard.getStatus",
        "dashboard.getData",
        "io.getStatus",
        "io.getLatestFrame",
        "sessions.getStatus",
    }
)


class SerialStudioError(RuntimeError):
    """Raised when the local Serial Studio read API cannot satisfy a request."""


@dataclass(frozen=True, slots=True)
class SourceRxSnapshot:
    """Latest receive-health facts reported for one configured source."""

    source_id: str
    source_title: str
    source_status: dict[str, Any]
    latest_frame: dict[str, Any]

    @property
    def age_ms(self) -> float | None:
        value = self.latest_frame.get("ageMs")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
        return None


class SerialStudioReadClient:
    """Small allow-listed client for Serial Studio's localhost JSON API."""

    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        *,
        timeout_s: float = 1.0,
    ) -> None:
        if host not in {"127.0.0.1", "::1", "localhost"}:
            raise ValueError("Serial Studio API host must be loopback")
        self.host = host
        self.port = int(port)
        self.timeout_s = float(timeout_s)
        self._socket: socket.socket | None = None
        self._reader: Any = None
        self._request_id = 0

    def connect(self) -> None:
        if self._socket is not None:
            return
        try:
            connection = socket.create_connection(
                (self.host, self.port), timeout=self.timeout_s
            )
            connection.settimeout(self.timeout_s)
            self._socket = connection
            self._reader = connection.makefile("rb")
        except OSError as error:
            self.close()
            raise SerialStudioError(
                f"Serial Studio API unavailable at {self.host}:{self.port}: {error}"
            ) from error

    def close(self) -> None:
        reader, connection = self._reader, self._socket
        self._reader = None
        self._socket = None
        if reader is not None:
            try:
                reader.close()
            except OSError:
                pass
        if connection is not None:
            try:
                connection.close()
            except OSError:
                pass

    def __enter__(self) -> "SerialStudioReadClient":
        self.connect()
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def list_sources(self) -> list[dict[str, Any]]:
        result = self._request("project.source.list")
        if isinstance(result, list):
            return [item for item in result if isinstance(item, dict)]
        if isinstance(result, dict):
            sources = result.get("sources")
            if isinstance(sources, list):
                return [item for item in sources if isinstance(item, dict)]
        raise SerialStudioError("project.source.list returned no source list")

    def dashboard_status(self) -> dict[str, Any]:
        return self._mapping_request("dashboard.getStatus")

    def source_config(self, source_id: str) -> dict[str, Any]:
        return self._mapping_request(
            "project.source.getConfig", {"sourceId": _source_param(source_id)}
        )

    def dashboard_data(self) -> dict[str, Any]:
        return self._mapping_request("dashboard.getData")

    def io_status(self, source_id: str) -> dict[str, Any]:
        return self._mapping_request("io.getStatus", {"sourceId": _source_param(source_id)})

    def latest_frame(self, source_id: str) -> dict[str, Any]:
        return self._mapping_request("io.getLatestFrame", {"sourceId": _source_param(source_id)})

    def sessions_status(self) -> dict[str, Any]:
        return self._mapping_request("sessions.getStatus")

    def source_rx_snapshot(
        self, source_id: str, source_title: str = ""
    ) -> SourceRxSnapshot:
        return SourceRxSnapshot(
            source_id=source_id,
            source_title=source_title,
            source_status=self.io_status(source_id),
            latest_frame=self.latest_frame(source_id),
        )

    def _mapping_request(
        self, method: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        result = self._request(method, params)
        if not isinstance(result, dict):
            raise SerialStudioError(f"{method} returned a non-object result")
        return result

    def _request(
        self, method: str, params: dict[str, Any] | None = None
    ) -> Any:
        if method not in _READ_COMMANDS:
            raise SerialStudioError(f"Serial Studio method is not read-allow-listed: {method}")
        self.connect()
        if self._socket is None:
            raise SerialStudioError("Serial Studio API socket was not established")

        self._request_id += 1
        request: dict[str, Any] = {
            "type": "command",
            "id": str(self._request_id),
            "command": method,
            "params": params or {},
        }
        payload = json.dumps(request, separators=(",", ":")).encode("utf-8") + b"\n"
        try:
            self._socket.sendall(payload)
            response = self._read_matching_response(request["id"])
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            self.close()
            raise SerialStudioError(f"Serial Studio API request failed: {error}") from error

        if not isinstance(response, dict):
            raise SerialStudioError("Serial Studio API returned a non-object response")
        if response.get("type") != "response":
            raise SerialStudioError(f"Serial Studio API returned an unexpected message type")
        if response.get("id") != request["id"]:
            raise SerialStudioError("Serial Studio API response id did not match the request")
        if response.get("success") is not True:
            raise SerialStudioError(
                f"Serial Studio API rejected {method}: {response.get('error', 'unknown error')}"
            )
        return response.get("result", {})

    def _read_matching_response(self, request_id: str) -> dict[str, Any]:
        """Demultiplex one command response from unsolicited stream messages.

        Serial Studio pushes parsed frames, raw data, and lifecycle events to
        every connected API client. Those messages may arrive between a command
        write and its response, so treating the next line as the response makes
        a live long-lived client fail as soon as telemetry is flowing.
        """

        if self._socket is None:
            raise SerialStudioError("Serial Studio API socket was not established")
        deadline = time.monotonic() + self.timeout_s
        try:
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError("timed out waiting for command response")
                self._socket.settimeout(remaining)
                message = json.loads(self._readline().decode("utf-8"))
                if not isinstance(message, dict):
                    raise SerialStudioError(
                        "Serial Studio API returned a non-object response"
                    )
                if _is_push_message(message):
                    continue
                if message.get("type") != "response":
                    raise SerialStudioError(
                        "Serial Studio API returned an unexpected message type"
                    )
                if message.get("id") != request_id:
                    raise SerialStudioError(
                        "Serial Studio API response id did not match the request"
                    )
                return message
        finally:
            if self._socket is not None:
                self._socket.settimeout(self.timeout_s)

    def _readline(self) -> bytes:
        if self._reader is None:
            raise SerialStudioError("Serial Studio API reader was not established")
        line = self._reader.readline()
        if not line:
            self.close()
            raise SerialStudioError("Serial Studio API closed the connection")
        return line


def api_up(
    host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, *, timeout_s: float = 0.25
) -> bool:
    """Return whether Serial Studio's loopback API accepts a read request."""

    try:
        with SerialStudioReadClient(host, port, timeout_s=timeout_s) as client:
            client.dashboard_status()
    except (SerialStudioError, ValueError):
        return False
    return True


def source_id_for(sources: list[dict[str, Any]], identity: str) -> str:
    """Resolve exactly one configured source by title, id, port, or device path."""

    matches: list[str] = []
    for source in sources:
        source_id = source.get("id") or source.get("sourceId")
        if not isinstance(source_id, (str, int)):
            continue
        searchable = {
            str(source_id),
            str(source.get("title", "")),
            str(source.get("name", "")),
            str(source.get("port", "")),
            str(source.get("device", "")),
        }
        if identity in searchable:
            matches.append(str(source_id))
    unique = sorted(set(matches))
    if len(unique) != 1:
        raise SerialStudioError(
            f"Expected one Serial Studio source for {identity!r}, found {len(unique)}"
        )
    return unique[0]


def holder_is_serial_studio(holder: str | None) -> bool:
    """Recognise a process description as Serial Studio ownership evidence."""

    return bool(holder and "serial studio" in holder.casefold())


def _source_param(source_id: str | int) -> str | int:
    """Keep source IDs numeric on Serial Studio's typed command surface."""

    if isinstance(source_id, str) and source_id.isdecimal():
        return int(source_id)
    return source_id


def _is_push_message(message: dict[str, Any]) -> bool:
    """Recognise the three documented Serial Studio server-push shapes."""

    return any(key in message for key in ("frames", "data", "event"))


def refuse_if_serial_studio_owns_usb(holder: str | None, device: str) -> None:
    """Refuse an exclusive probe while Serial Studio owns the target interface."""

    if holder_is_serial_studio(holder):
        raise SerialStudioError(
            f"Serial Studio owns {device}; release it before authoritative command/reply work"
        )
