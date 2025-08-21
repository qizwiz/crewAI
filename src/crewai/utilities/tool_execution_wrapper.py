"""
Tool Execution Wrapper for CrewAI Integration

This module provides wrapper classes and functions to integrate the tool execution
verification system with CrewAI's tool execution flow. It implements monkey patching
and wrapper strategies to hook into tool execution without breaking existing functionality.

Key Components:
- VerifiedToolWrapper: Wraps individual tools with verification
- patch_crewai_tool_execution: Monkey patches CrewAI's tool execution
- ToolExecutionVerificationHandler: Event handler for verification results

Integration Points:
- tool_usage.py:216 - tool.invoke(input=arguments)
- structured_tool.py:261 - self.func(**parsed_args, **kwargs)
"""

import logging
from typing import Any, Callable, Dict, Optional, Union
from functools import wraps

from .tool_execution_verifier import ToolExecutionMonitor, ToolExecutionCertificate

logger = logging.getLogger(__name__)


class VerifiedToolWrapper:
    """Wrapper class that adds execution verification to any tool."""
    
    def __init__(self, original_tool: Any, strict_mode: bool = False, enable_verification: bool = True):
        """
        Initialize the wrapper.
        
        Args:
            original_tool: The original tool to wrap
            strict_mode: If True, raises exceptions for fabricated results
            enable_verification: If False, bypasses verification (useful for testing)
        """
        self.original_tool = original_tool
        self.strict_mode = strict_mode
        self.enable_verification = enable_verification
        self.verification_results: list[ToolExecutionCertificate] = []
        
        # Copy all attributes from original tool
        for attr_name in dir(original_tool):
            if not attr_name.startswith('_') and attr_name not in ['invoke', 'ainvoke', '_run', 'func']:
                try:
                    setattr(self, attr_name, getattr(original_tool, attr_name))
                except (AttributeError, TypeError):
                    pass
    
    def invoke(self, input: Union[str, dict], config: Optional[dict] = None, **kwargs: Any) -> Any:
        """Wrap the invoke method with verification."""
        if not self.enable_verification:
            return self.original_tool.invoke(input, config, **kwargs)
        
        tool_name = getattr(self.original_tool, 'name', self.original_tool.__class__.__name__)
        
        # Start monitoring
        monitor = ToolExecutionMonitor(strict_mode=self.strict_mode)
        monitor.start_monitoring()
        
        try:
            # Execute the original tool
            result = self.original_tool.invoke(input, config, **kwargs)
        except Exception as e:
            # Still verify even if execution failed
            result = f"Tool execution failed: {str(e)}"
            certificate = monitor.stop_monitoring_and_verify(tool_name, result)
            self.verification_results.append(certificate)
            
            # Record in global handler
            try:
                global_verification_handler.handle_verification_result(certificate)
            except Exception:
                logger.debug("Failed to record verification result globally")
            
            # Log verification results for failed executions
            logger.warning(f"Tool '{tool_name}' failed but verification completed: {certificate.authenticity_level.value}")
            raise
        else:
            # Verify successful execution
            certificate = monitor.stop_monitoring_and_verify(tool_name, result)
            self.verification_results.append(certificate)
            
            # Record in global handler
            try:
                global_verification_handler.handle_verification_result(certificate)
            except Exception as e:
                logger.debug(f"Failed to record verification result globally: {e}")
            
            # Log verification results
            if certificate.is_fabricated():
                logger.warning(f"Tool fabrication detected: {tool_name} - {certificate.authenticity_level.value}")
                if self.strict_mode:
                    raise RuntimeError(f"Fabricated result blocked (strict_mode): {tool_name}")
            else:
                logger.info(f"Tool execution verified: {tool_name} - {certificate.authenticity_level.value}")
            
            return result
    
    async def ainvoke(self, input: Union[str, dict], config: Optional[dict] = None, **kwargs: Any) -> Any:
        """Wrap the async invoke method with verification."""
        if not self.enable_verification:
            return await self.original_tool.ainvoke(input, config, **kwargs)
        
        tool_name = getattr(self.original_tool, 'name', self.original_tool.__class__.__name__)
        
        # Start monitoring
        monitor = ToolExecutionMonitor(strict_mode=self.strict_mode)
        monitor.start_monitoring()
        
        try:
            # Execute the original tool
            result = await self.original_tool.ainvoke(input, config, **kwargs)
        except Exception as e:
            # Still verify even if execution failed
            result = f"Tool execution failed: {str(e)}"
            certificate = monitor.stop_monitoring_and_verify(tool_name, result)
            self.verification_results.append(certificate)
            
            logger.warning(f"Async tool '{tool_name}' failed but verification completed: {certificate.authenticity_level.value}")
            raise
        else:
            # Verify successful execution
            certificate = monitor.stop_monitoring_and_verify(tool_name, result)
            self.verification_results.append(certificate)
            
            if certificate.is_fabricated():
                logger.warning(f"Async tool fabrication detected: {tool_name} - {certificate.authenticity_level.value}")
            else:
                logger.info(f"Async tool execution verified: {tool_name} - {certificate.authenticity_level.value}")
            
            return result
    
    def _run(self, *args, **kwargs) -> Any:
        """Wrap the legacy _run method if it exists."""
        if hasattr(self.original_tool, '_run'):
            if not self.enable_verification:
                return self.original_tool._run(*args, **kwargs)
            
            tool_name = getattr(self.original_tool, 'name', self.original_tool.__class__.__name__)
            
            monitor = ToolExecutionMonitor(strict_mode=self.strict_mode)
            monitor.start_monitoring()
            
            try:
                result = self.original_tool._run(*args, **kwargs)
            except Exception as e:
                result = f"Tool execution failed: {str(e)}"
                certificate = monitor.stop_monitoring_and_verify(tool_name, result)
                self.verification_results.append(certificate)
                raise
            else:
                certificate = monitor.stop_monitoring_and_verify(tool_name, result)
                self.verification_results.append(certificate)
                return result
        else:
            raise AttributeError(f"Original tool {self.original_tool} has no _run method")
    
    def get_verification_history(self) -> list[ToolExecutionCertificate]:
        """Get the history of verification results for this tool."""
        return self.verification_results.copy()
    
    def get_latest_verification(self) -> Optional[ToolExecutionCertificate]:
        """Get the most recent verification result."""
        return self.verification_results[-1] if self.verification_results else None


