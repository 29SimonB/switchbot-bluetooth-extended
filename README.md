# SwitchBot Bluetooth Extended

Experimental Home Assistant custom integration for **SwitchBot Bot / WoHand** over local Bluetooth only. No SwitchBot Hub and no SwitchBot Cloud are required.

## Features

- One Home Assistant device per physical Bot
- Main Bot control with native Switch/Press-mode behavior
- Press / Switch mode selector
- Reverse on/off direction toggle
- Press-hold time
- Strength
- Battery
- Firmware
- Bluetooth RSSI (disabled by default)
- Bluetooth auto-discovery

## Installation (manual)

1. Copy `custom_components/switchbot_bluetooth_extended` into your Home Assistant `/config/custom_components/` directory.
2. Restart Home Assistant.
3. Remove/disable the same Bot from the built-in **SwitchBot Bluetooth** integration first, otherwise Home Assistant will have two integrations trying to represent/control the same physical device.
4. Go to **Settings → Devices & services → Add integration → SwitchBot Bluetooth Extended**.
5. Discovery starts immediately. Confirm a single discovered Bot, or select one when several are found. An empty search opens manual MAC entry; the device list also offers manual entry. Password-free Bots use a simple confirmation. Name and area assignment are handled by Home Assistant after setup.

## Notes

This integration intentionally supports **SwitchBot Bot only**. It uses `PySwitchbot` for BLE communication and reads/writes the Bot's actual settings.

### Supported mode settings

`PySwitchbot 2.7.0` exposes Press/Switch mode, strength, inverse direction and hold duration. Custom Mode is not exposed by the public Bot API in that library, so it is deliberately not included yet rather than sending guessed BLE commands.

## Publishing checklist

Repository and issue tracker: https://github.com/29SimonB/switchbot-bluetooth-extended. Maintainer: @29SimonB.

## Development status

Version 0.1.4 is a test build. Test on a spare/non-critical Bot first and review Home Assistant logs for `switchbot_bluetooth_extended` if setup fails.


## Version 0.1.1: discovery and ESPHome proxies

The ZIP contains `custom_components/` directly at its root. Replace the existing
`/config/custom_components/switchbot_bluetooth_extended/` folder with the folder
from this archive, then restart Home Assistant. Existing Extended entries and
unique IDs are preserved. Do not nest a second `custom_components` folder inside
that directory. The Bluetooth integration and ESPHome proxy remain installed.

Discovery requests an active scan through Home Assistant, parses both shared
advertisement caches with PySwitchbot, and resolves connection availability using
`async_ble_device_from_address(..., connectable=True)`. No adapter/interface is
selected and no standalone scanner is created. Seeing an advertisement alone does
not imply that a proxy supports active BLE connections.

Manual setup accepts colon-separated, hyphen-separated or compact BLE MACs,
normalizes them and checks for duplicate Extended entries. It accepts an address
whose model could not be parsed, but rejects a known non-Bot. A connectable device
must still be known to Home Assistant; manual input cannot bypass an offline or
passive-only proxy. Check the proxy's `bluetooth_proxy` configuration, active
connections and range if the form reports no route. Retry after advertisements
arrive. An optional Bot password is supported; recognized password-protected Bots
require it. Configuration does not press the Bot to test a password.

## Compatibility and validation

Compared on 2026-09-10 with the upstream Home Assistant `dev` SwitchBot config
flow, manifest and setup code. Uses the same pinned `PySwitchbot==2.7.0`, keeps
config-entry version 1 and the separate `switchbot_bluetooth_extended` domain.
The polling coordinator is classified as `local_polling`. This package is a test
build, not a claim of compatibility with every Home Assistant release.

Sources:
- https://github.com/home-assistant/core/blob/dev/homeassistant/components/switchbot/config_flow.py
- https://github.com/home-assistant/core/blob/dev/homeassistant/components/switchbot/manifest.json
- https://github.com/home-assistant/core/blob/dev/homeassistant/components/switchbot/__init__.py

See `VALIDATION.md` for checks and limitations. A live Home Assistant/ESPHome/Bot
hardware test is still required.


## Reverse direction

Reverse only affects Switch mode. In Press mode (or when data is unavailable),
the entity is unavailable and writes are rejected. It becomes usable again when
Switch mode is reported. Home Assistant's device page can still show its row;
this integration does not change the user's entity visibility preferences or
remove/recreate entities on mode changes. A conditional dashboard card can hide
that row entirely in Press mode.

## Branding

The maintainer-provided S/plus icon is bundled in the integration's `brand/`
directory, supported since Home Assistant 2026.3. It is not an official SwitchBot
logo. After upgrading, restart HA and refresh the browser if the old placeholder
is cached. Brand files are included in every install ZIP.

## Development and releases

This folder is a Git repository on `main`, with the 0.1.1 baseline tagged.
Install `requirements-test.txt` in a virtual environment and run `python -m pytest tests -q`. Tests simulate HA; they are not live hardware tests.

1. Push `main` to https://github.com/29SimonB/switchbot-bluetooth-extended.
2. Check that the GitHub Actions checks pass.
3. Update manifest version and CHANGELOG, run tests, then commit.
4. Tag that commit, for example `git tag v0.1.4`, and push the tag.
5. GitHub Actions runs tests and Hassfest, checks tag/version consistency, builds
   an install ZIP and creates a **draft** GitHub Release. Review and publish it.

`python scripts/build_release.py --tag v0.1.4` builds the same ZIP locally.
The workflow requires GitHub Actions to be enabled. A private repository can
use Git version control, but public distribution through HACS needs a public
repository. No GitHub repository or release is created merely by downloading
this folder. A HACS default-list submission is not included.

## State updates in 0.1.4

The switch publishes a provisional requested state while a command runs.
A failed command restores the previous displayed state and reports the error.
Successful commands publish PySwitchbot state without a redundant refresh.
Rapid clicks are serialized. No extra movement command is sent to stabilize
the UI. Changes made outside HA still use the existing polling interval.
