"""
Integration tests demonstrating the fix for CrewAI Issue #3154
"""

import unittest
import sys
import os
import time
from unittest.mock import Mock, patch

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from crewai.utilities.tool_execution_verifier import (
    ExecutionRegistry,
    ToolExecutionWrapper,
    verify_observation_token,
    execution_registry
)

class TestIssue3154Fix(unittest.TestCase):
    """Integration tests for the fix to CrewAI Issue #3154"""
    
    def setUp(self):
        """Set up test fixtures"""
        execution_registry._pending.clear()
        execution_registry._completed.clear()
    
    def test_legitimate_tool_execution_flow(self):
        """Test the complete legitimate tool execution flow"""
        # Simulate agent deciding to use a tool
        agent_id = "research_agent"
        task_id = "healthcare_research_task"
        tool_name = "WebSearchTool"
        
        # Step 1: Agent requests tool execution (would be in ToolUsage._use)
        token = execution_registry.request_execution(tool_name, agent_id, task_id)
        self.assertIsNotNone(token)
        self.assertEqual(token.tool_name, tool_name)
        
        # Step 2: Tool is actually executed with token (would wrap tool.invoke)
        def mock_web_search(query):
            time.sleep(0.001)  # Simulate network delay
            return f"Search results for '{query}': 10 articles found"
        
        wrapper = ToolExecutionWrapper(mock_web_search, tool_name)
        result = wrapper.execute_with_token(token, "AI in Healthcare")
        
        # Verify legitimate execution
        self.assertIn("Search results for 'AI in Healthcare'", result)
        
        # Step 3: Agent verifies the observation (would be in agent processing)
        is_valid = verify_observation_token(token.token_id)
        self.assertTrue(is_valid)
    
    def test_fabricated_observation_detection(self):
        """Test that fabricated observations are detected and rejected"""
        # Simulate what happens when an LLM fabricates an observation
        # without actually calling the tool
        
        # Agent generates a fake observation (the bug)
        fake_observation = {
            "content": "Search results show 15 articles about AI in Healthcare",
            "execution_token": "never-generated-token-id"
        }
        
        # Agent tries to verify the fake observation
        is_valid = verify_observation_token(fake_observation["execution_token"])
        self.assertFalse(is_valid)
        
        # System should reject this fabricated observation
        self.assertFalse(is_valid, "Fabricated observation should be rejected")
    
    def test_mixed_legitimate_and_fabricated(self):
        """Test system handles mixed legitimate and fabricated executions"""
        # Legitimate execution
        token1 = execution_registry.request_execution("Tool1", "agent1", "task1")
        tool1 = lambda x: f"Result1: {x}"
        wrapper1 = ToolExecutionWrapper(tool1, "Tool1")
        result1 = wrapper1.execute_with_token(token1, "input1")
        
        # Fabricated observation
        fake_token = "fake-token-12345"
        
        # Verify legitimate execution passes
        self.assertTrue(verify_observation_token(token1.token_id))
        
        # Verify fabricated observation fails
        self.assertFalse(verify_observation_token(fake_token))
    
    def test_performance_impact_is_minimal(self):
        """Test that the verification system has minimal performance impact"""
        def test_tool(input_data):
            return f"Processed: {input_data}"
        
        # Measure execution time with verification
        start_time = time.time()
        
        token = execution_registry.request_execution("PerformanceTestTool", "agent1", "task1")
        wrapper = ToolExecutionWrapper(test_tool, "PerformanceTestTool")
        result = wrapper.execute_with_token(token, "test_input")
        is_valid = verify_observation_token(token.token_id)
        
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        # Verify functionality
        self.assertTrue(is_valid)
        self.assertIn("Processed: test_input", result)
        
        # Verify performance impact is minimal (< 5ms)
        self.assertLess(execution_time, 5.0, 
                       f"Execution time {execution_time}ms exceeds 5ms threshold")

if __name__ == '__main__':
    unittest.main()