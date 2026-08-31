"""Serial Studio TCP bus (localhost:7777).

Serial Studio is the K1 observe/record instrument (dashboard, Historian, CSV).
It is not cadence transport authority. Silicon command paths use pyserial after
Serial Studio has released the USB ports. Do not steal usbmodem while it is open.

The k1_gate shuttle on :7777 is demoted. Cadence must refuse Serial-Studio-owned
USB rather than write through the control loop.
"""

from __future__ import annotations

import base64
import json
import socket
import time
import uuid
from pathlib import Path
from typing import Any

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 7777
MAIN_TITLE = "K1 Main RPL 9087A500"
BENCH_TITLE = "K1 Bench B489A500"
GATE_TABLE = "k1_gate"
PROFILE_OBSERVE = "OBSERVE"
PROFILE_GATE = "GATE"
# :chip_id prints 8-hex chip id (utilities.h print_chip_id), wrapped by sbr{{ / }}.
# Not the word "CHIP". Main RPL unit id is 9087A500.
CHIP_ID_MARKER = "9087A500"
CHIP_ID_ENVELOPE = "sbr{{"
_LAB_ROOT = Path(__file__).resolve().parents[2]
SHUTTLE_ROUNDTRIP_RECEIPT = (
    _LAB_ROOT / "artifacts" / "serial_studio" / "MAIN_RPL_SHUTTLE_ROUNDTRIP.json"
)
TIMER_OFF = 0
TIMER_AUTOSTART = 1
POLL_INTERVAL_MS = 250
RTRACE_END = "[RTRACE-END]"
PRSM_MAGIC = b"PRSM"


class SerialStudioError(RuntimeError):
    pass


class SerialStudioBus:
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, timeout: float = 5.0) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self._sock: socket.socket | None = None
        self._buf = b""

    def connect(self) -> None:
        if self._sock is not None:
            return
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(self.timeout)
        s.connect((self.host, self.port))
        self._sock = s
        self._buf = b""

    def close(self) -> None:
        if self._sock is not None:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None
        self._buf = b""

    def __enter__(self) -> SerialStudioBus:
        self.connect()
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def command(self, name: str, params: dict[str, Any] | None = None, timeout: float | None = None) -> dict[str, Any]:
        if self._sock is None:
            raise SerialStudioError("not connected to Serial Studio API")
        req_id = str(uuid.uuid4())
        msg: dict[str, Any] = {"type": "command", "id": req_id, "command": name}
        if params:
            msg["params"] = params
        self._sock.sendall((json.dumps(msg, separators=(",", ":")) + "\n").encode("utf-8"))
        deadline = time.time() + (timeout or self.timeout)
        while True:
            remaining = deadline - time.time()
            if remaining <= 0:
                raise TimeoutError(f"Serial Studio timeout on {name}")
            line = self._readline(remaining)
            if not line:
                continue
            try:
                resp = json.loads(line)
            except json.JSONDecodeError:
                continue
            if resp.get("type") != "response" or resp.get("id") != req_id:
                continue
            if resp.get("success"):
                result = resp.get("result")
                return result if isinstance(result, dict) else {"value": result}
            err = resp.get("error") or {}
            raise SerialStudioError(f"{err.get('code', 'ERR')}: {err.get('message', name)}")

    def _readline(self, remaining: float) -> str:
        assert self._sock is not None
        end = time.time() + remaining
        while True:
            nl = self._buf.find(b"\n")
            if nl != -1:
                raw = self._buf[:nl]
                self._buf = self._buf[nl + 1 :]
                return raw.decode("utf-8", "replace")
            if time.time() >= end:
                return ""
            self._sock.settimeout(max(0.05, end - time.time()))
            try:
                chunk = self._sock.recv(65536)
            except TimeoutError:
                continue
            except socket.timeout:
                continue
            if not chunk:
                raise SerialStudioError("Serial Studio API closed")
            self._buf += chunk


