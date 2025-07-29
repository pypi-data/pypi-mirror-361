*** Settings ***
Documentation     JWT performance test suite
Library           JWTLibrary
Library           Collections
Library           DateTime
Library           OperatingSystem

*** Variables ***
${PERF_SECRET}    performance_test_secret_key_12345
${ITERATIONS}     1000
${LARGE_ITERATIONS}    100

*** Test Cases ***
Performance Test Token Generation
    [Documentation]    Test JWT token generation performance
    [Tags]    jwt    performance    generation
    
    ${payload}=    Create Dictionary    user_id=12345    role=user    test=performance
    
    ${start_time}=    Get Current Date    result_format=epoch
    
    FOR    ${i}    IN RANGE    ${ITERATIONS}
        ${token}=    Generate JWT Token    ${payload}    ${PERF_SECRET}
        Should Not Be Empty    ${token}
    END
    
    ${end_time}=    Get Current Date    result_format=epoch
    ${duration}=    Evaluate    ${end_time} - ${start_time}
    ${tokens_per_second}=    Evaluate    ${ITERATIONS} / ${duration}
    
    Log    Generated ${ITERATIONS} tokens in ${duration} seconds
    Log    Performance: ${tokens_per_second} tokens/second
    
    # Performance assertion (should generate at least 100 tokens per second)
    Should Be True    ${tokens_per_second} > 100

Performance Test Token Decoding
    [Documentation]    Test JWT token decoding performance
    [Tags]    jwt    performance    decoding
    
    ${payload}=    Create Dictionary    user_id=67890    role=admin    test=decoding_perf
    ${token}=    Generate JWT Token    ${payload}    ${PERF_SECRET}
    
    ${start_time}=    Get Current Date    result_format=epoch
    
    FOR    ${i}    IN RANGE    ${ITERATIONS}
        ${decoded}=    Decode JWT Payload    ${token}    ${PERF_SECRET}
        Should Be Equal As Integers    ${decoded['user_id']}    67890
    END
    
    ${end_time}=    Get Current Date    result_format=epoch
    ${duration}=    Evaluate    ${end_time} - ${start_time}
    ${decodes_per_second}=    Evaluate    ${ITERATIONS} / ${duration}
    
    Log    Decoded ${ITERATIONS} tokens in ${duration} seconds
    Log    Performance: ${decodes_per_second} decodes/second
    
    # Performance assertion (should decode at least 200 tokens per second)
    Should Be True    ${decodes_per_second} > 200

Performance Test Token Verification
    [Documentation]    Test JWT token verification performance
    [Tags]    jwt    performance    verification
    
    ${payload}=    Create Dictionary    user_id=11111    role=tester    test=verification_perf
    ${token}=    Generate JWT Token    ${payload}    ${PERF_SECRET}
    
    ${start_time}=    Get Current Date    result_format=epoch
    
    FOR    ${i}    IN RANGE    ${ITERATIONS}
        ${is_valid}=    Verify JWT Token    ${token}    ${PERF_SECRET}
        Should Be True    ${is_valid}
    END
    
    ${end_time}=    Get Current Date    result_format=epoch
    ${duration}=    Evaluate    ${end_time} - ${start_time}
    ${verifications_per_second}=    Evaluate    ${ITERATIONS} / ${duration}
    
    Log    Verified ${ITERATIONS} tokens in ${duration} seconds
    Log    Performance: ${verifications_per_second} verifications/second
    
    # Performance assertion (should verify at least 200 tokens per second)
    Should Be True    ${verifications_per_second} > 200

Performance Test Large Payload Handling
    [Documentation]    Test JWT performance with large payloads
    [Tags]    jwt    performance    large-payload
    
    # Create large payload
    ${large_payload}=    Create Dictionary    user_id=99999    test=large_payload
    
    FOR    ${i}    IN RANGE    100
        Set To Dictionary    ${large_payload}    field_${i}=value_${i}_with_some_additional_data_to_make_it_longer
        ${nested_data}=    Create Dictionary
        ...    sub_field_1=nested_value_${i}_1
        ...    sub_field_2=nested_value_${i}_2
        ...    sub_field_3=nested_value_${i}_3
        Set To Dictionary    ${large_payload}    nested_${i}=${nested_data}
    END
    
    ${start_time}=    Get Current Date    result_format=epoch
    
    FOR    ${i}    IN RANGE    ${LARGE_ITERATIONS}
        ${token}=    Generate JWT Token    ${large_payload}    ${PERF_SECRET}
        ${decoded}=    Decode JWT Payload    ${token}    ${PERF_SECRET}
        Should Be Equal As Integers    ${decoded['user_id']}    99999
    END
    
    ${end_time}=    Get Current Date    result_format=epoch
    ${duration}=    Evaluate    ${end_time} - ${start_time}
    ${operations_per_second}=    Evaluate    ${LARGE_ITERATIONS} / ${duration}
    
    Log    Processed ${LARGE_ITERATIONS} large tokens in ${duration} seconds
    Log    Performance: ${operations_per_second} operations/second
    
    # Performance assertion for large payloads (should handle at least 10 per second)
    Should Be True    ${operations_per_second} > 10

