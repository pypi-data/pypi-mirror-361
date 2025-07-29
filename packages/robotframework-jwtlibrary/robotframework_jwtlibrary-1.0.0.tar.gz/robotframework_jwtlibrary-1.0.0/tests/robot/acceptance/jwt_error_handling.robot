*** Settings ***
Documentation     JWT error handling test suite
Library           JWTLibrary
Library           Collections

*** Variables ***
${SECRET_KEY}     error_test_secret_key
${INVALID_TOKEN}  invalid.token.format
${MALFORMED_TOKEN}  not-a-jwt-token
${EMPTY_TOKEN}    ${EMPTY}

*** Test Cases ***
Handle Invalid Token Formats
    [Documentation]    Test handling of various invalid token formats
    [Tags]    jwt    error-handling    invalid-tokens
    
    # Test completely invalid token
    ${is_valid}=    Verify JWT Token    ${INVALID_TOKEN}    ${SECRET_KEY}
    Should Be Equal    ${is_valid}    ${False}
    
    # Test malformed token
    ${is_valid_malformed}=    Verify JWT Token    ${MALFORMED_TOKEN}    ${SECRET_KEY}
    Should Be Equal    ${is_valid_malformed}    ${False}
    
    # Test empty token
    ${is_valid_empty}=    Verify JWT Token    ${EMPTY_TOKEN}    ${SECRET_KEY}
    Should Be Equal    ${is_valid_empty}    ${False}
    
    # Test token with wrong number of parts
    ${two_part_token}=    Set Variable    header.payload
    ${is_valid_two_parts}=    Verify JWT Token    ${two_part_token}    ${SECRET_KEY}
    Should Be Equal    ${is_valid_two_parts}    ${False}
    
    # Test token with too many parts
    ${four_part_token}=    Set Variable    header.payload.signature.extra
    ${is_valid_four_parts}=    Verify JWT Token    ${four_part_token}    ${SECRET_KEY}
    Should Be Equal    ${is_valid_four_parts}    ${False}
#
#Handle Decoding Errors
#    [Documentation]    Test error handling during token decoding
#    [Tags]    jwt    error-handling    decoding
#
#    # Test decoding invalid token with verification
#    Run Keyword And Expect Error    *JWT token decoding failed*
#    ...    Decode JWT Payload    ${INVALID_TOKEN}    ${SECRET_KEY}
#
#    # Test decoding with missing secret key when verification required
#    Run Keyword And Expect Error    *Secret key is required*
#    ...    Decode JWT Payload    ${INVALID_TOKEN}    verify_signature=${True}
#
#    # Test decoding malformed token
#    Run Keyword And Expect Error    *JWT token decoding failed*
#    ...    Decode JWT Payload    ${MALFORMED_TOKEN}    ${SECRET_KEY}
#
#    # Test header decoding of invalid token
#    Run Keyword And Expect Error    *JWT header decoding failed*
#    ...    Decode JWT Header    ${INVALID_TOKEN}

Handle Expired Tokens
    [Documentation]    Test handling of expired JWT tokens
    [Tags]    jwt    error-handling    expired-tokens
    
    # Create token that expires immediately (in the past)
    ${expired_payload}=    Create Dictionary    user_id=999    test=expired
    ${past_timestamp}=    Evaluate    __import__('time').time() - 360000 # 100 hours in the past
    ${past_datetime}=    Evaluate    __import__('datetime').datetime.fromtimestamp(${past_timestamp})
    
    ${expired_token}=    Generate JWT Token With Custom Expiration
    ...    ${expired_payload}    ${SECRET_KEY}    ${past_datetime}
    
    # Verify token is detected as expired
    ${exp_info}=    Check JWT Expiration    ${expired_token}
    Should Be Equal    ${exp_info['is_expired']}    ${True}
    Should Be True    ${exp_info['time_until_expiry']} < 0
    
    # Verify decoding with verification fails
    Run Keyword And Expect Error    *JWT token has expired*
    ...    Decode JWT Payload    ${expired_token}    ${SECRET_KEY}
    
    # Verify verification fails
    ${is_valid}=    Verify JWT Token    ${expired_token}    ${SECRET_KEY}
    Should Be Equal    ${is_valid}    ${False}

    # But unsafe decoding should still work
    ${unsafe_decoded}=    Decode JWT Payload    ${expired_token}    verify_signature=${False}
    Should Be Equal As Integers    ${unsafe_decoded['user_id']}    999

