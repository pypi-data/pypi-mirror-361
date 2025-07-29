*** Settings ***
Documentation     Advanced JWT features test suite
Library           JWTLibrary
Library           Collections
Library           DateTime
Library           String

*** Variables ***
${SECRET_KEY}     advanced_test_secret_key_456
${RSA_PUBLIC_KEY}    -----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----
${AUDIENCE}       my-api-service
${ISSUER}         auth-service
${SUBJECT}        user123

*** Test Cases ***
Advanced JWT Claims Validation
    [Documentation]    Test advanced JWT claims validation scenarios
    [Tags]    jwt    advanced    claims    validation
    
    # Create payload with standard JWT claims
    ${payload}=    Create Dictionary
    ...    iss=${ISSUER}
    ...    sub=${SUBJECT}
    ...    aud=${AUDIENCE}
    ...    user_id=12345
    ...    role=admin
    ...    permissions=["read", "write", "delete"]
    ...    metadata={"department": "engineering", "clearance": 5}
    
    ${token}=    Generate JWT Token    ${payload}    ${SECRET_KEY}
    
    # Validate issuer claim
    ${iss_claim}=    Get JWT Claim    ${token}    iss
    Should Be Equal    ${iss_claim}    ${ISSUER}
    
    # Validate subject claim
    ${sub_claim}=    Get JWT Claim    ${token}    sub
    Should Be Equal    ${sub_claim}    ${SUBJECT}
    
    # Validate audience claim
    ${aud_valid}=    Validate JWT Audience    ${token}    ${AUDIENCE}
    Should Be True    ${aud_valid}
    
    # Validate complex nested claims
    ${metadata}=    Get JWT Claim    ${token}    metadata
    ${metadata}=    Evaluate    json.loads('''${metadata}''')    json
    Should Be Equal    ${metadata["department"]}    engineering
    Should Be Equal As Integers    ${metadata['clearance']}    5
    
    # Validate array claims
    ${permissions}=    Get JWT Claim    ${token}    permissions
    ${permissions}=    Evaluate    json.loads('''${permissions}''')    json
    Should Contain    ${permissions}    read
    Should Contain    ${permissions}    write
    Should Contain    ${permissions}    delete
    Length Should Be    ${permissions}    3

#JWT Token Expiration Edge Cases
#    [Documentation]    Test JWT token expiration edge cases and scenarios
#    [Tags]    jwt    expiration    edge-cases
#
#    # Test very short expiration (1 minute)
#    ${short_payload}=    Create Dictionary    user_id=999    test=short_exp
#    ${short_exp_hours}=    Evaluate    1.0/60  # 1 minute in hours
#    ${short_token}=    Generate JWT Token    ${short_payload}    ${SECRET_KEY}
#    ...    expiration_hours=${short_exp_hours}
#
#    ${short_exp_info}=    Check JWT Expiration    ${short_token}
#    Should Be Equal    ${short_exp_info['is_expired']}    ${False}
#    Should Be True    ${short_exp_info['time_until_expiry']} < 120  # Less than 2 minutes
#
#    # Test custom expiration datetime
#    ${future_time}=    Add Time To Date    ${EMPTY}    2 hours    result_format=%Y-%m-%d %H:%M:%S
#    ${future_datetime}=    Convert Date    ${future_time}    datetime
#
#    ${custom_payload}=    Create Dictionary    user_id=888    test=custom_exp
#    ${custom_token}=    Generate JWT Token With Custom Expiration
#    ...    ${custom_payload}    ${SECRET_KEY}    ${future_datetime}
#
#    ${custom_exp_info}=    Check JWT Expiration    ${custom_token}
#    Should Be Equal    ${custom_exp_info['is_expired']}    ${False}
#
#    # Verify expiration time is approximately 2 hours from now
#    ${time_until_exp}=    Convert To Number    ${custom_exp_info['time_until_expiry']}
#    Should Be True    ${time_until_exp} > 7000  # More than ~1.9 hours
#    Should Be True    ${time_until_exp} < 7300  # Less than ~2.1 hours

