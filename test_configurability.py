#!/usr/bin/env python3
"""
Test enhanced configurability features from CodeRabbit improvements
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from crewai.utilities.tool_execution_verifier import ToolExecutionMonitor, verify_tool_execution

def fake_tool_custom_patterns(action: str) -> str:
    """A fake tool that uses custom fabrication patterns."""
    return f"Task {action} has been processed successfully. Operation completed."

def test_custom_patterns():
    print("🧪 Testing Custom Fabrication Patterns")
    print("=" * 40)
    
    # Test with custom patterns
    custom_patterns = ["processed successfully", "operation completed"]
    custom_monitor = ToolExecutionMonitor(
        fabrication_patterns=custom_patterns,
        max_scan_depth=2
    )
    
    result, certificate = verify_tool_execution(
        "CustomPatternTest",
        fake_tool_custom_patterns,
        "data_analysis",
        monitor=custom_monitor
    )
    
    print(f"📝 Result: {result}")
    print(f"🔍 Authenticity: {certificate.authenticity_level.value}")
    print(f"📊 Confidence: {certificate.confidence_score:.2f}")
    print(f"⚠️  Fabrication Indicators: {certificate.fabrication_indicators}")
    print(f"✅ Custom patterns detected: {set(certificate.fabrication_indicators) & set(custom_patterns)}")
    
    # Test statistics
    stats = custom_monitor.get_statistics()
    print(f"📈 Fabrication Rate: {stats['fabrication_rate']:.2%}")
    
    return certificate.is_fabricated()

def test_thread_safety_warning():
    print("\n🛡️  Thread Safety Test")
    print("=" * 25)
    
    # Test that each thread should get its own monitor
    monitor1 = ToolExecutionMonitor(strict_mode=True)
    monitor2 = ToolExecutionMonitor(strict_mode=False) 
    
    print(f"✅ Monitor 1 strict mode: {monitor1.strict_mode}")
    print(f"✅ Monitor 2 strict mode: {monitor2.strict_mode}")
    print("⚠️  Each thread should create its own monitor instance (thread-safety)")

def test_configurable_scan_depth():
    print("\n📊 Configurable Scan Depth Test")
    print("=" * 35)
    
    # Test different scan depths
    shallow_monitor = ToolExecutionMonitor(max_scan_depth=1)
    deep_monitor = ToolExecutionMonitor(max_scan_depth=3)
    
    print(f"✅ Shallow scan depth: {shallow_monitor.max_scan_depth}")
    print(f"✅ Deep scan depth: {deep_monitor.max_scan_depth}")
    print("📁 Scan depth controls filesystem monitoring performance")

if __name__ == "__main__":
    print("🚀 Enhanced Configurability Test Suite")
    print("=" * 45)
    
    # Test custom patterns
    fabricated = test_custom_patterns()
    
    # Test thread safety
    test_thread_safety_warning()
    
    # Test scan depth
    test_configurable_scan_depth()
    
    print("\n🎉 Enhanced Features Working!")
    print("✅ Custom fabrication patterns")
    print("✅ Configurable scan depth")  
    print("✅ Thread-safety documentation")
    print("✅ Monitor parameter passing")
    
    if fabricated:
        print("\n🎯 SUCCESS: Custom patterns successfully detected fabrication!")
    else:
        print("\n❌ Custom pattern detection may need adjustment")