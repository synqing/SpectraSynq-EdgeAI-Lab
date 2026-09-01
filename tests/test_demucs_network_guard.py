"""The Demucs network tripwire must go red before any downloader can run."""

from __future__ import annotations

import socket
import sys
import types
import urllib.request

import pytest

from edgeai.mir.demucs_network_guard import (
    DemucsNetworkForbidden,
    demucs_network_forbidden,
)


def test_socket_connect_and_create_connection_go_red() -> None:
    with demucs_network_forbidden():
        with pytest.raises(DemucsNetworkForbidden, match="DEMUCS_NETWORK_FORBIDDEN"):
            socket.socket().connect(("127.0.0.1", 9))
        with pytest.raises(DemucsNetworkForbidden, match="DEMUCS_NETWORK_FORBIDDEN"):
            socket.create_connection(("127.0.0.1", 9))


def test_socket_sendto_goes_red_before_a_packet_leaves() -> None:
    with demucs_network_forbidden(), socket.socket(
        socket.AF_INET, socket.SOCK_DGRAM
    ) as udp:
        with pytest.raises(DemucsNetworkForbidden, match="socket.socket.sendto"):
            udp.sendto(b"fake-model-request", ("127.0.0.1", 9))


def test_urllib_fake_download_goes_red(monkeypatch) -> None:
    def escaped(*_args, **_kwargs):
        raise AssertionError("urllib escaped the Demucs network guard")

    monkeypatch.setattr(urllib.request, "urlopen", escaped)
    with demucs_network_forbidden():
        with pytest.raises(DemucsNetworkForbidden, match="urllib.request.urlopen"):
            urllib.request.urlopen("https://example.invalid/fake-model")


def test_requests_and_hub_fake_downloads_go_red(monkeypatch) -> None:
    def escaped(*_args, **_kwargs):
        raise AssertionError("downloader escaped the Demucs network guard")

    class FakeSession:
        request = escaped

    requests = types.ModuleType("requests")
    requests.request = escaped
    requests.get = escaped
    requests.sessions = types.SimpleNamespace(Session=FakeSession)
    hub = types.ModuleType("huggingface_hub")
    hub.hf_hub_download = escaped
    hub.snapshot_download = escaped
    hub_file = types.ModuleType("huggingface_hub.file_download")
    hub_file.hf_hub_download = escaped
    hub_file.get_hf_file_metadata = escaped
    monkeypatch.setitem(sys.modules, "requests", requests)
    monkeypatch.setitem(sys.modules, "huggingface_hub", hub)
    monkeypatch.setitem(sys.modules, "huggingface_hub.file_download", hub_file)

    with demucs_network_forbidden():
        with pytest.raises(DemucsNetworkForbidden, match="requests.get"):
            requests.get("https://example.invalid/fake-model")
        with pytest.raises(DemucsNetworkForbidden, match="huggingface_hub.hf_hub_download"):
            hub.hf_hub_download("fake/repo", "model")
        with pytest.raises(
            DemucsNetworkForbidden,
            match="huggingface_hub.file_download.get_hf_file_metadata",
        ):
            hub_file.get_hf_file_metadata("https://example.invalid/fake-model")


def test_torch_hub_fake_download_goes_red(monkeypatch) -> None:
    import torch.hub

    def escaped(*_args, **_kwargs):
        raise AssertionError("torch.hub escaped the Demucs network guard")

    monkeypatch.setattr(torch.hub, "load_state_dict_from_url", escaped)
    with demucs_network_forbidden():
        with pytest.raises(DemucsNetworkForbidden, match="torch.hub.load_state_dict"):
            torch.hub.load_state_dict_from_url("https://example.invalid/fake-model")