Performance Test Different Algorithms
    [Documentation]    Test performance comparison across different algorithms
    [Tags]    jwt    performance    algorithms
    
    ${payload}=    Create Dictionary    user_id=55555    algorithm_test=true
    @{algorithms}=    Create List    HS256    HS384    HS512
    ${algorithm_results}=    Create Dictionary
    
    FOR    ${algorithm}    IN    @{algorithms}
        Log    Testing algorithm: ${algorithm}
        
        ${start_time}=    Get Current Date    result_format=epoch
        
        FOR    ${i}    IN RANGE    500
            ${token}=    Generate JWT Token    ${payload}    ${PERF_SECRET}    algorithm=${algorithm}
            ${decoded}=    Decode JWT Payload    ${token}    ${PERF_SECRET}    algorithm=${algorithm}
        END
        
        ${end_time}=    Get Current Date    result_format=epoch
        ${duration}=    Evaluate    ${end_time} - ${start_time}
        ${ops_per_second}=    Evaluate    500 / ${duration}
        
        Set To Dictionary    ${algorithm_results}    ${algorithm}=${ops_per_second}
        Log    ${algorithm}: ${ops_per_second} operations/second
    END
    
    # Log comparison results
    Log    Algorithm Performance Comparison:
    FOR    ${alg}    ${perf}    IN    &{algorithm_results}
        Log    ${alg}: ${perf} ops/sec
    END

Performance Test Concurrent Token Operations
    [Documentation]    Test performance under simulated concurrent load
    [Tags]    jwt    performance    concurrent
    
    ${payload}=    Create Dictionary    user_id=77777    concurrent_test=true
    
    # Simulate concurrent token generation
    ${start_time}=    Get Current Date    result_format=epoch
    
    # Generate multiple tokens rapidly
    @{tokens}=    Create List
    FOR    ${i}    IN RANGE    200
        ${token}=    Generate JWT Token    ${payload}    ${PERF_SECRET}
        Append To List    ${tokens}    ${token}
    END
    
    # Verify all tokens rapidly
    FOR    ${token}    IN    @{tokens}
        ${is_valid}=    Verify JWT Token    ${token}    ${PERF_SECRET}
        Should Be True    ${is_valid}
    END
    
    ${end_time}=    Get Current Date    result_format=epoch
    ${duration}=    Evaluate    ${end_time} - ${start_time}
    ${total_operations}=    Evaluate    200 * 2  # Generation + verification
    ${ops_per_second}=    Evaluate    ${total_operations} / ${duration}
    
    Log    Performed ${total_operations} operations in ${duration} seconds
    Log    Concurrent performance: ${ops_per_second} operations/second
    
    # Should handle concurrent operations efficiently
    Should Be True    ${ops_per_second} > 300

Performance Test Memory Usage Pattern
    [Documentation]    Test memory usage patterns with JWT operations
    [Tags]    jwt    performance    memory
    
    ${base_payload}=    Create Dictionary    user_id=88888    memory_test=true
    
    # Test with increasing payload sizes
    @{payload_sizes}=    Create List    10    50    100    200    500
    
    FOR    ${size}    IN    @{payload_sizes}
        Log    Testing payload size: ${size} fields
        
        # Create payload of specified size
        ${test_payload}=    Copy Dictionary    ${base_payload}
        FOR    ${i}    IN RANGE    ${size}
            Set To Dictionary    ${test_payload}    data_${i}=test_value_${i}
        END
        
        ${start_time}=    Get Current Date    result_format=epoch
        
        # Perform operations
        FOR    ${i}    IN RANGE    50
            ${token}=    Generate JWT Token    ${test_payload}    ${PERF_SECRET}
            ${decoded}=    Decode JWT Payload    ${token}    ${PERF_SECRET}
            ${info}=    Get JWT Token Info    ${token}
        END
        
        ${end_time}=    Get Current Date    result_format=epoch
        ${duration}=    Evaluate    ${end_time} - ${start_time}
        ${ops_per_second}=    Evaluate    150 / ${duration}  # 50 * 3 operations
        
        Log    Payload size ${size}: ${ops_per_second} ops/sec
    END

