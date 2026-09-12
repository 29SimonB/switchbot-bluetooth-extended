# Validation

## Automated checks

The `Checks` GitHub Actions workflow runs on pushes, pull requests and manual dispatch:

- **Regression tests:** real PySwitchbot and voluptuous, with simulated Home
  Assistant APIs. Covers discovery and proxy routes, manual MAC validation,
  duplicate setup, passwords, reverse availability, command errors and pending UI state.
- **Python compilation:** catches syntax errors in integration modules.
- **Release build:** creates an install ZIP and verifies its integrity.
- **Gitleaks:** scans fetched Git history and current files for recognizable secrets,
  with redacted output. This does not detect all personal information.
- **Hassfest:** checks Home Assistant integration metadata and conventions.

The tag-triggered release workflow repeats regression, compilation, build and Hassfest checks and requires its tag to
match the manifest version before creating a draft release.

## Run locally

Use Python 3.13 in a virtual environment:

```sh
python3.13 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-test.txt
python -m pytest tests -q
python -m compileall -q custom_components
python scripts/build_release.py
```

Pass `--tag v<version>` to the build script to check tag/version consistency.
Run these tests separately from Home Assistant's tests: they substitute HA modules.
Hassfest is run by GitHub Actions, not by the commands above.

## Evidence and limitations

The 0.1.5 baseline had 41 passing isolated regression cases. GitHub regression
and Hassfest jobs have passed, and the maintainer confirmed the live setup works
with a Bot and ESPHome proxy. This is not certification of every HA/proxy version.

The suite does **not** start a real Home Assistant instance or exercise real BLE
hardware. Startup, unload, entity-registry behavior, long-running connection loss
and simultaneous settings updates need broader integration testing. There is no
coverage threshold. The secret-scan job is part of the Checks workflow.
A passing Hassfest check is not a security audit.

## Repository audit (2026-09-12)

The 0.1.6 candidate passes 52 isolated regression cases on Python 3.13.
The changed settings behavior still needs the hardware acceptance check below.

Gitleaks 8.30.1 found no recognizable secrets in all eight existing commits or
the current files. This is a scanner result, not proof of absence. Real example
MAC addresses were replaced in current source/tests; historical versions still
contain the old identifier; the maintainer chose to retain history. PNG text metadata was removed without changing pixels.
Public project URLs and the GitHub codeowner remain intentionally.

## Hardware acceptance after behavior changes

1. Install the candidate release, restart HA and confirm the installed version.
2. Test discovered setup and manual setup with the proxy enabled.
3. Check on/off in Switch mode and press behavior in Press mode, including UI state.
4. Change mode, reverse, strength and hold time; verify the device's resulting settings.
5. Test an unreachable device and confirm an error rather than false success.
6. Restart HA and check existing entries and entity IDs remain intact.
7. Check app-originated changes after polling; avoid concurrent app and HA settings
   writes until their interaction has been explicitly tested.
