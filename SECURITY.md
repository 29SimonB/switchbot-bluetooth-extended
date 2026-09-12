# Security and privacy

The integration communicates locally through Home Assistant Bluetooth and
PySwitchbot. It does not require cloud credentials.

Never commit device passwords, API tokens, private SSH keys, Home Assistant
storage/backups or unredacted diagnostic logs. Use fictional device addresses in
examples and tests. The public repository URL and GitHub codeowner are intentional
project metadata, not private credentials.

Bot passwords supplied during setup are stored by Home Assistant in the config
entry. Treat Home Assistant storage and backups as sensitive. Debug logs and
errors can contain Bluetooth addresses; redact them before sharing.

Replacing identifying data in the current files does not remove it from earlier
Git commits, tags, forks, downloaded archives or releases. Historical versions
of this project contained a real example device address. Removing that history
requires a coordinated history rewrite and replacement of affected release assets.
A Bluetooth address is an identifier, not an authentication key.

If a credential is ever exposed, revoke or rotate it first. Do not include the
credential itself in a public issue. Secret scanning reduces risk but cannot prove
that a repository contains no sensitive information.
