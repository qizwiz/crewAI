#!/usr/bin/env python3
"""
Tool Execution Verification Demo

This script demonstrates the tool execution verification system by testing
real vs fake tool implementations. It shows how the system can detect when
tools are actually executing vs when they're fabricating results.

Usage:
    python demo_tool_verification.py

The demo will:
1. Test a real file writing tool that actually creates files
2. Test a fake file writing tool that only pretends to create files
3. Show the verification results for each
4. Demonstrate strict mode enforcement
"""

import os
import sys
import tempfile
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from crewai.utilities.tool_execution_verifier import (
    ToolExecutionMonitor, 
    ExecutionAuthenticityLevel,
    verify_tool_execution
)
from crewai.utilities.tool_execution_wrapper import (
    wrap_function_with_verification,
    enable_tool_verification,
    get_global_verification_statistics
)


def real_file_write_tool(filename: str, content: str) -> str:
    """A real tool that actually writes to the filesystem."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Verify the file was actually created
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            return f"File '{filename}' created successfully with {size} bytes"
        else:
            return f"Error: File '{filename}' was not created"
            
    except Exception as e:
        return f"Error writing file '{filename}': {str(e)}"


def fake_file_write_tool(filename: str, content: str) -> str:
    """A fake tool that fabricates filesystem operations."""
    # This tool doesn't actually write anything, just returns fabricated results
    return f"I have successfully created file '{filename}' with {len(content)} characters. The file has been written to disk and saved successfully."


def real_search_tool(query: str) -> str:
    """A real tool that actually searches (simulated with file operations)."""
    # Simulate real work by creating a temporary search index file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.search_index', delete=False) as f:
        f.write(f"search_query: {query}\n")
        f.write("results: [example1.txt, example2.txt, example3.txt]\n")
        index_file = f.name
    
    try:
        # Read back the results
        with open(index_file, 'r') as f:
            content = f.read()
        
        os.unlink(index_file)  # Clean up
        return f"Search completed for '{query}'. Found 3 results in index."
        
    except Exception as e:
        return f"Search failed: {str(e)}"


def fake_search_tool(query: str) -> str:
    """A fake tool that fabricates search results."""
    return f"Search results for '{query}' successfully obtained. I found 15 relevant documents matching your query. The search operation completed successfully and returned comprehensive results."


def run_verification_demo():
    """Run the complete verification demonstration."""
    print("🔍 CrewAI Tool Execution Verification Demo")
    print("=" * 50)
    print()
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = os.path.join(temp_dir, "test_output.txt")
        
        print("📁 Testing in temporary directory:", temp_dir)
        print()
        
        # Test 1: Real File Writer
        print("🟢 Test 1: REAL File Writer Tool")
        print("-" * 30)
        
        result, certificate = verify_tool_execution(
            "RealFileWriter", 
            real_file_write_tool, 
            test_file, 
            "Hello from real tool!"
        )
        
        print(f"📝 Tool Result: {result}")
        print(f"🔍 Authenticity: {certificate.authenticity_level.value}")
        print(f"📊 Confidence: {certificate.confidence_score:.2f}")
        print(f"🔧 Subprocess Spawned: {certificate.evidence.subprocess_spawned}")
        print(f"📁 Filesystem Changes: {certificate.evidence.filesystem_changes}")
        print(f"📈 Execution Time: {certificate.evidence.execution_time_ms:.1f}ms")
        print(f"⚠️  Fabrication Indicators: {certificate.fabrication_indicators}")
        
        # Verify the file actually exists
        if os.path.exists(test_file):
            print(f"✅ Verification: File actually exists on disk!")
            with open(test_file, 'r') as f:
                actual_content = f.read()
            print(f"📄 File Content: '{actual_content}'")
        else:
            print(f"❌ Verification: File does not exist on disk!")
        
        print()
        
        # Test 2: Fake File Writer
        print("🔴 Test 2: FAKE File Writer Tool")
        print("-" * 30)
        
        fake_file = os.path.join(temp_dir, "fake_output.txt")
        result, certificate = verify_tool_execution(
            "FakeFileWriter", 
            fake_file_write_tool, 
            fake_file, 
            "Hello from fake tool!"
        )
        
        print(f"📝 Tool Result: {result}")
        print(f"🔍 Authenticity: {certificate.authenticity_level.value}")
        print(f"📊 Confidence: {certificate.confidence_score:.2f}")
        print(f"🔧 Subprocess Spawned: {certificate.evidence.subprocess_spawned}")
        print(f"📁 Filesystem Changes: {certificate.evidence.filesystem_changes}")
        print(f"📈 Execution Time: {certificate.evidence.execution_time_ms:.1f}ms")
        print(f"⚠️  Fabrication Indicators: {certificate.fabrication_indicators}")
        
        # Verify the file does NOT exist
        if os.path.exists(fake_file):
            print(f"❌ Verification: File unexpectedly exists on disk!")
        else:
            print(f"✅ Verification: File correctly does not exist (fabricated result)")
        
        print()
        
        # Test 3: Real Search Tool
        print("🟢 Test 3: REAL Search Tool")
        print("-" * 25)
        
        result, certificate = verify_tool_execution(
            "RealSearchTool", 
            real_search_tool, 
            "artificial intelligence"
        )
        
        print(f"📝 Tool Result: {result}")
        print(f"🔍 Authenticity: {certificate.authenticity_level.value}")
        print(f"📊 Confidence: {certificate.confidence_score:.2f}")
        print(f"⚠️  Fabrication Indicators: {certificate.fabrication_indicators}")
        print()
        
        # Test 4: Fake Search Tool
        print("🔴 Test 4: FAKE Search Tool")
        print("-" * 25)
        
        result, certificate = verify_tool_execution(
            "FakeSearchTool", 
            fake_search_tool, 
            "artificial intelligence"
        )
        
        print(f"📝 Tool Result: {result}")
        print(f"🔍 Authenticity: {certificate.authenticity_level.value}")
        print(f"📊 Confidence: {certificate.confidence_score:.2f}")
        print(f"⚠️  Fabrication Indicators: {certificate.fabrication_indicators}")
        print()
        
        # Test 5: Strict Mode Demo
        print("⚡ Test 5: Strict Mode Enforcement")
        print("-" * 35)
        
        print("Testing fake tool with strict mode enabled...")
        
        monitor = ToolExecutionMonitor(strict_mode=True)
        monitor.start_monitoring()
        
        try:
            result = fake_file_write_tool("strict_test.txt", "content")
            certificate = monitor.stop_monitoring_and_verify("StrictFakeTest", result)
        except Exception as e:
            print(f"✅ Strict mode correctly blocked fabricated tool: {str(e)}")
        else:
            if certificate.is_fabricated():
                print(f"❌ Strict mode should have blocked this fabricated result!")
            else:
                print(f"✅ Tool passed strict mode verification")
        
        print()
        
        # Test 6: Function Wrapper Demo
        print("🔧 Test 6: Function Wrapper Integration")
        print("-" * 40)
        
        # Wrap the functions with verification
        verified_real_writer = wrap_function_with_verification(
            real_file_write_tool, 
            "WrappedRealWriter", 
            strict_mode=False
        )
        
        verified_fake_writer = wrap_function_with_verification(
            fake_file_write_tool, 
            "WrappedFakeWriter", 
            strict_mode=False
        )
        
        print("Testing wrapped real function:")
        result = verified_real_writer(os.path.join(temp_dir, "wrapped_real.txt"), "Wrapped content")
        print(f"📝 Wrapped Real Result: {result}")
        
        print("\nTesting wrapped fake function:")
        result = verified_fake_writer(os.path.join(temp_dir, "wrapped_fake.txt"), "Wrapped content")
        print(f"📝 Wrapped Fake Result: {result}")
        
        print()
    
    print("🎉 Verification Demo Complete!")
    print()
    print("🔍 Key Findings:")
    print("• Real tools show filesystem changes and/or subprocess activity")
    print("• Fake tools show fabrication patterns in their output text")
    print("• The system can distinguish between authentic and fabricated results")
    print("• Strict mode can block fabricated results automatically")
    print("• Function wrappers provide easy integration with existing code")
    print()
    print("📊 This demonstrates how the system solves CrewAI Issue #3154:")
    print("   'Agent does not actually invoke tools, only simulates tool usage'")


if __name__ == "__main__":
    run_verification_demo()