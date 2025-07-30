# Changelog – @fygaro/webhook

## [1.2.0] – 2025-07-10
### Added
* `raise_exceptions` constructor flag – opt-in detailed failure reasons without
  breaking the legacy `True/False` return contract.

---

## [1.1.0] – 2025-07-10
### Added
* `unsafe_skip_ts_validation` constructor flag that bypasses
  the timestamp-freshness check.
  *Meant **only** for local/unit tests; not safe for production.*
  Emits a **`RuntimeWarning`** the first time an instance is created with the flag
  enabled, to minimise accidental misuse.

---

## [1.0.0] – 2025-06-19
### Added
* Initial release with `FygaroWebhookValidator` class.
* Supports multiple secrets & multiple `v1=` hashes.
* Constant-time compare and configurable timestamp window.
