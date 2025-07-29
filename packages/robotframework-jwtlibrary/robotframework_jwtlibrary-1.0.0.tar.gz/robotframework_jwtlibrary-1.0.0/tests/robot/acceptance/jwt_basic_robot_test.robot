*** Settings ***
Documentation     Basic JWT operations test suite
Library           JWTLibrary
Library           Collections
Library           BuiltIn
Library           String

*** Variables ***
${SECRET_KEY}     my_test_secret_key_123
${ALGORITHM}      HS256
${USER_ID}        12345
${USERNAME}       testuser
${ROLE}          admin
${EMAIL}         test@example.com

*** Test Cases ***
Generate And Decode Basic JWT Token
    [Documentation]    Test basic JWT token generation and decoding
    [Tags]    jwt    basic    generation    decoding
    
    # Create test payload
    ${payload}=    Create Dictionary    
    ...    user_id=${USER_ID}
    ...    username=${USERNAME}
    ...    role=${ROLE}
    ...    email=${EMAIL}
    
    # Generate JWT token
    ${token}=    Generate JWT Token    ${payload}    ${SECRET_KEY}
    Should Not Be Empty    ${token}
    Log    Generated Token: ${token}
    
    # Verify token structure (should have 3 parts separated by dots)
    ${token_parts}=    Split String    ${token}    .
    Length Should Be    ${token_parts}    3
    
    # Decode the token payload
    ${decoded_payload}=    Decode JWT Payload    ${token}    ${SECRET_KEY}
    Log    Decoded Payload: ${decoded_payload}
    
    # Verify decoded data matches original payload
    Should Be Equal As Integers    ${decoded_payload['user_id']}    ${USER_ID}
    Should Be Equal    ${decoded_payload['username']}    ${USERNAME}
    Should Be Equal    ${decoded_payload['role']}    ${ROLE}
    Should Be Equal    ${decoded_payload['email']}    ${EMAIL}
    
    # Verify standard JWT claims are present
    Should Contain    ${decoded_payload}    iat
    Should Contain    ${decoded_payload}    exp
    Should Contain    ${decoded_payload}    nbf

Generate JWT Token With Different Algorithms
    [Documentation]    Test JWT token generation with different algorithms
    [Tags]    jwt    algorithms
    
    ${payload}=    Create Dictionary    user_id=999    test=algorithm
    
    # Test HS256 (default)
    ${token_hs256}=    Generate JWT Token    ${payload}    ${SECRET_KEY}
    ${header_hs256}=    Decode JWT Header    ${token_hs256}
    Should Be Equal    ${header_hs256['alg']}    HS256
    
    # Test HS384
    ${token_hs384}=    Generate JWT Token    ${payload}    ${SECRET_KEY}    algorithm=HS384
    ${header_hs384}=    Decode JWT Header    ${token_hs384}
    Should Be Equal    ${header_hs384['alg']}    HS384
    
    # Test HS512
    ${token_hs512}=    Generate JWT Token    ${payload}    ${SECRET_KEY}    algorithm=HS512
    ${header_hs512}=    Decode JWT Header    ${token_hs512}
    Should Be Equal    ${header_hs512['alg']}    HS512
    
    # Verify all tokens can be decoded with correct algorithm
    ${decoded_hs256}=    Decode JWT Payload    ${token_hs256}    ${SECRET_KEY}    algorithm=HS256
    ${decoded_hs384}=    Decode JWT Payload    ${token_hs384}    ${SECRET_KEY}    algorithm=HS384
    ${decoded_hs512}=    Decode JWT Payload    ${token_hs512}    ${SECRET_KEY}    algorithm=HS512
    
    Should Be Equal As Integers    ${decoded_hs256['user_id']}    999
    Should Be Equal As Integers    ${decoded_hs384['user_id']}    999
    Should Be Equal As Integers    ${decoded_hs512['user_id']}    999

