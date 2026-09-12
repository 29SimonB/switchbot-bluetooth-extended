"""Check release boundaries using a disposable project tree."""
import importlib.util
import json
from pathlib import Path
import zipfile

import pytest

spec = importlib.util.spec_from_file_location("release_builder", Path(__file__).resolve().parents[1] / "scripts/build_release.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


@pytest.fixture
def project(tmp_path):
    component = tmp_path / "custom_components" / builder.DOMAIN
    component.mkdir(parents=True)
    (component / "manifest.json").write_text(json.dumps({"version": "1.2.3"}))
    (component / "__init__.py").write_text("")
    for name in ("README.md", "CHANGELOG.md", "LICENSE", "hacs.json", "VALIDATION.md", "SECURITY.md"):
        (tmp_path / name).write_text("")
    return tmp_path, component


def test_archive_excludes_unexpected_files(project):
    root, component = project
    for name in (".env", "private.key", ".DS_Store", "debug.log"):
        (component / name).write_text("fixture")
    with zipfile.ZipFile(builder.build(root, "v1.2.3")) as archive:
        names = archive.namelist()
        assert f"custom_components/{builder.DOMAIN}/manifest.json" in names
        assert "SECURITY.md" in names
        assert len(names) == 8


def test_mismatched_tag_rejected(project):
    with pytest.raises(ValueError, match="does not match"):
        builder.build(project[0], "v9.9.9")


def test_source_symlink_rejected(project):
    root, component = project
    (component / "linked.py").symlink_to(root / "README.md")
    with pytest.raises(ValueError, match="Symlinks"):
        builder.build(root)
