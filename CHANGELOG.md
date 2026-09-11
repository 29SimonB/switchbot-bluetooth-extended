# Changelog

## 0.1.4 — 2026-09-11

- Show pending switch state during commands, roll back on failure and serialize rapid clicks.
- Publish PySwitchbot command state without a redundant post-command read.
- Start setup with discovery, auto-select a sole Bot and show password only when needed.
- Preserve manual MAC setup and use the user-supplied updated brand images.


## 0.1.3 — 2026-09-10

- Read the current Bot mode before each on/off action; do not fall back to Press
  when mode is unknown. Log the selected action at debug level.
- Physical return movement reported by the user still requires a live retest.

- Read on/off state through PySwitchbot instead of raw cached advertisements,
  preserving its protection against stale state immediately after commands.
- Add regression coverage for on/off overrides and subsequent advertisement updates.


## 0.1.2 — 2026-09-10

- Bundle an original local integration icon and logo.
- Make Reverse unavailable outside Switch mode and reject reverse writes when
  mode data is missing, stale or Press. Entity IDs and stored reverse setting remain.
- Add Git history, regression/Hassfest CI and a tag-triggered draft-release workflow.


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
