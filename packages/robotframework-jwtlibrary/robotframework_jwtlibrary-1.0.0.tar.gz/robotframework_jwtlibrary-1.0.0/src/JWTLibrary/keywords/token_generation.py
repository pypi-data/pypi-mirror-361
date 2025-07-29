"""Token generation keywords for JWT Library."""

from datetime import datetime, timezone
from typing import Any, Dict

import jwt
from robot.api import logger
from robot.api.deco import keyword

from ..constants import DEFAULT_ALGORITHM, DEFAULT_EXPIRATION_HOURS
from ..exceptions import JWTTokenGenerationError
from ..utils import (
    calculate_expiration,
    safe_json_dumps,
    validate_algorithm,
    validate_payload,
)


class TokenGenerationKeywords:
    """Keywords for JWT token generation."""

    @keyword("Generate JWT Token")
    def generate_jwt_token(
        self,
        payload: Dict[str, Any],
        secret_key: str,
        algorithm: str = None,
        expiration_hours: int = None,
    ) -> str:
        """
        Generates a JWT token with the given payload and secret key.

        Arguments:
        - ``payload``: Dictionary containing the token payload data
        - ``secret_key``: Secret key used for signing the token
        - ``algorithm``: JWT algorithm (default: HS256)
        - ``expiration_hours``: Token expiration time in hours (default: 24)

        Returns:
        - JWT token as string

        Examples:
        | ${payload}=    Create Dictionary    user_id=123    role=admin
        | ${token}=    Generate JWT Token    ${payload}    my_secret_key
        | ${token}=    Generate JWT Token    ${payload}    my_secret_key    algorithm=HS512
        | ${token}=    Generate JWT Token    ${payload}    my_secret_key    expiration_hours=1
        """
        try:
            # Validate inputs
            algorithm = algorithm or DEFAULT_ALGORITHM
            validate_algorithm(algorithm)

            expiration_hours = expiration_hours or DEFAULT_EXPIRATION_HOURS

            # Create a copy of payload to avoid modifying the original
            token_payload = payload.copy()

            # Validate and sanitize payload
            token_payload = validate_payload(token_payload)

            # Add standard JWT claims
            now = datetime.now(tz=timezone.utc)

            # Only add standard claims if they don't already exist
            if "iat" not in token_payload:
                token_payload["iat"] = now
            if "exp" not in token_payload:
                token_payload["exp"] = calculate_expiration(expiration_hours, now)
            if "nbf" not in token_payload:
                token_payload["nbf"] = now

            # Generate the token
            token = jwt.encode(token_payload, secret_key, algorithm=algorithm)

            logger.info(f"JWT token generated successfully with algorithm: {algorithm}")
            logger.debug(f"Token payload: {safe_json_dumps(payload, indent=2)}")

            return token

        except Exception as e:
            error_msg = f"JWT token generation failed: {str(e)}"
            logger.error(error_msg)
            raise JWTTokenGenerationError(error_msg)

    @keyword("Generate JWT Token With Claims")
    def generate_jwt_token_with_claims(
        self,
        secret_key: str,
        algorithm: str = None,
        expiration_hours: int = None,
        **claims,
    ) -> str:
        """
        Generates a JWT token with individual claims as keyword arguments.

        Arguments:
        - ``secret_key``: Secret key used for signing the token
        - ``algorithm``: JWT algorithm (default: HS256)
        - ``expiration_hours``: Token expiration time in hours (default: 24)
        - ``**claims``: Individual claims as keyword arguments

        Returns:
        - JWT token as string

        Examples:
        | ${token}=    Generate JWT Token With Claims    my_secret_key    user_id=123    role=admin
        | ${token}=    Generate JWT Token With Claims    my_secret_key    algorithm=HS512    user_id=456
        | ${token}=    Generate JWT Token With Claims    my_secret_key    expiration_hours=1    email=test@example.com
        """
        payload = dict(claims)
        return self.generate_jwt_token(payload, secret_key, algorithm, expiration_hours)

    @keyword("Generate JWT Token Without Expiration")
    def generate_jwt_token_without_expiration(
        self, payload: Dict[str, Any], secret_key: str, algorithm: str = None
    ) -> str:
        """
        Generates a JWT token without expiration claim.

        Arguments:
        - ``payload``: Dictionary containing the token payload data
        - ``secret_key``: Secret key used for signing the token
        - ``algorithm``: JWT algorithm (default: HS256)

        Returns:
        - JWT token as string

        Examples:
        | ${payload}=    Create Dictionary    user_id=123    role=admin
        | ${token}=    Generate JWT Token Without Expiration    ${payload}    my_secret_key
        """
        try:
            algorithm = algorithm or DEFAULT_ALGORITHM
            validate_algorithm(algorithm)

            # Create a copy and validate payload
            token_payload = validate_payload(payload.copy())

            # Add only iat and nbf, no exp
            now = datetime.utcnow()
            if "iat" not in token_payload:
                token_payload["iat"] = now
            if "nbf" not in token_payload:
                token_payload["nbf"] = now

            # Ensure no exp claim
            token_payload.pop("exp", None)

            # Generate the token
            token = jwt.encode(token_payload, secret_key, algorithm=algorithm)

            logger.info(f"JWT token without expiration generated successfully")
            logger.debug(f"Token payload: {safe_json_dumps(payload, indent=2)}")

            return token

        except Exception as e:
            error_msg = f"JWT token generation without expiration failed: {str(e)}"
            logger.error(error_msg)
            raise JWTTokenGenerationError(error_msg)

    @keyword("Generate JWT Token With Custom Expiration")
    def generate_jwt_token_with_custom_expiration(
        self,
        payload: Dict[str, Any],
        secret_key: str,
        expiration_datetime: datetime,
        algorithm: str = None,
    ) -> str:
        """
        Generates a JWT token with a specific expiration datetime.

        Arguments:
        - ``payload``: Dictionary containing the token payload data
        - ``secret_key``: Secret key used for signing the token
        - ``expiration_datetime``: Specific expiration datetime
        - ``algorithm``: JWT algorithm (default: HS256)

        Returns:
        - JWT token as string

        Examples:
        | ${exp_time}=    Add Time To Date    ${current_date}    2 hours
        | ${payload}=    Create Dictionary    user_id=123
        | ${token}=    Generate JWT Token With Custom Expiration    ${payload}    my_secret_key    ${exp_time}
        """
        try:
            algorithm = algorithm or DEFAULT_ALGORITHM
            validate_algorithm(algorithm)

            # Create a copy and validate payload
            token_payload = validate_payload(payload.copy())

            # Add standard claims with custom expiration
            now = datetime.now(tz=timezone.utc)
            token_payload["iat"] = now
            token_payload["exp"] = expiration_datetime
            token_payload["nbf"] = now

            # Generate the token
            token = jwt.encode(token_payload, secret_key, algorithm=algorithm)

            logger.info(f"JWT token with custom expiration generated successfully")
            logger.debug(f"Expiration time: {expiration_datetime.isoformat()}")

            return token

        except Exception as e:
            error_msg = f"JWT token generation with custom expiration failed: {str(e)}"
            logger.error(error_msg)
            raise JWTTokenGenerationError(error_msg)
