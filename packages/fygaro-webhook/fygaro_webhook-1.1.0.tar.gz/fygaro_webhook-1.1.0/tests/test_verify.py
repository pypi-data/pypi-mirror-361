import hmac, hashlib, json, time, pytest
from typing import Optional

from fygaro.webhook import FygaroWebhookValidator


def _make_header(secret: bytes, body: bytes, ts: Optional[int] = None) -> str:
    ts = ts or int(time.time())
    sig = hmac.new(secret, f"{ts}".encode() + b"." + body, hashlib.sha256).hexdigest()
    return f"t={ts},v1={sig}"


def test_validator_accepts_valid_signature():
    secret_current, secret_prev = b"current", b"prev"
    body = json.dumps({"ok": True}).encode()

    header = _make_header(secret_prev, body)

    validator = FygaroWebhookValidator(secrets=[secret_current, secret_prev])
    assert validator.verify_signature(header, body)


def test_validator_accepts_old_ts_when_unsafe_flag():
    secret = b"test"
    body = json.dumps({"ok": True}).encode()

    old_ts = int(time.time()) - 86_400  # 24 h ago → definitely staler than max_age
    header = _make_header(secret, body, ts=old_ts)

    with pytest.warns(RuntimeWarning, match="Timestamp validation DISABLED"):
        validator = FygaroWebhookValidator(
            secrets=[secret],
            unsafe_skip_ts_validation=True,
        )

    assert validator.verify_signature(header, body)


def test_validator_rejects_invalid_signature():
    secret_current, secret_prev = b"current", b"prev"
    body = json.dumps({"ok": True}).encode()

    bad_header = _make_header(b"invalid", body)

    validator = FygaroWebhookValidator(secrets=[secret_current, secret_prev])
    assert not validator.verify_signature(bad_header, body)


def test_validator_rejects_old_ts_by_default():
    secret = b"test"
    body = json.dumps({"ok": True}).encode()

    old_ts = int(time.time()) - 86_400
    bad_header = _make_header(secret, body, ts=old_ts)

    validator = FygaroWebhookValidator(secrets=[secret])
    assert not validator.verify_signature(bad_header, body)
