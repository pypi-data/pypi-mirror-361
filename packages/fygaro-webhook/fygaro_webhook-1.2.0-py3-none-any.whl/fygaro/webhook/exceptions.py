class SignatureVerificationError(Exception):
    """Base class for all signature-verification problems."""

class MissingHeaderError(SignatureVerificationError):
    """`signature_header` was None or empty."""

class TimestampInvalidError(SignatureVerificationError):
    """`t=` value missing or not an int."""

class TimestampExpiredError(SignatureVerificationError):
    """`t=` present but outside the allowed max_age window."""

class SignatureMismatchError(SignatureVerificationError):
    """None of the calculated digests matched any header candidate."""
