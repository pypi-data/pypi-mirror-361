"""Token decoding keywords for JWT Library."""

from typing import Any, Dict

import jwt
from robot.api import logger
from robot.api.deco import keyword

from ..constants import DEFAULT_ALGORITHM
from ..exceptions import (
    JWTClaimNotFoundError,
    JWTExpiredTokenError,
    JWTInvalidSignatureError,
    JWTTokenDecodingError,
)
from ..utils import (
    decode_jwt_header_unsafe,
    decode_jwt_payload_unsafe,
    safe_json_dumps,
    validate_algorithm,
)


class TokenDecodingKeywords:
    """Keywords for JWT token decoding."""

    @keyword("Decode JWT Payload")
    def decode_jwt_payload(
        self,
        token: str,
        secret_key: str = None,
        algorithm: str = None,
        verify_signature: bool = True,
    ) -> Dict[str, Any]:
        """
        Decodes a JWT token and returns the payload.

        Arguments:
        - ``token``: JWT token string to decode
        - ``secret_key``: Secret key used for verification
        - ``algorithm``: JWT algorithm (default: HS256)
        - ``verify_signature``: Whether to verify token signature (default: True)

        Returns:
        - Dictionary containing the decoded payload

        Examples:
        | ${payload}=    Decode JWT Payload    ${token}    my_secret_key
        | ${payload}=    Decode JWT Payload    ${token}    my_secret_key    algorithm=HS512
        | ${payload}=    Decode JWT Payload    ${token}    verify_signature=False
        """
        try:
            if verify_signature:
                if not secret_key:
                    raise JWTTokenDecodingError(
                        "Secret key is required when verify_signature is True"
                    )

                algorithm = algorithm or DEFAULT_ALGORITHM
                validate_algorithm(algorithm)
                algorithms = [algorithm]

                # Decode with verification
                payload = jwt.decode(token, secret_key, algorithms=algorithms)
            else:
                # Decode without verification
                payload = jwt.decode(token, options={"verify_signature": False})

            logger.info("JWT token decoded successfully")
            logger.debug(f"Decoded payload: {safe_json_dumps(payload, indent=2)}")

            return payload

        except jwt.ExpiredSignatureError:
            error_msg = "JWT token has expired"
            logger.error(error_msg)
            raise JWTExpiredTokenError(error_msg)
        except jwt.InvalidSignatureError:
            error_msg = "JWT token signature verification failed"
            logger.error(error_msg)
            raise JWTInvalidSignatureError(error_msg)
        except jwt.InvalidTokenError as e:
            error_msg = f"Invalid JWT token: {str(e)}"
            logger.error(error_msg)
            raise JWTTokenDecodingError(error_msg)
        except Exception as e:
            error_msg = f"JWT token decoding failed: {str(e)}"
            logger.error(error_msg)
            raise JWTTokenDecodingError(error_msg)

    @keyword("Decode JWT Header")
    def decode_jwt_header(self, token: str) -> Dict[str, Any]:
        """
        Decodes JWT token header without verification.

        Arguments:
        - ``token``: JWT token string

        Returns:
        - Dictionary containing the token header

        Examples:
        | ${header}=    Decode JWT Header    ${token}
        """
        try:
            header = decode_jwt_header_unsafe(token)
            logger.info("JWT header decoded successfully")
            logger.debug(f"Header: {safe_json_dumps(header, indent=2)}")
            return header
        except Exception as e:
            error_msg = f"JWT header decoding failed: {str(e)}"
            logger.error(error_msg)
            raise JWTTokenDecodingError(error_msg)

    @keyword("Get JWT Claim")
    def get_jwt_claim(
        self,
        token: str,
        claim_name: str,
        secret_key: str = None,
        verify_signature: bool = False,
    ) -> Any:
        """
        Extracts a specific claim from JWT token payload.

        Arguments:
        - ``token``: JWT token string
        - ``claim_name``: Name of the claim to extract
        - ``secret_key``: Secret key (required if verify_signature is True)
        - ``verify_signature``: Whether to verify token signature

        Returns:
        - Value of the specified claim

        Examples:
        | ${user_id}=    Get JWT Claim    ${token}    user_id
        | ${role}=    Get JWT Claim    ${token}    role    secret_key=my_secret_key    verify_signature=True
        """
        try:
            if verify_signature and not secret_key:
                raise JWTTokenDecodingError(
                    "Secret key is required when verify_signature is True"
                )

            # Get payload
            payload = self.decode_jwt_payload(
                token, secret_key, verify_signature=verify_signature
            )

            if claim_name not in payload:
                raise JWTClaimNotFoundError(
                    f"Claim '{claim_name}' not found in token payload"
                )

            claim_value = payload[claim_name]
            logger.info(f"Retrieved claim '{claim_name}': {claim_value}")
            return claim_value

        except (JWTTokenDecodingError, JWTClaimNotFoundError):
            raise
        except Exception as e:
            error_msg = f"Failed to get JWT claim '{claim_name}': {str(e)}"
            logger.error(error_msg)
            raise JWTTokenDecodingError(error_msg)

    @keyword("Get Multiple JWT Claims")
    def get_multiple_jwt_claims(
        self,
        token: str,
        claim_names: list,
        secret_key: str = None,
        verify_signature: bool = False,
    ) -> Dict[str, Any]:
        """
        Extracts multiple claims from JWT token payload.

        Arguments:
        - ``token``: JWT token string
        - ``claim_names``: List of claim names to extract
        - ``secret_key``: Secret key (required if verify_signature is True)
        - ``verify_signature``: Whether to verify token signature

        Returns:
        - Dictionary with claim names as keys and claim values

        Examples:
        | ${claims}=    Get Multiple JWT Claims    ${token}    ["user_id", "role", "email"]
        | ${claims}=    Get Multiple JWT Claims    ${token}    ["sub", "iat"]    my_secret_key    True
        """
        try:
            # Get payload
            payload = self.decode_jwt_payload(
                token, secret_key, verify_signature=verify_signature
            )

            claims = {}
            missing_claims = []

            for claim_name in claim_names:
                if claim_name in payload:
                    claims[claim_name] = payload[claim_name]
                else:
                    missing_claims.append(claim_name)

            if missing_claims:
                logger.warn(f"Claims not found: {missing_claims}")

            logger.info(f"Retrieved {len(claims)} claims: {list(claims.keys())}")
            return claims

        except JWTTokenDecodingError:
            raise
        except Exception as e:
            error_msg = f"Failed to get multiple JWT claims: {str(e)}"
            logger.error(error_msg)
            raise JWTTokenDecodingError(error_msg)

    @keyword("Decode JWT Payload Unsafe")
    def decode_jwt_payload_unsafe(self, token: str) -> Dict[str, Any]:
        """
        Decodes JWT token payload without any verification (unsafe).

        Arguments:
        - ``token``: JWT token string

        Returns:
        - Dictionary containing the decoded payload

        Examples:
        | ${payload}=    Decode JWT Payload Unsafe    ${token}

        Note: This keyword does not verify the token signature or expiration.
        Use only when you need to inspect token contents without validation.
        """
        try:
            payload = decode_jwt_payload_unsafe(token)
            logger.info("JWT payload decoded without verification")
            logger.debug(f"Payload: {safe_json_dumps(payload, indent=2)}")
            return payload
        except Exception as e:
            error_msg = f"JWT payload unsafe decoding failed: {str(e)}"
            logger.error(error_msg)
            raise JWTTokenDecodingError(error_msg)

    @keyword("Extract All JWT Claims")
    def extract_all_jwt_claims(
        self, token: str, secret_key: str = None, verify_signature: bool = False
    ) -> Dict[str, Any]:
        """
        Extracts all claims from JWT token payload with metadata.

        Arguments:
        - ``token``: JWT token string
        - ``secret_key``: Secret key (required if verify_signature is True)
        - ``verify_signature``: Whether to verify token signature

        Returns:
        - Dictionary with all claims and metadata

        Examples:
        | ${all_claims}=    Extract All JWT Claims    ${token}
        | ${all_claims}=    Extract All JWT Claims    ${token}    my_secret_key    True
        """
        from ..constants import STANDARD_CLAIMS

        try:
            # Get payload and header
            payload = self.decode_jwt_payload(
                token, secret_key, verify_signature=verify_signature
            )
            header = self.decode_jwt_header(token)

            # Separate standard and custom claims
            standard_claims = {}
            custom_claims = {}

            for key, value in payload.items():
                if key in STANDARD_CLAIMS:
                    standard_claims[key] = value
                else:
                    custom_claims[key] = value

            result = {
                "header": header,
                "standard_claims": standard_claims,
                "custom_claims": custom_claims,
                "all_payload": payload,
                "total_claims": len(payload),
            }

            logger.info(f"Extracted all claims: {len(payload)} total claims")
            return result

        except JWTTokenDecodingError:
            raise
        except Exception as e:
            error_msg = f"Failed to extract all JWT claims: {str(e)}"
            logger.error(error_msg)
            raise JWTTokenDecodingError(error_msg)