Handle Invalid Signatures
    [Documentation]    Test handling of tokens with invalid signatures
    [Tags]    jwt    error-handling    invalid-signatures
    
    # Create valid token
    ${payload}=    Create Dictionary    user_id=123    test=signature
    ${valid_token}=    Generate JWT Token    ${payload}    ${SECRET_KEY}
    
    # Try to verify with wrong secret key
    ${wrong_secret}=    Set Variable    wrong_secret_key
    
    # Verification should fail
    ${is_valid}=    Verify JWT Token    ${valid_token}    ${wrong_secret}
    Should Be Equal    ${is_valid}    ${False}
    
    # Decoding with wrong secret should fail
    Run Keyword And Expect Error    *JWT token signature verification failed*
    ...    Decode JWT Payload    ${valid_token}    ${wrong_secret}
    
    # Getting claims with verification should fail
    Run Keyword And Expect Error    *JWT token signature verification failed*
    ...    Get JWT Claim    ${valid_token}    user_id    secret_key=${wrong_secret}    verify_signature=${True}

Handle Missing Claims
    [Documentation]    Test handling of missing claims in tokens
    [Tags]    jwt    error-handling    missing-claims
    
    ${payload}=    Create Dictionary    user_id=456    role=user
    ${token}=    Generate JWT Token    ${payload}    ${SECRET_KEY}
    
    # Test getting non-existent claim
    Run Keyword And Expect Error    *Claim 'non_existent' not found*
    ...    Get JWT Claim    ${token}    non_existent
    
    # Test getting multiple claims where some don't exist
    ${claim_names}=    Create List    user_id    role    missing_claim    another_missing
    ${claims}=    Get Multiple JWT Claims    ${token}    ${claim_names}
    
    # Should get existing claims
    Should Be Equal As Integers    ${claims['user_id']}    456
    Should Be Equal    ${claims['role']}    user
    
    # Should not contain missing claims
    Should Not Contain    ${claims}    missing_claim
    Should Not Contain    ${claims}    another_missing

Handle Invalid Algorithm Errors
    [Documentation]    Test handling of invalid algorithm specifications
    [Tags]    jwt    error-handling    invalid-algorithms
    
    ${payload}=    Create Dictionary    user_id=789    test=algorithm
    
    # Test generation with invalid algorithm
    Run Keyword And Expect Error    *JWT token generation failed*
    ...    Generate JWT Token    ${payload}    ${SECRET_KEY}    algorithm=INVALID_ALG
    
    # Test generation with unsupported algorithm
    Run Keyword And Expect Error    *JWT token generation failed*
    ...    Generate JWT Token    ${payload}    ${SECRET_KEY}    algorithm=CUSTOM256

Handle Payload Type Errors
    [Documentation]    Test handling of invalid payload types and structures
    [Tags]    jwt    error-handling    payload-errors
    
    # Test with None payload
    Run Keyword And Expect Error    *
    ...    Generate JWT Token    ${None}    ${SECRET_KEY}
    
    # Test with string payload (should be dict)
    Run Keyword And Expect Error    *
    ...    Generate JWT Token    "invalid_payload"    ${SECRET_KEY}
    
    # Test with list payload (should be dict)
    ${list_payload}=    Create List    item1    item2
    Run Keyword And Expect Error    *
    ...    Generate JWT Token    ${list_payload}    ${SECRET_KEY}

