#!/usr/bin/env python3
"""Offline verification of every published file. Standard library only.

    python verify.py              # re-hash every file listed in SHA256SUMS
    python verify.py --selftest   # prove this checker can actually FAIL

A verifier that cannot go red is decoration: --selftest flips one byte of a
published file in a temporary copy of the tree and asserts the check reports it.
"""
from __future__ import annotations
import hashlib, pathlib, shutil, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parent
SUMS = ROOT / "SHA256SUMS"


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_sums(sums: pathlib.Path) -> list[tuple[str, str]]:
    out = []
    for line in sums.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        digest, name = line.split(None, 1)
        out.append((digest.lower(), name.strip().lstrip("*")))
    return out


def check(root: pathlib.Path, sums: pathlib.Path) -> list[str]:
    entries = load_sums(sums)
    if not entries:
        return ["SHA256SUMS is empty -- nothing was checked, which is a failure"]
    failures = []
    for digest, name in entries:
        p = root / name
        if not p.is_file():
            failures.append(f"MISSING  {name}")
        elif sha256(p) != digest:
            failures.append(f"MISMATCH {name}")
    return failures


def selftest() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        work = pathlib.Path(tmp) / "tree"
        shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        clean = check(work, work / "SHA256SUMS")
        if clean:
            print("SELFTEST FAIL -- the pristine copy does not verify:", clean)
            return 2
        _, name = load_sums(work / "SHA256SUMS")[0]
        target = work / name
        data = bytearray(target.read_bytes())
        data[len(data) // 2] ^= 0xFF
        target.write_bytes(bytes(data))
        failures = check(work, work / "SHA256SUMS")
        if any(f.startswith("MISMATCH") for f in failures):
            print(f"SELFTEST OK -- corrupting {name} was detected")
            return 0
        print("SELFTEST FAIL -- a corrupted file passed verification")
        return 2


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    failures = check(ROOT, SUMS)
    if failures:
        print("FAIL")
        for f in failures:
            print("  ", f)
        return 1
    print(f"OK -- {len(load_sums(SUMS))} files match SHA256SUMS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
