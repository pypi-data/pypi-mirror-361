"""Constants for JWT Library."""

# Default JWT algorithms
DEFAULT_ALGORITHM = "HS256"
SUPPORTED_ALGORITHMS = [
    "HS256",
    "HS384",
    "HS512",
    "RS256",
    "RS384",
    "RS512",
    "ES256",
    "ES384",
    "ES512",
    "PS256",
    "PS384",
    "PS512",
]

# Default settings
DEFAULT_EXPIRATION_HOURS = 24
DEFAULT_LEEWAY_SECONDS = 0

# Standard JWT claims
STANDARD_CLAIMS = {
    "iss": "issuer",
    "sub": "subject",
    "aud": "audience",
    "exp": "expiration_time",
    "nbf": "not_before",
    "iat": "issued_at",
    "jti": "jwt_id",
}

# Error messages
ERROR_MESSAGES = {
    "INVALID_TOKEN": "Invalid JWT token format",
    "EXPIRED_TOKEN": "JWT token has expired",
    "INVALID_SIGNATURE": "JWT token signature verification failed",
    "MISSING_SECRET_KEY": "Secret key is required for verification",
    "UNSUPPORTED_ALGORITHM": "Unsupported JWT algorithm",
    "CLAIM_NOT_FOUND": "Claim not found in token payload",
    "INVALID_PAYLOAD": "Invalid payload format",
    "GENERATION_FAILED": "JWT token generation failed",
    "DECODING_FAILED": "JWT token decoding failed",
}

# Logging levels
LOG_LEVELS = {"DEBUG": "DEBUG", "INFO": "INFO", "WARN": "WARN", "ERROR": "ERROR"}
