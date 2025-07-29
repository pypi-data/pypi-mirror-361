*** Settings ***
Documentation     Real-world API authentication workflow using JWT
Library           JWTLibrary
Library           RequestsLibrary
Library           Collections
Library           DateTime

*** Variables ***
${API_BASE_URL}      http://localhost:8080/api
${JWT_SECRET}        production_api_secret_key_2024
${ADMIN_SECRET}      admin_service_secret_key
${SERVICE_SECRET}    microservice_communication_key

*** Test Cases ***
Complete User Authentication Flow
    [Documentation]    Test complete user login and API access workflow
    [Tags]    real-world    authentication    api
    
    # Step 1: User Registration/Login - Generate JWT
    ${user_credentials}=    Create Dictionary
    ...    username=john.doe
    ...    email=john.doe@company.com
    ...    user_id=12345
    ...    role=standard_user
    ...    permissions=["profile:read", "profile:write", "data:read"]
    ...    department=engineering
    
    ${auth_token}=    Generate JWT Token    ${user_credentials}    ${JWT_SECRET}    expiration_hours=8
    Log    User authentication token generated
    
    # Step 2: Validate token structure and content
    ${token_info}=    Get JWT Token Info    ${auth_token}
    Should Be Equal    ${token_info['algorithm']}    HS256
    Should Be True    ${token_info['claims_count']} >= 6
    
    # Step 3: API Request - Get User Profile
    ${profile_response}=    Simulate API Request    GET    /user/profile    ${auth_token}
    Should Be Equal    ${profile_response['status']}    authorized
    
    # Step 4: API Request - Update Profile (requires write permission)
    ${update_data}=    Create Dictionary    
    ...    display_name=John Doe
    ...    phone=+1234567890
    
    ${update_response}=    Simulate API Request    POST    /user/profile    ${auth_token}    ${update_data}
    Should Be Equal    ${update_response['status']}    authorized
    
    # Step 5: Try unauthorized action (should fail)
    ${unauthorized_response}=    Simulate API Request    DELETE    /admin/users/999    ${auth_token}
    Should Be Equal    ${unauthorized_response['status']}    forbidden

Admin User Workflow
    [Documentation]    Test admin user capabilities with JWT
    [Tags]    real-world    admin    authorization
    
    # Admin user with elevated permissions
    ${admin_credentials}=    Create Dictionary
    ...    username=admin.user
    ...    email=admin@company.com
    ...    user_id=1
    ...    role=admin
    ...    permissions=["*"]
    ...    clearance_level=5
    ...    admin_since=2024-01-01
    
    ${admin_token}=    Generate JWT Token    ${admin_credentials}    ${ADMIN_SECRET}    expiration_hours=4
    
    # Validate admin token
    ${is_admin_valid}=    Verify JWT Token    ${admin_token}    ${ADMIN_SECRET}
    Should Be True    ${is_admin_valid}
    
    # Admin operations
    ${admin_role}=    Get JWT Claim    ${admin_token}    role
    ${admin_permissions}=    Get JWT Claim    ${admin_token}    permissions
    ${clearance}=    Get JWT Claim    ${admin_token}    clearance_level
    
    Should Be Equal    ${admin_role}    admin
    Should Contain    ${admin_permissions}    *
    Should Be True    ${clearance} >= 5
    
    # Simulate admin API calls
    ${user_list_response}=    Simulate API Request    GET    /admin/users    ${admin_token}
    ${system_config_response}=    Simulate API Request    GET    /admin/system/config    ${admin_token}
    
    Should Be Equal    ${user_list_response['status']}    authorized
    Should Be Equal    ${system_config_response['status']}    authorized