JWT Not Before (nbf) Claim Testing
    [Documentation]    Test JWT not before claim functionality
    [Tags]    jwt    nbf    not-before
    
    ${payload}=    Create Dictionary    user_id=777    future_token=true
    
    # Generate token and check nbf claim
    ${token}=    Generate JWT Token    ${payload}    ${SECRET_KEY}
    ${nbf_info}=    Check JWT Not Before    ${token}
    
    Should Be Equal    ${nbf_info['has_not_before']}    ${True}
    Should Be Equal    ${nbf_info['is_active']}    ${True}
    Should Be True    ${nbf_info['time_until_active']} == 0

JWT Algorithm Validation
    [Documentation]    Test JWT algorithm validation and verification
    [Tags]    jwt    algorithms    validation
    
    ${payload}=    Create Dictionary    user_id=555    alg_test=true
    
    # Test different algorithms
    @{algorithms}=    Create List    HS256    HS384    HS512
    
    FOR    ${algorithm}    IN    @{algorithms}
        ${token}=    Generate JWT Token    ${payload}    ${SECRET_KEY}    algorithm=${algorithm}
        
        # Verify algorithm in header
        ${alg_correct}=    Check JWT Algorithm    ${token}    ${algorithm}
        Should Be True    ${alg_correct}
        
        # Verify token can be decoded with correct algorithm
        ${decoded}=    Decode JWT Payload    ${token}    ${SECRET_KEY}    algorithm=${algorithm}
        Should Be Equal As Integers    ${decoded['user_id']}    555
        
        # Verify verification works
        ${verified}=    Verify JWT Token    ${token}    ${SECRET_KEY}    algorithm=${algorithm}
        Should Be True    ${verified}
    END

JWT Claims Type Validation
    [Documentation]    Test JWT claims data type validation
    [Tags]    jwt    types    validation

    # Create payload with various data types
    ${complex_payload}=    Create Dictionary
    ...    string_claim=hello
    ...    integer_claim=${123}
    ...    float_claim=${45.67}
    ...    boolean_claim=${True}
    ...    list_claim=["item1", "item2", "item3"]
    ...    dict_claim={"nested": "value", "number": 42}
    ...    null_claim=${None}

    ${token}=    Generate JWT Token    ${complex_payload}    ${SECRET_KEY}

    # Validate claim types
    ${type_validation}=    Validate JWT Claim Types    ${complex_payload}
    Should Be True    ${type_validation['is_valid']}

    # Extract and verify each claim type
    ${string_val}=    Get JWT Claim    ${token}    string_claim
    ${int_val}=    Get JWT Claim    ${token}    integer_claim
    ${float_val}=    Get JWT Claim    ${token}    float_claim
    ${bool_val}=    Get JWT Claim    ${token}    boolean_claim
    ${list_val}=    Get JWT Claim    ${token}    list_claim
    ${dict_val}=    Get JWT Claim    ${token}    dict_claim
    ${null_val}=    Get JWT Claim    ${token}    null_claim

    # Verify types are preserved
    Should Be Equal    ${string_val}    hello
    Should Be Equal As Integers    ${int_val}    123
    Should Be Equal As Numbers    ${float_val}    45.67
    Should Be Equal    ${bool_val}    ${True}
    Should Be Equal    ${list_val}    ["item1", "item2", "item3"]
    ${dict_val}=    Evaluate    json.loads('''${dict_val}''')    json
    Should Be Equal    ${dict_val["nested"]}    value
    Should Be Equal As Integers    ${dict_val['number']}    42
    Should Be Equal    ${null_val}    ${None}

