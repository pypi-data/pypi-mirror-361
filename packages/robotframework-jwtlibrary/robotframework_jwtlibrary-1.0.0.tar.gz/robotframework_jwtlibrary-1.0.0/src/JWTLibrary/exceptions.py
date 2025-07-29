"""Custom exceptions for JWT Library."""


class JWTLibraryError(Exception):
    """Base exception for JWT Library errors."""

    pass


class JWTTokenGenerationError(JWTLibraryError):
    """Raised when JWT token generation fails."""

    pass


class JWTTokenDecodingError(JWTLibraryError):
    """Raised when JWT token decoding fails."""

    pass


class JWTTokenValidationError(JWTLibraryError):
    """Raised when JWT token validation fails."""

    pass


class JWTExpiredTokenError(JWTLibraryError):
    """Raised when JWT token has expired."""

    pass


class JWTInvalidSignatureError(JWTLibraryError):
    """Raised when JWT token signature is invalid."""

    pass


class JWTInvalidTokenError(JWTLibraryError):
    """Raised when JWT token format is invalid."""

    pass


class JWTClaimNotFoundError(JWTLibraryError):
    """Raised when a requested claim is not found in token."""

    pass


class JWTInvalidAlgorithmError(JWTLibraryError):
    """Raised when an unsupported algorithm is specified."""

    pass