def holder_is_serial_studio(dev: str) -> bool:
    """True when Serial Studio already has the USB-CDC device open."""
    import subprocess

    r = subprocess.run(["lsof", "-n", "-P", dev], capture_output=True, text=True, timeout=3)
    blob = (r.stdout or "") + (r.stderr or "")
    return "Serial-St" in blob or "Serial Studio" in blob


def refuse_if_serial_studio_owns_usb(port: str) -> None:
    """Exclusive-port rule (D19): silicon command/reply owns the CDC; SS must release first."""
    if holder_is_serial_studio(port):
        raise SerialStudioError(
            "SERIAL_STUDIO_NOT_TRANSPORT: Serial Studio holds this USB port. "
            "Close Serial Studio. Cadence uses pyserial. "
            "Do not multiplex two owners on one CDC. Do not steal usbmodem."
        )


def shuttle_roundtrip_proven() -> bool:
    """True only after a PASS receipt for the Main RPL :chip_id shuttle.

    Cadence does not wait on this. The shuttle is demoted (D19).
    """
    path = SHUTTLE_ROUNDTRIP_RECEIPT
    if not path.is_file():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return False
    return data.get("MAIN_RPL_SHUTTLE_ROUNDTRIP") == "PASS"


def api_up(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.4)
    try:
        s.connect((host, port))
        return True
    except OSError:
        return False
    finally:
        s.close()


def source_id_for(sources: list[dict[str, Any]], *, title_substr: str) -> int | None:
    needle = title_substr.lower()
    for src in sources:
        title = str(src.get("title") or "")
        if needle in title.lower():
            return int(src["sourceId"])
    return None


def _gate_register_names(bus: SerialStudioBus) -> set[str]:
    try:
        info = bus.command("project.dataTable.get", {"name": GATE_TABLE})
    except SerialStudioError:
        return set()
    names: set[str] = set()
    for reg in info.get("registers") or []:
        n = str(reg.get("name") or "")
        if n:
            names.add(n)
    return names


def ensure_gate(bus: SerialStudioBus) -> None:
    listed = json.dumps(bus.command("project.dataTable.list"))
    if GATE_TABLE not in listed:
        bus.command("project.dataTable.add", {"name": GATE_TABLE})
    have = _gate_register_names(bus)
    for reg, default in (
        ("tx", ""),
        ("source", 1),
        ("mode", PROFILE_OBSERVE),
        ("last_error", ""),
        ("last_reply", ""),
    ):
        if reg in have:
            continue
        try:
            bus.command(
                "project.dataTable.addRegister",
                {"table": GATE_TABLE, "name": reg, "computed": True, "defaultValue": default},
            )
        except SerialStudioError:
            pass


def prune_gate_aliases(bus: SerialStudioBus) -> list[str]:
    """Drop accidental tx_2 / source_2 duplicates from a naive addRegister retry."""
    removed: list[str] = []
    for name in sorted(_gate_register_names(bus)):
        if name in ("tx", "source", "mode"):
            continue
        if name.startswith(("tx_", "source_", "mode_")):
            try:
                bus.command("project.dataTable.deleteRegister", {"table": GATE_TABLE, "name": name})
                removed.append(name)
            except SerialStudioError:
                pass
    return removed


def ensure_control_loop(bus: SerialStudioBus, code: str | None = None) -> dict[str, Any]:
    st = bus.command("controlScript.getStatus")
    if st.get("running"):
        return st
    if code is None:
        code = Path(
            "/Users/spectrasynq/Serial-Studio/examples/K1 Dual UART/k1_gate_loop.js"
        ).read_text()
    # controlScript.set is a no-op when the source is identical, and a
    # stopped-after-error loop will not restart on its own.
    code = code.rstrip() + f"\n// restart {int(time.time())}\n"
    return install_gate_loop(bus, code)


def _tx_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value == 0.0:
        return ""
    if isinstance(value, int) and value == 0:
        return ""
    return str(value).strip()


