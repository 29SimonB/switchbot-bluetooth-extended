# SwitchBot Bluetooth Extended

Control a **SwitchBot Bot (WoHand)** and its settings locally from Home Assistant.
Uses Home Assistant's Bluetooth infrastructure, including ESPHome Bluetooth proxies.
No SwitchBot account, cloud connection or SwitchBot Hub is required.

## Features

| Entity | Purpose |
| --- | --- |
| Bot | On/off in Switch mode; a press action in Press mode |
| Mode | Select Press or Switch |
| Reverse direction | Reverse on/off directions in Switch mode |
| Press-hold time | Set hold duration in seconds |
| Strength | Set strength as a percentage |
| Battery / Firmware | Device diagnostics |
| Bluetooth RSSI | Signal strength; disabled by default |

Only Bot devices are supported. Custom Mode is not implemented.
Reverse is unavailable in Press mode; Home Assistant may still display its row.
In Press mode the main switch state is assumed, not a persistent physical on/off state.

## Requirements

- Home Assistant 2026.8.0 or newer, as declared in `hacs.json`.
- A Bluetooth adapter or ESPHome Bluetooth proxy with active BLE connections enabled.
- A Bot within Bluetooth range.

The declared minimum is not a tested compatibility matrix. See [validation](VALIDATION.md).

## Install with HACS

1. In HACS, open **Custom repositories**, add
   `https://github.com/29SimonB/switchbot-bluetooth-extended` and select **Integration**.
2. Download **SwitchBot Bluetooth Extended** and restart Home Assistant.
3. Open **Settings → Devices & services → Add integration** and select
   **SwitchBot Bluetooth Extended**, or use its discovered Bot card.
4. Confirm the Bot. Home Assistant then offers name and area assignment.

Avoid configuring the same Bot for control through both this and the native
SwitchBot integration. Keep Home Assistant Bluetooth and the ESPHome proxy enabled.

For updates, download the new release in HACS and restart Home Assistant.
Existing Extended entries and entity IDs are preserved; do not remove them to update.

### Manual installation

From the release ZIP, copy only `custom_components/switchbot_bluetooth_extended`
to `/config/custom_components/`, then restart Home Assistant and configure it above.
The manifest must be at
`/config/custom_components/switchbot_bluetooth_extended/manifest.json`.
The repository's outer `custom_components` folder belongs in the repository;
HACS installs the integration folder into the correct location.

## Setup and troubleshooting

Discovery starts automatically. A single Bot opens confirmation; several Bots
open a selection list. When none are found, manual MAC entry opens. The device
list also provides manual entry.

Manual input accepts colon-separated, hyphen-separated or compact addresses,
for example `02:00:00:00:00:01` (a fictional address). A connectable route must
still be known to Home Assistant. Manual entry cannot reach an offline proxy.
Check active proxy connections, range and incoming advertisements, then retry.

A password is requested for recognized password-protected Bots, or optionally
when a manually entered device cannot be identified from advertisements.
Use the **Bot's device password** if you set one, not your account password.
Setup does not move the motor to test authentication.

Commands update the UI while running and report failures. Settings and changes
made outside Home Assistant are polled every 15 minutes, so app changes may take
time to appear. Bluetooth communication can also add command latency.

The supplied icon files are in the integration's `brand/` directory. Restart
Home Assistant and refresh the browser after updating. HACS's repository-list
icon is a separate display path; a working HA integration icon does not prove
that HACS will display it. An absent HACS icon does not affect device control.
This is an unofficial integration, not affiliated with SwitchBot.

Before posting logs, remove device addresses and other identifying information.
An optional Bot password is stored in Home Assistant's config entry; do not share
that storage file. See [security and privacy](SECURITY.md).

## Development and releases

See [validation and test instructions](VALIDATION.md) for automated checks,
coverage limits and manual acceptance checks.

1. Update the manifest version and [changelog](CHANGELOG.md) together.
2. Run tests and build the ZIP; commit and push, then check GitHub Actions.
3. Tag the checked commit `v<manifest version>` and push the tag.
4. The release workflow repeats validation, builds the install ZIP and creates
   a **draft release**. Review the draft and publish it for users.

The integration keeps its own `switchbot_bluetooth_extended` domain and uses
`PySwitchbot==2.7.0`. Discovery was compared with the native Home Assistant
[SwitchBot config flow](https://github.com/home-assistant/core/blob/dev/homeassistant/components/switchbot/config_flow.py).

Report reproducible problems in the repository's
[issue tracker](https://github.com/29SimonB/switchbot-bluetooth-extended/issues).
