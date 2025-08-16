"""
Test Suite for CrewAI Cryptographic Workflow Transparency
=========================================================

Comprehensive tests validating solution for Issue #3268: workflow step visibility.
"""

import unittest
import time
from unittest.mock import Mock

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from crewai.utilities.events.crypto_events import (
    CryptographicCommitmentCreatedEvent,
    CryptographicValidationCompletedEvent,
    CryptographicWorkflowAuditEvent
)
from crewai.utilities.events.listeners.crypto_listener import (
    CryptographicTraceListener,
    WorkflowStep
)


class TestCryptographicEvents(unittest.TestCase):
    """Test cryptographic event creation and validation"""
    
    def test_commitment_event_creation(self):
        """Test creating cryptographic commitment events"""
        event = CryptographicCommitmentCreatedEvent(
            commitment_word="thunderbolt",
            task_id="test_task",
            agent_id="test_agent",
            task_description="Test task",
            commitment_hash="abc123",
            agent_role="Test Agent"
        )
        
        self.assertEqual(event.task_id, "test_task")
        self.assertEqual(event.commitment_word, "thunderbolt")
        self.assertGreater(event.timestamp, 0)
    
    def test_validation_event_creation(self):
        """Test creating validation events"""
        event = CryptographicValidationCompletedEvent(
            validation_success=True,
            commitment_word="thunderbolt",
            revealed_word="thunderbolt",
            task_id="test_task",
            agent_id="test_agent",
            validation_time_ms=15.5,
            result_hash="def456"
        )
        
        self.assertTrue(event.validation_success)
        self.assertEqual(event.commitment_word, "thunderbolt")
        self.assertEqual(event.validation_time_ms, 15.5)