def wait_tx_clear(bus: SerialStudioBus, timeout_s: float = 1.0) -> None:
    """The control loop copies k1_gate.tx then clears it. Do not overwrite a live tx."""
    deadline = time.time() + timeout_s
    last = ""
    while time.time() < deadline:
        got = bus.command("project.dataTable.getValue", {"table": GATE_TABLE, "name": "tx"})
        last = _tx_text(got.get("value"))
        if not last:
            return
        time.sleep(0.004)
    st = bus.command("controlScript.getStatus")
    raise SerialStudioError(
        f"k1_gate.tx was not consumed (running={st.get('running')} leftover={last[:80]!r})"
    )


def send_line(bus: SerialStudioBus, text: str, *, source_id: int) -> None:
    """Queue a typed serial line for the control loop to emit on source_id."""
    if not text.endswith("\n"):
        text = text + "\n"
    ensure_gate(bus)
    ensure_control_loop(bus)
    leftover = _tx_text(
        bus.command("project.dataTable.getValue", {"table": GATE_TABLE, "name": "tx"}).get("value")
    )
    if leftover:
        time.sleep(0.12)
        leftover = _tx_text(
            bus.command("project.dataTable.getValue", {"table": GATE_TABLE, "name": "tx"}).get(
                "value"
            )
        )
        if leftover:
            bus.command("project.dataTable.setValue", {"table": GATE_TABLE, "name": "tx", "value": ""})
            time.sleep(0.05)
    bus.command("project.dataTable.setValue", {"table": GATE_TABLE, "name": "source", "value": int(source_id)})
    bus.command("project.dataTable.setValue", {"table": GATE_TABLE, "name": "tx", "value": text})
    # Control loop uses deviceWriteAndWait (up to 1.5 s for :chip_id/:dump).
    time.sleep(1.7)


def write_source0(bus: SerialStudioBus, text: str) -> dict[str, Any]:
    """Direct write — TCP io.writeData always hits source 0 (bench). Do not use for Main RPL."""
    payload = base64.b64encode(text.encode("utf-8")).decode("ascii")
    return bus.command("io.writeData", {"data": payload})


def collect_frames(
    bus: SerialStudioBus,
    *,
    source_id: int,
    until: str,
    timeout_s: float,
    dropped: list[int] | None = None,
) -> str:
    """Poll io.getLatestFrame for new lines. Parser-ignored rtrace lines still have .text.

    io.getLatestFrame retains one frame per source. Sequence gaps are drops, not silence.
    Large rtrace dumps must use SerialStudioPort (console export harvest), not this helper.
    """
    buf: list[str] = []
    last_seq = -1
    n_drop = 0
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        frame = bus.command(
            "io.getLatestFrame",
            {"sourceId": int(source_id), "encoding": "text"},
            timeout=1.0,
        )
        seq = int(frame.get("sequence") or 0)
        text = str(frame.get("text") or "")
        if frame.get("hasData") and seq != last_seq and text:
            if last_seq >= 0 and seq > last_seq + 1:
                n_drop += seq - last_seq - 1
            last_seq = seq
            buf.append(text if text.endswith("\n") else text + "\n")
            if until in text:
                break
        time.sleep(0.004)
    if dropped is not None:
        dropped.append(n_drop)
    return "".join(buf)


def install_gate_loop(bus: SerialStudioBus, code: str) -> dict[str, Any]:
    dry = bus.command("controlScript.dryRun", {"code": code})
    if dry.get("valid") is False:
        raise SerialStudioError(f"control script invalid: {dry}")
    return bus.command("controlScript.set", {"code": code})


def _poll_action_ids(bus: SerialStudioBus) -> list[int]:
    listed = bus.command("project.action.list")
    out: list[int] = []
    for act in listed.get("actions") or []:
        title = str(act.get("title") or "")
        if title.lower().startswith("poll "):
            out.append(int(act["actionId"]))
    return out


def _export_actions(bus: SerialStudioBus) -> list[dict[str, Any]]:
    exported = bus.command("project.exportJson")
    cfg = exported.get("config")
    if isinstance(cfg, str):
        cfg = json.loads(cfg)
    if not isinstance(cfg, dict):
        return []
    acts = cfg.get("actions") or []
    return acts if isinstance(acts, list) else []


