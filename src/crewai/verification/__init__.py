"""
CrewAI Tool Execution Verification System

Prevents agents from fabricating tool execution by implementing cryptographic
verification that tools were actually executed via their .run() method.

🔧 Generated with Claude Code for CrewAI Issue #3154
"""

from .tool_execution_verifier import ToolExecutionVerifier, get_global_verifier

__all__ = ["ToolExecutionVerifier", "get_global_verifier"]
