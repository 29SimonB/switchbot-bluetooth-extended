"""Build an install ZIP from an explicit set of supported file types."""
import argparse
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "switchbot_bluetooth_extended"


def build(root: Path, tag: str | None = None) -> Path:
    component = root / "custom_components" / DOMAIN
    version = json.loads((component / "manifest.json").read_text())["version"]
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:[a-zA-Z0-9.-]*)", version):
        raise ValueError("Invalid manifest version")
    if tag and tag != f"v{version}":
        raise ValueError(f"Tag {tag} does not match manifest v{version}")
    files = []
    for path in sorted(component.rglob("*")):
        relative = path.relative_to(component)
        if any(part.startswith(".") or part == "__pycache__" for part in relative.parts):
            continue
        allowed = (
            len(relative.parts) == 1 and path.suffix in {".py", ".json"}
            or len(relative.parts) == 2 and relative.parts[0] == "translations" and path.suffix == ".json"
            or len(relative.parts) == 2 and relative.parts[0] == "brand" and path.suffix == ".png"
        )
        if allowed and path.is_file():
            if path.is_symlink() or any(parent.is_symlink() for parent in path.parents if parent != root):
                raise ValueError("Symlinks are not allowed in release inputs")
            files.append(path)
    for name in ("README.md", "CHANGELOG.md", "LICENSE", "hacs.json", "VALIDATION.md", "SECURITY.md"):
        path = root / name
        if path.is_symlink():
            raise ValueError("Symlinks are not allowed in release inputs")
        files.append(path)
    out = root / "dist" / f"switchbot-bluetooth-extended-{version}.zip"
    out.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(root))
    with zipfile.ZipFile(out) as archive:
        if archive.testzip() is not None:
            raise ValueError("Invalid release ZIP")
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag")
    args = parser.parse_args()
    print(build(ROOT, args.tag))
