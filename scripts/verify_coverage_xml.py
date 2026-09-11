#!/usr/bin/env python3
"""Reject missing, stale, empty, malformed, or unrecognized coverage XML."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path


ROOTS = {"coverage", "CoverageSession"}


def verify(inputs: list[Path], since: float) -> list[str]:
    candidates: set[Path] = set()
    for item in inputs:
        if item.is_dir():
            candidates.update(item.rglob("*.xml"))
        elif item.suffix.lower() == ".xml":
            candidates.add(item)

    valid: list[str] = []
    errors: list[str] = []
    for path in sorted(candidates):
        try:
            stat = path.stat()
            if stat.st_size == 0:
                raise ValueError("empty")
            if stat.st_mtime + 1 < since:
                raise ValueError("stale")
            root = ET.parse(path).getroot().tag.rsplit("}", 1)[-1]
            if root not in ROOTS:
                raise ValueError(f"unrecognized root {root!r}")
            valid.append(str(path.resolve()))
        except (OSError, ET.ParseError, ValueError) as exc:
            errors.append(f"{path}: {exc}")

    if not valid:
        detail = "; ".join(errors) if errors else "no XML files found"
        raise ValueError(detail)
    return valid


def self_test() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        since = time.time() - 1
        good = root / "coverage.xml"
        good.write_text('<coverage line-rate="1" />', encoding="utf-8")
        assert verify([root], since) == [str(good.resolve())]
        good.write_text("<coverage>", encoding="utf-8")
        try:
            verify([root], since)
        except ValueError:
            pass
        else:
            raise AssertionError("malformed XML was accepted")
        good.write_text('<coverage line-rate="1" />', encoding="utf-8")
        os.utime(good, (since - 10, since - 10))
        for inputs in ([root], []):
            try:
                verify(inputs, since)
            except ValueError:
                pass
            else:
                raise AssertionError("missing or stale XML was accepted")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="*", type=Path)
    parser.add_argument("--since", type=float, default=0)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    try:
        files = verify(args.inputs, args.since)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps({"files": files}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
