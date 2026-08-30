#!/usr/bin/env python3
"""Fetch standard MUSDB18 STEMS (not HQ) from Zenodo, or print the manual path.

Audio is gitignored. Educational/NC. commercial_training_lineage=false.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path("datasets/musdb18")
ZIP_NAME = "musdb18.zip"
URL = "https://zenodo.org/api/records/1117372/files/musdb18.zip/content"
MD5 = "af06762477334799bfc5abf237648207"
SIZE = 4684228845
UA = "SpectraSynq-EdgeAI-Lab (research; MUSDB18 educational use)"


def _md5(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1 << 20)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def fetch(dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".zip.partial")
    existing = tmp.stat().st_size if tmp.is_file() else 0
    headers = {"User-Agent": UA}
    if existing:
        headers["Range"] = f"bytes={existing}-"
        print(f"resume from {existing} bytes", flush=True)
    req = Request(URL, headers=headers)
    with urlopen(req, timeout=120) as resp, tmp.open("ab" if existing else "wb") as out:
        total = existing + int(resp.headers.get("Content-Length") or 0)
        n = existing
        last = -1
        while True:
            chunk = resp.read(1 << 20)
            if not chunk:
                break
            out.write(chunk)
            n += len(chunk)
            pct = int(100 * n / SIZE)
            if pct != last and pct % 2 == 0:
                print(f"{n}/{SIZE} {pct}%", flush=True)
                last = pct
    got = _md5(tmp)
    if got != MD5:
        raise SystemExit(f"md5 mismatch {got} != {MD5}")
    tmp.replace(dest)
    print(f"ok {dest} md5={got}", flush=True)
    return dest


def unzip(zpath: Path, dest: Path) -> None:
    import zipfile

    print(f"unzip {zpath} -> {dest}", flush=True)
    with zipfile.ZipFile(zpath) as zf:
        zf.extractall(dest)
    print("unzip done", flush=True)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--fetch", action="store_true", help="download + md5 + unzip")
    p.add_argument("--unzip-only", action="store_true")
    args = p.parse_args()
    zpath = ROOT / ZIP_NAME
    if not args.fetch and not args.unzip_only:
        print(
            "MUSDB18 STEMS is ~4.7 GB from Zenodo 1117372.\n"
            "Run: uv run python scripts/download_musdb.py --fetch\n"
            f"Expected: {ROOT}/train  and  {ROOT}/test\n"
            "Licence: educational/NC. Do not train a shipping model on this."
        )
        return 0
    if args.fetch:
        if zpath.is_file() and zpath.stat().st_size == SIZE and _md5(zpath) == MD5:
            print(f"already have {zpath}", flush=True)
        else:
            fetch(zpath)
    if args.fetch or args.unzip_only:
        if not (ROOT / "train").is_dir():
            unzip(zpath, ROOT)
        else:
            print("train/ already present", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
