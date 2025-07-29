"""Utility keywords for JWT Library."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Union

from robot.api import logger
from robot.api.deco import keyword

from ..utils import get_token_info, safe_json_dumps


class UtilityKeywords:
    """Utility keywords for JWT operations."""

    @keyword("Create JWT Payload")
    def create_jwt_payload(self, **kwargs) -> Dict[str, Any]:
        """
        Creates a JWT payload dictionary from keyword arguments.
        Arguments:
        - ``**kwargs``: Key-value pairs to include in payload
        Returns:
        - Dictionary containing the payload
        Examples:
        | ${payload}=    Create JWT Payload    user_id=123
         role=admin    email=user@example.com
        """
        payload = dict(kwargs)
        logger.info(f"Created JWT payload with keys: {list(payload.keys())}")
        return payload

    @keyword("Get JWT Token Info")
    def get_jwt_token_info(self, token: str) -> Dict[str, Any]:
        """
        Gets comprehensive information about a JWT token without verification.
        Arguments:
        - ``token``: JWT token string
        Returns:
        - Dictionary with detailed token information
        Examples:
        | ${info}=    Get JWT Token Info    ${token}
        | Log    Token algorithm: ${info['algorithm']}
        """
        try:
            info = get_token_info(token)
            logger.info("JWT token information retrieved successfully")
            logger.debug(f"Token info: {safe_json_dumps(info, indent=2)}")
            return info
        except Exception as e:
            logger.error(f"Failed to get JWT token info: {str(e)}")
            raise

    @keyword("Compare JWT Tokens")
    def compare_jwt_tokens(self, token1: str, token2: str) -> Dict[str, Any]:
        """
        Compares two JWT tokens and returns differences.
        Arguments:
        - ``token1``: First JWT token
        - ``token2``: Second JWT token
        Returns:
        - Dictionary with comparison results
        Examples:
        | ${comparison}=    Compare JWT Tokens    ${token1}    ${token2}
        | Should Be True    ${comparison['are_identical']}
        """
        try:
            from .token_decoding import TokenDecodingKeywords

            decoder = TokenDecodingKeywords()
            # Decode both tokens without verification
            payload1 = decoder.decode_jwt_payload_unsafe(token1)
            payload2 = decoder.decode_jwt_payload_unsafe(token2)
            header1 = decoder.decode_jwt_header(token1)
            header2 = decoder.decode_jwt_header(token2)
            # Compare payloads
            payload_differences = {}
            all_keys = set(payload1.keys()) | set(payload2.keys())
            for key in all_keys:
                val1 = payload1.get(key, "<MISSING>")
                val2 = payload2.get(key, "<MISSING>")
                if val1 != val2:
                    payload_differences[key] = {"token1": val1, "token2": val2}
            # Compare headers
            header_differences = {}
            all_header_keys = set(header1.keys()) | set(header2.keys())
            for key in all_header_keys:
                val1 = header1.get(key, "<MISSING>")
                val2 = header2.get(key, "<MISSING>")
                if val1 != val2:
                    header_differences[key] = {"token1": val1, "token2": val2}
            are_identical = (
                len(payload_differences) == 0 and len(header_differences) == 0
            )
            comparison_result = {
                "are_identical": are_identical,
                "payload_differences": payload_differences,
                "header_differences": header_differences,
                "payload_differences_count": len(payload_differences),
                "header_differences_count": len(header_differences),
            }
            logger.info(
                f"JWT token comparison: "
                f"{'Identical' if are_identical else 'Different'}"
            )
            return comparison_result
        except Exception as e:
            logger.error(f"JWT token comparison failed: {str(e)}")
            raise

    @keyword("Extract JWT Timestamps")
    def extract_jwt_timestamps(self, token: str) -> Dict[str, Any]:
        """
        Extracts all timestamp claims from JWT token.
        Arguments:
        - ``token``: JWT token string
        Returns:
        - Dictionary with timestamp information
        Examples:
        | ${timestamps}=    Extract JWT Timestamps    ${token}
        | Log    Token issued at: ${timestamps['issued_at']}
        """
        try:
            from .token_decoding import TokenDecodingKeywords

            decoder = TokenDecodingKeywords()
            payload = decoder.decode_jwt_payload_unsafe(token)
            timestamps = {}
            # Extract timestamp claims
            timestamp_claims = ["iat", "exp", "nbf"]
            for claim in timestamp_claims:
                if claim in payload:
                    timestamp = payload[claim]
                    if isinstance(timestamp, (int, float)):
                        dt = datetime.fromtimestamp(timestamp)
                        timestamps[claim] = {
                            "timestamp": timestamp,
                            "datetime": dt.isoformat(),
                            "human_readable": dt.strftime("%Y-%m-%d %H:%M:%S UTC"),
                        }
            # Add computed fields
            current_time = datetime.utcnow()
            if "iat" in timestamps:
                issued_dt = datetime.fromtimestamp(timestamps["iat"]["timestamp"])
                timestamps["age_seconds"] = (current_time - issued_dt).total_seconds()
            if "exp" in timestamps:
                exp_dt = datetime.fromtimestamp(timestamps["exp"]["timestamp"])
                timestamps["expires_in_seconds"] = (
                    exp_dt - current_time
                ).total_seconds()
                timestamps["is_expired"] = current_time > exp_dt
            logger.info(f"Extracted {len(timestamps)} timestamp claims from JWT")
            return timestamps
        except Exception as e:
            logger.error(f"JWT timestamp extraction failed: {str(e)}")
            raise

    @keyword("Generate Current Timestamp")
    def generate_current_timestamp(self) -> int:
        """
        Generates current UTC timestamp for JWT claims.
        Returns:
        - Current timestamp as integer
        Examples:
        | ${current_time}=    Generate Current Timestamp
        | ${payload}=    Create Dictionary    iat=${current_time}
        """
        timestamp = int(datetime.now(tz=timezone.utc).timestamp())
        logger.info(f"Generated current timestamp: {timestamp}")
        return timestamp

    @keyword("Generate Future Timestamp")
    def generate_future_timestamp(
        self, hours: int = 24, minutes: int = 0, seconds: int = 0
    ) -> int:
        """
        Generates future timestamp for JWT expiration claims.
        Arguments:
        - ``hours``: Hours to add (default: 24)
        - ``minutes``: Minutes to add (default: 0)
        - ``seconds``: Seconds to add (default: 0)
        Returns:
        - Future timestamp as integer
        Examples:
        | ${exp_time}=    Generate Future Timestamp    hours=1
        | ${exp_time}=    Generate Future Timestamp    hours=0    minutes=30
        """
        future_time = datetime.now(tz=timezone.utc) + timedelta(
            hours=hours, minutes=minutes, seconds=seconds
        )
        timestamp = int(future_time.timestamp())
        logger.info(
            f"Generated future timestamp: {timestamp} "
            f"({hours}h {minutes}m {seconds}s from now)"
        )
        return timestamp

    @keyword("Convert Timestamp To Datetime")
    def convert_timestamp_to_datetime(self, timestamp: Union[int, float]) -> str:
        """
        Converts Unix timestamp to human-readable datetime string.
        Arguments:
        - ``timestamp``: Unix timestamp
        Returns:
        - ISO format datetime string
        Examples:
        | ${datetime_str}=    Convert Timestamp To Datetime    1640995200
        """
        try:
            dt = datetime.fromtimestamp(timestamp)
            datetime_str = dt.isoformat()
            logger.info(f"Converted timestamp {timestamp} to {datetime_str}")
            return datetime_str
        except Exception as e:
            logger.error(f"Timestamp conversion failed: {str(e)}")
            raise

    @keyword("Create JWT Header")
    def create_jwt_header(self, algorithm: str = "HS256", **kwargs) -> Dict[str, Any]:
        """
        Creates a JWT header dictionary.
        Arguments:
        - ``algorithm``: JWT algorithm (default: HS256)
        - ``**kwargs``: Additional header parameters
        Returns:
        - Dictionary containing the header
        Examples:
        | ${header}=    Create JWT Header    algorithm=RS256    kid=key1
        """
        header = {"alg": algorithm, "typ": "JWT"}
        header.update(kwargs)
        logger.info(f"Created JWT header with algorithm: {algorithm}")
        return header

    @keyword("Format JWT Claims For Logging")
    def format_jwt_claims_for_logging(
        self, claims: Dict[str, Any], mask_sensitive: bool = True
    ) -> str:
        """
        Formats JWT claims for safe logging.
        Arguments:
        - ``claims``: Dictionary of JWT claims
        - ``mask_sensitive``: Whether to mask sensitive values
        Returns:
        - Formatted string suitable for logging
        Examples:
        | ${log_str}=    Format JWT Claims For Logging    ${claims}
        | Log    Claims: ${log_str}
        """
        try:
            if mask_sensitive:
                from ..utils import mask_sensitive_data

                safe_claims = mask_sensitive_data(claims)
            else:
                safe_claims = claims
            formatted = safe_json_dumps(safe_claims, indent=2)
            logger.debug("Formatted JWT claims for logging")
            return formatted
        except Exception as e:
            logger.error(f"JWT claims formatting failed: {str(e)}")
            return str(claims)

    @keyword("Validate JWT Claim Types")
    def validate_jwt_claim_types(self, claims: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates JWT claim data types.
        Arguments:
        - ``claims``: Dictionary of JWT claims
        Returns:
        - Dictionary with validation results
        Examples:
        | ${validation}=    Validate JWT Claim Types    ${claims}
        | Should Be True    ${validation['is_valid']}
        """
        validation_result = {"is_valid": True, "errors": [], "warnings": []}
        # Check standard claim types
        type_expectations = {
            "iss": str,  # issuer
            "sub": str,  # subject
            "aud": (str, list),  # audience
            "exp": (int, float),  # expiration
            "nbf": (int, float),  # not before
            "iat": (int, float),  # issued at
            "jti": str,  # JWT ID
        }
        for claim_name, claim_value in claims.items():
            if claim_name in type_expectations:
                expected_type = type_expectations[claim_name]
                if not isinstance(claim_value, expected_type):
                    validation_result["errors"].append(
                        f"Claim '{claim_name}' should be {expected_type}"
                        f", got {type(claim_value)}"
                    )
                    validation_result["is_valid"] = False
        # Additional validations
        if "exp" in claims and "iat" in claims:
            if claims["exp"] <= claims["iat"]:
                validation_result["warnings"].append(
                    "Expiration time should be after issued at time"
                )
        logger.info(
            f"JWT claim type validation:"
            f" {'Valid' if validation_result['is_valid'] else 'Invalid'}"
        )
        return validation_result
