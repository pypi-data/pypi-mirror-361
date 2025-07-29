*** Settings ***
Documentation     JWT API integration test suite
Library           JWTLibrary
Library           RequestsLibrary
Library           Collections
Library           DateTime

*** Variables ***
${API_SECRET}     integration_test_secret_key
${API_BASE_URL}   http://localhost:8000
${SERVICE_SECRET}  service_to_service_secret

*** Test Cases ***
Test JWT Authentication Flow
    [Documentation]    Test complete JWT authentication flow with API
    [Tags]    jwt    integration    api    authentication
    
    # Step 1: Generate user authentication token
    ${user_payload}=    Create Dictionary
    ...    user_id=12345
    ...    username=testuser
    ...    email=test@example.com
    ...    role=user
    ...    permissions=["read", "write"]
    
    ${auth_token}=    Generate JWT Token    ${user_payload}    ${API_SECRET}    expiration_hours=1
    
    # Step 2: Validate token structure
    ${token_info}=    Get JWT Token Info    ${auth_token}
    Should Be Equal    ${token_info['algorithm']}    HS256
    Should Be True    ${token_info['claims_count']} > 5
    
    # Step 3: Verify token before API call
    ${is_valid}=    Verify JWT Token    ${auth_token}    ${API_SECRET}
    Should Be True    ${is_valid}
    
    # Step 4: Extract user information from token
    ${user_id}=    Get JWT Claim    ${auth_token}    user_id
    ${role}=    Get JWT Claim    ${auth_token}    role
    ${permissions}=    Get JWT Claim    ${auth_token}    permissions
    
    Should Be Equal As Integers    ${user_id}    12345
    Should Be Equal    ${role}    user
    Should Contain    ${permissions}    read
    Should Contain    ${permissions}    write
    
    # Step 5: Simulate API header preparation
    ${auth_header}=    Set Variable    Bearer ${auth_token}
    Log    Authorization header prepared: ${auth_header}

Test Service-to-Service JWT Communication
    [Documentation]    Test JWT tokens for service-to-service communication
    [Tags]    jwt    integration    microservices
    
    # Service A generates token for Service B
    ${service_a_payload}=    Create Dictionary
    ...    iss=service-a
    ...    aud=service-b
    ...    sub=system
    ...    scope=data:read data:write
    ...    service_id=svc-001
    ...    environment=test
    
    ${service_token}=    Generate JWT Token    ${service_a_payload}    ${SERVICE_SECRET}    expiration_hours=0.5
    
    # Service B validates the token
    ${token_valid}=    Verify JWT Token    ${service_token}    ${SERVICE_SECRET}
    Should Be True    ${token_valid}
    
    # Service B extracts service information
    ${issuer}=    Get JWT Claim    ${service_token}    iss
    ${audience}=    Get JWT Claim    ${service_token}    aud
    ${scope}=    Get JWT Claim    ${service_token}    scope
    
    Should Be Equal    ${issuer}    service-a
    Should Be Equal    ${audience}    service-b
    Should Contain    ${scope}    data:read
    
    # Validate audience specifically
    ${aud_valid}=    Validate JWT Audience    ${service_token}    service-b
    Should Be True    ${aud_valid}
    
    # Validate expected claims
    ${expected_claims}=    Create Dictionary    iss=service-a    aud=service-b    sub=system
    ${claims_valid}=    Validate JWT Claims    ${service_token}    ${expected_claims}    ${SERVICE_SECRET}    ${True}
    Should Be True    ${claims_valid}

