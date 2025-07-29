"""
Main JWT Library for Robot Framework

This library provides keywords for JSON Web Token (JWT) operations in Robot Framework tests.

Author: JWT Robot Framework Library Team
Version: 1.0.0
License: Apache 2.0
"""

import logging

from .keywords.token_decoding import TokenDecodingKeywords
from .keywords.token_generation import TokenGenerationKeywords
from .keywords.token_validation import TokenValidationKeywords
from .keywords.utilities import UtilityKeywords
from .version import __version__

# Define a logger attribute
logger = logging.getLogger(__name__)


class JWTLibrary(
    TokenGenerationKeywords,
    TokenDecodingKeywords,
    TokenValidationKeywords,
    UtilityKeywords,
):
    """
    JWT Library provides keywords for encoding, decoding, and validating JSON Web Tokens.

    = Table of contents =

    - `Introduction`
    - `Keywords`
    - `Examples`

    = Introduction =

    This library enables Robot Framework tests to work with JSON Web Tokens (JWT).
    It provides functionality to:

    - Generate JWT tokens with custom payloads
    - Decode JWT tokens and extract payloads
    - Validate JWT signatures and claims
    - Handle token expiration and timing
    - Compare and analyze token contents

    The library supports various JWT algorithms including:
    - HMAC: HS256, HS384, HS512
    - RSA: RS256, RS384, RS512
    - ECDSA: ES256, ES384, ES512
    - PSS: PS256, PS384, PS512

    = Installation =

    This library requires the PyJWT package:

    | pip install PyJWT robotframework

    = Keywords =

    == Token Generation ==
    - `Generate JWT Token` - Creates JWT tokens with custom payloads
    - `Generate JWT Token With Claims` - Creates tokens using keyword arguments
    - `Generate JWT Token Without Expiration` - Creates non-expiring tokens
    - `Generate JWT Token With Custom Expiration` - Creates tokens with specific expiration

    == Token Decoding ==
    - `Decode JWT Payload` - Decodes token payloads with optional verification
    - `Decode JWT Header` - Decodes token headers
    - `Get JWT Claim` - Extracts specific claims from tokens
    - `Get Multiple JWT Claims` - Extracts multiple claims
    - `Extract All JWT Claims` - Gets all claims with metadata

    == Token Validation ==
    - `Verify JWT Token` - Validates token signatures and expiration
    - `Check JWT Expiration` - Checks token expiration status
    - `Validate JWT Claims` - Validates expected claim values
    - `Check JWT Algorithm` - Validates token algorithm
    - `Validate JWT Structure` - Validates token format
    - `Check JWT Not Before` - Validates nbf claim
    - `Validate JWT Audience` - Validates audience claim

    == Utilities ==
    - `Create JWT Payload` - Helper to create payload dictionaries
    - `Get JWT Token Info` - Gets comprehensive token information
    - `Compare JWT Tokens` - Compares two tokens
    - `Extract JWT Timestamps` - Extracts timestamp claims
    - `Generate Current Timestamp` - Creates current timestamp
    - `Generate Future Timestamp` - Creates future timestamp
    - `Convert Timestamp To Datetime` - Converts timestamps to datetime
    - `Create JWT Header` - Creates header dictionaries
    - `Format JWT Claims For Logging` - Formats claims for safe logging
    - `Validate JWT Claim Types` - Validates claim data types

    = Usage Examples =

    == Basic Token Operations ==

    | *** Settings ***
    | Library    JWTLibrary
    |
    | *** Variables ***
    | ${SECRET_KEY}    my_secret_key_123
    |
    | *** Test Cases ***
    | Basic JWT Operations
    |     # Create payload
    |     ${payload}=    Create Dictionary    user_id=123    role=admin
    |
    |     # Generate token
    |     ${token}=    Generate JWT Token    ${payload}    ${SECRET_KEY}
    |
    |     # Decode and verify
    |     ${decoded}=    Decode JWT Payload    ${token}    ${SECRET_KEY}
    |     Should Be Equal    ${decoded['user_id']}    123
    |
    |     # Validate token
    |     ${is_valid}=    Verify JWT Token    ${token}    ${SECRET_KEY}
    |     Should Be True    ${is_valid}

    == Advanced Token Validation ==

    | Advanced JWT Validation
    |     ${payload}=    Create Dictionary    user_id=456    role=user    email=test@example.com
    |     ${token}=    Generate JWT Token    ${payload}    ${SECRET_KEY}    expiration_hours=1
    |
    |     # Check expiration
    |     ${exp_info}=    Check JWT Expiration    ${token}
    |     Should Be Equal    ${exp_info['is_expired']}    ${False}
    |
    |     # Validate specific claims
    |     ${expected}=    Create Dictionary    role=user    user_id=456
    |     ${claims_valid}=    Validate JWT Claims    ${token}    ${expected}    ${SECRET_KEY}    True
    |     Should Be True    ${claims_valid}
    |
    |     # Check algorithm
    |     ${alg_correct}=    Check JWT Algorithm    ${token}    HS256
    |     Should Be True    ${alg_correct}

    == Token Comparison and Analysis ==

    | JWT Analysis
    |     ${payload1}=    Create Dictionary    user_id=123    role=admin
    |     ${payload2}=    Create Dictionary    user_id=123    role=user
    |
    |     ${token1}=    Generate JWT Token    ${payload1}    ${SECRET_KEY}
    |     ${token2}=    Generate JWT Token    ${payload2}    ${SECRET_KEY}
    |
    |     # Compare tokens
    |     ${comparison}=    Compare JWT Tokens    ${token1}    ${token2}
    |     Should Be Equal    ${comparison['are_identical']}    ${False}
    |     Should Be Equal    ${comparison['payload_differences_count']}    1
    |
    |     # Get detailed token info
    |     ${info}=    Get JWT Token Info    ${token1}
    |     Log    Token Algorithm: ${info['algorithm']}
    |     Log    Claims Count: ${info['claims_count']}

    = Error Handling =

    The library provides specific exceptions for different error conditions:

    - `JWTTokenGenerationError` - Token generation failures
    - `JWTTokenDecodingError` - Token decoding failures
    - `JWTTokenValidationError` - Token validation failures
    - `JWTExpiredTokenError` - Expired token errors
    - `JWTInvalidSignatureError` - Signature verification failures
    - `JWTInvalidTokenError` - Invalid token format errors
    - `JWTClaimNotFoundError` - Missing claim errors

    = Security Considerations =

    - Always use strong secret keys for HMAC algorithms
    - Consider using RSA or ECDSA for distributed systems
    - Validate all claims, especially audience and issuer
    - Check token expiration and not-before claims
    - Use appropriate token lifetimes for your use case
    - Store secret keys securely, never in code or logs

    = Performance Notes =

    - Token verification involves cryptographic operations
    - Cache decoded payloads when possible
    - Use shorter tokens for better performance
    - Consider token format for network efficiency
    """

    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    ROBOT_LIBRARY_VERSION = __version__
    ROBOT_LIBRARY_DOC_FORMAT = "ROBOT"

    def __init__(self):
        """Initialize the JWT Library with default settings."""
        # Initialize parent classes
        TokenGenerationKeywords.__init__(self)
        TokenDecodingKeywords.__init__(self)
        TokenValidationKeywords.__init__(self)
        UtilityKeywords.__init__(self)

        # Library metadata
        self.library_name = "JWTLibrary"
        self.library_version = __version__


