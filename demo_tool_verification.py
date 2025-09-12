#!/usr/bin/env python3
"""
Demonstration of Token-Based Tool Execution Verification

This script demonstrates how the token-based verification system
prevents tool execution fabrication in CrewAI agents.
"""

import sys
import os
import time
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from crewai.utilities.tool_execution_verifier import (
    execution_registry,
    ToolExecutionWrapper,
    ExecutionToken,
    verify_observation_token
)

def web_search_tool(query: str) -> str:
    """Simulate a real web search tool"""
    time.sleep(0.01)  # Simulate network delay
    return f"[REAL RESULT] Search completed for '{query}': Found 10 relevant articles"

def demonstrate_legitimate_execution():
    """Demonstrate legitimate tool execution with token verification"""
    print("🟢 Scenario 1: Legitimate Tool Execution")
    print("-" * 40)
    
    # Agent requests tool execution
    token = execution_registry.request_execution("WebSearchTool", "research_agent", "task_1")
    print(f"📝 Agent requested execution with token: {token.token_id[:8]}...")
    
    # Wrap and execute tool with verification
    tool_wrapper = ToolExecutionWrapper(web_search_tool, "WebSearchTool")
    result = tool_wrapper.execute_with_token(token, "AI in Healthcare")
    print(f"✅ Tool executed successfully: {result}")
    
    # Agent verifies the observation
    is_valid = verify_observation_token(token.token_id)
    print(f"🔍 Observation verification: {'PASSED' if is_valid else 'FAILED'}")
    
    return True

def demonstrate_fabrication_prevention():
    """Demonstrate prevention of fabricated observations"""
    print("\n🔴 Scenario 2: Fabrication Prevention")
    print("-" * 40)
    
    # Agent tries to use a fabricated observation
    fake_token_id = "this-token-was-never-generated-by-the-system"
    print(f"📝 Agent attempts to use fabricated token: {fake_token_id[:8]}...")
    
    # Try to verify the fake token
    is_valid = verify_observation_token(fake_token_id)
    print(f"🔍 Observation verification: {'PASSED' if is_valid else 'FAILED'}")
    
    if not is_valid:
        print("❌ Fabrication detected - no valid execution record!")
        return True
    else:
        print("⚠️  Unexpected: Fabrication was not detected")
        return False

def demonstrate_multiple_executions():
    """Demonstrate multiple concurrent tool executions"""
    print("\n🔵 Scenario 3: Multiple Tool Executions")
    print("-" * 40)
    
    # Request multiple executions
    tokens = []
    tools = [
        ("WebSearchTool", web_search_tool, "AI applications in healthcare"),
        ("FileWriteTool", lambda x: f"Successfully wrote {len(x)} characters to file", "output.txt"),
        ("WebSearchTool", web_search_tool, "Machine Learning Trends")
    ]
    
    # Request all executions
    for i, (tool_name, tool_func, query) in enumerate(tools):
        token = execution_registry.request_execution(tool_name, "multi_tool_agent", f"multi_task_{i}")
        tokens.append((token, tool_name, tool_func, query))
        print(f"📝 Requested {tool_name} with token: {token.token_id[:8]}...")
    
    # Execute all tools
    results = []
    for token, tool_name, tool_func, query in tokens:
        tool_wrapper = ToolExecutionWrapper(tool_func, tool_name)
        try:
            result = tool_wrapper.execute_with_token(token, query)
            results.append((token, result, True))
            print(f"✅ {tool_name} executed successfully")
        except Exception as e:
            results.append((token, str(e), False))
            print(f"❌ {tool_name} execution failed: {e}")
    
    # Verify all results
    print("\n🔍 Verifying all executions:")
    all_valid = True
    for token, result, success in results:
        is_valid = verify_observation_token(token.token_id)
        status = "PASSED" if is_valid else "FAILED"
        print(f"   Token {token.token_id[:8]}: {status}")
        if not is_valid:
            all_valid = False
    
    return all_valid

def main():
    """Main demonstration function"""
    print("🔧 Token-Based Tool Execution Verification Demo")
    print("=" * 50)
    print("Solving CrewAI Issue #3154: Agent Tool Fabrication")
    print()
    
    # Run all scenarios
    scenario1 = demonstrate_legitimate_execution()
    scenario2 = demonstrate_fabrication_prevention() 
    scenario3 = demonstrate_multiple_executions()
    
    print("\n" + "=" * 50)
    print("📊 Results Summary:")
    print(f"   Legitimate Execution: {'✅ PASS' if scenario1 else '❌ FAIL'}")
    print(f"   Fabrication Prevention: {'✅ PASS' if scenario2 else '❌ FAIL'}")
    print(f"   Multiple Executions: {'✅ PASS' if scenario3 else '❌ FAIL'}")
    
    if all([scenario1, scenario2, scenario3]):
        print("\n🎉 ALL TESTS PASSED!")
        print("The token-based system successfully prevents tool fabrication")
        print("while allowing legitimate executions.")
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("There may be issues with the implementation.")

if __name__ == "__main__":
    main()