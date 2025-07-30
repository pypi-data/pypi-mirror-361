"""Fygaro Webhook - pure-stdlib signature verification."""

from importlib import metadata as _md
from .validator import FygaroWebhookValidator
from .exceptions import (
    SignatureVerificationError,
    MissingHeaderError,
    TimestampInvalidError,
    TimestampExpiredError,
    SignatureMismatchError,
)

__all__ = [
    "FygaroWebhookValidator",
    "SignatureVerificationError",
    "MissingHeaderError",
    "TimestampInvalidError",
    "TimestampExpiredError",
    "SignatureMismatchError",
]

try:
    __version__: str = _md.version(__name__)

except _md.PackageNotFoundError:  # running from source tree
    __version__ = "0.0.0"