Test JWT Token Refresh Workflow
    [Documentation]    Test token refresh and re-authentication workflow
    [Tags]    jwt    integration    refresh
    
    # Generate initial token with short expiration
    ${initial_payload}=    Create Dictionary
    ...    user_id=99999
    ...    session_id=sess-123
    ...    role=admin
    ...    refresh_allowed=true
    
    ${short_token}=    Generate JWT Token    ${initial_payload}    ${API_SECRET}    expiration_hours=0.01  # Very short
    
    # Verify initial token is valid
    ${initial_valid}=    Verify JWT Token    ${short_token}    ${API_SECRET}
    Should Be True    ${initial_valid}
    
    # Wait for token to expire
    Sleep    1 minute
    
    # Verify token is now expired
    ${exp_info}=    Check JWT Expiration    ${short_token}
    Should Be True    ${exp_info['is_expired']}
    
    # Generate refresh token with extended expiration
    ${refresh_payload}=    Create Dictionary
    ...    user_id=99999
    ...    session_id=sess-123
    ...    role=admin
    ...    refreshed_at=${EMPTY}
    
    ${current_time}=    Get Current Date    result_format=epoch
    Set To Dictionary    ${refresh_payload}    refreshed_at=${current_time}
    
    ${refresh_token}=    Generate JWT Token    ${refresh_payload}    ${API_SECRET}    expiration_hours=2
    
    # Verify refresh token
    ${refresh_valid}=    Verify JWT Token    ${refresh_token}    ${API_SECRET}
    Should Be True    ${refresh_valid}
    
    # Compare original and refresh tokens
    ${comparison}=    Compare JWT Tokens    ${short_token}    ${refresh_token}
    Should Be Equal    ${comparison['are_identical']}    ${False}
    Should Contain    ${comparison['payload_differences']}    refreshed_at

Test Multi-Tenant JWT Isolation
    [Documentation]    Test JWT token isolation between different tenants
    [Tags]    jwt    integration    multi-tenant
    
    # Tenant A token
    ${tenant_a_payload}=    Create Dictionary
    ...    user_id=1001
    ...    tenant_id=tenant-a
    ...    role=admin
    ...    data_access=["tenant-a-data"]
    
    ${tenant_a_secret}=    Set Variable    tenant_a_secret_key
    ${tenant_a_token}=    Generate JWT Token    ${tenant_a_payload}    ${tenant_a_secret}
    
    # Tenant B token
    ${tenant_b_payload}=    Create Dictionary
    ...    user_id=2001
    ...    tenant_id=tenant-b
    ...    role=user
    ...    data_access=["tenant-b-data"]
    
    ${tenant_b_secret}=    Set Variable    tenant_b_secret_key
    ${tenant_b_token}=    Generate JWT Token    ${tenant_b_payload}    ${tenant_b_secret}
    
    # Verify tenant isolation - Tenant A token should not validate with Tenant B secret
    ${cross_tenant_valid}=    Verify JWT Token    ${tenant_a_token}    ${tenant_b_secret}
    Should Be Equal    ${cross_tenant_valid}    ${False}
    
    # Verify tenant-specific tokens work with their own secrets
    ${tenant_a_valid}=    Verify JWT Token    ${tenant_a_token}    ${tenant_a_secret}
    ${tenant_b_valid}=    Verify JWT Token    ${tenant_b_token}    ${tenant_b_secret}
    Should Be True    ${tenant_a_valid}
    Should Be True    ${tenant_b_valid}
    
    # Verify tenant-specific data access
    ${tenant_a_access}=    Get JWT Claim    ${tenant_a_token}    data_access
    ${tenant_b_access}=    Get JWT Claim    ${tenant_b_token}    data_access
    
    Should Contain    ${tenant_a_access}    tenant-a-data
    Should Not Contain    ${tenant_a_access}    tenant-b-data
    Should Contain    ${tenant_b_access}    tenant-b-data
    Should Not Contain    ${tenant_b_access}    tenant-a-data

