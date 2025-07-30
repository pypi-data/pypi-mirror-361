"""
validator.py - single-class API for Fygaro webhook validation.

• Pure standard library (hashlib, hmac, time)
• Handles multiple secrets (rotation) and multiple v1= entries
• Constant-time comparisons via hmac.compare_digest
• Ready for future algorithm tags by extending _HASH_FUNCTIONS
"""

from __future__ import annotations

import hashlib
import hmac
import time
import warnings

from typing import Dict, Final, List, Mapping, Sequence, Union, Optional

# ------------------------------------------------------------------ #
# Configuration
# ------------------------------------------------------------------ #
DEFAULT_MAX_AGE_SECONDS: Final[int] = 5 * 60  # five minutes
_HASH_FUNCTIONS: Dict[str, callable] = {
    "v1": hashlib.sha256,  # current production hash
    # "v2": hashlib.sha512,  # example future upgrade
}
_HEADER_TS_KEY: Final[str] = "t"


def _parse_header(header: str) -> Mapping[str, List[str]]:
    """t=123,v1=a,v1=b → {'t':['123'], 'v1':['a','b']}"""
    parsed: Dict[str, List[str]] = {}
    for token in header.split(","):
        if "=" in token:
            k, v = token.split("=", 1)
            parsed.setdefault(k.strip(), []).append(v.strip())

    return parsed


def _normalize_secret(secret: Union[bytes, str]) -> bytes:
    """Accept bytes or UTF-8 str. Strings are encoded to bytes."""
    return secret if isinstance(secret, bytes) else secret.encode()


class FygaroWebhookValidator:
    """
    Lightweight, dependency-free webhook signature validator.

    Parameters
    ----------
    secrets : list[bytes | str]
        One or more webhook signing secrets.  *Strings are UTF-8 encoded.*
    max_age : int, default ``300``
        Maximum allowed age of the ``t=`` timestamp inside the header.
    unsafe_skip_ts_validation : bool, default ``False``
        *Test-only.*  When **True** the timestamp freshness check is
        **skipped entirely**.  A :class:`RuntimeWarning` is emitted on
        object creation to minimise the risk of accidental use outside
        tests.

    Notes
    -----
    The validator supports secret rotation (multiple ``secrets``) and
    future signature versions (multiple ``vX=`` entries).  All hash
    comparisons use :func:`hmac.compare_digest` for constant-time safety.
    """

    __slots__ = ("_secret_bytes", "_max_age", "_skip_ts")

    def __init__(
        self,
        *,
        secrets: Sequence[Union[bytes, str]],
        max_age: int = DEFAULT_MAX_AGE_SECONDS,
        unsafe_skip_ts_validation: bool = False,
    ) -> None:
        self._secret_bytes: List[bytes] = [_normalize_secret(s) for s in secrets]
        self._max_age: int = max_age
        self._skip_ts: bool = unsafe_skip_ts_validation

        if self._skip_ts:
            warnings.warn(
                "Timestamp validation DISABLED - for test use only!",
                RuntimeWarning,
                stacklevel=2,
            )

    # ---------------------------------------------------------- #
    def verify_signature(self, signature_header: Optional[str], body: bytes) -> bool:
        """Return *True* if the signature is valid, else *False*."""
        if signature_header is None:
            return False

        parsed = _parse_header(signature_header)

        # -------------------------------------------------- #
        # 1. Timestamp freshness (unless explicitly skipped)
        # -------------------------------------------------- #
        try:
            ts = int(parsed[_HEADER_TS_KEY][0])

        except (KeyError, ValueError, IndexError):
            return False

        if not self._skip_ts and abs(time.time() - ts) > self._max_age:
            return False

        # -------------------------------------------------- #
        # 2. Compute expected digests for every secret × version
        # -------------------------------------------------- #
        for secret in self._secret_bytes:
            for version, hash_fn in _HASH_FUNCTIONS.items():
                if version not in parsed:
                    continue

                expected = hmac.new(
                    secret,
                    f"{ts}".encode() + b"." + body,
                    hash_fn,
                ).hexdigest()

                if any(
                    hmac.compare_digest(expected, candidate)
                    for candidate in parsed[version]
                ):
                    return True

        return False
