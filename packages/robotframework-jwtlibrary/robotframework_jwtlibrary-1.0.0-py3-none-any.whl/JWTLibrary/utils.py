"""Utility functions for JWT Library."""

import base64
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union

from .constants import STANDARD_CLAIMS, SUPPORTED_ALGORITHMS
from .exceptions import JWTInvalidAlgorithmError, JWTInvalidTokenError


def validate_algorithm(algorithm: str) -> str:
    """
    Validates if the algorithm is supported.
    Args:
        algorithm: JWT algorithm to validate
    Returns:
        Validated algorithm string
    Raises:
        JWTInvalidAlgorithmError: If algorithm is not supported
    """
    if algorithm not in SUPPORTED_ALGORITHMS:
        raise JWTInvalidAlgorithmError(
            f"Algorithm '{algorithm}' is not supported. "
            f"Supported algorithms: {', '.join(SUPPORTED_ALGORITHMS)}"
        )
    return algorithm


def format_datetime_for_jwt(dt: datetime) -> int:
    """
    Converts datetime to JWT timestamp format.
    Args:
        dt: Datetime object
    Returns:
        Unix timestamp as integer
    """
    return int(dt.timestamp())


def parse_jwt_timestamp(timestamp: Union[int, float]) -> datetime:
    """
    Converts JWT timestamp to datetime object.
    Args:
        timestamp: Unix timestamp
    Returns:
        Datetime object
    """
    return datetime.fromtimestamp(timestamp)


def safe_json_dumps(obj: Any, **kwargs) -> str:
    """
    Safely converts object to JSON string with datetime handling.
    Args:
        obj: Object to convert
        **kwargs: Additional arguments for json.dumps
    Returns:
        JSON string
    """

    def default_serializer(o):
        if isinstance(o, datetime):
            return o.isoformat()
        raise TypeError(f"Object of type {type(o)} is not JSON serializable")

    return json.dumps(obj, default=default_serializer, **kwargs)


def mask_sensitive_data(
    data: Dict[str, Any], sensitive_keys: list = None
) -> Dict[str, Any]:
    """
    Masks sensitive data in dictionary for logging.
    Args:
        data: Dictionary containing data
        sensitive_keys: List of keys to mask (default: common sensitive keys)
    Returns:
        Dictionary with masked sensitive values
    """
    if sensitive_keys is None:
        sensitive_keys = ["password", "secret", "key", "token", "auth"]
    masked_data = data.copy()
    for key, value in masked_data.items():
        if any(
            sensitive_key.lower() in key.lower() for sensitive_key in sensitive_keys
        ):
            if isinstance(value, str) and len(value) > 8:
                masked_data[key] = value[:4] + "*" * (len(value) - 8) + value[-4:]
            else:
                masked_data[key] = "***"
    return masked_data


def validate_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates and sanitizes JWT payload.
    Args:
        payload: JWT payload dictionary
    Returns:
        Validated payload
    Raises:
        JWTInvalidTokenError: If payload is invalid
    """
    if not isinstance(payload, dict):
        raise JWTInvalidTokenError("Payload must be a dictionary")
    # Check for reserved claims with wrong types
    for claim, description in STANDARD_CLAIMS.items():
        if claim in payload:
            value = payload[claim]
            # Check timestamp claims
            if claim in ["exp", "nbf", "iat"]:
                if not isinstance(value, (int, float, datetime)):
                    raise JWTInvalidTokenError(
                        f"Claim '{claim}' ({description}) must be a number or datetime"
                    )
                # Convert datetime to timestamp
                if isinstance(value, datetime):
                    payload[claim] = format_datetime_for_jwt(value)
    return payload


def calculate_expiration(
    expiration_hours: Optional[int] = None, base_time: Optional[datetime] = None
) -> datetime:
    """
    Calculates expiration datetime.
    Args:
        expiration_hours: Hours until expiration
        base_time: Base time to calculate from (default: now)
    Returns:
        Expiration datetime
    """
    if base_time is None:
        base_time = datetime.now(tz=timezone.utc)
    if expiration_hours is None:
        from .constants import DEFAULT_EXPIRATION_HOURS

        expiration_hours = DEFAULT_EXPIRATION_HOURS
    return base_time + timedelta(hours=expiration_hours)


def decode_jwt_header_unsafe(token: str) -> Dict[str, Any]:
    """
    Decodes JWT header without verification (unsafe).
    Args:
        token: JWT token string
    Returns:
        Header dictionary
    Raises:
        JWTInvalidTokenError: If token format is invalid
    """
    try:
        # Split token into parts
        parts = token.split(".")
        if len(parts) != 3:
            raise JWTInvalidTokenError("Invalid JWT token format")
        # Decode header (first part)
        header_b64 = parts[0]
        # Add padding if needed
        padding = len(header_b64) % 4
        if padding:
            header_b64 += "=" * (4 - padding)
        header_bytes = base64.urlsafe_b64decode(header_b64)
        header = json.loads(header_bytes.decode("utf-8"))
        return header
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as e:
        raise JWTInvalidTokenError(f"Failed to decode JWT header: {str(e)}")


def decode_jwt_payload_unsafe(token: str) -> Dict[str, Any]:
    """
    Decodes JWT payload without verification (unsafe).
    Args:
        token: JWT token string
    Returns:
        Payload dictionary
    Raises:
        JWTInvalidTokenError: If token format is invalid
    """
    try:
        # Split token into parts
        parts = token.split(".")
        if len(parts) != 3:
            raise JWTInvalidTokenError("Invalid JWT token format")
        # Decode payload (second part)
        payload_b64 = parts[1]
        # Add padding if needed
        padding = len(payload_b64) % 4
        if padding:
            payload_b64 += "=" * (4 - padding)
        payload_bytes = base64.urlsafe_b64decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))
        return payload
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as e:
        raise JWTInvalidTokenError(f"Failed to decode JWT payload: {str(e)}")


def get_token_info(token: str) -> Dict[str, Any]:
    """
    Gets basic information about a JWT token without verification.
    Args:
        token: JWT token string
    Returns:
        Dictionary with token information
    """
    try:
        header = decode_jwt_header_unsafe(token)
        payload = decode_jwt_payload_unsafe(token)
        # Extract basic info
        info = {
            "algorithm": header.get("alg"),
            "type": header.get("typ"),
            "issued_at": payload.get("iat"),
            "expires_at": payload.get("exp"),
            "not_before": payload.get("nbf"),
            "issuer": payload.get("iss"),
            "subject": payload.get("sub"),
            "audience": payload.get("aud"),
            "jwt_id": payload.get("jti"),
            "claims_count": len(payload),
            "header_params": list(header.keys()),
            "payload_claims": list(payload.keys()),
        }
        # Add expiration status if exp claim exists
        if info["expires_at"]:
            exp_dt = parse_jwt_timestamp(info["expires_at"])
            now = datetime.utcnow()
            info["is_expired"] = now > exp_dt
            info["time_until_expiry"] = (exp_dt - now).total_seconds()
        return info
    except Exception as e:
        raise JWTInvalidTokenError(f"Failed to get token info: {str(e)}")
