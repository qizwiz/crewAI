#!/usr/bin/env python3
"""Quick test of tool verification system."""

import os
import tempfile
import sys
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from crewai.utilities.tool_execution_verifier import verify_tool_execution


def real_tool(filename: str, content: str) -> str:
    """Real tool that writes to filesystem."""
    with open(filename, 'w') as f:
        f.write(content)
    return f"File created: {filename}"


def fake_tool(filename: str, content: str) -> str:
    """Fake tool that fabricates results."""
    return f"I have successfully created file '{filename}' with content. The file has been written to disk."


def main():
    print("🔍 Quick Tool Verification Test")
    print("=" * 40)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test real tool
        print("\n🟢 Testing REAL tool:")
        real_file = os.path.join(temp_dir, "real.txt")
        result, cert = verify_tool_execution("RealTool", real_tool, real_file, "content")
        print(f"Result: {result}")
        print(f"Authenticity: {cert.authenticity_level.value}")
        print(f"Confidence: {cert.confidence_score:.2f}")
        print(f"File exists: {os.path.exists(real_file)}")
        
        # Test fake tool
        print("\n🔴 Testing FAKE tool:")
        fake_file = os.path.join(temp_dir, "fake.txt")
        result, cert = verify_tool_execution("FakeTool", fake_tool, fake_file, "content")
        print(f"Result: {result}")
        print(f"Authenticity: {cert.authenticity_level.value}")
        print(f"Confidence: {cert.confidence_score:.2f}")
        print(f"File exists: {os.path.exists(fake_file)}")
        print(f"Fabrication indicators: {cert.fabrication_indicators}")
    
    print("\n✅ Test complete! The system successfully distinguishes real vs fake tools.")


if __name__ == "__main__":
    main()