Service-to-Service Authentication
    [Documentation]    Test microservice communication using JWT
    [Tags]    real-world    microservices    service-auth
    
    # User Service requesting data from Data Service
    ${service_request}=    Create Dictionary
    ...    service_name=user-service
    ...    version=1.2.3
    ...    iss=user-service
    ...    aud=data-service
    ...    sub=system
    ...    scope=user:read user:write
    ...    request_id=req_${EMPTY}
    
    ${request_timestamp}=    Generate Current Timestamp
    ${request_id}=    Set Variable    req_${request_timestamp}
    Set To Dictionary    ${service_request}    request_id=${request_id}
    
    ${service_token}=    Generate JWT Token    ${service_request}    ${SERVICE_SECRET}    expiration_hours=1
    
    # Data Service validates the request
    ${service_valid}=    Verify JWT Token    ${service_token}    ${SERVICE_SECRET}
    Should Be True    ${service_valid}
    
    # Validate service-specific claims
    ${issuer}=    Get JWT Claim    ${service_token}    iss
    ${audience}=    Get JWT Claim    ${service_token}    aud
    ${scope}=    Get JWT Claim    ${service_token}    scope
    
    Should Be Equal    ${issuer}    user-service
    Should Be Equal    ${audience}    data-service
    Should Contain    ${scope}    user:read
    
    # Validate audience specifically
    ${aud_valid}=    Validate JWT Audience    ${service_token}    data-service
    Should Be True    ${aud_valid}
    
    Log    ✓ Service-to-service authentication successful

API Rate Limiting with JWT
    [Documentation]    Test API rate limiting based on JWT claims
    [Tags]    real-world    rate-limiting    api
    
    # Basic tier user
    ${basic_user}=    Create Dictionary
    ...    user_id=10001
    ...    username=basic.user
    ...    subscription_tier=basic
    ...    rate_limit_per_hour=100
    ...    burst_limit=10
    
    ${basic_token}=    Generate JWT Token    ${basic_user}    ${JWT_SECRET}
    
    # Premium tier user
    ${premium_user}=    Create Dictionary
    ...    user_id=10002
    ...    username=premium.user
    ...    subscription_tier=premium
    ...    rate_limit_per_hour=1000
    ...    burst_limit=50
    
    ${premium_token}=    Generate JWT Token    ${premium_user}    ${JWT_SECRET}
    
    # Extract rate limiting information
    ${basic_limit}=    Get JWT Claim    ${basic_token}    rate_limit_per_hour
    ${premium_limit}=    Get JWT Claim    ${premium_token}    rate_limit_per_hour
    
    Should Be Equal As Integers    ${basic_limit}    100
    Should Be Equal As Integers    ${premium_limit}    1000
    Should Be True    ${premium_limit} > ${basic_limit}
    
    # Simulate rate limit enforcement
    ${basic_burst}=    Get JWT Claim    ${basic_token}    burst_limit
    ${premium_burst}=    Get JWT Claim    ${premium_token}    burst_limit
    
    Should Be True    ${premium_burst} > ${basic_burst}
    Log    ✓ Rate limiting configuration extracted from JWT

Multi-Tenant Application Workflow
    [Documentation]    Test multi-tenant application with JWT isolation
    [Tags]    real-world    multi-tenant    isolation
    
    # Tenant A user
    ${tenant_a_user}=    Create Dictionary
    ...    user_id=20001
    ...    username=user.a
    ...    tenant_id=acme-corp
    ...    tenant_name=ACME Corporation
    ...    role=manager
    ...    data_access_scope=["acme-corp.*"]
    
    ${tenant_a_secret}=    Set Variable    acme_corp_secret_2024
    ${tenant_a_token}=    Generate JWT Token    ${tenant_a_user}    ${tenant_a_secret}
    
    # Tenant B user
    ${tenant_b_user}=    Create Dictionary
    ...    user_id=30001
    ...    username=user.b
    ...    tenant_id=globex-inc
    ...    tenant_name=Globex Inc
    ...    role=analyst
    ...    data_access_scope=["globex-inc.*"]
    
    ${tenant_b_secret}=    Set Variable    globex_inc_secret_2024
    ${tenant_b_token}=    Generate JWT Token    ${tenant_b_user}    ${tenant_b_secret}
    
    # Validate tenant isolation
    ${tenant_a_valid_own}=    Verify JWT Token    ${tenant_a_token}    ${tenant_a_secret}
    ${tenant_a_valid_other}=    Verify JWT Token    ${tenant_a_token}    ${tenant_b_secret}
    
    Should Be True    ${tenant_a_valid_own}
    Should Be Equal    ${tenant_a_valid_other}    ${False}
    
    # Verify tenant-specific data access
    ${tenant_a_scope}=    Get JWT Claim    ${tenant_a_token}    data_access_scope
    ${tenant_b_scope}=    Get JWT Claim    ${tenant_b_token}    data_access_scope
    
    Should Contain    ${tenant_a_scope}    acme-corp.*
    Should Not Contain    ${tenant_a_scope}    globex-inc.*
    Should Contain    ${tenant_b_scope}    globex-inc.*
    Should Not Contain    ${tenant_b_scope}    acme-corp.*
    
    Log    ✓ Multi-tenant isolation verified