Test JWT API Rate Limiting Simulation
    [Documentation]    Test JWT tokens in rate limiting scenarios
    [Tags]    jwt    integration    rate-limiting
    
    # Generate tokens for different rate limit tiers
    ${basic_user_payload}=    Create Dictionary
    ...    user_id=3001
    ...    tier=basic
    ...    rate_limit=100
    ...    requests_per_minute=10
    
    ${premium_user_payload}=    Create Dictionary
    ...    user_id=3002
    ...    tier=premium
    ...    rate_limit=1000
    ...    requests_per_minute=100
    
    ${basic_token}=    Generate JWT Token    ${basic_user_payload}    ${API_SECRET}
    ${premium_token}=    Generate JWT Token    ${premium_user_payload}    ${API_SECRET}
    
    # Extract rate limiting information
    ${basic_limit}=    Get JWT Claim    ${basic_token}    rate_limit
    ${premium_limit}=    Get JWT Claim    ${premium_token}    rate_limit
    
    Should Be Equal As Integers    ${basic_limit}    100
    Should Be Equal As Integers    ${premium_limit}    1000
    Should Be True    ${premium_limit} > ${basic_limit}
    
    # Simulate rate limit validation
    ${basic_rpm}=    Get JWT Claim    ${basic_token}    requests_per_minute
    ${premium_rpm}=    Get JWT Claim    ${premium_token}    requests_per_minute
    
    Should Be True    ${premium_rpm} > ${basic_rpm}

Test JWT RBAC (Role-Based Access Control)
    [Documentation]    Test JWT tokens for role-based access control
    [Tags]    jwt    integration    rbac    authorization
    
    # Admin user token
    ${admin_payload}=    Create Dictionary
    ...    user_id=4001
    ...    role=admin
    ...    permissions=["users:read", "users:write", "users:delete", "system:config"]
    ...    scope=admin
    
    # Regular user token
    ${user_payload}=    Create Dictionary
    ...    user_id=4002
    ...    role=user
    ...    permissions=["profile:read", "profile:write"]
    ...    scope=user
    
    # Read-only user token
    ${readonly_payload}=    Create Dictionary
    ...    user_id=4003
    ...    role=readonly
    ...    permissions=["profile:read"]
    ...    scope=readonly
    
    ${admin_token}=    Generate JWT Token    ${admin_payload}    ${API_SECRET}
    ${user_token}=    Generate JWT Token    ${user_payload}    ${API_SECRET}
    ${readonly_token}=    Generate JWT Token    ${readonly_payload}    ${API_SECRET}
    
    # Test admin permissions
    ${admin_perms}=    Get JWT Claim    ${admin_token}    permissions
    Should Contain    ${admin_perms}    users:read
    Should Contain    ${admin_perms}    users:write
    Should Contain    ${admin_perms}    users:delete
    Should Contain    ${admin_perms}    system:config
    
    # Test user permissions
    ${user_perms}=    Get JWT Claim    ${user_token}    permissions
    Should Contain    ${user_perms}    profile:read
    Should Contain    ${user_perms}    profile:write
    Should Not Contain    ${user_perms}    users:delete
    
    # Test readonly permissions
    ${readonly_perms}=    Get JWT Claim    ${readonly_token}    permissions
    Should Contain    ${readonly_perms}    profile:read
    Should Not Contain    ${readonly_perms}    profile:write
    Should Not Contain    ${readonly_perms}    users:read
    
    # Validate role hierarchy
    ${admin_role}=    Get JWT Claim    ${admin_token}    role
    ${user_role}=    Get JWT Claim    ${user_token}    role
    ${readonly_role}=    Get JWT Claim    ${readonly_token}    role
    
    Should Be Equal    ${admin_role}    admin
    Should Be Equal    ${user_role}    user
    Should Be Equal    ${readonly_role}    readonly

Test JWT Session Management
    [Documentation]    Test JWT tokens for session management scenarios
    [Tags]    jwt    integration    session-management
    
    # Create session token
    ${session_id}=    Set Variable    sess_${EMPTY}
    ${timestamp}=    Generate Current Timestamp
    ${session_id}=    Set Variable    sess_${timestamp}
    
    ${session_payload}=    Create Dictionary
    ...    user_id=5001
    ...    session_id=${session_id}
    ...    device=web-browser
    ...    ip_address=192.168.1.100
    ...    user_agent=Mozilla/5.0...
    ...    last_activity=${timestamp}
    
    ${session_token}=    Generate JWT Token    ${session_payload}    ${API_SECRET}    expiration_hours=8
    
    # Verify session information
    ${extracted_session_id}=    Get JWT Claim    ${session_token}    session_id
    ${device}=    Get JWT Claim    ${session_token}    device
    ${last_activity}=    Get JWT Claim    ${session_token}    last_activity
    
    Should Be Equal    ${extracted_session_id}    ${session_id}
    Should Be Equal    ${device}    web-browser
    Should Be Equal As Integers    ${last_activity}    ${timestamp}
    
    # Test session activity update
    Sleep    2s
    ${new_activity_time}=    Generate Current Timestamp
    ${updated_payload}=    Copy Dictionary    ${session_payload}
    Set To Dictionary    ${updated_payload}    last_activity=${new_activity_time}
    
    ${updated_token}=    Generate JWT Token    ${updated_payload}    ${API_SECRET}    expiration_hours=8
    
    # Compare session tokens
    ${session_comparison}=    Compare JWT Tokens    ${session_token}    ${updated_token}
    Should Be Equal    ${session_comparison['are_identical']}    ${False}
    Should Contain    ${session_comparison['payload_differences']}    last_activity