def set_profile(bus: SerialStudioBus, profile: str) -> dict[str, Any]:
    """OBSERVE: 250 ms poll actions on. GATE: polls off, console export on.

    GATE must not add per-frame device printf. It only silences Serial Studio's
    own timers so a silicon run is not competing with :event_status/:fps.
    """
    name = profile.strip().upper()
    if name not in (PROFILE_OBSERVE, PROFILE_GATE):
        raise SerialStudioError(f"unknown profile {profile!r}")
    ensure_gate(bus)
    ids = _poll_action_ids(bus)
    if name == PROFILE_GATE:
        timer = TIMER_OFF
        interval = POLL_INTERVAL_MS
        bus.command("consoleExport.setEnabled", {"enabled": True})
    else:
        timer = TIMER_AUTOSTART
        interval = POLL_INTERVAL_MS
        try:
            bus.command("consoleExport.setEnabled", {"enabled": False})
        except SerialStudioError:
            pass
    for action_id in ids:
        bus.command(
            "project.action.update",
            {"actionId": action_id, "timerMode": timer, "timerIntervalMs": interval},
        )
    try:
        bus.command("project.dataTable.setValue", {"table": GATE_TABLE, "name": "mode", "value": name})
    except SerialStudioError:
        pass
    modes = []
    for a in _export_actions(bus):
        tm = a.get("timerMode")
        modes.append(int(tm) if tm is not None else -1)
    return {"profile": name, "poll_action_ids": ids, "timer_modes": modes}


def console_export_dir(project_title: str) -> Path:
    return Path.home() / "Documents" / "Serial Studio" / "Console" / project_title


def newest_console_log(*, source_id: int, newer_than: float) -> Path | None:
    title = ""
    try:
        # Best-effort; callers may pass a glob root instead.
        pass
    except Exception:
        title = ""
    roots = [
        Path.home() / "Documents" / "Serial Studio" / "Console",
        Path.home() / "Documents" / "Serial-Studio" / "Console",
    ]
    newest: Path | None = None
    newest_mtime = newer_than
    needle = f"_device{int(source_id)}"
    for root in roots:
        if not root.is_dir():
            continue
        for path in root.rglob("*.txt"):
            if needle not in path.name and source_id != 0:
                continue
            try:
                mtime = path.stat().st_mtime
            except OSError:
                continue
            if mtime >= newest_mtime and (newest is None or mtime >= newest_mtime):
                if mtime >= newer_than - 1.0:
                    newest = path
                    newest_mtime = mtime
    _ = title
    return newest


