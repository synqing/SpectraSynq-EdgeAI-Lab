"""Tests for the read-only Serial Studio integration boundary."""

from __future__ import annotations

import json
import socket
import threading
import time
from collections.abc import Callable

import pytest

from edgeai.serial_studio import (
    SerialStudioError,
    SerialStudioReadClient,
    api_up,
    holder_is_serial_studio,
    refuse_if_serial_studio_owns_usb,
    source_id_for,
)


def _start_server(
    responder: Callable[[dict], dict], seen: list[dict]
) -> tuple[int, threading.Thread]:
    port_box: list[int] = []

    def serve() -> None:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        port_box.append(server.getsockname()[1])
        connection, _ = server.accept()
        buffer = b""
        try:
            while True:
                chunk = connection.recv(65536)
                if not chunk:
                    break
                buffer += chunk
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    request = json.loads(line)
                    seen.append(request)
                    response = responder(request)
                    connection.sendall(json.dumps(response).encode() + b"\n")
        finally:
            connection.close()
            server.close()

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    for _ in range(100):
        if port_box:
            return port_box[0], thread
        time.sleep(0.005)
    raise AssertionError("test server did not bind")


def _success(request: dict, result: object) -> dict:
    return {
        "type": "response",
        "id": request["id"],
        "success": True,
        "result": result,
    }


def test_client_only_emits_read_allowlisted_commands() -> None:
    seen: list[dict] = []
    replies = {
        "project.source.list": {
            "sources": [
                {"sourceId": 0, "title": "K1 Bench B489A500"},
                {"sourceId": 1, "title": "K1 Main 9087A500"},
            ]
        },
        "dashboard.getStatus": {"active": True},
        "dashboard.getData": {"groups": []},
        "io.getStatus": {"connected": True},
        "io.getLatestFrame": {"hasData": True, "ageMs": 17},
        "sessions.getStatus": {"enabled": True},
    }
    port, thread = _start_server(
        lambda request: _success(request, replies[request["command"]]), seen
    )

    with SerialStudioReadClient(port=port, timeout_s=1) as client:
        assert len(client.list_sources()) == 2
        assert client.dashboard_status()["active"] is True
        assert client.dashboard_data() == {"groups": []}
        snapshot = client.source_rx_snapshot("1", "Main")
        assert snapshot.age_ms == 17
        assert client.sessions_status()["enabled"] is True

    thread.join(timeout=1)
    commands = [request["command"] for request in seen]
    assert commands == [
        "project.source.list",
        "dashboard.getStatus",
        "dashboard.getData",
        "io.getStatus",
        "io.getLatestFrame",
        "sessions.getStatus",
    ]
    assert all(request["type"] == "command" for request in seen)
    assert not any("write" in command.casefold() for command in commands)


def test_private_request_rejects_a_write_before_connecting() -> None:
    client = SerialStudioReadClient(port=1)
    with pytest.raises(SerialStudioError, match="not read-allow-listed"):
        client._request("io.writeData", {"data": "forbidden"})


def test_client_rejects_non_loopback_api_host() -> None:
    with pytest.raises(ValueError, match="loopback"):
        SerialStudioReadClient("192.0.2.10")


def test_client_surfaces_server_refusal() -> None:
    seen: list[dict] = []
    port, thread = _start_server(
        lambda request: {
            "type": "response",
            "id": request["id"],
            "success": False,
            "error": {"code": "EXECUTION_ERROR", "message": "no project"},
        },
        seen,
    )
    with SerialStudioReadClient(port=port, timeout_s=1) as client:
        with pytest.raises(SerialStudioError, match="no project"):
            client.dashboard_status()
    thread.join(timeout=1)


def test_source_identity_requires_exactly_one_match() -> None:
    sources = [
        {"sourceId": 0, "title": "K1 Bench B489A500"},
        {"sourceId": 1, "title": "K1 Main 9087A500"},
    ]
    assert source_id_for(sources, "K1 Main 9087A500") == "1"
    assert source_id_for(sources, "0") == "0"
    with pytest.raises(SerialStudioError, match="found 0"):
        source_id_for(sources, "unknown")


def test_api_up_false_on_closed_port() -> None:
    assert api_up(port=1) is False


def test_usb_ownership_guard_uses_process_identity() -> None:
    assert holder_is_serial_studio("/Applications/Serial Studio.app/Contents/MacOS/Serial Studio")
    assert not holder_is_serial_studio("screen /dev/cu.usbmodem101")
    refuse_if_serial_studio_owns_usb("screen", "/dev/cu.usbmodem101")
    with pytest.raises(SerialStudioError, match="release it"):
        refuse_if_serial_studio_owns_usb("Serial Studio", "/dev/cu.usbmodem101")
