*** Settings ***
Documentation     Simple JWT usage examples
Library           JWTLibrary
Library           Collections

*** Variables ***
${SECRET_KEY}     my_application_secret_key

*** Test Cases ***
Example 1: Basic Token Generation and Validation
    [Documentation]    Shows basic JWT token creation and validation
    [Tags]    example    basic
    
    # Step 1: Create user data
    ${user_data}=    Create Dictionary
    ...    user_id=12345
    ...    username=john_doe
    ...    email=john@example.com
    ...    role=user
    
    # Step 2: Generate JWT token
    ${jwt_token}=    Generate JWT Token    ${user_data}    ${SECRET_KEY}
    Log    Generated JWT Token: ${jwt_token}
    
    # Step 3: Verify the token is valid
    ${is_valid}=    Verify JWT Token    ${jwt_token}    ${SECRET_KEY}
    Should Be True    ${is_valid}
    Log    ✓ Token is valid
    
    # Step 4: Decode the token to get user data back
    ${decoded_data}=    Decode JWT Payload    ${jwt_token}    ${SECRET_KEY}
    Should Be Equal    ${decoded_data['username']}    john_doe
    Should Be Equal    ${decoded_data['role']}    user
    Log    ✓ User data successfully retrieved from token

Example 2: Working with Token Expiration
    [Documentation]    Shows how to work with token expiration
    [Tags]    example    expiration
    
    ${user_data}=    Create Dictionary    user_id=67890    session=temp
    
    # Create token that expires in 1 hour
    ${short_token}=    Generate JWT Token    ${user_data}    ${SECRET_KEY}    expiration_hours=1
    
    # Check when the token expires
    ${expiration_info}=    Check JWT Expiration    ${short_token}
    Log    Token expires at: ${expiration_info['expires_at']}
    Log    Time until expiration: ${expiration_info['time_until_expiry']} seconds
    Should Be Equal    ${expiration_info['is_expired']}    ${False}
    
    # Create token without expiration
    ${permanent_token}=    Generate JWT Token Without Expiration    ${user_data}    ${SECRET_KEY}
    ${perm_exp_info}=    Check JWT Expiration    ${permanent_token}
    Should Be Equal    ${perm_exp_info['has_expiration']}    ${False}
    Log    ✓ Permanent token created successfully

Example 3: Extracting Specific Claims
    [Documentation]    Shows how to extract specific information from tokens
    [Tags]    example    claims
    
    ${employee_data}=    Create Dictionary
    ...    employee_id=E001
    ...    name=Alice Smith
    ...    department=Engineering
    ...    clearance_level=3
    ...    email=alice@company.com
    
    ${token}=    Generate JWT Token    ${employee_data}    ${SECRET_KEY}
    
    # Extract individual pieces of information
    ${employee_id}=    Get JWT Claim    ${token}    employee_id
    ${department}=    Get JWT Claim    ${token}    department
    ${clearance}=    Get JWT Claim    ${token}    clearance_level
    
    Log    Employee ID: ${employee_id}
    Log    Department: ${department}
    Log    Clearance Level: ${clearance}
    
    # Extract multiple claims at once
    ${claim_names}=    Create List    name    email    department
    ${employee_info}=    Get Multiple JWT Claims    ${token}    ${claim_names}
    
    Should Be Equal    ${employee_info['name']}    Alice Smith
    Should Be Equal    ${employee_info['email']}    alice@company.com
    Log    ✓ Employee information extracted successfully

Example 4: Using Different JWT Algorithms
    [Documentation]    Shows how to use different JWT signing algorithms
    [Tags]    example    algorithms
    
    ${api_data}=    Create Dictionary    api_key=abc123    service=payment
    
    # Use HS256 (default)
    ${token_hs256}=    Generate JWT Token    ${api_data}    ${SECRET_KEY}
    ${header_hs256}=    Decode JWT Header    ${token_hs256}
    Should Be Equal    ${header_hs256['alg']}    HS256
    
    # Use HS512 for higher security
    ${token_hs512}=    Generate JWT Token    ${api_data}    ${SECRET_KEY}    algorithm=HS512
    ${header_hs512}=    Decode JWT Header    ${token_hs512}
    Should Be Equal    ${header_hs512['alg']}    HS512
    
    # Verify both tokens work with their respective algorithms
    ${valid_256}=    Verify JWT Token    ${token_hs256}    ${SECRET_KEY}    algorithm=HS256
    ${valid_512}=    Verify JWT Token    ${token_hs512}    ${SECRET_KEY}    algorithm=HS512
    Should Be True    ${valid_256}
    Should Be True    ${valid_512}
    
    Log    ✓ Successfully used multiple JWT algorithms

