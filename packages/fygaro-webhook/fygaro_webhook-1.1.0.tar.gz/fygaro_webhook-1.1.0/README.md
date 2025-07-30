# fygaro-webhook

> **Webhook signature verification for Fygaro — pure Python stdlib, zero runtime deps**

This helper validates the `Fygaro-Signature` header of incoming webhooks.
It supports secret rotation (multiple active secrets), deterministic unit‑testing, and is ready for future
hash algorithms.

---

## Installation

```bash
pip install fygaro-webhook
```

*Requires Python ≥ 3.8.*

---

## Quick start

```python
from fygaro.webhook import FygaroWebhookValidator

validator = FygaroWebhookValidator(
    secrets=[
        "my-primary-secret",  # str or bytes
        # "my-previous-secret",   # include during rotation windows
    ],
    # max_age=300,          # optional (default = 5 min)
)

if not validator.verify_signature(
    signature_header=request.headers["Fygaro-Signature"],
    body=request.body,  # raw bytes exactly as sent
):
    raise ValueError("Invalid signature")

# …process JSON, return 200…
```

---

## API reference

### `class FygaroWebhookValidator`

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `secrets` | `Sequence[str \| bytes]` | ✔ | — | One or more active webhook secrets. Provide **all currently valid** secrets during a rotation window. Each secret can be a UTF‑8 `str` or raw `bytes`. |
| `max_age` | `int` | ✖ | `300` | Maximum allowable clock skew (in seconds) between the timestamp in the header and the server time. A low value mitigates replay attacks |
| `unsafe_skip_ts_validation` | `bool` | ✖ | `False` | **Test only.** When `True`, the timestamp‑freshness check is skipped and a `RuntimeWarning` is emitted on instantiation. Never enable in production. |

---

#### `validator.verify_signature(signature_header: str, body: bytes) -> bool`

| Argument | Type | Description |
|----------|------|-------------|
| `signature_header` | `str` | The exact value of the incoming **Fygaro‑Signature** HTTP header. |
| `body` | `bytes` | The unmodified request body (raw bytes). **Do not** `.decode()` or re‑serialize. |

Return value:

* `True` — signature is valid **and** timestamp is within `max_age` (unless skipped).
* `False` — signature mismatch, stale timestamp, or malformed header.

---

## Writing deterministic unit tests

To keep fixtures stable you can bypass the timestamp‑freshness check **without** touching production code:

```python
validator = FygaroWebhookValidator(
    secrets=[b"test-secret"],
    unsafe_skip_ts_validation=True,  # ← test‑only flag
)
```

*The first instance created with `unsafe_skip_ts_validation=True` emits a
`RuntimeWarning` to remind you that this path is unsafe for live traffic.*

---

## Changelog

See [`CHANGELOG.md`](CHANGELOG.md) for release notes.

---

## License

MIT © Fygaro — support: [support@fygaro.com](mailto:support@fygaro.com)