#Handle Secret Key Errors
#    [Documentation]    Test handling of invalid secret keys
#    [Tags]    jwt    error-handling    secret-key-errors
#
#    ${payload}=    Create Dictionary    user_id=999    test=secret
#
#    # Test with None secret key
#    Run Keyword And Expect Error    *
#    ...    Generate JWT Token    ${payload}    ${None}
#
#    # Test with empty secret key
#    Run Keyword And Expect Error    *
#    ...    Generate JWT Token    ${payload}    ${EMPTY}
#
#    # Test verification with None secret key
#    ${valid_token}=    Generate JWT Token    ${payload}    ${SECRET_KEY}
#    ${is_valid}=    Verify JWT Token    ${valid_token}    ${None}
#    Should Be Equal    ${is_valid}    ${False}
#
#Handle Token Structure Validation Errors
#    [Documentation]    Test token structure validation error scenarios
#    [Tags]    jwt    error-handling    structure-validation
#
#    # Test validation of completely invalid token
#    ${structure_info}=    Validate JWT Structure    ${INVALID_TOKEN}
#    Should Be Equal    ${structure_info['is_valid_structure']}    ${False}
#    Should Be Equal    ${structure_info['has_three_parts']}    ${False}
#    Should Not Be Empty    ${structure_info['errors']}
#
#    # Test validation of malformed token
#    ${malformed_structure}=    Validate JWT Structure    ${MALFORMED_TOKEN}
#    Should Be Equal    ${malformed_structure['is_valid_structure']}    ${False}
#    Should Not Be Empty    ${malformed_structure['errors']}
#
#    # Test validation of token with invalid base64
#    ${invalid_b64_token}=    Set Variable    invalid_header.invalid_payload.invalid_signature
#    ${invalid_structure}=    Validate JWT Structure    ${invalid_b64_token}
#    Should Be Equal    ${invalid_structure['is_valid_structure']}    ${False}
#
#Handle Timestamp Conversion Errors
#    [Documentation]    Test timestamp conversion error handling
#    [Tags]    jwt    error-handling    timestamp-errors
#
#    # Test with invalid timestamp
#    Run Keyword And Expect Error    *
#    ...    Convert Timestamp To Datetime    invalid_timestamp
#
#    # Test with negative timestamp
#    Run Keyword And Expect Error    *
#    ...    Convert Timestamp To Datetime    -1
#
#    # Test with extremely large timestamp
#    ${large_timestamp}=    Evaluate    9999999999999
#    Run Keyword And Expect Error    *
#    ...    Convert Timestamp To Datetime    ${large_timestamp}

Handle Claims Validation Errors
    [Documentation]    Test claims validation error scenarios
    [Tags]    jwt    error-handling    claims-validation
    
    ${payload}=    Create Dictionary    user_id=123    role=user
    ${token}=    Generate JWT Token    ${payload}    ${SECRET_KEY}
    
    # Test claims validation with None expected claims
    Run Keyword And Expect Error    *
    ...    Validate JWT Claims    ${token}    ${None}
    
    # Test claims validation with invalid token
    ${expected_claims}=    Create Dictionary    user_id=123
    ${claims_valid}=    Validate JWT Claims    ${INVALID_TOKEN}    ${expected_claims}
    Should Be Equal    ${claims_valid}    ${False}
    
    # Test audience validation with invalid token
    ${aud_valid}=    Validate JWT Audience    ${INVALID_TOKEN}    my-audience
    Should Be Equal    ${aud_valid}    ${False}