def wrap_tool_with_verification(tool: Any, strict_mode: bool = False, enable_verification: bool = True) -> VerifiedToolWrapper:
    """
    Wrap a tool with execution verification.
    
    Args:
        tool: The tool to wrap
        strict_mode: If True, raises exceptions for fabricated results
        enable_verification: If False, bypasses verification
    
    Returns:
        Wrapped tool with verification capabilities
    """
    return VerifiedToolWrapper(tool, strict_mode=strict_mode, enable_verification=enable_verification)


def wrap_function_with_verification(func: Callable, tool_name: str, strict_mode: bool = False) -> Callable:
    """
    Wrap a function with execution verification.
    
    Args:
        func: The function to wrap
        tool_name: Name of the tool for identification
        strict_mode: If True, raises exceptions for fabricated results
    
    Returns:
        Wrapped function with verification
    """
    @wraps(func)
    def verified_wrapper(*args, **kwargs):
        monitor = ToolExecutionMonitor(strict_mode=strict_mode)
        monitor.start_monitoring()
        
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            result = f"Function execution failed: {str(e)}"
            monitor.stop_monitoring_and_verify(tool_name, result)
            raise
        else:
            certificate = monitor.stop_monitoring_and_verify(tool_name, result)
            if certificate.is_fabricated():
                logger.warning(f"Function fabrication detected: {tool_name} - {certificate.authenticity_level.value}")
            return result
    
    return verified_wrapper


# Monkey patching strategies for CrewAI integration