class SerialStudioPort:
    """pyserial-shaped shim so C0-v2 / cadence can keep cmd()/dump_rtrace().

    Writes go through k1_gate (never io.writeData). Reads poll io.getLatestFrame.
    Large dumps: io.getLatestFrame is one-frame-deep, so a sequence gap is a
    drop. After :rtrace_dump the shim waits for [RTRACE-END] then splices the
    console-export file (every RX chunk) if GATE enabled it.
    """

    def __init__(self, bus: SerialStudioBus, *, source_id: int, port: str = "serial-studio:7777") -> None:
        self.bus = bus
        self.source_id = int(source_id)
        self.port = port
        self.timeout = 0.2
        self.write_timeout = 1.0
        self.dropped_sequences = 0
        self._rx = bytearray()
        self._last_seq = -1
        self._dump_armed = False
        self._dump_t0 = 0.0

    def write(self, data: bytes | str) -> int:
        raw = data.encode("ascii") if isinstance(data, str) else bytes(data)
        if raw.startswith(PRSM_MAGIC):
            raise SerialStudioError(
                "binary PRSM cannot go through k1_gate (string table). "
                "C0-v2 uses :c0_hex text. Do not reopen the two-clock runner."
            )
        text = raw.decode("utf-8")
        if ":rtrace_dump" in text:
            self._dump_armed = True
            self._dump_t0 = time.time()
        send_line(self.bus, text, source_id=self.source_id)
        return len(raw)

    def flush(self) -> None:
        wait_tx_clear(self.bus, timeout_s=1.0)

    def reset_input_buffer(self) -> None:
        self._rx.clear()
        try:
            frame = self.bus.command(
                "io.getLatestFrame",
                {"sourceId": self.source_id, "encoding": "text"},
                timeout=1.0,
            )
            if frame.get("hasData"):
                self._last_seq = int(frame.get("sequence") or 0)
        except (SerialStudioError, TimeoutError):
            pass

    def read(self, size: int = 1) -> bytes:
        if size <= 0:
            return b""
        deadline = time.time() + max(self.timeout, 0.0)
        while len(self._rx) < size and time.time() <= deadline:
            self._pump()
            if self._dump_armed and RTRACE_END.encode("ascii") in self._rx:
                self._harvest_console()
                self._dump_armed = False
                break
            if not self._rx:
                time.sleep(0.002)
        n = min(size, len(self._rx))
        out = bytes(self._rx[:n])
        del self._rx[:n]
        return out

    def close(self) -> None:
        self.bus.close()

    def _pump(self) -> None:
        try:
            frame = self.bus.command(
                "io.getLatestFrame",
                {"sourceId": self.source_id, "encoding": "text"},
                timeout=1.0,
            )
        except (SerialStudioError, TimeoutError):
            return
        if not frame.get("hasData"):
            return
        seq = int(frame.get("sequence") or 0)
        text = str(frame.get("text") or "")
        if not text or seq == self._last_seq:
            return
        if self._last_seq >= 0 and seq > self._last_seq + 1:
            self.dropped_sequences += seq - self._last_seq - 1
        self._last_seq = seq
        blob = text if text.endswith("\n") else text + "\n"
        self._rx.extend(blob.encode("utf-8", "replace"))

    def _harvest_console(self) -> None:
        """Splice console-export RX (chunked, not latest-only) if GATE armed it."""
        time.sleep(0.35)
        try:
            self.bus.command("consoleExport.close", {})
        except SerialStudioError:
            pass
        log = newest_console_log(source_id=self.source_id, newer_than=self._dump_t0 - 2.0)
        if log is None or not log.is_file():
            return
        try:
            text = log.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return
        if RTRACE_END not in text and "[RTRACE-BEGIN" not in text:
            return
        # Console files may stamp lines. Keep payload lines the dump decoder understands.
        keep: list[str] = []
        for line in text.splitlines():
            s = line
            if " -> " in s:
                s = s.split(" -> ", 1)[-1]
            keep.append(s)
        joined = "\n".join(keep) + "\n"
        self._rx = bytearray(joined.encode("utf-8", "replace"))
        try:
            self.bus.command("consoleExport.setEnabled", {"enabled": True})
        except SerialStudioError:
            pass


def open_k1_serial(
    port: str,
    *,
    source_title: str = MAIN_TITLE,
    profile: str = PROFILE_GATE,
) -> Any:
    """Legacy :7777 shuttle opener. Cadence must not call this (D19)."""
    if holder_is_serial_studio(port) and not api_up():
        raise SerialStudioError(
            "Serial Studio holds USB but API :7777 is down. Enable API & Plugins."
        )
    if api_up():
        bus = SerialStudioBus()
        bus.connect()
        sources = bus.command("project.source.list").get("sources") or []
        sid = source_id_for(sources, title_substr=source_title)
        if sid is None:
            bus.close()
            raise SerialStudioError(f"source {source_title!r} not in project")
        prune_gate_aliases(bus)
        ensure_control_loop(bus)
        set_profile(bus, profile)
        return SerialStudioPort(bus, source_id=sid, port=port)
    import serial

    s = serial.Serial()
    s.port = port
    s.baudrate = 115200
    s.timeout = 0.2
    s.write_timeout = 1.0
    s.dtr = True
    s.rts = False
    s.open()
    time.sleep(0.35)
    s.reset_input_buffer()
    return s