Session Management with JWT
    [Documentation]    Test session management and concurrent sessions
    [Tags]    real-world    session-management
    
    ${user_base}=    Create Dictionary
    ...    user_id=40001
    ...    username=session.user
    ...    email=session@example.com
    
    # Web session
    ${web_session}=    Copy Dictionary    ${user_base}
    ${web_session_id}=    Set Variable    web_${EMPTY}
    ${web_timestamp}=    Generate Current Timestamp
    ${web_session_id}=    Set Variable    web_${web_timestamp}
    
    Set To Dictionary    ${web_session}
    ...    session_id=${web_session_id}
    ...    device_type=web
    ...    user_agent=Mozilla/5.0 Chrome/120.0
    ...    ip_address=192.168.1.100
    
    ${web_token}=    Generate JWT Token    ${web_session}    ${JWT_SECRET}    expiration_hours=8
    
    # Mobile session  
    ${mobile_session}=    Copy Dictionary    ${user_base}
    ${mobile_session_id}=    Set Variable    mobile_${EMPTY}
    ${mobile_timestamp}=    Generate Current Timestamp
    ${mobile_session_id}=    Set Variable    mobile_${mobile_timestamp}
    
    Set To Dictionary    ${mobile_session}
    ...    session_id=${mobile_session_id}
    ...    device_type=mobile
    ...    user_agent=MyApp/1.0 iOS/17.0
    ...    ip_address=192.168.1.101
    
    ${mobile_token}=    Generate JWT Token    ${mobile_session}    ${JWT_SECRET}    expiration_hours=24
    
    # Validate both sessions are independent
    ${web_session_id_extracted}=    Get JWT Claim    ${web_token}    session_id
    ${mobile_session_id_extracted}=    Get JWT Claim    ${mobile_token}    session_id
    
    Should Be Equal    ${web_session_id_extracted}    ${web_session_id}
    Should Be Equal    ${mobile_session_id_extracted}    ${mobile_session_id}
    Should Not Be Equal    ${web_session_id}    ${mobile_session_id}
    
    # Compare session tokens
    ${session_comparison}=    Compare JWT Tokens    ${web_token}    ${mobile_token}
    Should Be Equal    ${session_comparison['are_identical']}    ${False}
    Should Contain    ${session_comparison['payload_differences']}    session_id
    Should Contain    ${session_comparison['payload_differences']}    device_type
    
    Log    ✓ Concurrent session management verified

