"""Unit tests for JWT Library main functionality."""

import time
from datetime import datetime, timedelta, timezone

import jwt
import pytest

from JWTLibrary.exceptions import (
    JWTClaimNotFoundError,
    JWTExpiredTokenError,
    JWTInvalidSignatureError,
    JWTTokenDecodingError,
    JWTTokenGenerationError,
)
from JWTLibrary.jwt_library import JWTLibrary


class TestJWTLibrary:
    """Test cases for JWT Library main functionality."""

    def setup_method(self):
        """Setup test fixtures."""
        self.jwt_lib = JWTLibrary()
        self.secret_key = "test_secret_key_123"
        self.test_payload = {
            "user_id": 123,
            "username": "testuser",
            "role": "admin",
            "email": "test@example.com",
        }

    def test_library_initialization(self):
        """Test library initialization."""
        assert self.jwt_lib.library_name == "JWTLibrary"
        assert hasattr(self.jwt_lib, "library_version")
        assert self.jwt_lib.ROBOT_LIBRARY_SCOPE == "GLOBAL"

    def test_generate_basic_jwt_token(self):
        """Test basic JWT token generation."""
        token = self.jwt_lib.generate_jwt_token(self.test_payload, self.secret_key)
        assert isinstance(token, str)
        assert len(token.split(".")) == 3  # JWT has 3 parts
        # Verify token can be decoded
        decoded = jwt.decode(token, self.secret_key, algorithms=["HS256"])
        assert decoded["user_id"] == 123
        assert decoded["username"] == "testuser"
        assert decoded["role"] == "admin"

    def test_generate_jwt_token_with_custom_algorithm(self):
        """Test JWT token generation with custom algorithm."""
        token = self.jwt_lib.generate_jwt_token(
            self.test_payload, self.secret_key, algorithm="HS512"
        )
        # Verify token header contains correct algorithm
        header = jwt.get_unverified_header(token)
        assert header["alg"] == "HS512"
        # Verify token can be decoded with correct algorithm
        decoded = jwt.decode(token, self.secret_key, algorithms=["HS512"])
        assert decoded["user_id"] == 123

    def test_generate_jwt_token_with_custom_expiration(self):
        """Test JWT token generation with custom expiration."""
        token = self.jwt_lib.generate_jwt_token(
            self.test_payload, self.secret_key, expiration_hours=1
        )
        decoded = jwt.decode(token, self.secret_key, algorithms=["HS256"])
        # Check expiration is approximately 1 hour from now
        exp_time = datetime.fromtimestamp(decoded["exp"])
        expected_exp = datetime.now() + timedelta(hours=1)
        time_diff = abs((exp_time - expected_exp).total_seconds())
        assert time_diff < 60  # Within 1 minute tolerance

    def test_generate_jwt_token_invalid_algorithm(self):
        """Test JWT token generation with invalid algorithm."""
        with pytest.raises(JWTTokenGenerationError):
            self.jwt_lib.generate_jwt_token(
                self.test_payload, self.secret_key, algorithm="INVALID"
            )

    def test_decode_jwt_payload_valid_token(self):
        """Test decoding valid JWT payload."""
        token = self.jwt_lib.generate_jwt_token(self.test_payload, self.secret_key)
        decoded = self.jwt_lib.decode_jwt_payload(token, self.secret_key)
        assert decoded["user_id"] == 123
        assert decoded["username"] == "testuser"
        assert decoded["role"] == "admin"

    def test_decode_jwt_payload_without_verification(self):
        """Test decoding JWT payload without signature verification."""
        token = self.jwt_lib.generate_jwt_token(self.test_payload, self.secret_key)
        decoded = self.jwt_lib.decode_jwt_payload(token, verify_signature=False)
        assert decoded["user_id"] == 123
        assert decoded["username"] == "testuser"

    def test_decode_jwt_payload_wrong_secret(self):
        """Test decoding JWT payload with wrong secret key."""
        token = self.jwt_lib.generate_jwt_token(self.test_payload, self.secret_key)
        with pytest.raises(JWTInvalidSignatureError):
            self.jwt_lib.decode_jwt_payload(token, "wrong_secret")

    def test_decode_jwt_payload_expired_token(self):
        """Test decoding expired JWT token."""
        # Create token that expires immediately
        past_time = datetime.now(tz=timezone.utc) - timedelta(hours=1)
        token = self.jwt_lib.generate_jwt_token_with_custom_expiration(
            self.test_payload, self.secret_key, past_time
        )
        with pytest.raises(JWTExpiredTokenError):
            self.jwt_lib.decode_jwt_payload(token, self.secret_key)

    def test_decode_jwt_payload_invalid_token(self):
        """Test decoding invalid JWT token."""
        with pytest.raises(JWTTokenDecodingError):
            self.jwt_lib.decode_jwt_payload("invalid.token.here", self.secret_key)

    def test_decode_jwt_header(self):
        """Test decoding JWT header."""
        token = self.jwt_lib.generate_jwt_token(self.test_payload, self.secret_key)
        header = self.jwt_lib.decode_jwt_header(token)
        assert header["alg"] == "HS256"
        assert header["typ"] == "JWT"

    def test_verify_jwt_token_valid(self):
        """Test verifying valid JWT token."""
        token = self.jwt_lib.generate_jwt_token(self.test_payload, self.secret_key)
        is_valid = self.jwt_lib.verify_jwt_token(token, self.secret_key)
        assert is_valid is True

    def test_verify_jwt_token_invalid(self):
        """Test verifying invalid JWT token."""
        is_valid = self.jwt_lib.verify_jwt_token("invalid.token.here", self.secret_key)
        assert is_valid is False

    def test_verify_jwt_token_wrong_secret(self):
        """Test verifying JWT token with wrong secret."""
        token = self.jwt_lib.generate_jwt_token(self.test_payload, self.secret_key)
        is_valid = self.jwt_lib.verify_jwt_token(token, "wrong_secret")
        assert is_valid is False

    def test_get_jwt_claim_existing(self):
        """Test getting existing JWT claim."""
        token = self.jwt_lib.generate_jwt_token(self.test_payload, self.secret_key)
        user_id = self.jwt_lib.get_jwt_claim(token, "user_id")
        assert user_id == 123

    def test_get_jwt_claim_missing(self):
        """Test getting non-existing JWT claim."""
        token = self.jwt_lib.generate_jwt_token(self.test_payload, self.secret_key)
        with pytest.raises(JWTClaimNotFoundError):
            self.jwt_lib.get_jwt_claim(token, "non_existing_claim")

    def test_get_jwt_claim_with_verification(self):
        """Test getting JWT claim with signature verification."""
        token = self.jwt_lib.generate_jwt_token(self.test_payload, self.secret_key)
        role = self.jwt_lib.get_jwt_claim(
            token, "role", secret_key=self.secret_key, verify_signature=True
        )
        assert role == "admin"

    def test_check_jwt_expiration_not_expired(self):
        """Test checking expiration of non-expired token."""
        token = self.jwt_lib.generate_jwt_token(self.test_payload, self.secret_key)
        exp_info = self.jwt_lib.check_jwt_expiration(token)
        assert exp_info["is_expired"] is False
        assert exp_info["time_until_expiry"] > 0
        assert exp_info["has_expiration"] is True

    def test_check_jwt_expiration_expired(self):
        """Test checking expiration of expired token."""
        past_time = datetime.now(tz=timezone.utc) - timedelta(days=1)
        token = self.jwt_lib.generate_jwt_token_with_custom_expiration(
            self.test_payload, self.secret_key, past_time
        )
        exp_info = self.jwt_lib.check_jwt_expiration(token)
        assert exp_info["is_expired"] is True
        assert exp_info["time_until_expiry"] < 0

    def test_check_jwt_expiration_no_exp_claim(self):
        """Test checking expiration of token without exp claim."""
        token = self.jwt_lib.generate_jwt_token_without_expiration(
            self.test_payload, self.secret_key
        )
        exp_info = self.jwt_lib.check_jwt_expiration(token)
        assert exp_info["has_expiration"] is False
        assert exp_info["is_expired"] is False

    def test_create_jwt_payload(self):
        """Test creating JWT payload from keyword arguments."""
        payload = self.jwt_lib.create_jwt_payload(
            user_id=456, role="user", email="user@test.com"
        )
        assert payload["user_id"] == 456
        assert payload["role"] == "user"
        assert payload["email"] == "user@test.com"

    def test_validate_jwt_claims_valid(self):
        """Test validating JWT claims with correct values."""
        token = self.jwt_lib.generate_jwt_token(self.test_payload, self.secret_key)
        expected_claims = {"user_id": 123, "role": "admin"}
        is_valid = self.jwt_lib.validate_jwt_claims(token, expected_claims)
        assert is_valid is True

    def test_validate_jwt_claims_invalid(self):
        """Test validating JWT claims with incorrect values."""
        token = self.jwt_lib.generate_jwt_token(self.test_payload, self.secret_key)
        expected_claims = {"user_id": 456, "role": "user"}  # Wrong values
        is_valid = self.jwt_lib.validate_jwt_claims(token, expected_claims)
        assert is_valid is False

    def test_generate_jwt_token_with_claims(self):
        """Test generating JWT token using keyword arguments."""
        token = self.jwt_lib.generate_jwt_token_with_claims(
            self.secret_key, user_id=789, role="moderator", email="mod@test.com"
        )
        decoded = self.jwt_lib.decode_jwt_payload(token, self.secret_key)
        assert decoded["user_id"] == 789
        assert decoded["role"] == "moderator"
        assert decoded["email"] == "mod@test.com"

    def test_compare_jwt_tokens_identical(self):
        """Test comparing identical JWT tokens."""
        payload = {"user_id": 123, "role": "admin"}
        token1 = self.jwt_lib.generate_jwt_token(payload, self.secret_key)
        time.sleep(1)  # Ensure iat is different
        token2 = self.jwt_lib.generate_jwt_token(payload, self.secret_key)

        # Note: Tokens won't be identical due to iat timestamp
        comparison = self.jwt_lib.compare_jwt_tokens(token1, token2)
        assert comparison["are_identical"] is False  # Due to different iat timestamps

    def test_compare_jwt_tokens_different(self):
        """Test comparing different JWT tokens."""
        payload1 = {"user_id": 123, "role": "admin"}
        payload2 = {"user_id": 456, "role": "user"}
        token1 = self.jwt_lib.generate_jwt_token(payload1, self.secret_key)
        token2 = self.jwt_lib.generate_jwt_token(payload2, self.secret_key)
        comparison = self.jwt_lib.compare_jwt_tokens(token1, token2)
        assert comparison["are_identical"] is False
        assert comparison["payload_differences_count"] > 0

    def test_get_jwt_token_info(self):
        """Test getting comprehensive JWT token information."""
        token = self.jwt_lib.generate_jwt_token(self.test_payload, self.secret_key)
        info = self.jwt_lib.get_jwt_token_info(token)
        assert info["algorithm"] == "HS256"
        assert info["type"] == "JWT"
        assert info["claims_count"] > 0
        assert "issued_at" in info
        assert "expires_at" in info

    def test_extract_jwt_timestamps(self):
        """Test extracting JWT timestamp claims."""
        token = self.jwt_lib.generate_jwt_token(self.test_payload, self.secret_key)
        timestamps = self.jwt_lib.extract_jwt_timestamps(token)
        assert "iat" in timestamps
        assert "exp" in timestamps
        assert "age_seconds" in timestamps
        assert "expires_in_seconds" in timestamps

    def test_generate_current_timestamp(self):
        """Test generating current timestamp."""
        timestamp = self.jwt_lib.generate_current_timestamp()
        assert isinstance(timestamp, int)
        current_time = datetime.now(tz=timezone.utc).timestamp()
        assert abs(timestamp - current_time) < 2  # Within 2 seconds

    def test_generate_future_timestamp(self):
        """Test generating future timestamp."""
        timestamp = self.jwt_lib.generate_future_timestamp(hours=1)
        assert isinstance(timestamp, int)
        expected_time = (datetime.now(tz=timezone.utc) + timedelta(hours=1)).timestamp()
        assert abs(timestamp - expected_time) < 2  # Within 2 seconds

    def test_convert_timestamp_to_datetime(self):
        """Test converting timestamp to datetime string."""
        timestamp = int(datetime.utcnow().timestamp())
        datetime_str = self.jwt_lib.convert_timestamp_to_datetime(timestamp)
        assert isinstance(datetime_str, str)
        # Should be able to parse back to datetime
        parsed_dt = datetime.fromisoformat(datetime_str)
        assert isinstance(parsed_dt, datetime)

    def test_error_handling_robustness(self):
        """Test library handles various error conditions gracefully."""
        # Test with None inputs
        with pytest.raises((JWTTokenGenerationError, TypeError)):
            self.jwt_lib.generate_jwt_token(None, self.secret_key)
        # Test with empty payload
        empty_payload = {}
        token = self.jwt_lib.generate_jwt_token(empty_payload, self.secret_key)
        assert isinstance(token, str)
        # Test with very long secret key
        long_secret = "x" * 1000
        token = self.jwt_lib.generate_jwt_token(self.test_payload, long_secret)
        assert isinstance(token, str)

    def test_multiple_algorithms_support(self):
        """Test library supports multiple JWT algorithms."""
        algorithms = ["HS256", "HS384", "HS512"]
        for alg in algorithms:
            token = self.jwt_lib.generate_jwt_token(
                self.test_payload, self.secret_key, algorithm=alg
            )
            # Verify algorithm in header
            header = self.jwt_lib.decode_jwt_header(token)
            assert header["alg"] == alg
            # Verify token can be decoded
            decoded = self.jwt_lib.decode_jwt_payload(
                token, self.secret_key, algorithm=alg
            )
            assert decoded["user_id"] == 123

    def test_edge_cases(self):
        """Test various edge cases."""
        # Very short expiration
        token = self.jwt_lib.generate_jwt_token(
            self.test_payload, self.secret_key, expiration_hours=0.001  # Very short
        )
        assert isinstance(token, str)
        # Large payload
        large_payload = {f"key_{i}": f"value_{i}" for i in range(100)}
        token = self.jwt_lib.generate_jwt_token(large_payload, self.secret_key)
        assert isinstance(token, str)
        # Unicode in payload
        unicode_payload = {"message": "Hello 世界", "emoji": "🚀"}
        token = self.jwt_lib.generate_jwt_token(unicode_payload, self.secret_key)
        decoded = self.jwt_lib.decode_jwt_payload(token, self.secret_key)
        assert decoded["message"] == "Hello 世界"
        assert decoded["emoji"] == "🚀"
