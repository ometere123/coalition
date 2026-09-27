"""Prepare the stable GenVM v0.3.0-rc7 runner bundle for gltest v0.29.2.

The stable v0.29.2 Direct Mode loader expects a historical file named
`genvm-universal.tar.xz`. The rc7 release now publishes the runner-only
archive as `genvm-runners-all.tar.xz`. Direct Mode needs only those runner
archives, so cache the official asset under the legacy local filename.
"""

from pathlib import Path
import os
import tarfile
import tempfile
import urllib.request

VERSION = "v0.3.0-rc7"
RUNNER_HASH = "1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6"
URL = f"https://github.com/genlayerlabs/genvm/releases/download/{VERSION}/genvm-runners-all.tar.xz"
CACHE_DIR = Path.home() / ".cache" / "gltest-direct"
DEST = CACHE_DIR / f"genvm-universal-{VERSION}.tar.xz"


def valid_bundle(path: Path) -> bool:
    if not path.exists() or path.stat().st_size == 0:
        return False
    target = f"runners/py-genlayer/{RUNNER_HASH[:2]}/{RUNNER_HASH[2:]}.tar"
    try:
        with tarfile.open(path, "r:xz") as archive:
            names = set(archive.getnames())
        return target in names
    except Exception:
        return False


def main() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if valid_bundle(DEST):
        print(f"OK: stable runner bundle already cached at {DEST}")
        return

    if DEST.exists():
        DEST.unlink()

    print(f"Downloading official stable runner bundle: {URL}")
    request = urllib.request.Request(URL, headers={"User-Agent": "coalition-direct-mode"})
    with urllib.request.urlopen(request, timeout=300) as response:
        with tempfile.NamedTemporaryFile(delete=False, dir=CACHE_DIR, suffix=".part") as tmp:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                tmp.write(chunk)
            temp_path = Path(tmp.name)

    os.replace(temp_path, DEST)
    if not valid_bundle(DEST):
        DEST.unlink(missing_ok=True)
        raise SystemExit("Downloaded bundle does not contain COALITION stable py-genlayer runner hash")

    print(f"OK: prepared {DEST}")
    print(f"OK: contains py-genlayer:{RUNNER_HASH}")


if __name__ == "__main__":
    main()
