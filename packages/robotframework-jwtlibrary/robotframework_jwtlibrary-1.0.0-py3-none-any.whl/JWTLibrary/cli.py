"""Command-line interface for JWT Library."""

import argparse
import json
import sys
from datetime import datetime

from .exceptions import JWTLibraryError
from .jwt_library import JWTLibrary
from .version import __version__


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="jwt-robot-tool",
        description="JWT Robot Framework Library CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a JWT token
  jwt-robot-tool generate --payload '{"user_id": 123}' --secret mykey

  # Decode a JWT token
  jwt-robot-tool decode --token <token> --secret mykey

  # Validate a JWT token
  jwt-robot-tool validate --token <token> --secret mykey

  # Get token information
  jwt-robot-tool info --token <token>

  # Compare two tokens
  jwt-robot-tool compare --token1 <token1> --token2 <token2>
        """,
    )
    parser.add_argument(
        "--version", action="version", version=f"JWT Library {__version__}"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate a JWT token")
    generate_parser.add_argument(
        "--payload", required=True, help="JSON payload for the token"
    )
    generate_parser.add_argument(
        "--secret", required=True, help="Secret key for signing"
    )
    generate_parser.add_argument(
        "--algorithm", default="HS256", help="JWT algorithm (default: HS256)"
    )
    generate_parser.add_argument(
        "--expiration-hours",
        type=int,
        default=24,
        help="Token expiration in hours (default: 24)",
    )
    generate_parser.add_argument(
        "--no-expiration", action="store_true", help="Generate token without expiration"
    )
    # Decode command
    decode_parser = subparsers.add_parser("decode", help="Decode a JWT token")
    decode_parser.add_argument("--token", required=True, help="JWT token to decode")
    decode_parser.add_argument(
        "--secret", help="Secret key for verification (optional for unsafe decode)"
    )
    decode_parser.add_argument(
        "--algorithm", default="HS256", help="JWT algorithm (default: HS256)"
    )
    decode_parser.add_argument(
        "--no-verify", action="store_true", help="Decode without signature verification"
    )
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate a JWT token")
    validate_parser.add_argument("--token", required=True, help="JWT token to validate")
    validate_parser.add_argument(
        "--secret", required=True, help="Secret key for validation"
    )
    validate_parser.add_argument(
        "--algorithm", default="HS256", help="JWT algorithm (default: HS256)"
    )
    validate_parser.add_argument(
        "--expected-claims", help="JSON object of expected claims"
    )
    # Info command
    info_parser = subparsers.add_parser("info", help="Get JWT token information")
    info_parser.add_argument("--token", required=True, help="JWT token to analyze")

    # Compare command
    compare_parser = subparsers.add_parser("compare", help="Compare two JWT tokens")
    compare_parser.add_argument("--token1", required=True, help="First JWT token")
    compare_parser.add_argument("--token2", required=True, help="Second JWT token")
    # Verify command
    verify_parser = subparsers.add_parser(
        "verify", help="Verify JWT token signature and expiration"
    )
    verify_parser.add_argument("--token", required=True, help="JWT token to verify")
    verify_parser.add_argument(
        "--secret", required=True, help="Secret key for verification"
    )
    verify_parser.add_argument(
        "--algorithm", default="HS256", help="JWT algorithm (default: HS256)"
    )
    return parser


def command_generate(args, jwt_lib: JWTLibrary) -> int:
    """Handle the generate command."""
    try:
        # Parse payload JSON
        payload = json.loads(args.payload)

        if args.no_expiration:
            token = jwt_lib.generate_jwt_token_without_expiration(
                payload, args.secret, args.algorithm
            )
        else:
            token = jwt_lib.generate_jwt_token(
                payload, args.secret, args.algorithm, args.expiration_hours
            )

        print(f"Generated JWT Token:")
        print(token)
        print()

        # Show token info
        info = jwt_lib.get_jwt_token_info(token)
        print("Token Information:")
        print(json.dumps(info, indent=2, default=str))
        return 0

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON payload - {e}", file=sys.stderr)
        return 1
    except JWTLibraryError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


def command_decode(args, jwt_lib: JWTLibrary) -> int:
    """Handle the decode command."""
    try:
        verify_signature = not args.no_verify and args.secret is not None

        if verify_signature:
            payload = jwt_lib.decode_jwt_payload(
                args.token, args.secret, args.algorithm, verify_signature=True
            )
            print("✓ Token signature verified and decoded successfully")
        else:
            payload = jwt_lib.decode_jwt_payload(args.token, verify_signature=False)
            print("⚠ Token decoded without verification (unsafe)")
        print()
        print("Decoded Payload:")
        print(json.dumps(payload, indent=2, default=str))

        # Also show header
        header = jwt_lib.decode_jwt_header(args.token)
        print()
        print("Token Header:")
        print(json.dumps(header, indent=2))
        return 0

    except JWTLibraryError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


def command_validate(args, jwt_lib: JWTLibrary) -> int:
    """Handle the validate command."""
    try:
        # Verify token
        is_valid = jwt_lib.verify_jwt_token(args.token, args.secret, args.algorithm)

        if is_valid:
            print("✓ Token is valid")
        else:
            print("✗ Token is invalid")
            return 1

        # Check expiration
        exp_info = jwt_lib.check_jwt_expiration(args.token)
        if exp_info["has_expiration"]:
            if exp_info["is_expired"]:
                print("✗ Token has expired")
                return 1
            else:
                print(f"✓ Token expires in {exp_info['time_until_expiry']:.0f} seconds")
        else:
            print("ℹ Token has no expiration")

        # Validate expected claims if provided
        if args.expected_claims:
            expected = json.loads(args.expected_claims)
            claims_valid = jwt_lib.validate_jwt_claims(
                args.token, expected, args.secret, verify_signature=True
            )

            if claims_valid:
                print("✓ Expected claims match")
            else:
                print("✗ Expected claims do not match")
                return 1

        print()
        print("Validation Summary:")
        print(f"  Signature: {'Valid' if is_valid else 'Invalid'}")
        print(
            f"  Expiration: {'Valid' if not exp_info.get('is_expired', False) else 'Expired'}"
        )
        if args.expected_claims:
            print(f"  Claims: {'Valid' if claims_valid else 'Invalid'}")

        return 0

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in expected claims - {e}", file=sys.stderr)
        return 1
    except JWTLibraryError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


def command_info(args, jwt_lib: JWTLibrary) -> int:
    """Handle the info command."""
    try:
        # Get comprehensive token info
        info = jwt_lib.get_jwt_token_info(args.token)

        print("JWT Token Information:")
        print("=" * 50)
        print(f"Algorithm: {info.get('algorithm', 'Unknown')}")
        print(f"Type: {info.get('type', 'Unknown')}")
        print(f"Claims Count: {info.get('claims_count', 0)}")

        if info.get("issued_at"):
            issued_dt = datetime.fromtimestamp(info["issued_at"])
            print(f"Issued At: {issued_dt.isoformat()}")

        if info.get("expires_at"):
            expires_dt = datetime.fromtimestamp(info["expires_at"])
            print(f"Expires At: {expires_dt.isoformat()}")

            if info.get("is_expired") is not None:
                status = "Expired" if info["is_expired"] else "Valid"
                print(f"Status: {status}")

        if info.get("not_before"):
            nbf_dt = datetime.fromtimestamp(info["not_before"])
            print(f"Not Before: {nbf_dt.isoformat()}")

        print(f"Issuer: {info.get('issuer', 'Not specified')}")
        print(f"Subject: {info.get('subject', 'Not specified')}")
        print(f"Audience: {info.get('audience', 'Not specified')}")

        print()
        print("Header Parameters:")
        for param in info.get("header_params", []):
            print(f"  - {param}")

        print()
        print("Payload Claims:")
        for claim in info.get("payload_claims", []):
            print(f"  - {claim}")

        # Extract timestamps for detailed analysis
        timestamps = jwt_lib.extract_jwt_timestamps(args.token)
        if timestamps:
            print()
            print("Timestamp Analysis:")
            for claim, ts_info in timestamps.items():
                if isinstance(ts_info, dict) and "human_readable" in ts_info:
                    print(f"  {claim}: {ts_info['human_readable']}")

        return 0

    except JWTLibraryError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


def command_compare(args, jwt_lib: JWTLibrary) -> int:
    """Handle the compare command."""
    try:
        comparison = jwt_lib.compare_jwt_tokens(args.token1, args.token2)

        print("JWT Token Comparison:")
        print("=" * 50)

        if comparison["are_identical"]:
            print("✓ Tokens are identical")
        else:
            print("✗ Tokens are different")

        print(f"Payload differences: {comparison['payload_differences_count']}")
        print(f"Header differences: {comparison['header_differences_count']}")

        if comparison["payload_differences"]:
            print()
            print("Payload Differences:")
            for claim, diff in comparison["payload_differences"].items():
                print(f"  {claim}:")
                print(f"    Token 1: {diff['token1']}")
                print(f"    Token 2: {diff['token2']}")

        if comparison["header_differences"]:
            print()
            print("Header Differences:")
            for param, diff in comparison["header_differences"].items():
                print(f"  {param}:")
                print(f"    Token 1: {diff['token1']}")
                print(f"    Token 2: {diff['token2']}")

        return 0

    except JWTLibraryError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


def command_verify(args, jwt_lib: JWTLibrary) -> int:
    """Handle the verify command."""
    try:
        is_valid = jwt_lib.verify_jwt_token(args.token, args.secret, args.algorithm)

        if is_valid:
            print("✓ Token verification successful")
            print("  - Signature is valid")
            print("  - Token is not expired")
            print("  - Token format is correct")
            return 0
        else:
            print("✗ Token verification failed")

            # Try to provide more specific information
            try:
                # Check structure
                structure = jwt_lib.validate_jwt_structure(args.token)
                if not structure["is_valid_structure"]:
                    print("  - Invalid token structure")
                    for error in structure.get("errors", []):
                        print(f"    • {error}")
                else:
                    # Check expiration if structure is valid
                    exp_info = jwt_lib.check_jwt_expiration(args.token)
                    if exp_info.get("is_expired"):
                        print("  - Token has expired")
                    else:
                        print("  - Invalid signature or algorithm mismatch")
            except:
                print("  - Unable to determine specific cause")

            return 1

    except JWTLibraryError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 1
    # Initialize JWT Library
    jwt_lib = JWTLibrary()
    # Route to appropriate command handler
    command_handlers = {
        "generate": command_generate,
        "decode": command_decode,
        "validate": command_validate,
        "info": command_info,
        "compare": command_compare,
        "verify": command_verify,
    }
    handler = command_handlers.get(args.command)
    if handler:
        return handler(args, jwt_lib)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