Performance Test Batch Operations
    [Documentation]    Test performance of batch JWT operations
    [Tags]    jwt    performance    batch
    
    # Generate batch of different payloads
    @{payloads}=    Create List
    FOR    ${i}    IN RANGE    100
        ${payload}=    Create Dictionary
        ...    user_id=${i}
        ...    username=user_${i}
        ...    role=batch_user
        ...    batch_id=${i}
        Append To List    ${payloads}    ${payload}
    END
    
    ${start_time}=    Get Current Date    result_format=epoch
    
    # Batch generate tokens
    @{tokens}=    Create List
    FOR    ${payload}    IN    @{payloads}
        ${token}=    Generate JWT Token    ${payload}    ${PERF_SECRET}
        Append To List    ${tokens}    ${token}
    END
    
    # Batch verify tokens
    ${valid_count}=    Set Variable    0
    FOR    ${token}    IN    @{tokens}
        ${is_valid}=    Verify JWT Token    ${token}    ${PERF_SECRET}
        ${valid_count}=    Evaluate    ${valid_count} + (1 if ${is_valid} else 0)
    END
    
    ${end_time}=    Get Current Date    result_format=epoch
    ${duration}=    Evaluate    ${end_time} - ${start_time}
    ${total_ops}=    Evaluate    len($tokens) * 2  # Generate + verify
    ${ops_per_second}=    Evaluate    ${total_ops} / ${duration}
    
    Log    Batch processed ${total_ops} operations in ${duration} seconds
    Log    Batch performance: ${ops_per_second} operations/second
    Log    Valid tokens: ${valid_count}/${total_ops//2}
    
    Should Be Equal As Integers    ${valid_count}    100
    Should Be True    ${ops_per_second} > 200

Performance Test Token Claim Extraction
    [Documentation]    Test performance of claim extraction operations
    [Tags]    jwt    performance    claims
    
    # Create token with many claims
    ${rich_payload}=    Create Dictionary
    ...    user_id=99999
    ...    username=performance_user
    ...    email=perf@test.com
    ...    role=admin
    ...    department=engineering
    ...    clearance_level=5
    ...    permissions=["read", "write", "delete", "admin"]
    ...    settings={"theme": "dark", "lang": "en"}
    ...    metadata={"created": "2024-01-01", "updated": "2024-01-15"}
    
    FOR    ${i}    IN RANGE    20
        Set To Dictionary    ${rich_payload}    extra_field_${i}=extra_value_${i}
    END
    
    ${token}=    Generate JWT Token    ${rich_payload}    ${PERF_SECRET}
    
    ${start_time}=    Get Current Date    result_format=epoch
    
    # Extract claims repeatedly
    FOR    ${i}    IN RANGE    ${ITERATIONS}
        ${user_id}=    Get JWT Claim    ${token}    user_id
        ${username}=    Get JWT Claim    ${token}    username
        ${role}=    Get JWT Claim    ${token}    role
        ${permissions}=    Get JWT Claim    ${token}    permissions
    END
    
    ${end_time}=    Get Current Date    result_format=epoch
    ${duration}=    Evaluate    ${end_time} - ${start_time}
    ${extractions_per_second}=    Evaluate    (${ITERATIONS} * 4) / ${duration}
    
    Log    Extracted ${ITERATIONS * 4} claims in ${duration} seconds
    Log    Claim extraction performance: ${extractions_per_second} extractions/second
    
    Should Be True    ${extractions_per_second} > 1000

*** Keywords ***
Log Performance Results
    [Arguments]    ${test_name}    ${operations}    ${duration}    ${threshold}
    [Documentation]    Helper keyword to log and validate performance results
    
    ${ops_per_second}=    Evaluate    ${operations} / ${duration}
    
    Log    === Performance Results: ${test_name} ===
    Log    Operations: ${operations}
    Log    Duration: ${duration} seconds
    Log    Performance: ${ops_per_second} ops/second
    Log    Threshold: ${threshold} ops/second
    Log    Status: ${'PASS' if ${ops_per_second} > ${threshold} else 'FAIL'}
    Log    ============================================
    
    Should Be True    ${ops_per_second} > ${threshold}    
    ...    Performance below threshold: ${ops_per_second} < ${threshold}

Create Performance Payload
    [Arguments]    ${size}=10    ${user_id}=12345
    [Documentation]    Helper to create payloads of different sizes for testing
    
    ${payload}=    Create Dictionary    user_id=${user_id}    test=performance
    
    FOR    ${i}    IN RANGE    ${size}
        Set To Dictionary    ${payload}    field_${i}=value_${i}
    END
    
    RETURN    ${payload}

Measure Operation Time
    [Arguments]    ${operation_keyword}    @{args}
    [Documentation]    Helper to measure execution time of operations
    
    ${start_time}=    Get Current Date    result_format=epoch
    ${result}=    Run Keyword    ${operation_keyword}    @{args}
    ${end_time}=    Get Current Date    result_format=epoch
    ${duration}=    Evaluate    ${end_time} - ${start_time}
    
    RETURN    ${result}    ${duration}

Performance Benchmark Summary
    [Documentation]    Generate performance benchmark summary
    
    Log    === JWT Library Performance Benchmark Summary ===
    Log    Test Environment: Robot Framework + Python
    Log    JWT Algorithm: HS256 (default)
    Log    Expected Performance Thresholds:
    Log    - Token Generation: > 100 tokens/second
    Log    - Token Decoding: > 200 decodes/second
    Log    - Token Verification: > 200 verifications/second
    Log    - Large Payload Operations: > 10 operations/second
    Log    - Claim Extraction: > 1000 extractions/second
    Log    ================================================
