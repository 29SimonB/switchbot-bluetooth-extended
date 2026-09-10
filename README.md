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
5. Choose **Search for Bots**, select the Bot, and confirm. Alternatively choose **Enter BLE MAC manually**. An empty search automatically opens manual entry.

## Notes

This integration intentionally supports **SwitchBot Bot only**. It uses `PySwitchbot` for BLE communication and reads/writes the Bot's actual settings.

### Supported mode settings

`PySwitchbot 2.7.0` exposes Press/Switch mode, strength, inverse direction and hold duration. Custom Mode is not exposed by the public Bot API in that library, so it is deliberately not included yet rather than sending guessed BLE commands.

## Publishing checklist

Before publishing, set `documentation` and `issue_tracker` to your actual repository URLs and add your GitHub handle to `codeowners`. The documentation link currently points to upstream Bluetooth guidance, not documentation for these extra entities.

## Development status

Version 0.1.1 is a test build. Test on a spare/non-critical Bot first and review Home Assistant logs for `switchbot_bluetooth_extended` if setup fails.


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
The polling coordinator is classified as `local_poll`. This package is a test
build, not a claim of compatibility with every Home Assistant release.

Sources:
- https://github.com/home-assistant/core/blob/dev/homeassistant/components/switchbot/config_flow.py
- https://github.com/home-assistant/core/blob/dev/homeassistant/components/switchbot/manifest.json
- https://github.com/home-assistant/core/blob/dev/homeassistant/components/switchbot/__init__.py

See `VALIDATION.md` for checks and limitations. A live Home Assistant/ESPHome/Bot
hardware test is still required.
