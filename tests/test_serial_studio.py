"""Serial Studio TCP helpers. Cadence does not use the :7777 shuttle (D19)."""

from __future__ import annotations

import json
import socket
import threading
import time

from edgeai.serial_studio import (
    MAIN_TITLE,
    PRSM_MAGIC,
    PROFILE_GATE,
    SerialStudioBus,
    SerialStudioError,
    SerialStudioPort,
    api_up,
    collect_frames,
    refuse_if_serial_studio_owns_usb,
    send_line,
    set_profile,
    source_id_for,
)


def _serve(replies: dict[str, dict], port_holder: list[int]) -> None:
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", 0))
    srv.listen(1)
    port_holder.append(srv.getsockname()[1])
    port_holder.append(1)  # ready
    conn, _ = srv.accept()
    buf = b""
    try:
        while True:
            chunk = conn.recv(65536)
            if not chunk:
                break
            buf += chunk
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                req = json.loads(line.decode())
                cmd = req["command"]
                body = replies.get(cmd, {})
                resp = {"type": "response", "id": req["id"], "success": True, "result": body}
                conn.sendall((json.dumps(resp) + "\n").encode())
    finally:
        conn.close()
        srv.close()


def test_source_id_maps_main_rpl_not_bench():
    sources = [
        {"sourceId": 0, "title": "K1 Bench B489A500"},
        {"sourceId": 1, "title": "K1 Main RPL 9087A500"},
    ]
    assert source_id_for(sources, title_substr="9087A500") == 1
    assert source_id_for(sources, title_substr="B489A500") == 0
    assert source_id_for(sources, title_substr=MAIN_TITLE) == 1


def test_send_line_sets_gate_table_not_io_write_data():
    seen: list[dict] = []

    def serve() -> None:
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(("127.0.0.1", 0))
        port_box.append(srv.getsockname()[1])
        srv.listen(1)
        conn, _ = srv.accept()
        buf = b""
        try:
            while True:
                chunk = conn.recv(65536)
                if not chunk:
                    break
                buf += chunk
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    req = json.loads(line.decode())
                    seen.append(req)
                    conn.sendall(
                        (
                            json.dumps(
                                {
                                    "type": "response",
                                    "id": req["id"],
                                    "success": True,
                                    "result": {"tables": [{"name": "k1_gate"}]},
                                }
                            )
                            + "\n"
                        ).encode()
                    )
        finally:
            conn.close()
            srv.close()

    port_box: list[int] = []
    t = threading.Thread(target=serve, daemon=True)
    t.start()
    for _ in range(50):
        if port_box:
            break
        time.sleep(0.01)
    bus = SerialStudioBus(port=port_box[0], timeout=2)
    bus.connect()
    send_line(bus, ":c0_status=1", source_id=1)
    bus.close()
    cmds = [r["command"] for r in seen]
    assert "io.writeData" not in cmds
    sets = [r for r in seen if r["command"] == "project.dataTable.setValue"]
    assert any(r["params"]["name"] == "source" and r["params"]["value"] == 1 for r in sets)
    assert any(r["params"]["name"] == "tx" and ":c0_status=1" in str(r["params"]["value"]) for r in sets)


def test_collect_frames_joins_new_sequences_until_marker():
    frames = [
        {"hasData": True, "sequence": 1, "text": "F,0,1,18,aa\n"},
        {"hasData": True, "sequence": 2, "text": "[RTRACE-END]\n"},
    ]
    idx = {"i": 0}

    def serve() -> None:
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(("127.0.0.1", 0))
        port_box.append(srv.getsockname()[1])
        srv.listen(1)
        conn, _ = srv.accept()
        buf = b""
        try:
            while True:
                chunk = conn.recv(65536)
                if not chunk:
                    break
                buf += chunk
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    req = json.loads(line.decode())
                    fr = frames[min(idx["i"], len(frames) - 1)]
                    idx["i"] += 1
                    conn.sendall(
                        (
                            json.dumps(
                                {
                                    "type": "response",
                                    "id": req["id"],
                                    "success": True,
                                    "result": fr,
                                }
                            )
                            + "\n"
                        ).encode()
                    )
        finally:
            conn.close()
            srv.close()

    port_box: list[int] = []
    t = threading.Thread(target=serve, daemon=True)
    t.start()
    for _ in range(50):
        if port_box:
            break
        time.sleep(0.01)
    bus = SerialStudioBus(port=port_box[0], timeout=2)
    bus.connect()
    text = collect_frames(bus, source_id=1, until="[RTRACE-END]", timeout_s=2)
    bus.close()
    assert "F,0,1,18,aa" in text
    assert "[RTRACE-END]" in text


