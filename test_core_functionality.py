#!/usr/bin/env python3
"""
Simple test script to verify core functionality
"""

import sys
import os
import time

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from crewai.utilities.tool_execution_verifier import (
    execution_registry,
    ToolExecutionWrapper,
    verify_observation_token
)

def test_core_functionality():
    """Test the core functionality of the verification system"""
    print("🧪 Testing Core Functionality")
    print("=" * 30)
    
    # Test 1: Legitimate execution
    print("Test 1: Legitimate tool execution")
    token = execution_registry.request_execution("TestTool", "test_agent", "test_task")
    
    def test_tool(input_data):
        time.sleep(0.001)  # Simulate work
        return f"Processed: {input_data}"
    
    wrapper = ToolExecutionWrapper(test_tool, "TestTool")
    result = wrapper.execute_with_token(token, "test_input")
    
    is_valid = verify_observation_token(token.token_id)
    print(f"   Result: {result}")
    print(f"   Verification: {'PASSED' if is_valid else 'FAILED'}")
    assert is_valid, "Legitimate execution should pass verification"
    print("   ✅ PASS")
    print()
    
    # Test 2: Fabrication detection
    print("Test 2: Fabrication detection")
    fake_token = "this-token-does-not-exist"
    is_valid = verify_observation_token(fake_token)
    print(f"   Verification of fake token: {'PASSED' if is_valid else 'FAILED'}")
    assert not is_valid, "Fabricated observation should fail verification"
    print("   ✅ PASS")
    print()
    
    # Test 3: Performance
    print("Test 3: Performance impact")
    start_time = time.time()
    
    token2 = execution_registry.request_execution("PerfTest", "agent1", "task1")
    wrapper2 = ToolExecutionWrapper(test_tool, "PerfTest")
    result2 = wrapper2.execute_with_token(token2, "perf_test")
    is_valid2 = verify_observation_token(token2.token_id)
    
    elapsed_ms = (time.time() - start_time) * 1000
    print(f"   Execution time: {elapsed_ms:.3f}ms")
    print(f"   Result: {result2}")
    print(f"   Verification: {'PASSED' if is_valid2 else 'FAILED'}")
    assert elapsed_ms < 10.0, f"Performance impact {elapsed_ms}ms exceeds 10ms threshold"
    print("   ✅ PASS")
    print()
    
    print("🎉 All core functionality tests PASSED!")

if __name__ == "__main__":
    test_core_functionality()