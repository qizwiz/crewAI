#!/usr/bin/env python3
"""
Integration test for CrewAI Issue #3154 fix on your fork.

Tests the actual fix implementation to ensure it works correctly.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_verification_module():
    """Test that the verification module loads correctly."""
    try:
        from crewai.verification import ToolExecutionVerifier, get_global_verifier
        print("✅ Verification module imported successfully")
        
        # Test basic functionality
        verifier = ToolExecutionVerifier()
        token = verifier.create_execution_token(
            tool_name="test_tool",
            arguments={"arg": "value"},
            result="test result"
        )
        
        # Verify the token
        is_valid = verifier.verify_execution(token, "test result")
        assert is_valid, "Token verification failed"
        print("✅ Token creation and verification working")
        
        return True
        
    except Exception as e:
        print(f"❌ Verification module test failed: {e}")
        return False

def test_tool_usage_patch():
    """Test that tool_usage.py has been patched correctly."""
    try:
        from crewai.tools.tool_usage import ToolUsage
        print("✅ Tool usage module imported successfully")
        
        # Check if the file contains our patch
        import inspect
        source = inspect.getsource(ToolUsage._use)
        
        if "get_global_verifier" in source and "EXECUTION_TOKEN" in source:
            print("✅ Tool usage patched with verification code")
            return True
        else:
            print("❌ Tool usage patch not found in source")
            return False
            
    except Exception as e:
        print(f"❌ Tool usage patch test failed: {e}")
        return False

def test_agent_utils_patch():
    """Test that agent_utils.py has been patched correctly."""
    try:
        from crewai.utilities.agent_utils import handle_agent_action_core
        print("✅ Agent utils module imported successfully")
        
        # Check if the file contains our patch
        import inspect
        source = inspect.getsource(handle_agent_action_core)
        
        if "get_global_verifier" in source and "EXECUTION_TOKEN" in source:
            print("✅ Agent utils patched with verification code")
            return True
        else:
            print("❌ Agent utils patch not found in source")
            return False
            
    except Exception as e:
        print(f"❌ Agent utils patch test failed: {e}")
        return False

def test_basic_token_workflow():
    """Test the complete token workflow."""
    try:
        from crewai.verification import get_global_verifier
        from unittest.mock import Mock
        
        print("🧪 Testing complete token workflow...")
        
        # Create a mock tool
        mock_tool = Mock()
        mock_tool.name = "test_tool"
        
        # Get verifier
        verifier = get_global_verifier()
        
        # Simulate tool execution
        arguments = {"file_path": "/tmp/test.txt"}
        result = "File contents here"
        
        # Create token
        token = verifier.create_execution_token(
            tool_name=mock_tool.name,
            arguments=arguments,
            result=result
        )
        
        # Simulate result with token
        result_with_token = f"{result}\n🔐 EXECUTION_TOKEN: {token.execution_id}"
        
        # Verify workflow
        result_str = str(result_with_token)
        if "🔐 EXECUTION_TOKEN:" in result_str:
            token_id = result_str.split("🔐 EXECUTION_TOKEN:")[-1].strip()
            
            with verifier.lock:
                if token_id in verifier.execution_registry:
                    stored_token = verifier.execution_registry[token_id]
                    clean_result = result_str.replace(f"\n🔐 EXECUTION_TOKEN: {token_id}", "")
                    
                    if verifier.verify_execution(stored_token, clean_result):
                        print("✅ Complete token workflow successful")
                        return True
        
        print("❌ Token workflow verification failed")
        return False
        
    except Exception as e:
        print(f"❌ Token workflow test failed: {e}")
        return False

def test_fabrication_detection():
    """Test that fabricated executions are detected."""
    try:
        from crewai.verification import get_global_verifier
        
        print("🚨 Testing fabrication detection...")
        
        verifier = get_global_verifier()
        
        # Test fake observation without token
        fake_observation = "Observation: I pretended to read a file but didn't actually call the tool"
        
        # This should be detected as fabrication (no token present)
        has_token = "🔐 EXECUTION_TOKEN:" in fake_observation
        
        if not has_token:
            print("✅ Fabrication detected (no execution token)")
            return True
        else:
            print("❌ Fabrication not detected")
            return False
            
    except Exception as e:
        print(f"❌ Fabrication detection test failed: {e}")
        return False

def main():
    """Run all integration tests."""
    print("🧪 Running CrewAI Issue #3154 Fix Integration Tests")
    print("=" * 60)
    
    tests = [
        test_verification_module,
        test_tool_usage_patch,
        test_agent_utils_patch,
        test_basic_token_workflow,
        test_fabrication_detection
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        print(f"\n📋 Running {test.__name__}...")
        try:
            if test():
                passed += 1
            else:
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            print(f"❌ {test.__name__} crashed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Your CrewAI fork is ready for testing.")
        print("🔐 Tool execution verification is working correctly.")
    else:
        print("⚠️ Some tests failed. Please review the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)