"""Write or verify a checksum inventory of the repository's published files."""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/repo_manifest.json"


def files():
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path == MANIFEST:
            continue
        relative = path.relative_to(ROOT)
        if any(part in {".git", "build", "__pycache__"} for part in relative.parts):
            continue
        yield path, str(relative)


def inventory():
    return [
        {"path": name, "bytes": path.stat().st_size,
         "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        for path, name in files()
    ]


if __name__ == "__main__":
    actual = {"version": "4.0", "files": inventory()}
    if sys.argv[1:] == ["--write"]:
        MANIFEST.write_text(json.dumps(actual, ensure_ascii=False, indent=2) + "\n")
        print(f"Recorded {len(actual['files'])} files")
    elif sys.argv[1:] == ["--verify"]:
        expected = json.loads(MANIFEST.read_text())
        if actual != expected:
            raise SystemExit("Manifest differs: a file was added, changed or removed")
        print(f"Verified {len(actual['files'])} files")
    else:
        raise SystemExit("Usage: python3 src/manifest.py --write|--verify")