# For backward compatibility and direct import
if __name__ == "__main__":
    # Example usage when run directly

    print("JWT Library Example Usage")
    print("=" * 50)

    jwt_lib = JWTLibrary()

    # Example 1: Basic token operations
    print("\n1. Basic Token Operations:")
    payload = {"user_id": 123, "username": "testuser", "role": "admin"}
    secret_key = "my_secret_key_123"

    token = jwt_lib.generate_jwt_token(payload, secret_key)

    print(f"Generated Token: {token[:50]}...")

    decoded_payload = jwt_lib.decode_jwt_payload(token, secret_key)
    print(f"Decoded Successfully: {decoded_payload['user_id']}")

    is_valid = jwt_lib.verify_jwt_token(token, secret_key)
    print(f"Token Valid: {is_valid}")

    # Example 2: Token analysis
    print("\n2. Token Analysis:")
    token_info = jwt_lib.get_jwt_token_info(token)
    print(f"Algorithm: {token_info['algorithm']}")
    print(f"Claims Count: {token_info['claims_count']}")

    # Example 3: Expiration check
    print("\n3. Expiration Check:")
    exp_info = jwt_lib.check_jwt_expiration(token)
    print(f"Expires At: {exp_info['expires_at']}")
    print(f"Is Expired: {exp_info['is_expired']}")
    # Example 4: Claim validation
    print("\n4. Claim Validation:")
    expected_claims = {"user_id": 123, "role": "admin"}
    claims_valid = jwt_lib.validate_jwt_claims(token, expected_claims, secret_key, True)
    print(f"Claims Valid: {claims_valid}")

    # Example 5: Utility functions
    print("\n5. Utility Functions:")
    current_ts = jwt_lib.generate_current_timestamp()
    future_ts = jwt_lib.generate_future_timestamp(hours=1)
    print(f"Current Timestamp: {current_ts}")
    print(f"Future Timestamp: {future_ts}")
    print("\nJWT Library examples completed successfully!")