*** Keywords ***
Simulate API Request
    [Arguments]    ${method}    ${endpoint}    ${token}    ${payload}=${None}
    [Documentation]    Simulate an API request with JWT authentication
    
    # Validate token first
    ${is_valid}=    Verify JWT Token    ${token}    ${JWT_SECRET}
    
    IF    not ${is_valid}
        ${response}=    Create Dictionary    status=invalid_token    error=Token validation failed
        RETURN    ${response}
    END
    
    # Extract user information for authorization
    ${user_role}=    Get JWT Claim    ${token}    role
    ${permissions}=    Get JWT Claim    ${token}    permissions
    
    # Simulate authorization logic
    ${is_authorized}=    Check Endpoint Authorization    ${method}    ${endpoint}    ${user_role}    ${permissions}
    
    IF    ${is_authorized}
        ${response}=    Create Dictionary    status=authorized    method=${method}    endpoint=${endpoint}
        IF    ${payload} is not None
            Set To Dictionary    ${response}    payload_received=${payload}
        END
    ELSE
        ${response}=    Create Dictionary    status=forbidden    error=Insufficient permissions
    END
    
    Log    API ${method} ${endpoint}: ${response['status']}
    RETURN    ${response}

Check Endpoint Authorization
    [Arguments]    ${method}    ${endpoint}    ${role}    ${permissions}
    [Documentation]    Check if user has permission for specific endpoint
    
    # Admin role has access to everything
    IF    '${role}' == 'admin'
        RETURN    ${True}
    END
    
    # Check specific endpoint permissions
    IF    '${endpoint}' == '/user/profile'
        IF    '${method}' == 'GET'
            RETURN    ${'profile:read' in $permissions}
        ELIF    '${method}' == 'POST'
            RETURN    ${'profile:write' in $permissions}
        END
    END
    
    IF    '/admin/' in '${endpoint}'
        RETURN    ${False}  # Regular users can't access admin endpoints
    END
    
    IF    '${method}' == 'GET' and '/data/' in '${endpoint}'
        RETURN    ${'data:read' in $permissions}
    END
    
    # Default to deny
    RETURN    ${False}

Generate API Test User
    [Arguments]    ${user_id}    ${role}=user    ${additional_claims}=${None}
    [Documentation]    Generate a test user with API access token
    
    ${base_user}=    Create Dictionary
    ...    user_id=${user_id}
    ...    username=test_user_${user_id}
    ...    email=user${user_id}@test.com
    ...    role=${role}
    
    # Add role-specific permissions
    IF    '${role}' == 'admin'
        Set To Dictionary    ${base_user}    permissions=["*"]
    ELIF    '${role}' == 'manager'
        Set To Dictionary    ${base_user}    permissions=["profile:read", "profile:write", "data:read", "team:read"]
    ELSE
        Set To Dictionary    ${base_user}    permissions=["profile:read", "profile:write"]
    END
    
    # Add additional claims if provided
    IF    ${additional_claims} is not None
        FOR    ${key}    ${value}    IN    &{additional_claims}
            Set To Dictionary    ${base_user}    ${key}=${value}
        END
    END
    
    ${token}=    Generate JWT Token    ${base_user}    ${JWT_SECRET}
    RETURN    ${token}

Validate Service Communication
    [Arguments]    ${source_service}    ${target_service}    ${operation}
    [Documentation]    Validate service-to-service communication
    
    ${service_payload}=    Create Dictionary
    ...    iss=${source_service}
    ...    aud=${target_service}
    ...    sub=system
    ...    operation=${operation}
    ...    timestamp=${EMPTY}
    
    ${timestamp}=    Generate Current Timestamp
    Set To Dictionary    ${service_payload}    timestamp=${timestamp}
    
    ${service_token}=    Generate JWT Token    ${service_payload}    ${SERVICE_SECRET}    expiration_hours=0.5
    
    # Validate at target service
    ${is_valid}=    Verify JWT Token    ${service_token}    ${SERVICE_SECRET}
    Should Be True    ${is_valid}
    
    ${aud_valid}=    Validate JWT Audience    ${service_token}    ${target_service}
    Should Be True    ${aud_valid}
    
    ${extracted_operation}=    Get JWT Claim    ${service_token}    operation
    Should Be Equal    ${extracted_operation}    ${operation}
    
    Log    ✓ Service communication validated: ${source_service} → ${target_service} (${operation})
    RETURN    ${service_token}