Handle Edge Case Scenarios
    [Documentation]    Test various edge case error scenarios
    [Tags]    jwt    error-handling    edge-cases
    
    # Test with very long claim names
    ${long_claim_name}=    Evaluate    'very_long_claim_name' * 100
    ${payload}=    Create Dictionary    ${long_claim_name}=value
    ${token}=    Generate JWT Token    ${payload}    ${SECRET_KEY}
    
    # Should be able to extract the long claim name
    ${long_claim_value}=    Get JWT Claim    ${token}    ${long_claim_name}
    Should Be Equal    ${long_claim_value}    value
    
    # Test with very long claim values
    ${long_value}=    Evaluate    'x' * 10000
    ${long_payload}=    Create Dictionary    user_id=123    long_field=${long_value}
    ${long_token}=    Generate JWT Token    ${long_payload}    ${SECRET_KEY}
    
    ${extracted_long_value}=    Get JWT Claim    ${long_token}    long_field
    Should Be Equal    ${extracted_long_value}    ${long_value}
    
    # Test with special characters in claims
    ${special_payload}=    Create Dictionary
    ...    user_id=123
    ...    special_chars=!@#$%^&*()
    ...    unicode_chars=🚀🎉✨
    ...    quotes="'test'"
    ...    newlines=line1\nline2
    
    ${special_token}=    Generate JWT Token    ${special_payload}    ${SECRET_KEY}
    ${decoded_special}=    Decode JWT Payload    ${special_token}    ${SECRET_KEY}
    
    Should Be Equal    ${decoded_special['special_chars']}    !@#$%^&*()
    Should Be Equal    ${decoded_special['unicode_chars']}    🚀🎉✨
    Should Be Equal    ${decoded_special['quotes']}    "'test'"

Recovery From Errors
    [Documentation]    Test error recovery and graceful degradation
    [Tags]    jwt    error-handling    recovery
    
    # Test that library continues to work after errors
    ${payload}=    Create Dictionary    user_id=123    test=recovery
    
    # Cause an error
    Run Keyword And Expect Error    *
    ...    Generate JWT Token    ${payload}    ${SECRET_KEY}    algorithm=INVALID
    
    # Verify library still works normally after error
    ${valid_token}=    Generate JWT Token    ${payload}    ${SECRET_KEY}
    ${decoded}=    Decode JWT Payload    ${valid_token}    ${SECRET_KEY}
    Should Be Equal As Integers    ${decoded['user_id']}    123
    
    # Cause another error
    Run Keyword And Expect Error    *
    ...    Decode JWT Payload    ${INVALID_TOKEN}    ${SECRET_KEY}
    
    # Verify library still works
    ${is_valid}=    Verify JWT Token    ${valid_token}    ${SECRET_KEY}
    Should Be True    ${is_valid}

*** Keywords ***
Verify Error Contains Message
    [Arguments]    ${keyword}    ${expected_message}    @{args}
    [Documentation]    Helper to verify error messages contain expected text
    
    ${error_occurred}=    Run Keyword And Return Status
    ...    Run Keyword    ${keyword}    @{args}
    
    Should Be Equal    ${error_occurred}    ${False}
    
    ${error_message}=    Run Keyword And Expect Error    *
    ...    Run Keyword    ${keyword}    @{args}
    
    Should Contain    ${error_message}    ${expected_message}

Test Error Robustness
    [Arguments]    ${test_name}    ${operation_keyword}    @{args}
    [Documentation]    Helper to test operation robustness with various invalid inputs
    
    Log    Testing ${test_name} robustness
    
    # Test with None inputs
    FOR    ${i}    IN RANGE    len($args)
        ${modified_args}=    Copy List    ${args}
        Set List Value    ${modified_args}    ${i}    ${None}
        
        ${status}=    Run Keyword And Return Status
        ...    Run Keyword    ${operation_keyword}    @{modified_args}
        
        # Operation should either succeed or fail gracefully
        Log    ${test_name} with None at position ${i}: ${'PASS' if $status else 'EXPECTED FAIL'}
    END

Create Error Test Matrix
    [Arguments]    ${base_payload}    ${base_secret}
    [Documentation]    Helper to create various error test combinations
    
    # Invalid payloads to test
    @{invalid_payloads}=    Create List    ${None}    ${EMPTY}    invalid_string    12345
    
    # Invalid secrets to test
    @{invalid_secrets}=    Create List    ${None}    ${EMPTY}    12345
    
    # Invalid algorithms to test
    @{invalid_algorithms}=    Create List    INVALID    NONE    ${None}    12345
    
    # Return test matrix
    ${test_matrix}=    Create Dictionary
    ...    invalid_payloads=${invalid_payloads}
    ...    invalid_secrets=${invalid_secrets}
    ...    invalid_algorithms=${invalid_algorithms}
    
    RETURN    ${test_matrix}