*** Keywords ***
Simulate API Request With JWT
    [Arguments]    ${token}    ${endpoint}    ${method}=GET
    [Documentation]    Helper keyword to simulate API request with JWT token
    
    ${headers}=    Create Dictionary    Authorization=Bearer ${token}
    Log    Simulating ${method} request to ${endpoint}
    Log    Headers: ${headers}
    
    # In real scenario, this would make actual HTTP request
    # For integration test, we just validate the token format
    Should Not Be Empty    ${token}
    Should Contain    ${token}    .    # JWT has dots
    
    RETURN    ${headers}

Validate JWT For Endpoint Access
    [Arguments]    ${token}    ${required_permission}    ${secret_key}=${API_SECRET}
    [Documentation]    Helper to validate JWT token has required permission for endpoint
    
    ${is_valid}=    Verify JWT Token    ${token}    ${secret_key}
    Should Be True    ${is_valid}
    
    ${permissions}=    Get JWT Claim    ${token}    permissions
    Should Contain    ${permissions}    ${required_permission}
    
    Log    Token validated for permission: ${required_permission}

Create Multi Service Environment
    [Documentation]    Helper to create multiple service tokens for testing
    
    # Auth Service
    ${auth_service_payload}=    Create Dictionary
    ...    service=auth
    ...    iss=auth-service
    ...    capabilities=["authenticate", "authorize"]
    
    # User Service  
    ${user_service_payload}=    Create Dictionary
    ...    service=user
    ...    iss=user-service
    ...    capabilities=["user:crud", "profile:manage"]
    
    # Data Service
    ${data_service_payload}=    Create Dictionary
    ...    service=data
    ...    iss=data-service
    ...    capabilities=["data:read", "data:write", "data:analytics"]
    
    ${auth_token}=    Generate JWT Token    ${auth_service_payload}    ${SERVICE_SECRET}
    ${user_token}=    Generate JWT Token    ${user_service_payload}    ${SERVICE_SECRET}
    ${data_token}=    Generate JWT Token    ${data_service_payload}    ${SERVICE_SECRET}
    
    ${service_tokens}=    Create Dictionary
    ...    auth=${auth_token}
    ...    user=${user_token}
    ...    data=${data_token}
    
    RETURN    ${service_tokens}

Verify Service Communication Chain
    [Arguments]    ${service_tokens}
    [Documentation]    Helper to verify service-to-service communication chain
    
    # Verify each service token
    FOR    ${service}    ${token}    IN    &{service_tokens}
        ${is_valid}=    Verify JWT Token    ${token}    ${SERVICE_SECRET}
        Should Be True    ${is_valid}
        
        ${service_name}=    Get JWT Claim    ${token}    service
        Should Be Equal    ${service_name}    ${service}
        
        Log    Service ${service} token validated successfully
    END
    
    # Verify service capabilities
    ${auth_caps}=    Get JWT Claim    ${service_tokens['auth']}    capabilities
    ${user_caps}=    Get JWT Claim    ${service_tokens['user']}    capabilities
    ${data_caps}=    Get JWT Claim    ${service_tokens['data']}    capabilities
    
    Should Contain    ${auth_caps}    authenticate
    Should Contain    ${user_caps}    user:crud
    Should Contain    ${data_caps}    data:read
