"""
Test suite for token-based tool execution verification system
"""

import unittest
import sys
import os
import time
import threading

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from crewai.utilities.tool_execution_verifier import (
    ExecutionRegistry,
    ExecutionToken,
    ExecutionStatus,
    ToolExecutionWrapper,
    verify_observation_token,
    execution_registry
)

class TestTool:
    """Mock tool for testing"""
    def __init__(self, name="TestTool"):
        self.name = name
        self.call_count = 0
    
    def run(self, *args, **kwargs):
        self.call_count += 1
        time.sleep(0.001)  # Simulate minimal work
        return f"Result from {self.name}: args={args}, kwargs={kwargs}"

class TestToolExecutionVerifier(unittest.TestCase):
    """Test cases for the token-based execution verification system"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Clear the registry for each test
        execution_registry._pending.clear()
        execution_registry._completed.clear()
    
    def test_legitimate_execution(self):
        """Test that legitimate tool execution works correctly"""
        # Request execution
        token = execution_registry.request_execution("TestTool", "agent1", "task1")
        
        # Wrap and execute tool
        tool = TestTool()
        wrapper = ToolExecutionWrapper(tool.run, "TestTool")
        
        result = wrapper.execute_with_token(token, "arg1", kwarg1="value1")
        
        # Verify result
        self.assertEqual(result, "Result from TestTool: args=('arg1',), kwargs={'kwarg1': 'value1'}")
        self.assertEqual(tool.call_count, 1)
        
        # Verify token
        is_valid = verify_observation_token(token.token_id)
        self.assertTrue(is_valid)
    
    def test_fabrication_prevention(self):
        """Test that fabricated observations are rejected"""
        fake_token_id = "this-token-was-never-generated"
        
        is_valid = verify_observation_token(fake_token_id)
        self.assertFalse(is_valid)
    
    def test_invalid_token_execution(self):
        """Test that execution with invalid token fails"""
        tool = TestTool()
        wrapper = ToolExecutionWrapper(tool.run, "TestTool")
        
        fake_token = ExecutionToken(
            token_id="fake-token",
            tool_name="TestTool",
            agent_id="agent1",
            task_id="task1",
            timestamp=time.time()
        )
        
        with self.assertRaises(ValueError) as context:
            wrapper.execute_with_token(fake_token, "arg1")
        
        self.assertIn("Invalid or expired execution token", str(context.exception))
        self.assertEqual(tool.call_count, 0)
    
    def test_concurrent_executions(self):
        """Test multiple concurrent tool executions"""
        def execute_tool(tool_id):
            tool = TestTool(f"Tool{tool_id}")
            token = execution_registry.request_execution(f"Tool{tool_id}", "agent1", f"task{tool_id}")
            wrapper = ToolExecutionWrapper(tool.run, f"Tool{tool_id}")
            result = wrapper.execute_with_token(token, f"input{tool_id}")
            return token, result, tool.call_count
        
        # Run multiple executions concurrently
        threads = []
        results = []
        
        def worker(tool_id):
            result = execute_tool(tool_id)
            results.append(result)
        
        # Start 5 concurrent executions
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all to complete
        for thread in threads:
            thread.join()
        
        # Verify all executions completed successfully
        self.assertEqual(len(results), 5)
        
        for token, result, call_count in results:
            self.assertTrue(verify_observation_token(token.token_id))
            self.assertEqual(call_count, 1)
    
    def test_tool_execution_failure(self):
        """Test that failed tool executions are properly recorded"""
        def failing_tool():
            raise Exception("Tool execution failed")
        
        token = execution_registry.request_execution("FailingTool", "agent1", "task1")
        wrapper = ToolExecutionWrapper(failing_tool, "FailingTool")
        
        with self.assertRaises(Exception) as context:
            wrapper.execute_with_token(token)
        
        self.assertIn("Tool execution failed", str(context.exception))
        
        # Verify token shows failed execution
        record = execution_registry.verify_token(token.token_id)
        self.assertIsNotNone(record)
        self.assertEqual(record.status, ExecutionStatus.FAILED)
        self.assertIn("Tool execution failed", record.error)
    
    def test_registry_singleton(self):
        """Test that ExecutionRegistry is a proper singleton"""
        registry1 = ExecutionRegistry()
        registry2 = ExecutionRegistry()
        
        self.assertIs(registry1, registry2)
    
    def test_token_uniqueness(self):
        """Test that tokens are unique"""
        tokens = set()
        
        for i in range(100):
            token = execution_registry.request_execution(f"Tool{i}", "agent1", f"task{i}")
            self.assertNotIn(token.token_id, tokens)
            tokens.add(token.token_id)

if __name__ == '__main__':
    unittest.main()