class TestCryptographicTraceListener(unittest.TestCase):
    """Test the main CryptographicTraceListener functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.listener = CryptographicTraceListener()
        
        # Mock CrewAI objects
        self.mock_task = Mock()
        self.mock_task.id = "test_task"
        self.mock_task.description = "Test task description"
        
        self.mock_agent = Mock()
        self.mock_agent.id = "test_agent"
        self.mock_agent.role = "Test Agent"
        
        self.mock_source = Mock()
        self.mock_source.agent = self.mock_agent
        
        self.mock_task_event = Mock()
        self.mock_task_event.task = self.mock_task
        
        self.mock_completed_event = Mock()
        self.mock_completed_event.task_id = "test_task"
        self.mock_completed_event.output = "Task completed successfully"
    
    def test_listener_initialization(self):
        """Test listener initialization"""
        self.assertIsNone(self.listener.redis_client)
        self.assertEqual(self.listener.active_commitments, {})
        self.assertIsNone(self.listener.workflow_audit)
        self.assertGreater(len(self.listener.commitment_words), 0)
    
    def test_task_started_creates_commitment(self):
        """Test that task started creates cryptographic commitment"""
        event = self.listener.on_task_started(self.mock_source, self.mock_task_event)
        
        # Should initialize workflow audit
        self.assertIsNotNone(self.listener.workflow_audit)
        
        # Should create commitment
        self.assertIn("test_task", self.listener.active_commitments)
        commitment = self.listener.active_commitments["test_task"]
        self.assertIn("word", commitment)
        self.assertIn("hash", commitment)
        
        # Should create workflow step
        self.assertEqual(len(self.listener.workflow_audit["steps"]), 1)
        step = self.listener.workflow_audit["steps"][0]
        self.assertEqual(step.task_id, "test_task")
        self.assertEqual(step.agent_id, "test_agent")
        
        # Should return commitment event
        self.assertIsInstance(event, CryptographicCommitmentCreatedEvent)
        self.assertEqual(event.task_id, "test_task")
    
    def test_task_completed_validates_commitment(self):
        """Test that task completed validates commitment"""
        # First start a task
        self.listener.on_task_started(self.mock_source, self.mock_task_event)
        
        # Then complete it
        event = self.listener.on_task_completed(self.mock_source, self.mock_completed_event)
        
        # Should validate step
        step = self.listener.workflow_audit["steps"][0]
        self.assertTrue(step.validation_success)
        self.assertIsNotNone(step.revealed_word)
        self.assertIsNotNone(step.validation_time_ms)
        
        # Should increment validated count
        self.assertEqual(self.listener.workflow_audit["validated_steps"], 1)
        
        # Should return validation event
        self.assertIsInstance(event, CryptographicValidationCompletedEvent)
        self.assertTrue(event.validation_success)
    
    def test_transparency_report_issue_3268(self):
        """Test complete transparency report - solves Issue #3268"""
        # Simulate complete workflow
        self.listener.on_task_started(self.mock_source, self.mock_task_event)
        self.listener.on_task_completed(self.mock_source, self.mock_completed_event)
        
        # Get transparency report - THIS SOLVES ISSUE #3268
        report = self.listener.get_transparency_report()
        
        # Validate report structure
        self.assertIn("workflow_transparency", report)
        transparency = report["workflow_transparency"]
        
        # Check execution summary
        summary = transparency["execution_summary"]
        self.assertEqual(summary["total_steps"], 1)
        self.assertEqual(summary["validated_steps"], 1)
        self.assertEqual(summary["integrity_score"], 1.0)
        
        # Check detailed steps - KEY SOLUTION TO ISSUE #3268
        steps = transparency["detailed_steps"]
        self.assertEqual(len(steps), 1)
        
        step = steps[0]
        self.assertEqual(step["task_id"], "test_task")
        self.assertEqual(step["task_description"], "Test task description")
        self.assertEqual(step["agent_id"], "test_agent")
        self.assertEqual(step["agent_role"], "Test Agent")
        self.assertTrue(step["validation_success"])
        
        # Check cryptographic proof
        proof = transparency["cryptographic_proof"]
        self.assertTrue(proof["tamper_proof"])
        self.assertEqual(proof["validated_by"], "cryptographic_commitments")
        self.assertTrue(proof["audit_trail_complete"])
    
    def test_transparency_report_no_workflow(self):
        """Test transparency report when no workflow exists"""
        report = self.listener.get_transparency_report()
        self.assertIn("error", report)
    
    def test_multiple_tasks_workflow(self):
        """Test workflow with multiple tasks"""
        # Create multiple tasks
        for i in range(3):
            task = Mock()
            task.id = f"task_{i}"
            task.description = f"Task {i}"
            
            agent = Mock()
            agent.id = f"agent_{i}"
            agent.role = f"Agent {i}"
            
            source = Mock()
            source.agent = agent
            
            task_event = Mock()
            task_event.task = task
            
            completed_event = Mock()
            completed_event.task_id = f"task_{i}"
            completed_event.output = f"Output {i}"
            
            # Start and complete task
            self.listener.on_task_started(source, task_event)
            self.listener.on_task_completed(source, completed_event)
        
        # Validate final state
        self.assertEqual(self.listener.workflow_audit["total_steps"], 3)
        self.assertEqual(self.listener.workflow_audit["validated_steps"], 3)
        self.assertEqual(len(self.listener.workflow_audit["steps"]), 3)
        
        # Check transparency report
        report = self.listener.get_transparency_report()
        transparency = report["workflow_transparency"]
        self.assertEqual(len(transparency["detailed_steps"]), 3)
        self.assertEqual(transparency["execution_summary"]["integrity_score"], 1.0)


class TestWorkflowStep(unittest.TestCase):
    """Test workflow step data structure"""
    
    def test_workflow_step_creation(self):
        """Test creating workflow steps"""
        step = WorkflowStep(
            step_id="step_1",
            task_id="task_1",
            agent_id="agent_1",
            agent_role="Test Agent",
            task_description="Test task",
            commitment_word="thunderbolt",
            commitment_created_at=time.time()
        )
        
        self.assertEqual(step.step_id, "step_1")
        self.assertEqual(step.task_id, "task_1")
        self.assertEqual(step.commitment_word, "thunderbolt")
        self.assertIsNone(step.validation_success)  # Not yet validated


if __name__ == "__main__":
    # Run all tests
    unittest.main(verbosity=2)