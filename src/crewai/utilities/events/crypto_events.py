"""
Cryptographic Events for CrewAI Workflow Transparency
====================================================

Extends CrewAI's event system with cryptographic accountability events.
Addresses Issue #3268: "How to know which steps crew took to complete the goal"
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import time


@dataclass
class CryptographicCommitmentCreatedEvent:
    """Event emitted when a cryptographic commitment is created for a task"""
    commitment_word: str
    task_id: str
    agent_id: str
    task_description: str
    commitment_hash: str
    agent_role: str
    workflow_id: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class CryptographicValidationCompletedEvent:
    """Event emitted when cryptographic commitment validation completes"""
    validation_success: bool
    commitment_word: str
    revealed_word: str
    task_id: str
    agent_id: str
    validation_time_ms: float
    result_hash: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class CryptographicWorkflowAuditEvent:
    """Event emitted for complete workflow audit information"""
    workflow_id: str
    total_tasks: int
    validated_tasks: int
    failed_validations: int
    workflow_integrity_score: float
    audit_trail: List[Dict[str, Any]]
    crew_name: Optional[str] = None
    timestamp: float = field(default_factory=time.time)