Generate JWT Token With Custom Expiration
    [Documentation]    Test JWT token generation with custom expiration time
    [Tags]    jwt    expiration
    
    ${payload}=    Create Dictionary    user_id=777    role=temp_user
    
    # Generate token with 1 hour expiration
    ${token_1h}=    Generate JWT Token    ${payload}    ${SECRET_KEY}    expiration_hours=1
    
    # Generate token with 24 hour expiration (default)
    ${token_24h}=    Generate JWT Token    ${payload}    ${SECRET_KEY}
    
    # Check expiration details
    ${exp_info_1h}=    Check JWT Expiration    ${token_1h}
    ${exp_info_24h}=    Check JWT Expiration    ${token_24h}
    
    # Both tokens should not be expired
    Should Be Equal    ${exp_info_1h['is_expired']}    ${False}
    Should Be Equal    ${exp_info_24h['is_expired']}    ${False}
    
    # 24h token should expire later than 1h token
    Should Be True    ${exp_info_24h['time_until_expiry']} > ${exp_info_1h['time_until_expiry']}

Generate JWT Token Without Expiration
    [Documentation]    Test JWT token generation without expiration claim
    [Tags]    jwt    no-expiration
    
    ${payload}=    Create Dictionary    user_id=888    permanent=true
    
    # Generate token without expiration
    ${token}=    Generate JWT Token Without Expiration    ${payload}    ${SECRET_KEY}
    
    # Check expiration info
    ${exp_info}=    Check JWT Expiration    ${token}
    Should Be Equal    ${exp_info['has_expiration']}    ${False}
    Should Be Equal    ${exp_info['is_expired']}    ${False}
    Should Be Equal    ${exp_info['expires_at']}    ${None}

JWT Token Verification
    [Documentation]    Test JWT token verification functionality
    [Tags]    jwt    verification
    
    ${payload}=    Create Dictionary    user_id=555    role=user
    ${token}=    Generate JWT Token    ${payload}    ${SECRET_KEY}
    
    # Verify with correct secret key
    ${is_valid_correct}=    Verify JWT Token    ${token}    ${SECRET_KEY}
    Should Be True    ${is_valid_correct}
    
    # Verify with wrong secret key
    ${is_valid_wrong}=    Verify JWT Token    ${token}    wrong_secret_key
    Should Be Equal    ${is_valid_wrong}    ${False}
    
    # Verify invalid token format
    ${is_valid_invalid}=    Verify JWT Token    invalid.token.format    ${SECRET_KEY}
    Should Be Equal    ${is_valid_invalid}    ${False}

Extract Specific JWT Claims
    [Documentation]    Test extracting specific claims from JWT tokens
    [Tags]    jwt    claims
    
    ${payload}=    Create Dictionary    
    ...    user_id=123
    ...    username=claimtest
    ...    role=admin
    ...    department=engineering
    ...    clearance_level=5
    
    ${token}=    Generate JWT Token    ${payload}    ${SECRET_KEY}
    
    # Extract individual claims
    ${user_id}=    Get JWT Claim    ${token}    user_id
    ${username}=    Get JWT Claim    ${token}    username
    ${role}=    Get JWT Claim    ${token}    role
    ${department}=    Get JWT Claim    ${token}    department
    ${clearance}=    Get JWT Claim    ${token}    clearance_level
    
    # Verify extracted claims
    Should Be Equal As Integers    ${user_id}    123
    Should Be Equal    ${username}    claimtest
    Should Be Equal    ${role}    admin
    Should Be Equal    ${department}    engineering
    Should Be Equal As Integers    ${clearance}    5
    
    # Extract multiple claims at once
    ${claim_names}=    Create List    user_id    role    department
    ${multiple_claims}=    Get Multiple JWT Claims    ${token}    ${claim_names}
    
    Should Be Equal As Integers    ${multiple_claims['user_id']}    123
    Should Be Equal    ${multiple_claims['role']}    admin
    Should Be Equal    ${multiple_claims['department']}    engineering

