# Validation — 0.1.3

- 32 isolated regression tests passed using Python 3.13, PySwitchbot 2.7.0,
  voluptuous and pytest. Home Assistant framework/Bluetooth APIs were stubbed;
  the advertisement parser and Switchbot device class were real.
- Covered local and ESPHome-proxy discovery, passive advertisements with a
  separate connectable route, passive-only rejection, empty-search fallback,
  accepted/invalid MAC formats, duplicates, non-Bots, encrypted Bot passwords,
  retry after proxy arrival, runtime device resolution and route changes,
  manual setup without parseable advertisements, and failed basic-info reads.
- Parsed all Python files and JSON files; checked translation-key parity.
- Compared APIs, requirement pin and matchers against current upstream SwitchBot
  source (links in README). This is source review, not a full Hassfest run.
- ZIP integrity and root layout checked before delivery.

Not run: full Home Assistant startup/config-flow test suite, Hassfest, or live
BLE communication with a Bot and ESPHome proxy. The existing HACS minimum
Home Assistant 2026.8.0 is retained, not independently certified.

## Run isolated tests

In a disposable virtual environment install `PySwitchbot==2.7.0`, `voluptuous`
and `pytest`, then run `python -m pytest tests`. Run these tests separately from
Home Assistant's own test suite because they substitute HA modules.

## Live acceptance check

1. Replace the integration folder and restart HA; verify version 0.1.2 in logs.
2. Leave the Bluetooth integration and ESPHome proxy enabled. Open Extended,
   choose Search for Bots and verify the Bot appears. Confirm once.
3. Alternatively enter the Bot MAC manually. Verify invalid addresses and
   passive-only/unreachable devices show an error and allow retry.
4. Verify battery/settings load and existing mode/hold/strength controls operate.
   Avoid concurrent commands from the native integration during this test.
5. Restart HA and check the entry/entities retain their identities.

Additional 0.1.2 checks: Reverse availability transitions and rejected writes
in Press/missing/stale mode, plus allowed writes in Switch mode. Brand PNGs
were generated, resized and visually inspected. GitHub workflows are prepared
but have not run remotely; Hassfest has not run locally.

0.1.3 adds command-state and fresh-mode regression tests. Physical return
movement is not yet verified fixed on hardware.
