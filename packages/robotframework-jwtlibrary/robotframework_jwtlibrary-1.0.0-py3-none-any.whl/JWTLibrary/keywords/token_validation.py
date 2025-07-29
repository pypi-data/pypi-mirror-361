"""Token validation keywords for JWT Library."""

from datetime import datetime, timezone
from typing import Any, Dict, Union

import jwt
from robot.api import logger
from robot.api.deco import keyword

from ..constants import DEFAULT_ALGORITHM
from ..exceptions import JWTTokenValidationError
from ..utils import parse_jwt_timestamp, validate_algorithm


class TokenValidationKeywords:
    """Keywords for JWT token validation."""

    @keyword("Verify JWT Token")
    def verify_jwt_token(
        self, token: str, secret_key: str, algorithm: str = None
    ) -> bool:
        """
        Verifies if a JWT token is valid and not expired.
        Arguments:
        - ``token``: JWT token string to verify
        - ``secret_key``: Secret key used for verification
        - ``algorithm``: JWT algorithm (default: HS256)
        Returns:
        - True if token is valid, False otherwise
        Examples:
        | ${is_valid}=    Verify JWT Token    ${token}    my_secret_key
        | Should Be True    ${is_valid}
        """
        try:
            algorithm = algorithm or DEFAULT_ALGORITHM
            validate_algorithm(algorithm)

            jwt.decode(token, secret_key, algorithms=[algorithm])
            logger.info("JWT token verification successful")
            return True
        except (
            jwt.ExpiredSignatureError,
            jwt.InvalidSignatureError,
            jwt.InvalidTokenError,
        ):
            logger.info("JWT token verification failed")
            return False
        except Exception as e:
            logger.error(f"JWT token verification error: {str(e)}")
            return False

    @keyword("Check JWT Expiration")
    def check_jwt_expiration(
        self, token: str, secret_key: str = None
    ) -> Dict[str, Any]:
        """
        Checks JWT token expiration details.
        Arguments:
        - ``token``: JWT token string
        - ``secret_key``: Secret key for verification (optional)
        Returns:
        - Dictionary with expiration information:
          - expires_at: Expiration timestamp
          - is_expired: Boolean indicating if token is expired
          - time_until_expiry: Seconds until expiration (negative if expired)
        Examples:
        | ${exp_info}=    Check JWT Expiration    ${token}
        | Should Be True    ${exp_info['is_expired']} == False
        """
        try:
            # Decode without verification to get expiration info
            payload = jwt.decode(token, options={"verify_signature": False})

            if "exp" not in payload:
                return {
                    "expires_at": None,
                    "is_expired": False,
                    "time_until_expiry": None,
                    "has_expiration": False,
                }
            exp_timestamp = payload["exp"]
            exp_datetime = parse_jwt_timestamp(exp_timestamp)
            current_time = datetime.now(tz=timezone.utc)
            # Ensure both datetimes are timezone-aware for comparison
            if exp_datetime.tzinfo is None:
                exp_datetime = exp_datetime.replace(tzinfo=timezone.utc)
            is_expired = current_time > exp_datetime
            time_until_expiry = (exp_datetime - current_time).total_seconds()
            expiration_info = {
                "expires_at": exp_datetime.isoformat(),
                "is_expired": is_expired,
                "time_until_expiry": time_until_expiry,
                "has_expiration": True,
            }
            logger.info(
                f"Token expiration check: expires in {time_until_expiry} seconds"
            )
            return expiration_info
        except Exception as e:
            error_msg = f"JWT expiration check failed: {str(e)}"
            logger.error(error_msg)
            raise JWTTokenValidationError(error_msg)

    @keyword("Validate JWT Claims")
    def validate_jwt_claims(
        self,
        token: str,
        expected_claims: Dict[str, Any],
        secret_key: str = None,
        verify_signature: bool = False,
    ) -> bool:
        """
        Validates that JWT token contains expected claims with correct values.
        Arguments:
        - ``token``: JWT token string
        - ``expected_claims``: Dictionary of expected claim key-value pairs
        - ``secret_key``: Secret key (required if verify_signature is True)
        - ``verify_signature``: Whether to verify token signature
        Returns:
        - True if all expected claims match, False otherwise

        Examples:
        | ${expected}=    Create Dictionary    user_id=123    role=admin
        | ${valid}=    Validate JWT Claims    ${token}    ${expected}
        | Should Be True    ${valid}
        """
        try:
            from .token_decoding import TokenDecodingKeywords

            decoder = TokenDecodingKeywords()

            # Get payload
            payload = decoder.decode_jwt_payload(
                token, secret_key, verify_signature=verify_signature
            )

            # Check each expected claim
            mismatched_claims = []
            missing_claims = []
            for claim_name, expected_value in expected_claims.items():
                if claim_name not in payload:
                    missing_claims.append(claim_name)
                elif payload[claim_name] != expected_value:
                    mismatched_claims.append(
                        {
                            "claim": claim_name,
                            "expected": expected_value,
                            "actual": payload[claim_name],
                        }
                    )

            if missing_claims or mismatched_claims:
                logger.info(
                    f"Claim validation failed - Missing: {missing_claims}, Mismatched: {mismatched_claims}"
                )
                return False

            logger.info(f"All {len(expected_claims)} claims validated successfully")
            return True

        except Exception as e:
            logger.error(f"JWT claims validation error: {str(e)}")
            return False

    @keyword("Check JWT Algorithm")
    def check_jwt_algorithm(self, token: str, expected_algorithm: str) -> bool:
        """
        Checks if JWT token uses expected algorithm.
        Arguments:
        - ``token``: JWT token string
        - ``expected_algorithm``: Expected algorithm (e.g., HS256, RS256)
        Returns:
        - True if algorithm matches, False otherwise
        Examples:
        | ${correct_alg}=    Check JWT Algorithm    ${token}    HS256
        | Should Be True    ${correct_alg}
        """
        try:
            from .token_decoding import TokenDecodingKeywords

            decoder = TokenDecodingKeywords()

            header = decoder.decode_jwt_header(token)
            actual_algorithm = header.get("alg")

            if actual_algorithm == expected_algorithm:
                logger.info(
                    f"JWT algorithm verification successful: {actual_algorithm}"
                )
                return True
            else:
                logger.info(
                    f"JWT algorithm mismatch - Expected: {expected_algorithm}, Actual: {actual_algorithm}"
                )
                return False

        except Exception as e:
            logger.error(f"JWT algorithm check error: {str(e)}")
            return False

    @keyword("Validate JWT Structure")
    def validate_jwt_structure(self, token: str) -> Dict[str, Any]:
        """
        Validates JWT token structure and returns detailed information.
        Arguments:
        - ``token``: JWT token string
        Returns:
        - Dictionary with structure validation results
        Examples:
        | ${structure}=    Validate JWT Structure    ${token}
        | Should Be True    ${structure['is_valid_structure']}
        """
        try:
            validation_result = {
                "is_valid_structure": False,
                "has_three_parts": False,
                "has_valid_header": False,
                "has_valid_payload": False,
                "header_info": None,
                "payload_info": None,
                "errors": [],
            }
            # Check if token has three parts
            parts = token.split(".")
            if len(parts) == 3:
                validation_result["has_three_parts"] = True
            else:
                validation_result["errors"].append(
                    f"Token has {len(parts)} parts, expected 3"
                )
                return validation_result

            try:
                from .token_decoding import TokenDecodingKeywords

                decoder = TokenDecodingKeywords()
                # Validate header
                header = decoder.decode_jwt_header(token)
                validation_result["has_valid_header"] = True
                validation_result["header_info"] = {
                    "algorithm": header.get("alg"),
                    "type": header.get("typ"),
                    "keys": list(header.keys()),
                }

            except Exception as e:
                validation_result["errors"].append(f"Invalid header: {str(e)}")

            try:
                # Validate payload
                payload = decoder.decode_jwt_payload_unsafe(token)
                validation_result["has_valid_payload"] = True
                validation_result["payload_info"] = {
                    "claims_count": len(payload),
                    "has_expiration": "exp" in payload,
                    "has_issued_at": "iat" in payload,
                    "claims": list(payload.keys()),
                }

            except Exception as e:
                validation_result["errors"].append(f"Invalid payload: {str(e)}")

            # Overall validation
            validation_result["is_valid_structure"] = (
                validation_result["has_three_parts"]
                and validation_result["has_valid_header"]
                and validation_result["has_valid_payload"]
            )

            logger.info(
                f"JWT structure validation: {'Valid' if validation_result['is_valid_structure'] else 'Invalid'}"
            )
            return validation_result

        except Exception as e:
            error_msg = f"JWT structure validation failed: {str(e)}"
            logger.error(error_msg)
            raise JWTTokenValidationError(error_msg)

    @keyword("Check JWT Not Before")
    def check_jwt_not_before(self, token: str) -> Dict[str, Any]:
        """
        Checks JWT token 'not before' (nbf) claim.
        Arguments:
        - ``token``: JWT token string
        Returns:
        - Dictionary with 'not before' information
        Examples:
        | ${nbf_info}=    Check JWT Not Before    ${token}
        | Should Be True    ${nbf_info['is_active']}
        """
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            if "nbf" not in payload:
                return {
                    "not_before": None,
                    "is_active": True,
                    "time_until_active": 0,
                    "has_not_before": False,
                }
            nbf_timestamp = payload["nbf"]
            nbf_datetime = parse_jwt_timestamp(nbf_timestamp)
            current_time = datetime.now()
            is_active = current_time >= nbf_datetime
            time_until_active = (nbf_datetime - current_time).total_seconds()
            nbf_info = {
                "not_before": nbf_datetime.isoformat(),
                "is_active": is_active,
                "time_until_active": max(0, time_until_active),
                "has_not_before": True,
            }
            logger.info(
                f"JWT not before check: {'Active' if is_active else f'Active in {time_until_active} seconds'}"
            )
            return nbf_info
        except Exception as e:
            error_msg = f"JWT not before check failed: {str(e)}"
            logger.error(error_msg)
            raise JWTTokenValidationError(error_msg)

    @keyword("Validate JWT Audience")
    def validate_jwt_audience(
        self,
        token: str,
        expected_audience: Union[str, list],
        secret_key: str = None,
        verify_signature: bool = False,
    ) -> bool:
        """
        Validates JWT token audience claim.
        Arguments:
        - ``token``: JWT token string
        - ``expected_audience``: Expected audience (string or list)
        - ``secret_key``: Secret key (required if verify_signature is True)
        - ``verify_signature``: Whether to verify token signature
        Returns:
        - True if audience matches, False otherwise
        Examples:
        | ${valid_aud}=    Validate JWT Audience    ${token}    my-api
        | ${valid_aud}=    Validate JWT Audience    ${token}    ["api1", "api2"]
        """
        try:
            from .token_decoding import TokenDecodingKeywords

            decoder = TokenDecodingKeywords()
            payload = decoder.decode_jwt_payload(
                token, secret_key, verify_signature=verify_signature
            )
            if "aud" not in payload:
                logger.info("Token does not contain audience claim")
                return False
            actual_audience = payload["aud"]
            # Handle different audience formats
            if isinstance(expected_audience, str):
                if isinstance(actual_audience, str):
                    is_valid = actual_audience == expected_audience
                elif isinstance(actual_audience, list):
                    is_valid = expected_audience in actual_audience
                else:
                    is_valid = False
            elif isinstance(expected_audience, list):
                if isinstance(actual_audience, str):
                    is_valid = actual_audience in expected_audience
                elif isinstance(actual_audience, list):
                    is_valid = any(aud in expected_audience for aud in actual_audience)
                else:
                    is_valid = False
            else:
                is_valid = False
            logger.info(
                f"JWT audience validation: " f"{'Valid' if is_valid else 'Invalid'}"
            )
            return is_valid
        except Exception as e:
            logger.error(f"JWT audience validation error: {str(e)}")
            return False
