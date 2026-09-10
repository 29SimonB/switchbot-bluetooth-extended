# Changelog

## 0.1.1 — 2026-09-10

- Request active scans via Home Assistant before listing discovered Bots.
- Parse both HA advertisement caches and resolve connectable routes via HA;
  support proxy advertisements without selecting a local adapter.
- Align Bluetooth manifest matchers with native SwitchBot; filter for Bots in flow.
- Add manual BLE MAC entry, normalization, duplicate and reachability checks,
  clear retryable errors and known non-Bot rejection.
- Support Bot passwords in confirmation and runtime setup.
- Resolve the BLE device via HA at runtime, including manual setup without a
  parseable advertisement. Preserve domain, entry version and existing unique IDs.
- Add config-entry-only schema, correct polling classification, remove placeholder
  repository links, update German/English texts and simplify ZIP root structure.

## 0.1.0

- Initial experimental Bot integration with mode, strength, reverse and hold time.
