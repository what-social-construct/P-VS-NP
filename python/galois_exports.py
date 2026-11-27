"""Verify or restore the pinned Lean sources used by the public application."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys

LEAN = Path(__file__).resolve().parents[1] / "lean"
BEGIN = b"-- BEGIN GALOIS EXPORT\n"
END = b"-- END GALOIS EXPORT\n"


def marked_parts(path):
    data = path.read_bytes()
    if data.count(BEGIN) != 1 or data.count(END) != 1:
        raise ValueError(f"{path}: expected one pair of export markers")
    prefix, marked = data.split(BEGIN)
    if END not in marked:
        raise ValueError(f"{path}: reversed export markers")
    body, suffix = marked.split(END)
    return prefix + BEGIN, body, END + suffix


def upstream_bytes(checkout, revision, entry):
    data = subprocess.check_output(
        ["git", "-C", str(checkout), "show", f"{revision}:{entry['source']}"]
    )
    if "lines" in entry:
        first, last = entry["lines"]
        lines = data.splitlines(keepends=True)
        if not 1 <= first <= last <= len(lines):
            raise ValueError(f"{entry['source']}: invalid line range")
        data = b"".join(lines[first-1:last])
    return data


def verify_exports(checkout, restore):
    lock = json.loads((LEAN / "galois-exports.json").read_text())
    revision = lock["revision"]
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("the export revision must be a full Git commit hash")
    replacements = {}
    for entry in lock["exports"]:
        path = LEAN / entry["destination"]
        if "lines" in entry:
            prefix, body, suffix = marked_parts(path)
        else:
            prefix, suffix = b"", b""
            body = path.read_bytes() if path.exists() else None
        if checkout is not None:
            source = upstream_bytes(checkout, revision, entry)
            if sha256(source).hexdigest() != entry["sha256"]:
                raise ValueError(f"{entry['source']}: upstream bytes differ from the reviewed digest")
            if restore and body != source:
                replacements[path] = prefix + source + suffix
                body = source
        if body is None or sha256(body).hexdigest() != entry["sha256"]:
            raise ValueError(f"{entry['destination']}: exported source differs from the reviewed digest")
    # Validate every slice before updating any tracked source.
    for path, data in replacements.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    print(f"Verified {len(lock['exports'])} Galois exports at {revision}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, help="compare against Git objects in this local checkout")
    parser.add_argument("--restore", action="store_true", help="restore the reviewed bytes from --upstream")
    args = parser.parse_args()
    if args.restore and args.upstream is None:
        parser.error("--restore requires --upstream")
    try:
        verify_exports(args.upstream, args.restore)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        sys.exit(str(error))