def test_api_up_false_on_closed_port():
    assert api_up(port=1) is False


def test_refuse_if_serial_studio_owns_usb_allows_unowned_path():
    refuse_if_serial_studio_owns_usb("/dev/does-not-exist-ss-refuse-test")


def test_collect_frames_counts_sequence_gaps():
    frames = [
        {"hasData": True, "sequence": 1, "text": "A\n"},
        {"hasData": True, "sequence": 4, "text": "END\n"},
    ]
    idx = {"i": 0}

    def serve() -> None:
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(("127.0.0.1", 0))
        port_box.append(srv.getsockname()[1])
        srv.listen(1)
        conn, _ = srv.accept()
        buf = b""
        try:
            while True:
                chunk = conn.recv(65536)
                if not chunk:
                    break
                buf += chunk
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    req = json.loads(line.decode())
                    fr = frames[min(idx["i"], len(frames) - 1)]
                    idx["i"] += 1
                    conn.sendall(
                        (
                            json.dumps(
                                {
                                    "type": "response",
                                    "id": req["id"],
                                    "success": True,
                                    "result": fr,
                                }
                            )
                            + "\n"
                        ).encode()
                    )
        finally:
            conn.close()
            srv.close()

    port_box: list[int] = []
    t = threading.Thread(target=serve, daemon=True)
    t.start()
    for _ in range(50):
        if port_box:
            break
        time.sleep(0.01)
    bus = SerialStudioBus(port=port_box[0], timeout=2)
    bus.connect()
    dropped: list[int] = []
    text = collect_frames(bus, source_id=1, until="END", timeout_s=2, dropped=dropped)
    bus.close()
    assert "A" in text and "END" in text
    assert dropped and dropped[0] == 2


def test_port_refuses_binary_prsm():
    port = SerialStudioPort(SerialStudioBus(), source_id=1)
    try:
        port.write(PRSM_MAGIC + b"\x00" * 30)
        raise AssertionError("expected SerialStudioError")
    except SerialStudioError as e:
        assert "PRSM" in str(e)


def test_set_profile_gate_turns_poll_timers_off():
    seen: list[dict] = []

    def serve() -> None:
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(("127.0.0.1", 0))
        port_box.append(srv.getsockname()[1])
        srv.listen(1)
        conn, _ = srv.accept()
        buf = b""
        try:
            while True:
                chunk = conn.recv(65536)
                if not chunk:
                    break
                buf += chunk
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    req = json.loads(line.decode())
                    seen.append(req)
                    cmd = req["command"]
                    if cmd == "project.action.list":
                        body = {
                            "actions": [
                                {"actionId": 0, "title": "Poll B489A500"},
                                {"actionId": 1, "title": "Poll 9087A500"},
                            ]
                        }
                    elif cmd == "project.exportJson":
                        body = {
                            "config": {
                                "actions": [
                                    {"actionId": 0, "timerMode": 0, "title": "Poll B489A500"},
                                    {"actionId": 1, "timerMode": 0, "title": "Poll 9087A500"},
                                ]
                            }
                        }
                    else:
                        body = {"tables": [{"name": "k1_gate"}]}
                    conn.sendall(
                        (
                            json.dumps(
                                {
                                    "type": "response",
                                    "id": req["id"],
                                    "success": True,
                                    "result": body,
                                }
                            )
                            + "\n"
                        ).encode()
                    )
        finally:
            conn.close()
            srv.close()

    port_box: list[int] = []
    t = threading.Thread(target=serve, daemon=True)
    t.start()
    for _ in range(50):
        if port_box:
            break
        time.sleep(0.01)
    bus = SerialStudioBus(port=port_box[0], timeout=2)
    bus.connect()
    info = set_profile(bus, PROFILE_GATE)
    bus.close()
    updates = [r for r in seen if r["command"] == "project.action.update"]
    assert len(updates) == 2
    assert all(r["params"]["timerMode"] == 0 for r in updates)
    assert info["profile"] == "GATE"