def patch_crewai_tool_execution(strict_mode: bool = False, enable_verification: bool = True):
    """
    Monkey patch CrewAI's tool execution to add verification.
    
    This function patches the key execution points in CrewAI to automatically
    add verification to all tool executions.
    
    Args:
        strict_mode: If True, raises exceptions for fabricated results
        enable_verification: If False, bypasses verification
    """
    try:
        # Patch ToolUsage._use method
        from crewai.tools.tool_usage import ToolUsage
        
        original_tool_usage_use = ToolUsage._use
        
        def verified_tool_usage_use(self, tool_string: str, tool: Any, calling: Any) -> str:
            # Wrap the tool with verification before using it
            if enable_verification and not isinstance(tool, VerifiedToolWrapper):
                tool = wrap_tool_with_verification(tool, strict_mode=strict_mode, enable_verification=enable_verification)
            
            return original_tool_usage_use(self, tool_string, tool, calling)
        
        ToolUsage._use = verified_tool_usage_use  # type: ignore[method-assign]
        logger.info("Successfully patched ToolUsage._use for verification")
        
    except ImportError as e:
        logger.warning(f"Could not patch ToolUsage: {e}")
    
    try:
        # Patch CrewStructuredTool.invoke method
        from crewai.tools.structured_tool import CrewStructuredTool
        
        original_invoke = CrewStructuredTool.invoke
        
        def verified_invoke(self, input: Union[str, dict], config: Optional[dict] = None, **kwargs: Any) -> Any:
            if not enable_verification:
                return original_invoke(self, input, config, **kwargs)
            
            tool_name = getattr(self, 'name', self.__class__.__name__)
            
            monitor = ToolExecutionMonitor(strict_mode=strict_mode)
            monitor.start_monitoring()
            
            try:
                result = original_invoke(self, input, config, **kwargs)
            except Exception as e:
                result = f"Structured tool execution failed: {str(e)}"
                monitor.stop_monitoring_and_verify(tool_name, result)
                raise
            else:
                certificate = monitor.stop_monitoring_and_verify(tool_name, result)
                if certificate.is_fabricated():
                    logger.warning(f"Structured tool fabrication detected: {tool_name} - {certificate.authenticity_level.value}")
                return result
        
        CrewStructuredTool.invoke = verified_invoke  # type: ignore[method-assign]
        logger.info("Successfully patched CrewStructuredTool.invoke for verification")
        
    except ImportError as e:
        logger.warning(f"Could not patch CrewStructuredTool: {e}")


def unpatch_crewai_tool_execution():
    """
    Remove monkey patches and restore original CrewAI tool execution.
    
    This function attempts to restore the original behavior by reloading the modules.
    Note: This may not work perfectly in all cases due to Python's import system.
    """
    logger.warning("Unpatching is experimental and may require restarting the Python process")
    
    try:
        import importlib
        
        # Reload the modules to restore original behavior
        from crewai.tools import tool_usage
        from crewai.tools import structured_tool
        
        importlib.reload(tool_usage)
        importlib.reload(structured_tool)
        
        logger.info("Attempted to restore original CrewAI tool execution behavior")
        
    except Exception as e:
        logger.error(f"Failed to unpatch CrewAI tool execution: {e}")


class ToolExecutionVerificationHandler:
    """Handler for processing tool execution verification results."""
    
    def __init__(self):
        self.verification_history: list[ToolExecutionCertificate] = []
        self.fabrication_count = 0
        self.authentic_count = 0
    
    def handle_verification_result(self, certificate: ToolExecutionCertificate) -> None:
        """Process a verification result."""
        self.verification_history.append(certificate)
        
        if certificate.is_fabricated():
            self.fabrication_count += 1
            logger.warning(f"Fabrication detected: {certificate.tool_name} - {certificate.authenticity_level.value}")
        elif certificate.is_authentic():
            self.authentic_count += 1
            logger.info(f"Authentic execution: {certificate.tool_name} - {certificate.authenticity_level.value}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get verification statistics."""
        total = len(self.verification_history)
        if total == 0:
            return {"total": 0, "fabrication_rate": 0.0, "authentic_rate": 0.0}
        
        return {
            "total_verifications": total,
            "fabrication_count": self.fabrication_count,
            "authentic_count": self.authentic_count,
            "fabrication_rate": self.fabrication_count / total,
            "authentic_rate": self.authentic_count / total,
            "verification_history": [
                {
                    "tool_name": cert.tool_name,
                    "authenticity_level": cert.authenticity_level.value,
                    "confidence_score": cert.confidence_score,
                    "timestamp": cert.verification_timestamp
                }
                for cert in self.verification_history
            ]
        }


# Global verification handler instance
global_verification_handler = ToolExecutionVerificationHandler()


# Configuration functions

def enable_tool_verification(strict_mode: bool = False):
    """
    Enable tool execution verification globally.
    
    Args:
        strict_mode: If True, raises exceptions for fabricated results
    """
    patch_crewai_tool_execution(strict_mode=strict_mode, enable_verification=True)
    logger.info(f"Tool execution verification enabled (strict_mode={strict_mode})")


def disable_tool_verification():
    """Disable tool execution verification globally."""
    patch_crewai_tool_execution(strict_mode=False, enable_verification=False)
    logger.info("Tool execution verification disabled")


def get_global_verification_statistics() -> Dict[str, Any]:
    """Get global verification statistics."""
    return global_verification_handler.get_statistics()


# Example usage
if __name__ == "__main__":
    # Example of enabling verification
    enable_tool_verification(strict_mode=False)
    
    print("Tool execution verification enabled!")
    print("All CrewAI tool executions will now be monitored for authenticity.")
    print("Check logs for verification results.")