JWT Claims Validation
    [Documentation]    Test JWT claims validation functionality
    [Tags]    jwt    validation
    
    ${payload}=    Create Dictionary    
    ...    user_id=456
    ...    role=manager
    ...    email=manager@company.com
    ...    active=true
    
    ${token}=    Generate JWT Token    ${payload}    ${SECRET_KEY}
    
    # Test valid claims validation
    ${expected_valid}=    Create Dictionary    
    ...    user_id=456
    ...    role=manager
    ...    active=true
    
    ${validation_result}=    Validate JWT Claims    ${token}    ${expected_valid}
    Should Be True    ${validation_result}
    
    # Test invalid claims validation
    ${expected_invalid}=    Create Dictionary    
    ...    user_id=999
    ...    role=admin
    
    ${validation_result_invalid}=    Validate JWT Claims    ${token}    ${expected_invalid}
    Should Be Equal    ${validation_result_invalid}    ${False}

JWT Token Structure Validation
    [Documentation]    Test JWT token structure validation
    [Tags]    jwt    structure
    
    ${payload}=    Create Dictionary    user_id=321    test=structure
    ${token}=    Generate JWT Token    ${payload}    ${SECRET_KEY}
    
    # Validate structure of valid token
    ${structure_info}=    Validate JWT Structure    ${token}
    Should Be True    ${structure_info['is_valid_structure']}
    Should Be True    ${structure_info['has_three_parts']}
    Should Be True    ${structure_info['has_valid_header']}
    Should Be True    ${structure_info['has_valid_payload']}
    
    # Check header info
    Should Be Equal    ${structure_info['header_info']['algorithm']}    HS256
    Should Be Equal    ${structure_info['header_info']['type']}    JWT
    
    # Check payload info
    Should Be True    ${structure_info['payload_info']['claims_count']} > 0
    Should Be True    ${structure_info['payload_info']['has_expiration']}
    Should Be True    ${structure_info['payload_info']['has_issued_at']}

JWT Utility Functions
    [Documentation]    Test JWT utility functions
    [Tags]    jwt    utilities
    
    # Test payload creation
    ${created_payload}=    Create JWT Payload    
    ...    user_id=999
    ...    service=api
    ...    version=1.0
    
    Should Be Equal As Integers    ${created_payload['user_id']}    999
    Should Be Equal    ${created_payload['service']}    api
    Should Be Equal    ${created_payload['version']}    1.0
    
    # Test timestamp generation
    ${current_ts}=    Generate Current Timestamp
    ${future_ts}=    Generate Future Timestamp    hours=1
    
    Should Be True    ${future_ts} > ${current_ts}
    
    # Test timestamp conversion
    ${datetime_str}=    Convert Timestamp To Datetime    ${current_ts}
    Should Contain    ${datetime_str}    T    # ISO format contains T
    
    # Generate token and get info
    ${token}=    Generate JWT Token    ${created_payload}    ${SECRET_KEY}
    ${token_info}=    Get JWT Token Info    ${token}
    
    Should Be Equal    ${token_info['algorithm']}    HS256
    Should Be Equal    ${token_info['type']}    JWT
    Should Be True    ${token_info['claims_count']} > 0

JWT Token Comparison
    [Documentation]    Test JWT token comparison functionality
    [Tags]    jwt    comparison
    
    # Create two different payloads
    ${payload1}=    Create Dictionary    user_id=111    role=user    team=alpha
    ${payload2}=    Create Dictionary    user_id=222    role=admin    team=beta
    
    ${token1}=    Generate JWT Token    ${payload1}    ${SECRET_KEY}
    ${token2}=    Generate JWT Token    ${payload2}    ${SECRET_KEY}
    
    # Compare different tokens
    ${comparison}=    Compare JWT Tokens    ${token1}    ${token2}
    Should Be Equal    ${comparison['are_identical']}    ${False}
    Should Be True    ${comparison['payload_differences_count']} > 0
    
    # Verify specific differences
    Should Contain    ${comparison['payload_differences']}    user_id
    Should Contain    ${comparison['payload_differences']}    role
    Should Contain    ${comparison['payload_differences']}    team