JWT Timestamp Utilities
    [Documentation]    Test JWT timestamp utility functions
    [Tags]    jwt    timestamps    utilities
    
    # Generate various timestamps
    ${current_ts}=    Generate Current Timestamp
    ${future_1h}=    Generate Future Timestamp    hours=1
    ${future_30m}=    Generate Future Timestamp    minutes=30
    ${future_custom}=    Generate Future Timestamp    hours=2    minutes=15    seconds=30
    
    # Verify timestamp relationships
    Should Be True    ${future_1h} > ${current_ts}
    Should Be True    ${future_30m} > ${current_ts}
    Should Be True    ${future_custom} > ${future_1h}
    
    # Convert timestamps to datetime strings
    ${current_dt}=    Convert Timestamp To Datetime    ${current_ts}
    ${future_dt}=    Convert Timestamp To Datetime    ${future_1h}
    
    Should Contain    ${current_dt}    T    # ISO format
    Should Contain    ${future_dt}    T
    
    # Create token with timestamp claims
    ${ts_payload}=    Create Dictionary
    ...    user_id=999
    ...    created_at=${current_ts}
    ...    expires_manually=${future_1h}
    
    ${token}=    Generate JWT Token    ${ts_payload}    ${SECRET_KEY}
    
    # Extract and verify timestamp claims
    ${timestamps}=    Extract JWT Timestamps    ${token}
    Should Contain    ${timestamps}    iat
    Should Contain    ${timestamps}    exp
    Should Contain    ${timestamps}    age_seconds
    Should Contain    ${timestamps}    expires_in_seconds

JWT Header Customization
    [Documentation]    Test JWT header customization and validation
    [Tags]    jwt    headers    customization
    
    # Create custom header
    ${custom_header}=    Create JWT Header    
    ...    algorithm=HS384
    ...    kid=key-id-123
    ...    custom_param=custom_value
    
    Should Be Equal    ${custom_header['alg']}    HS384
    Should Be Equal    ${custom_header['typ']}    JWT
    Should Be Equal    ${custom_header['kid']}    key-id-123
    Should Be Equal    ${custom_header['custom_param']}    custom_value
    
    # Generate token and verify header
    ${payload}=    Create Dictionary    user_id=123    header_test=true
    ${token}=    Generate JWT Token    ${payload}    ${SECRET_KEY}    algorithm=HS384
    
    ${decoded_header}=    Decode JWT Header    ${token}
    Should Be Equal    ${decoded_header['alg']}    HS384
    Should Be Equal    ${decoded_header['typ']}    JWT

#JWT Claims Extraction and Analysis
#    [Documentation]    Test comprehensive claims extraction and analysis
#    [Tags]    jwt    claims    extraction    analysis
#
#    # Create comprehensive payload
#   # Create audience list
#    @{audience_list}=    Create List    api-service    web-app
#    ${comprehensive_payload}=    Create Dictionary
#    ...    iss=auth-service
#    ...    sub=user-12345
#    ...    aud=${audience_list}
#    ...    user_id=12345
#    ...    username=advanced_user
#    ...    email=user@company.com
#    ...    roles=["admin", "manager"]
#    ...    permissions={"read": true, "write": true, "delete": false}
#    ...    profile={"name": "John Doe", "department": "Engineering"}
#    ...    settings={"theme": "dark", "notifications": true}
#
#
#    ${token}=    Generate JWT Token    ${comprehensive_payload}    ${SECRET_KEY}
#
#    # Extract all claims with metadata
#    ${all_claims}=    Extract All JWT Claims    ${token}    ${SECRET_KEY}    True
##
##    # Verify structure
#    Should Contain    ${all_claims}    header
##    Should Contain    ${all_claims}    standard_claims
##    Should Contain    ${all_claims}    custom_claims
##    Should Contain    ${all_claims}    all_payload
##    Should Contain    ${all_claims}    total_claims
#
#    # Verify standard claims
#    Should Contain    ${all_claims['standard_claims']}    iss
#    Should Contain    ${all_claims['standard_claims']}    sub
#    Should Contain    ${all_claims['standard_claims']}    aud
#
#    # Verify custom claims
#    Should Contain    ${all_claims['custom_claims']}    user_id
#    Should Contain    ${all_claims['custom_claims']}    username
#    Should Contain    ${all_claims['custom_claims']}    roles
#
#    # Verify total claims count
#    Should Be True    ${all_claims['total_claims']} > 10
#
#    # Extract multiple specific claims
#    ${claim_names}=    Create List    user_id    username    email    roles
#    ${multiple_claims}=    Get Multiple JWT Claims    ${token}    ${claim_names}
#    ...    ${SECRET_KEY}    True
#
#    Should Be Equal As Integers    ${multiple_claims['user_id']}    12345
#    Should Be Equal    ${multiple_claims['username']}    advanced_user
#    Should Be Equal    ${multiple_claims['email']}    user@company.com
#    Should Contain    ${multiple_claims['roles']}    admin
#    Should Contain    ${multiple_claims['roles']}    manager