Example 5: Error Handling
    [Documentation]    Shows how JWT operations handle errors gracefully
    [Tags]    example    error-handling
    
    ${valid_data}=    Create Dictionary    user_id=999    test=error_demo
    ${valid_token}=    Generate JWT Token    ${valid_data}    ${SECRET_KEY}
    
    # Try to verify token with wrong secret - should return False, not crash
    ${wrong_secret_result}=    Verify JWT Token    ${valid_token}    wrong_secret
    Should Be Equal    ${wrong_secret_result}    ${False}
    Log    ✓ Wrong secret key handled gracefully
    
    # Try to verify completely invalid token - should return False
    ${invalid_token_result}=    Verify JWT Token    invalid.token.here    ${SECRET_KEY}
    Should Be Equal    ${invalid_token_result}    ${False}
    Log    ✓ Invalid token handled gracefully
    
    # Try to get non-existent claim - should raise clear error
    Run Keyword And Expect Error    *Claim 'nonexistent' not found*
    ...    Get JWT Claim    ${valid_token}    nonexistent
    Log    ✓ Missing claim error handled with clear message

Example 6: Creating Payloads Easily
    [Documentation]    Shows convenient ways to create JWT payloads
    [Tags]    example    payload-creation
    
    # Method 1: Using Create JWT Payload keyword
    ${payload1}=    Create JWT Payload
    ...    user_id=111
    ...    role=admin
    ...    active=true
    ...    login_count=5
    
    # Method 2: Using Generate JWT Token With Claims
    ${token1}=    Generate JWT Token With Claims    ${SECRET_KEY}
    ...    user_id=222
    ...    role=user
    ...    department=sales
    
    # Method 3: Traditional dictionary creation
    ${payload2}=    Create Dictionary
    ...    user_id=333
    ...    preferences={"theme": "dark", "notifications": true}
    
    ${token2}=    Generate JWT Token    ${payload2}    ${SECRET_KEY}
    
    # Verify all methods work
    ${decoded1}=    Decode JWT Payload    ${token1}    ${SECRET_KEY}
    ${decoded2}=    Decode JWT Payload    ${token2}    ${SECRET_KEY}
    
    Should Be Equal As Integers    ${decoded1['user_id']}    222
    Should Be Equal As Integers    ${decoded2['user_id']}    333
    Log    ✓ All payload creation methods work correctly

*** Keywords ***
Demo User Login Workflow
    [Arguments]    ${username}    ${user_id}    ${role}
    [Documentation]    Example workflow for user login with JWT
    
    Log    Starting login workflow for user: ${username}
    
    # Step 1: Create user session data
    ${session_data}=    Create Dictionary
    ...    user_id=${user_id}
    ...    username=${username}
    ...    role=${role}
    ...    login_time=${EMPTY}
    
    ${login_timestamp}=    Generate Current Timestamp
    Set To Dictionary    ${session_data}    login_time=${login_timestamp}
    
    # Step 2: Generate session token (valid for 8 hours)
    ${session_token}=    Generate JWT Token    ${session_data}    ${SECRET_KEY}    expiration_hours=8
    
    # Step 3: Verify token is valid
    ${is_valid}=    Verify JWT Token    ${session_token}    ${SECRET_KEY}
    Should Be True    ${is_valid}
    
    Log    ✓ Login successful - Session token created
    RETURN    ${session_token}

Demo API Authorization Check
    [Arguments]    ${token}    ${required_role}
    [Documentation]    Example workflow for API endpoint authorization
    
    Log    Checking authorization for role: ${required_role}
    
    # Step 1: Verify token is valid and not expired
    ${is_valid}=    Verify JWT Token    ${token}    ${SECRET_KEY}
    Should Be True    ${is_valid}    Token is invalid or expired
    
    # Step 2: Extract user role from token
    ${user_role}=    Get JWT Claim    ${token}    role
    
    # Step 3: Check if user has required role
    Should Be Equal    ${user_role}    ${required_role}    Insufficient permissions
    
    Log    ✓ Authorization successful - User has ${required_role} role
    RETURN    ${True}

Demo Token Refresh
    [Arguments]    ${old_token}
    [Documentation]    Example workflow for refreshing an expired token
    
    Log    Refreshing token...
    
    # Step 1: Extract user data from old token (even if expired)
    ${old_data}=    Decode JWT Payload    ${old_token}    verify_signature=False
    
    # Step 2: Create new token with updated timestamp
    ${refresh_data}=    Copy Dictionary    ${old_data}
    ${refresh_timestamp}=    Generate Current Timestamp
    Set To Dictionary    ${refresh_data}    refreshed_at=${refresh_timestamp}
    
    # Step 3: Generate new token
    ${new_token}=    Generate JWT Token    ${refresh_data}    ${SECRET_KEY}
    
    Log    ✓ Token refreshed successfully
    RETURN    ${new_token}