Decode JWT Without Verification
    [Documentation]    Test decoding JWT without signature verification
    [Tags]    jwt    unsafe-decoding
    
    ${payload}=    Create Dictionary    user_id=666    unsafe=True
    ${token}=    Generate JWT Token    ${payload}    ${SECRET_KEY}
    
    # Decode without verification (unsafe)
    ${decoded_unsafe}=    Decode JWT Payload    ${token}    verify_signature=False
    Should Be Equal As Integers    ${decoded_unsafe['user_id']}    666
    Should Be Equal    ${decoded_unsafe['unsafe']}    True
    
    # Should work even with wrong or no secret key
    ${decoded_no_secret}=    Decode JWT Payload Unsafe    ${token}
    Should Be Equal As Integers    ${decoded_no_secret['user_id']}    666

Generate JWT Token With Claims Keyword Arguments
    [Documentation]    Test generating tokens using keyword arguments
    [Tags]    jwt    keyword-args
    
    # Generate token using keyword arguments
    ${token}=    Generate JWT Token With Claims    ${SECRET_KEY}
    ...    user_id=789
    ...    name=John Doe
    ...    role=developer
    ...    projects=["project1", "project2"]
    
    # Verify token content
    ${decoded}=    Decode JWT Payload    ${token}    ${SECRET_KEY}
    Should Be Equal As Integers    ${decoded['user_id']}    789
    Should Be Equal    ${decoded['name']}    John Doe
    Should Be Equal    ${decoded['role']}    developer
    Should Be Equal    ${decoded['projects']}    ["project1", "project2"]

*** Keywords ***
Log JWT Token Details
    [Arguments]    ${token}    ${secret_key}=${SECRET_KEY}
    [Documentation]    Helper keyword to log comprehensive JWT token details
    
    ${header}=    Decode JWT Header    ${token}
    ${payload}=    Decode JWT Payload    ${token}    ${secret_key}
    ${token_info}=    Get JWT Token Info    ${token}
    ${exp_info}=    Check JWT Expiration    ${token}
    
    Log    === JWT Token Details ===
    Log    Header: ${header}
    Log    Payload: ${payload}
    Log    Token Info: ${token_info}
    Log    Expiration Info: ${exp_info}
    Log    ========================

Create Test User Payload
    [Arguments]    ${user_id}    ${username}    ${role}=user
    [Documentation]    Helper keyword to create standardized user payload
    
    ${payload}=    Create Dictionary
    ...    user_id=${user_id}
    ...    username=${username}
    ...    role=${role}
    ...    created_at=${EMPTY}
    
    ${current_time}=    Generate Current Timestamp
    Set To Dictionary    ${payload}    created_at=${current_time}
    
    RETURN    ${payload}

Verify JWT Token Contains Standard Claims
    [Arguments]    ${token}    ${secret_key}=${SECRET_KEY}
    [Documentation]    Helper keyword to verify standard JWT claims
    
    ${payload}=    Decode JWT Payload    ${token}    ${secret_key}
    
    # Verify standard claims exist
    Should Contain    ${payload}    iat    # Issued At
    Should Contain    ${payload}    exp    # Expiration
    Should Contain    ${payload}    nbf    # Not Before
    
    # Verify claim types
    Should Be True    isinstance($payload['iat'], (int, float))
    Should Be True    isinstance($payload['exp'], (int, float))
    Should Be True    isinstance($payload['nbf'], (int, float))
    
    # Verify logical order: nbf <= iat < exp
    Should Be True    ${payload['nbf']} <= ${payload['iat']}
    Should Be True    ${payload['iat']} < ${payload['exp']}