JWT Token Comparison Advanced
    [Documentation]    Test advanced JWT token comparison scenarios
    [Tags]    jwt    comparison    advanced
    
    # Create base payload
    ${base_payload}=    Create Dictionary
    ...    user_id=100
    ...    role=user
    ...    department=sales
    ...    active=true
    
    # Create modified payload
    ${modified_payload}=    Create Dictionary
    ...    user_id=200
    ...    role=admin
    ...    department=engineering
    ...    active=true
    ...    new_field=added
    
    ${token1}=    Generate JWT Token    ${base_payload}    ${SECRET_KEY}
    ${token2}=    Generate JWT Token    ${modified_payload}    ${SECRET_KEY}
    
    # Detailed comparison
    ${comparison}=    Compare JWT Tokens    ${token1}    ${token2}
    
    Should Be Equal    ${comparison['are_identical']}    ${False}
    Should Be True    ${comparison['payload_differences_count']} >= 3
    
    # Verify specific differences
    Should Be Equal As Integers    
    ...    ${comparison['payload_differences']['user_id']['token1']}    100
    Should Be Equal As Integers    
    ...    ${comparison['payload_differences']['user_id']['token2']}    200
    
    Should Be Equal    
    ...    ${comparison['payload_differences']['role']['token1']}    user
    Should Be Equal    
    ...    ${comparison['payload_differences']['role']['token2']}    admin

JWT Error Handling and Recovery
    [Documentation]    Test JWT error handling and recovery scenarios
    [Tags]    jwt    error-handling    recovery
    
    ${valid_payload}=    Create Dictionary    user_id=123    test=error_handling
    ${valid_token}=    Generate JWT Token    ${valid_payload}    ${SECRET_KEY}
    
    # Test handling of missing claims
    Run Keyword And Expect Error    *Claim*not found*
    ...    Get JWT Claim    ${valid_token}    non_existing_claim
    
    # Test handling of invalid token formats
    ${invalid_structure}=    Validate JWT Structure    invalid-token-format
    Should Be Equal    ${invalid_structure['is_valid_structure']}    ${False}
    Should Be Equal    ${invalid_structure['has_three_parts']}    ${False}
    
    # Test verification of invalid tokens
    ${invalid_verified}=    Verify JWT Token    invalid.token.here    ${SECRET_KEY}
    Should Be Equal    ${invalid_verified}    ${False}
    
    # Test decoding with wrong algorithm
    ${wrong_alg_verified}=    Verify JWT Token    ${valid_token}    ${SECRET_KEY}    algorithm=HS512
    Should Be Equal    ${wrong_alg_verified}    ${False}

