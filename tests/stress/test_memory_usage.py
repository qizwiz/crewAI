#!/usr/bin/env python3
"""
Memory Usage Stress Test for CrewAI Workflow Transparency
=========================================================

CRITICAL FOR PROFESSIONAL REPUTATION:
- Validates no memory leaks under extended usage
- Ensures stable memory footprint with large workflows
- Detects memory growth patterns that could cause production issues

This test MUST pass before any public submission.
"""

import gc
import sys
import time
import psutil
import threading
from typing import List, Dict, Any
from dataclasses import fields

# Add src to path for testing
sys.path.insert(0, '/Users/jonathanhill/src/crewai-professional/src')

from crewai.utilities.events.crypto_events_fixed import (
    CryptographicCommitmentCreatedEvent,
    CryptographicValidationCompletedEvent,
    CryptographicWorkflowAuditEvent,
    get_event_fields_summary,
    validate_event_completeness
)


class MemoryProfiler:
    """Professional memory profiling for reputation protection"""
    
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.process = psutil.Process()
        self.baseline_memory = 0
        self.peak_memory = 0
        self.memory_samples = []
        self.start_time = 0
        
    def start_monitoring(self):
        """Start memory monitoring"""
        self.start_time = time.time()
        self.baseline_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        self.peak_memory = self.baseline_memory
        print(f"🔍 {self.test_name}: Starting memory monitoring")
        print(f"   Baseline memory: {self.baseline_memory:.2f} MB")
        
    def sample_memory(self):
        """Take a memory sample"""
        current_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        self.memory_samples.append({
            'timestamp': time.time() - self.start_time,
            'memory_mb': current_memory
        })
        
        if current_memory > self.peak_memory:
            self.peak_memory = current_memory
            
        return current_memory
    
    def analyze_memory_pattern(self) -> Dict[str, Any]:
        """Analyze memory usage patterns for leaks"""
        if len(self.memory_samples) < 10:
            return {"error": "Insufficient samples for analysis"}
        
        # Calculate memory growth trend
        first_half = self.memory_samples[:len(self.memory_samples)//2]
        second_half = self.memory_samples[len(self.memory_samples)//2:]
        
        first_half_avg = sum(s['memory_mb'] for s in first_half) / len(first_half)
        second_half_avg = sum(s['memory_mb'] for s in second_half) / len(second_half)
        
        memory_growth = second_half_avg - first_half_avg
        memory_growth_percent = (memory_growth / first_half_avg) * 100
        
        return {
            'baseline_memory_mb': self.baseline_memory,
            'peak_memory_mb': self.peak_memory,
            'final_memory_mb': self.memory_samples[-1]['memory_mb'],
            'memory_growth_mb': memory_growth,
            'memory_growth_percent': memory_growth_percent,
            'total_samples': len(self.memory_samples),
            'test_duration_seconds': self.memory_samples[-1]['timestamp'],
            'leak_detected': memory_growth_percent > 10.0,  # Alert if >10% growth
            'memory_stable': abs(memory_growth_percent) < 5.0  # Stable if <5% change
        }
    
    def generate_report(self) -> str:
        """Generate professional memory analysis report"""
        analysis = self.analyze_memory_pattern()
        
        report = f"""
🔍 MEMORY USAGE ANALYSIS: {self.test_name}
{'='*60}

Baseline Memory: {analysis.get('baseline_memory_mb', 0):.2f} MB
Peak Memory: {analysis.get('peak_memory_mb', 0):.2f} MB  
Final Memory: {analysis.get('final_memory_mb', 0):.2f} MB
Memory Growth: {analysis.get('memory_growth_mb', 0):.2f} MB ({analysis.get('memory_growth_percent', 0):.1f}%)

Test Duration: {analysis.get('test_duration_seconds', 0):.1f} seconds
Total Samples: {analysis.get('total_samples', 0)}

MEMORY LEAK STATUS: {'🚨 DETECTED' if analysis.get('leak_detected', False) else '✅ NONE DETECTED'}
MEMORY STABILITY: {'✅ STABLE' if analysis.get('memory_stable', False) else '⚠️ UNSTABLE'}

REPUTATION IMPACT: {'❌ RISKY - DO NOT SUBMIT' if analysis.get('leak_detected', False) else '✅ SAFE FOR SUBMISSION'}
        """
        
        return report


def test_event_creation_memory_usage():
    """Test memory usage during intensive event creation"""
    
    profiler = MemoryProfiler("Event Creation Stress Test")
    profiler.start_monitoring()
    
    events_created = 0
    target_events = 10000
    
    try:
        for i in range(target_events):
            # Create comprehensive event with all fields
            event = CryptographicCommitmentCreatedEvent(
                task_id=f"stress_test_task_{i}",
                agent_id=f"stress_test_agent_{i % 100}",  # Reuse agent IDs
                workflow_id=f"stress_test_workflow_{i // 1000}",  # Group workflows
                task_description=f"Stress test task {i} with detailed description for memory testing",
                agent_role=f"Stress Test Agent Role {i % 10}",
                expected_output=f"Expected output for stress test task {i}",
                commitment_word=f"commitment_word_{i}",
                commitment_hash=f"hash_{i:08d}",
                security_level="high",
                compliance_tags=["STRESS_TEST", "MEMORY_VALIDATION"],
                audit_category="stress_testing",
                crew_name=f"Stress_Test_Crew_{i // 100}",
                environment="testing"
            )
            
            # Validate event completeness
            validation = validate_event_completeness(event)
            if not validation['is_valid']:
                raise RuntimeError(f"Event validation failed: {validation['errors']}")
            
            # Get field summary (tests dynamic iteration)
            field_summary = get_event_fields_summary(event)
            expected_field_count = len(fields(CryptographicCommitmentCreatedEvent))
            if field_summary['total_fields'] != expected_field_count:
                raise RuntimeError(f"Field count mismatch: expected {expected_field_count}, got {field_summary['total_fields']}")
            
            events_created += 1
            
            # Sample memory every 100 events
            if i % 100 == 0:
                current_memory = profiler.sample_memory()
                print(f"   Created {events_created:,} events, Memory: {current_memory:.2f} MB")
            
            # Force garbage collection every 1000 events
            if i % 1000 == 0:
                gc.collect()
        
        print(f"\n✅ Successfully created {events_created:,} events")
        
    except Exception as e:
        print(f"\n❌ Test failed after {events_created:,} events: {e}")
        raise
    
    finally:
        # Final memory sample
        profiler.sample_memory()
        
        # Generate memory report
        report = profiler.generate_report()
        print(report)
        
        # Check for memory leaks
        analysis = profiler.analyze_memory_pattern()
        if analysis.get('leak_detected', False):
            raise RuntimeError("MEMORY LEAK DETECTED - Cannot proceed with submission")
        
        if not analysis.get('memory_stable', True):
            print("⚠️ WARNING: Memory usage appears unstable")
        
        return analysis


def test_concurrent_workflow_memory():
    """Test memory usage with concurrent workflow processing"""
    
    profiler = MemoryProfiler("Concurrent Workflow Memory Test")
    profiler.start_monitoring()
    
    workflows_completed = 0
    target_workflows = 100
    events_per_workflow = 50
    
    def create_workflow_events(workflow_id: int) -> List[Any]:
        """Create a complete workflow's worth of events"""
        nonlocal workflows_completed
        
        workflow_events = []
        
        try:
            # Create commitment events
            for task_id in range(events_per_workflow):
                commitment_event = CryptographicCommitmentCreatedEvent(
                    task_id=f"workflow_{workflow_id}_task_{task_id}",
                    agent_id=f"agent_{task_id % 10}",
                    workflow_id=f"concurrent_workflow_{workflow_id}",
                    task_description=f"Concurrent task {task_id} in workflow {workflow_id}",
                    agent_role=f"Concurrent Agent {task_id % 5}",
                    expected_output=f"Output for task {task_id}",
                    commitment_word=f"concurrent_{workflow_id}_{task_id}",
                    commitment_hash=f"hash_{workflow_id}_{task_id}",
                    compliance_tags=["CONCURRENT_TEST"],
                    crew_name=f"Concurrent_Crew_{workflow_id}"
                )
                workflow_events.append(commitment_event)
                
                # Create corresponding validation event
                validation_event = CryptographicValidationCompletedEvent(
                    task_id=f"workflow_{workflow_id}_task_{task_id}",
                    agent_id=f"agent_{task_id % 10}",
                    workflow_id=f"concurrent_workflow_{workflow_id}",
                    validation_success=True,
                    commitment_word=f"concurrent_{workflow_id}_{task_id}",
                    revealed_word=f"concurrent_{workflow_id}_{task_id}",
                    result_hash=f"result_hash_{workflow_id}_{task_id}",
                    validation_time_ms=float(task_id % 100),
                    confidence_score=0.95,
                    compliance_status="compliant"
                )
                workflow_events.append(validation_event)
            
            # Create workflow audit event
            audit_event = CryptographicWorkflowAuditEvent(
                workflow_id=f"concurrent_workflow_{workflow_id}",
                crew_name=f"Concurrent_Crew_{workflow_id}",
                session_id=f"session_{workflow_id}",
                total_tasks=events_per_workflow,
                validated_tasks=events_per_workflow,
                failed_validations=0,
                workflow_integrity_score=1.0,
                audit_trail=[{"task_id": i, "status": "completed"} for i in range(events_per_workflow)],
                execution_start_time=time.time(),
                execution_end_time=time.time() + 1.0,
                total_execution_time_ms=1000.0,
                average_task_time_ms=20.0,
                slowest_task_time_ms=50.0,
                fastest_task_time_ms=10.0,
                compliance_framework=["CONCURRENT_TEST"],
                environment="testing"
            )
            workflow_events.append(audit_event)
            
            workflows_completed += 1
            return workflow_events
            
        except Exception as e:
            print(f"❌ Workflow {workflow_id} failed: {e}")
            raise
    
    # Create workflows concurrently using threading
    threads = []
    total_events_created = 0
    
    def workflow_wrapper(workflow_id: int):
        """Wrapper that doesn't accumulate events to test pure processing"""
        nonlocal total_events_created
        events = create_workflow_events(workflow_id)
        total_events_created += len(events)
        # Events go out of scope and get garbage collected
        return len(events)
    
    try:
        for workflow_id in range(target_workflows):
            thread = threading.Thread(target=workflow_wrapper, args=(workflow_id,))
            threads.append(thread)
            thread.start()
            
            # Sample memory every 10 workflows
            if workflow_id % 10 == 0:
                current_memory = profiler.sample_memory()
                print(f"   Started {workflow_id + 1} workflows, Memory: {current_memory:.2f} MB")
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=30)  # 30 second timeout per thread
        
        # Force garbage collection to clean up
        gc.collect()
        time.sleep(0.1)  # Allow GC to complete
        
        print(f"\n✅ Successfully completed {workflows_completed}/{target_workflows} concurrent workflows")
        print(f"   Total events processed: {total_events_created:,}")
        
    except Exception as e:
        print(f"\n❌ Concurrent test failed: {e}")
        raise
    
    finally:
        # Final memory sample and analysis
        profiler.sample_memory()
        report = profiler.generate_report()
        print(report)
        
        analysis = profiler.analyze_memory_pattern()
        if analysis.get('leak_detected', False):
            raise RuntimeError("MEMORY LEAK DETECTED in concurrent processing")
        
        return analysis


def test_long_running_memory_stability():
    """Test memory stability over extended time period"""
    
    profiler = MemoryProfiler("Long Running Stability Test")
    profiler.start_monitoring()
    
    duration_minutes = 2  # 2 minute test for CI
    end_time = time.time() + (duration_minutes * 60)
    cycle_count = 0
    
    print(f"🕐 Running stability test for {duration_minutes} minutes...")
    
    try:
        while time.time() < end_time:
            cycle_count += 1
            
            # Create various event types in a cycle
            for i in range(10):  # 10 events per cycle
                # Commitment event
                commitment = CryptographicCommitmentCreatedEvent(
                    task_id=f"stability_task_{cycle_count}_{i}",
                    agent_id=f"stability_agent_{i % 3}",
                    workflow_id=f"stability_workflow_{cycle_count}",
                    task_description=f"Long running stability test task {i}",
                    agent_role="Stability Test Agent",
                    expected_output="Stability test output",
                    commitment_word=f"stability_{cycle_count}_{i}",
                    commitment_hash=f"stable_hash_{cycle_count}_{i}",
                    environment="long_running_test"
                )
                
                # Validation event
                validation = CryptographicValidationCompletedEvent(
                    task_id=f"stability_task_{cycle_count}_{i}",
                    agent_id=f"stability_agent_{i % 3}",
                    workflow_id=f"stability_workflow_{cycle_count}",
                    validation_success=True,
                    commitment_word=f"stability_{cycle_count}_{i}",
                    revealed_word=f"stability_{cycle_count}_{i}",
                    result_hash=f"result_{cycle_count}_{i}",
                    validation_time_ms=float(i * 5)
                )
                
                # Validate and get field summaries
                validate_event_completeness(commitment)
                validate_event_completeness(validation)
                get_event_fields_summary(commitment)
                get_event_fields_summary(validation)
            
            # Sample memory every 10 cycles
            if cycle_count % 10 == 0:
                current_memory = profiler.sample_memory()
                elapsed = time.time() - profiler.start_time
                print(f"   Cycle {cycle_count}, Elapsed: {elapsed:.1f}s, Memory: {current_memory:.2f} MB")
            
            # Force garbage collection every 50 cycles
            if cycle_count % 50 == 0:
                gc.collect()
            
            # Small delay to simulate real usage
            time.sleep(0.01)  # 10ms
        
        print(f"\n✅ Completed {cycle_count} cycles over {duration_minutes} minutes")
        
    except Exception as e:
        print(f"\n❌ Stability test failed at cycle {cycle_count}: {e}")
        raise
    
    finally:
        profiler.sample_memory()
        report = profiler.generate_report()
        print(report)
        
        analysis = profiler.analyze_memory_pattern()
        if analysis.get('leak_detected', False):
            raise RuntimeError("MEMORY LEAK DETECTED in long-running test")
        
        return analysis


def main():
    """Run comprehensive memory stress tests"""
    
    print("🧠 MEMORY STRESS TESTING FOR PROFESSIONAL REPUTATION")
    print("=" * 65)
    print("⚠️  CRITICAL: These tests MUST pass before public submission")
    print("🎯 Validating memory usage patterns under stress conditions")
    print()
    
    test_results = {}
    
    try:
        # Test 1: Event Creation Memory Usage
        print("📝 Test 1: Event Creation Memory Usage")
        print("-" * 40)
        result1 = test_event_creation_memory_usage()
        test_results['event_creation'] = result1
        print("✅ Test 1 PASSED\n")
        
        # Test 2: Concurrent Workflow Memory
        print("🔄 Test 2: Concurrent Workflow Memory")
        print("-" * 40)
        result2 = test_concurrent_workflow_memory()
        test_results['concurrent_workflows'] = result2
        print("✅ Test 2 PASSED\n")
        
        # Test 3: Long Running Stability
        print("⏱️ Test 3: Long Running Memory Stability")
        print("-" * 40)
        result3 = test_long_running_memory_stability()
        test_results['long_running_stability'] = result3
        print("✅ Test 3 PASSED\n")
        
        # Overall Analysis
        print("📊 OVERALL MEMORY ANALYSIS")
        print("=" * 40)
        
        total_leak_detected = any(
            result.get('leak_detected', False) 
            for result in test_results.values()
        )
        
        total_stable = all(
            result.get('memory_stable', False)
            for result in test_results.values()
        )
        
        max_growth = max(
            result.get('memory_growth_percent', 0)
            for result in test_results.values()
        )
        
        print(f"Memory Leak Detected: {'❌ YES' if total_leak_detected else '✅ NO'}")
        print(f"Memory Stable: {'✅ YES' if total_stable else '❌ NO'}")
        print(f"Maximum Growth: {max_growth:.1f}%")
        
        if total_leak_detected:
            print("\n🚨 CRITICAL: MEMORY LEAKS DETECTED")
            print("❌ DO NOT SUBMIT - REPUTATION AT RISK")
            sys.exit(1)
        
        if not total_stable:
            print("\n⚠️ WARNING: Memory usage shows instability")
            print("🔍 Review recommended before submission")
        
        print("\n🎯 MEMORY STRESS TESTS COMPLETED SUCCESSFULLY")
        print("✅ Safe for professional submission")
        print("🏆 Reputation protection validated")
        
    except Exception as e:
        print(f"\n💥 MEMORY STRESS TEST FAILED: {e}")
        print("❌ CRITICAL: Cannot proceed with submission")
        print("🔧 Fix memory issues before attempting submission")
        sys.exit(1)


if __name__ == "__main__":
    main()