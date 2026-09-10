"""Build install ZIP with deterministic ordering and validate its tag/version."""
from pathlib import Path
import argparse
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--tag")
args = parser.parse_args()
version = json.loads((ROOT / "custom_components/switchbot_bluetooth_extended/manifest.json").read_text())["version"]
if args.tag and args.tag != f"v{version}":
    raise SystemExit(f"Tag {args.tag} does not match manifest v{version}")
out = ROOT / "dist" / f"switchbot-bluetooth-extended-{version}.zip"
out.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
    for path in sorted((ROOT / "custom_components").rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
            archive.write(path, path.relative_to(ROOT))
    for name in ("README.md", "CHANGELOG.md", "LICENSE", "hacs.json", "VALIDATION.md"):
        archive.write(ROOT / name, name)
with zipfile.ZipFile(out) as archive:
    assert archive.testzip() is None
print(out)