JWT Logging and Debugging
    [Documentation]    Test JWT logging and debugging utilities
    [Tags]    jwt    logging    debugging
    
    ${debug_payload}=    Create Dictionary
    ...    user_id=999
    ...    password=secret123
    ...    api_key=sk-1234567890
    ...    token=bearer-token
    ...    public_info=this is safe
    
    # Test safe logging format
    ${safe_log}=    Format JWT Claims For Logging    ${debug_payload}    mask_sensitive=${True}
    Should Contain    ${safe_log}    public_info
    Should Contain    ${safe_log}    this is safe
    # Sensitive data should be masked
    Should Not Contain    ${safe_log}    secret123
    Should Not Contain    ${safe_log}    sk-1234567890
    
    # Test unsafe logging (for debugging)
    ${unsafe_log}=    Format JWT Claims For Logging    ${debug_payload}    mask_sensitive=${False}
    Should Contain    ${unsafe_log}    secret123
    Should Contain    ${unsafe_log}    sk-1234567890
    
    # Generate token and get comprehensive info
    ${token}=    Generate JWT Token    ${debug_payload}    ${SECRET_KEY}
    ${token_info}=    Get JWT Token Info    ${token}
    
    Log    === Debug Token Information ===
    Log    ${token_info}
    Log    ===============================

JWT Performance and Load Testing
    [Documentation]    Test JWT performance with various payload sizes
    [Tags]    jwt    performance    load
    
    # Test with small payload
    ${small_payload}=    Create Dictionary    user_id=1    role=user
    ${start_time}=    Get Current Date    result_format=epoch
    ${small_token}=    Generate JWT Token    ${small_payload}    ${SECRET_KEY}
    ${small_decoded}=    Decode JWT Payload    ${small_token}    ${SECRET_KEY}
    ${end_time}=    Get Current Date    result_format=epoch
    ${small_duration}=    Evaluate    ${end_time} - ${start_time}
    
    # Test with large payload
    ${large_payload}=    Create Dictionary
    FOR    ${i}    IN RANGE    100
        Set To Dictionary    ${large_payload}    field_${i}=value_${i}
    END
    
    ${start_time_large}=    Get Current Date    result_format=epoch
    ${large_token}=    Generate JWT Token    ${large_payload}    ${SECRET_KEY}
    ${large_decoded}=    Decode JWT Payload    ${large_token}    ${SECRET_KEY}
    ${end_time_large}=    Get Current Date    result_format=epoch
    ${large_duration}=    Evaluate    ${end_time_large} - ${start_time_large}
    
    # Verify both operations completed successfully
    Should Be Equal As Integers    ${small_decoded['user_id']}    1
    Should Be Equal    ${large_decoded['field_50']}    value_50
    
    Log    Small payload duration: ${small_duration}s
    Log    Large payload duration: ${large_duration}s
    
    # Performance should be reasonable (under 1 second for large payload)
    Should Be True    ${large_duration} < 1.0

*** Keywords ***
Create Multi-Audience Token
    [Arguments]    ${payload}    ${audiences}
    [Documentation]    Helper to create token with multiple audiences
    
    Set To Dictionary    ${payload}    aud=${audiences}
    ${token}=    Generate JWT Token    ${payload}    ${SECRET_KEY}
    RETURN    ${token}

Verify Complex Claim Structure
    [Arguments]    ${token}    ${claim_name}    ${expected_structure}
    [Documentation]    Helper to verify complex nested claim structures
    
    ${claim_value}=    Get JWT Claim    ${token}    ${claim_name}
    
    FOR    ${key}    ${expected_value}    IN    &{expected_structure}
        Should Be Equal    ${claim_value[${key}]}    ${expected_value}
    END

Log Performance Metrics
    [Arguments]    ${operation}    ${duration}    ${payload_size}
    [Documentation]    Helper to log performance metrics
    
    Log    === Performance Metrics ===
    Log    Operation: ${operation}
    Log    Duration: ${duration}s
    Log    Payload Size: ${payload_size} fields
    Log    Performance: ${{${payload_size}/${duration}}} fields/second
    Log    =========================
