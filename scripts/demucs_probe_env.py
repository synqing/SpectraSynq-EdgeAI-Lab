#!/usr/bin/env python3
"""Build the ignored Demucs probe venv exclusively from SHA-pinned local wheels.

This script never resolves against an index and never touches pyproject.toml or
uv.lock. Cache bodies are validated as wheels, renamed in an ignored wheelhouse,
then installed into artifacts/demucs_host/.probe_venv/ with PIP_NO_INDEX=1.
"""

from __future__ import annotations

import argparse
import email
import hashlib
import json
import os
import re
import shutil
import subprocess
import zipfile
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = ROOT / "artifacts/demucs_host"
DEFAULT_VENV = ARTIFACT_ROOT / ".probe_venv"
DEFAULT_WHEELHOUSE = ARTIFACT_ROOT / "wheelhouse"
DEFAULT_RECEIPT = ROOT / "docs/mir/receipts/demucs/J2_ENV.json"
BASE_PYTHON = Path(
    "/Users/spectrasynq/miniforge3/envs/trinity-music-intent-v0_1/bin/python"
)


class WheelPin(NamedTuple):
    project: str
    version: str
    cache_body: str
    sha256: str


WHEELS = (
    WheelPin("demucs", "4.1.0", "/Users/spectrasynq/Library/Caches/pip/http-v2/d/0/3/1/4/d031491481c0ce1d27f83219ea9af10a18fb8ee603c137911f20f616.body", "4916a804702033ce934a6cdfa7e38dde03f7a7a6e85f41d0120eefe9e2966758"),
    WheelPin("einops", "0.7.0", "/Users/spectrasynq/Library/Caches/pip/http-v2/f/7/4/8/a/f748afc33325b676a0c9b7aa3572935f1d86e264e124386e2e05e9cd.body", "0f3096f26b914f465f6ff3c66f5478f9a5e380bb367ffc6493a68143fbbf1fd1"),
    WheelPin("huggingface-hub", "0.36.2", "/Users/spectrasynq/Library/Caches/pip/http-v2/4/2/d/0/6/42d06d173e1f82d3695859a85244d3309fb98847555c9651a4b30d5a.body", "48f0c8eac16145dfce371e9d2d7772854a4f591bcb56c9cf548accf531d54270"),
    WheelPin("julius", "0.2.8", "/Users/spectrasynq/Library/Caches/pip/http-v2/6/6/f/9/e/66f9ea72656a4f5b9bbf96a1c427422fb8f82acf3a18cbe27923cce1.body", "6891235cbc355e629d839f87489bff8ca46e57a0e7cc35abb909c7a2aa538c25"),
    WheelPin("lameenc", "1.8.4", "/Users/spectrasynq/Library/Caches/pip/http-v2/d/e/4/7/5/de47593c2d247bbc2427d634f73275f4988043c32ca230cb642e6043.body", "abedb78eebd63a226d1fdf8c75c2cb0d1b4df3d1227585e3e8d5f6b9cff22cb2"),
    WheelPin("PyYAML", "6.0.3", "/Users/spectrasynq/Library/Caches/pip/http-v2/d/f/8/1/8/df81886714b54404e117f63ef5cc13e3f49981e19471f28dabd1ec77.body", "652cb6edd41e718550aad172851962662ff2681490a8a711af6a4d288dd96824"),
    WheelPin("safetensors", "0.7.0", "/Users/spectrasynq/Library/Caches/pip/http-v2/3/c/1/b/3/3c1b329d5f269d0f1b3b8d95accafcb70401ae364f74a1646ad52ce2.body", "94fd4858284736bb67a897a41608b5b0c2496c9bdb3bf2af1fa3409127f20d57"),
    WheelPin("sphn", "0.2.1", "/Users/spectrasynq/Library/Caches/pip/http-v2/6/8/2/2/8/68228ef029e762d4b9c10712afe3e7d22d98fff2f3cf7e088d3d8025.body", "a2238bcb66c21322ddc4a9308d7fbd4903175951ee4357cad8056c5e371e447f"),
    WheelPin("torch", "2.2.2", "/Users/spectrasynq/Library/Caches/pip/http-v2/7/7/6/a/1/776a1b4291c31ce5eb486fa4642c564d61d2f16a668987ff1d0744a3.body", "49aa4126ede714c5aeef7ae92969b4b0bbe67f19665106463c39f22e0a1860d1"),
    WheelPin("tqdm", "4.67.3", "/Users/spectrasynq/Library/Caches/pip/http-v2/3/7/c/5/1/37c518ffee828550acec5a0fd158a5f1d852928eea13df9d077b428b.body", "ee1e4c0e59148062281c49d80b25b67771a127c85fc9676d3be5f243206826bf"),
    WheelPin("numpy", "1.26.4", "/Users/spectrasynq/Library/Caches/pip/http-v2/e/d/2/3/7/ed23775a5844ad74465b9f8aac1fc0e0509ca784db0b56a938ef1fd6.body", "edd8b5fe47dab091176d21bb6de568acdd906d1887a4584a15a9a96a1dca06ef"),
    WheelPin("filelock", "3.19.1", "/Users/spectrasynq/Library/Caches/pip/http-v2/0/3/9/d/b/039db589a9fd13ac2a4a1b65e6cfb6e24eac0b4306b13a37c92afbfa.body", "d38e30481def20772f5baf097c122c3babc4fcdb7e14e57049eb9d88c6dc017d"),
    WheelPin("typing-extensions", "4.15.0", "/Users/spectrasynq/Library/Caches/pip/http-v2/e/0/b/4/f/e0b4f4d1d5b8bb8b844f230fb9255eeabd73b4bd6598e826c4219d4f.body", "f0fa19c6845758ab08074a0cfa8b7aecb71c999ca73d62883bc25cc018c4e548"),
    WheelPin("sympy", "1.14.0", "/Users/spectrasynq/Library/Caches/pip/http-v2/a/7/0/9/4/a7094ed5a4cc16f47a5321a9f38285921c17bacfd72d0b4f42bc4cf5.body", "e091cc3e99d2141a0ba2847328f5479b05d94a6635cb96148ccb3f34671bd8f5"),
    WheelPin("networkx", "3.2.1", "/Users/spectrasynq/Library/Caches/pip/http-v2/e/1/0/6/c/e106c860fe66155447d95810c58ecc3a39b35b2ed9285340d276f297.body", "f18c69adc97877c42332c170849c96cefa91881c99a7cb3e95b7c659ebdc1ec2"),
    WheelPin("Jinja2", "3.1.6", "/Users/spectrasynq/Library/Caches/pip/http-v2/0/6/7/d/e/067de891d4624fc09de1c690b01d8bf477f69f0ce81f8101b21b3549.body", "85ece4451f492d0c13c5dd7c13a64681a86afae63a5f347908daf103ce6d2f67"),
    WheelPin("fsspec", "2025.10.0", "/Users/spectrasynq/Library/Caches/pip/http-v2/d/5/d/7/a/d5d7ae30e479ef0cba1bee19d33976732745ef5c16715f9ac3ccf779.body", "7c7712353ae7d875407f97715f0e1ffcc21e33d5b24556cb1e090ae9409ec61d"),
    WheelPin("mpmath", "1.3.0", "/Users/spectrasynq/Library/Caches/pip/http-v2/3/d/2/3/a/3d23a5ad548471fdadffd54fe2363185ef4648db7c0bf11d16c83f16.body", "a0b2b9fe80bbcd81a6647ff13108738cfb482d481d826cc0e02f5b35e5c88d2c"),
    WheelPin("MarkupSafe", "3.0.3", "/Users/spectrasynq/Library/Caches/pip/http-v2/b/3/8/f/1/b38f100ba5b2312fcdf7e3b0ba0daa4b7072c1f9148fb6cd366bb77d.body", "4bd4cd07944443f5a265608cc6aab442e4f74dff8088b0dfc8238647b8f6ae9a"),
    WheelPin("packaging", "25.0", "/Users/spectrasynq/Library/Caches/pip/http-v2/7/b/6/b/b/7b6bbe6761c4b96a22fceae90ae94b84afddc06ce20edb28bf2eaf86.body", "29572ef2b1f17581046b3a2227d5c611fb25ec70ca1ba8554b24b0e69331a484"),
    WheelPin("requests", "2.32.5", "/Users/spectrasynq/Library/Caches/pip/http-v2/0/7/5/4/6/0754653d3535372fb243dff0d5ea56432167ba71b1cd19ce67d1cc3c.body", "2462f94637a34fd532264295e186976db0f5d453d1cdd31473c85a6a161affb6"),
    WheelPin("hf-xet", "1.4.3", "/Users/spectrasynq/Library/Caches/pip/http-v2/4/a/4/2/e/4a42ef9536da2ca92aac7d301e95a0d2815a7516cb325bd17cecb120.body", "e23717ce4186b265f69afa66e6f0069fe7efbf331546f5c313d00e123dc84583"),
    WheelPin("charset-normalizer", "3.4.7", "/Users/spectrasynq/Library/Caches/pip/http-v2/5/5/c/7/4/55c746dc83348d0c40c9f086a27bfa46d4b2ae97139df40f9fd93387.body", "7641bb8895e77f921102f72833904dcd9901df5d6d72a2ab8f31d04b7e51e4e7"),
    WheelPin("idna", "3.13", "/Users/spectrasynq/Library/Caches/pip/http-v2/a/c/b/4/e/acb4e40f64eef2a73d680e437d7e413b10909b60941ff39f0528cce7.body", "892ea0cde124a99ce773decba204c5552b69c3c67ffd5f232eb7696135bc8bb3"),
    WheelPin("urllib3", "2.6.3", "/Users/spectrasynq/Library/Caches/pip/http-v2/8/8/f/0/6/88f06a944c734c3736badbb02d887cddfeb74de4f837c06db79e749c.body", "bf272323e553dfb2e87d9bfd225ca7b0f467b919d7bbd355436d3fd37cb0acd4"),
    WheelPin("certifi", "2026.4.22", "/Users/spectrasynq/Library/Caches/pip/http-v2/4/7/7/4/2/47742615f5189ebbf61bb31c8c50f7f39cc38c5173f10ec7146e3989.body", "3cb2210c8f88ba2318d29b0388d1023c8492ff72ecdde4ebdaddbb13a31b1c4a"),
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_project(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def wheel_identity(path: Path) -> tuple[str, str, str]:
    with zipfile.ZipFile(path) as archive:
        metadata_name = next(
            name for name in archive.namelist() if name.endswith(".dist-info/METADATA")
        )
        wheel_name = next(
            name for name in archive.namelist() if name.endswith(".dist-info/WHEEL")
        )
        metadata = email.message_from_bytes(archive.read(metadata_name))
        wheel = archive.read(wheel_name).decode("utf-8")
    tags = [line.split(": ", 1)[1] for line in wheel.splitlines() if line.startswith("Tag: ")]
    if len(tags) != 1:
        raise RuntimeError(f"expected one wheel tag in {path}, got {tags}")
    return metadata["Name"], metadata["Version"], tags[0]


def materialise_wheel(pin: WheelPin, wheelhouse: Path) -> dict[str, str]:
    source = Path(pin.cache_body)
    if not source.is_file():
        raise RuntimeError(f"LOCAL_WHEEL_MISSING: {pin.project} {pin.version}")
    actual_sha = sha256_file(source)
    if actual_sha != pin.sha256:
        raise RuntimeError(f"LOCAL_WHEEL_SHA256_MISMATCH: {pin.project}")
    project, version, tag = wheel_identity(source)
    if canonical_project(project) != canonical_project(pin.project) or version != pin.version:
        raise RuntimeError(
            f"LOCAL_WHEEL_IDENTITY_MISMATCH: expected {pin.project} {pin.version}, "
            f"got {project} {version}"
        )
    filename_project = re.sub(r"[-_.]+", "_", project)
    destination = wheelhouse / f"{filename_project}-{version}-{tag}.whl"
    if destination.exists() and sha256_file(destination) != pin.sha256:
        raise RuntimeError(f"WHEELHOUSE_SHA256_MISMATCH: {destination}")
    if not destination.exists():
        shutil.copyfile(source, destination)
    return {
        "project": project,
        "version": version,
        "tag": tag,
        "sha256": actual_sha,
        "cache_body": str(source),
        "wheelhouse_file": str(destination),
    }


def _run(command: list[str], *, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
        env=env,
        timeout=600,
    )


def build_environment(venv: Path, wheelhouse: Path) -> dict[str, object]:
    pyproject = ROOT / "pyproject.toml"
    lockfile = ROOT / "uv.lock"
    before = {str(path): sha256_file(path) for path in (pyproject, lockfile)}
    wheelhouse.mkdir(parents=True, exist_ok=True)
    inventory = [materialise_wheel(pin, wheelhouse) for pin in WHEELS]

    if not BASE_PYTHON.is_file():
        raise RuntimeError(f"LOCAL_PYTHON_MISSING: {BASE_PYTHON}")
    if not venv.exists():
        subprocess.run(
            [str(BASE_PYTHON), "-m", "venv", str(venv)],
            check=True,
            timeout=120,
        )
    venv_python = venv / "bin/python"
    if not venv_python.is_file():
        raise RuntimeError(f"PROBE_VENV_INCOMPLETE: {venv_python}")

    env = os.environ.copy()
    env.update(
        {
            "PIP_NO_INDEX": "1",
            "PIP_DISABLE_PIP_VERSION_CHECK": "1",
            "HF_HUB_OFFLINE": "1",
            "TRANSFORMERS_OFFLINE": "1",
        }
    )
    install = _run(
        [
            str(venv_python),
            "-m",
            "pip",
            "install",
            "--no-index",
            "--find-links",
            str(wheelhouse),
            "demucs==4.1.0",
            # Demucs imports NumPy on every platform but 4.1.0 declares it
            # only for Intel macOS. Name the pinned arm64 wheel explicitly.
            "numpy==1.26.4",
        ],
        env=env,
    )
    check = _run([str(venv_python), "-m", "pip", "check"], env=env)
    freeze = _run([str(venv_python), "-m", "pip", "freeze", "--all"], env=env)
    pyvenv = (venv / "pyvenv.cfg").read_text(encoding="utf-8")
    if "include-system-site-packages = false" not in pyvenv.lower():
        raise RuntimeError("PROBE_VENV_NOT_ISOLATED")

    after = {str(path): sha256_file(path) for path in (pyproject, lockfile)}
    if before != after:
        raise RuntimeError("PROJECT_DEPENDENCY_FILES_MUTATED")
    return {
        "job": "J2_ENV",
        "label": "HOST-ONLY",
        "verdict": "OFFLINE_PROBE_ENV_READY",
        "venv": str(venv),
        "include_system_site_packages": False,
        "pip_no_index": True,
        "network_fetch": False,
        "project_dependency_hashes_before": before,
        "project_dependency_hashes_after": after,
        "project_dependencies_unchanged": before == after,
        "wheels": inventory,
        "pip_install_stdout": install.stdout.splitlines(),
        "pip_check": check.stdout.strip(),
        "installed": freeze.stdout.splitlines(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the local-only Demucs probe venv.")
    parser.add_argument("--venv", type=Path, default=DEFAULT_VENV)
    parser.add_argument("--wheelhouse", type=Path, default=DEFAULT_WHEELHOUSE)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    args = parser.parse_args(argv)
    try:
        receipt = build_environment(args.venv, args.wheelhouse)
        code = 0
    except (OSError, RuntimeError, subprocess.SubprocessError, zipfile.BadZipFile) as exc:
        receipt = {
            "job": "J2_ENV",
            "label": "HOST-ONLY",
            "verdict": "OFFLINE_ENV_UNAVAILABLE",
            "error": str(exc),
            "network_fetch": False,
        }
        code = 2
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(receipt["verdict"], flush=True)
    if code:
        print(receipt.get("error", "offline environment unavailable"), flush=True)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
