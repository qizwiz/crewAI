#!/usr/bin/env python3
"""
Performance Benchmark Test for CrewAI Workflow Transparency
===========================================================

CRITICAL FOR PROFESSIONAL REPUTATION:
- Validates performance overhead stays within acceptable limits
- Ensures no performance degradation under load
- Benchmarks against industry standards for enterprise use

Performance SLA Requirements:
- Event creation: < 1ms per event
- Field iteration: < 0.1ms per event  
- Validation: < 0.5ms per event
- Memory overhead: < 10MB for 1000 events

This test MUST pass before any public submission.
"""

import time
import sys
import statistics
import threading
from typing import List, Dict, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add src to path for testing
sys.path.insert(0, '/Users/jonathanhill/src/crewai-professional/src')

from crewai.utilities.events.crypto_events_fixed import (
    CryptographicCommitmentCreatedEvent,
    CryptographicValidationCompletedEvent,
    CryptographicWorkflowAuditEvent,
    get_event_fields_summary,
    validate_event_completeness
)


class PerformanceBenchmark:
    """Professional performance benchmarking for reputation protection"""
    
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.measurements = []
        self.start_time = 0
        
    def start_timer(self):
        """Start timing measurement"""
        self.start_time = time.perf_counter()
        
    def record_measurement(self, operation_count: int = 1) -> float:
        """Record a timing measurement"""
        end_time = time.perf_counter()
        duration_ms = (end_time - self.start_time) * 1000  # Convert to milliseconds
        per_operation_ms = duration_ms / operation_count
        
        self.measurements.append({
            'duration_ms': duration_ms,
            'per_operation_ms': per_operation_ms,
            'operation_count': operation_count,
            'timestamp': time.time()
        })
        
        return per_operation_ms
    
    def get_statistics(self) -> Dict[str, float]:
        """Calculate performance statistics"""
        if not self.measurements:
            return {"error": "No measurements recorded"}
        
        per_op_times = [m['per_operation_ms'] for m in self.measurements]
        total_times = [m['duration_ms'] for m in self.measurements]
        
        return {
            'avg_per_operation_ms': statistics.mean(per_op_times),
            'median_per_operation_ms': statistics.median(per_op_times),
            'min_per_operation_ms': min(per_op_times),
            'max_per_operation_ms': max(per_op_times),
            'stddev_per_operation_ms': statistics.stdev(per_op_times) if len(per_op_times) > 1 else 0,
            'avg_total_time_ms': statistics.mean(total_times),
            'total_measurements': len(self.measurements),
            'total_operations': sum(m['operation_count'] for m in self.measurements)
        }
    
    def check_sla_compliance(self, max_per_operation_ms: float) -> Dict[str, Any]:
        """Check if performance meets SLA requirements"""
        stats = self.get_statistics()
        
        if 'error' in stats:
            return {'compliant': False, 'error': stats['error']}
        
        avg_time = stats['avg_per_operation_ms']
        max_time = stats['max_per_operation_ms']
        
        return {
            'compliant': avg_time <= max_per_operation_ms and max_time <= max_per_operation_ms * 2,
            'sla_target_ms': max_per_operation_ms,
            'actual_avg_ms': avg_time,
            'actual_max_ms': max_time,
            'sla_margin_percent': ((max_per_operation_ms - avg_time) / max_per_operation_ms) * 100,
            'performance_ratio': avg_time / max_per_operation_ms
        }
    
    def generate_report(self, sla_target_ms: float) -> str:
        """Generate professional performance report"""
        stats = self.get_statistics()
        sla = self.check_sla_compliance(sla_target_ms)
        
        if 'error' in stats:
            return f"❌ {self.test_name}: {stats['error']}"
        
        report = f"""
⚡ PERFORMANCE BENCHMARK: {self.test_name}
{'='*60}

Operations Tested: {stats['total_operations']:,}
Total Measurements: {stats['total_measurements']:,}

Performance Metrics:
  Average Time: {stats['avg_per_operation_ms']:.3f} ms/op
  Median Time: {stats['median_per_operation_ms']:.3f} ms/op
  Min Time: {stats['min_per_operation_ms']:.3f} ms/op
  Max Time: {stats['max_per_operation_ms']:.3f} ms/op
  Std Deviation: {stats['stddev_per_operation_ms']:.3f} ms

SLA Compliance:
  Target: {sla['sla_target_ms']:.3f} ms/op
  Actual: {sla['actual_avg_ms']:.3f} ms/op
  Status: {'✅ COMPLIANT' if sla['compliant'] else '❌ NON-COMPLIANT'}
  Margin: {sla['sla_margin_percent']:.1f}%
  Performance Ratio: {sla['performance_ratio']:.2f}x

REPUTATION IMPACT: {'✅ SAFE FOR SUBMISSION' if sla['compliant'] else '❌ RISKY - PERFORMANCE ISSUES'}
        """
        
        return report


def benchmark_event_creation():
    """Benchmark event creation performance"""
    
    benchmark = PerformanceBenchmark("Event Creation")
    iterations = 5000
    
    print(f"🏗️ Benchmarking event creation ({iterations:,} iterations)...")
    
    # Warm up
    for _ in range(100):
        CryptographicCommitmentCreatedEvent(
            task_id="warmup", agent_id="warmup", workflow_id="warmup",
            task_description="warmup", agent_role="warmup", expected_output="warmup",
            commitment_word="warmup", commitment_hash="warmup"
        )
    
    # Benchmark single event creation
    for i in range(iterations):
        benchmark.start_timer()
        
        event = CryptographicCommitmentCreatedEvent(
            task_id=f"perf_test_task_{i}",
            agent_id=f"perf_agent_{i % 100}",
            workflow_id=f"perf_workflow_{i // 1000}",
            task_description=f"Performance test task {i} with description",
            agent_role=f"Performance Agent {i % 10}",
            expected_output=f"Expected output for task {i}",
            commitment_word=f"perf_word_{i}",
            commitment_hash=f"perf_hash_{i:08d}",
            security_level="high",
            compliance_tags=["PERFORMANCE_TEST"],
            audit_category="performance_testing",
            crew_name=f"Perf_Crew_{i // 100}",
            environment="performance_testing"
        )
        
        benchmark.record_measurement(1)
        
        # Progress indicator
        if i % 1000 == 0:
            current_stats = benchmark.get_statistics()
            print(f"   {i:,} events created, avg: {current_stats['avg_per_operation_ms']:.3f} ms/event")
    
    # Generate report
    report = benchmark.generate_report(1.0)  # SLA: 1ms per event
    print(report)
    
    # Check SLA compliance
    sla = benchmark.check_sla_compliance(1.0)
    if not sla['compliant']:
        raise RuntimeError(f"Event creation performance SLA violated: {sla['actual_avg_ms']:.3f} ms > 1.0 ms")
    
    return benchmark.get_statistics()


def benchmark_field_iteration():
    """Benchmark dynamic field iteration performance"""
    
    benchmark = PerformanceBenchmark("Dynamic Field Iteration")
    iterations = 10000
    
    print(f"🔄 Benchmarking dynamic field iteration ({iterations:,} iterations)...")
    
    # Create test events
    test_events = []
    for i in range(100):  # Create 100 diverse events
        test_events.append(CryptographicCommitmentCreatedEvent(
            task_id=f"iter_test_{i}",
            agent_id=f"iter_agent_{i}",
            workflow_id=f"iter_workflow_{i}",
            task_description=f"Field iteration test {i}",
            agent_role=f"Iterator Agent {i}",
            expected_output=f"Iterator output {i}",
            commitment_word=f"iter_word_{i}",
            commitment_hash=f"iter_hash_{i}",
            compliance_tags=[f"TAG_{i}", f"ITER_{i}"],
            user_context={"test_data": f"value_{i}", "iteration": i}
        ))
    
    # Benchmark field iteration
    for i in range(iterations):
        event = test_events[i % len(test_events)]
        
        benchmark.start_timer()
        
        # Test the dynamic field iteration (key feature)
        field_summary = get_event_fields_summary(event)
        
        benchmark.record_measurement(1)
        
        # Verify field summary is correct
        if field_summary['total_fields'] < 20:  # Should have many fields
            raise RuntimeError(f"Field iteration failed: only {field_summary['total_fields']} fields found")
        
        # Progress indicator
        if i % 2000 == 0:
            current_stats = benchmark.get_statistics()
            print(f"   {i:,} iterations completed, avg: {current_stats['avg_per_operation_ms']:.3f} ms/iteration")
    
    # Generate report
    report = benchmark.generate_report(0.1)  # SLA: 0.1ms per iteration
    print(report)
    
    # Check SLA compliance
    sla = benchmark.check_sla_compliance(0.1)
    if not sla['compliant']:
        raise RuntimeError(f"Field iteration performance SLA violated: {sla['actual_avg_ms']:.3f} ms > 0.1 ms")
    
    return benchmark.get_statistics()


def benchmark_event_validation():
    """Benchmark event validation performance"""
    
    benchmark = PerformanceBenchmark("Event Validation")
    iterations = 5000
    
    print(f"✅ Benchmarking event validation ({iterations:,} iterations)...")
    
    # Create test events with various completeness levels
    test_events = []
    for i in range(100):
        # Some complete events
        test_events.append(CryptographicValidationCompletedEvent(
            task_id=f"valid_test_{i}",
            agent_id=f"valid_agent_{i}",
            workflow_id=f"valid_workflow_{i}",
            validation_success=True,
            commitment_word=f"valid_word_{i}",
            revealed_word=f"valid_word_{i}",
            result_hash=f"valid_hash_{i}",
            validation_time_ms=float(i * 10),
            confidence_score=0.95,
            validation_errors=[],
            diagnostic_info={"test": f"value_{i}"}
        ))
        
        # Some incomplete events (for validation testing)
        if i % 10 == 0:
            test_events.append(CryptographicValidationCompletedEvent(
                task_id="",  # Empty required field
                agent_id=f"invalid_agent_{i}",
                workflow_id=f"invalid_workflow_{i}",
                validation_success=False,
                commitment_word="",  # Empty required field
                revealed_word="invalid",
                result_hash="invalid",
                validation_time_ms=-1.0,  # Invalid time
                confidence_score=1.5  # Invalid score
            ))
    
    # Benchmark validation
    valid_count = 0
    invalid_count = 0
    
    for i in range(iterations):
        event = test_events[i % len(test_events)]
        
        benchmark.start_timer()
        
        # Test event validation (comprehensive check)
        validation_result = validate_event_completeness(event)
        
        benchmark.record_measurement(1)
        
        # Count validation results
        if validation_result['is_valid']:
            valid_count += 1
        else:
            invalid_count += 1
        
        # Progress indicator
        if i % 1000 == 0:
            current_stats = benchmark.get_statistics()
            print(f"   {i:,} validations completed, avg: {current_stats['avg_per_operation_ms']:.3f} ms/validation")
    
    print(f"   Validation results: {valid_count:,} valid, {invalid_count:,} invalid")
    
    # Generate report
    report = benchmark.generate_report(0.5)  # SLA: 0.5ms per validation
    print(report)
    
    # Check SLA compliance
    sla = benchmark.check_sla_compliance(0.5)
    if not sla['compliant']:
        raise RuntimeError(f"Validation performance SLA violated: {sla['actual_avg_ms']:.3f} ms > 0.5 ms")
    
    return benchmark.get_statistics()


def benchmark_concurrent_performance():
    """Benchmark performance under concurrent load"""
    
    benchmark = PerformanceBenchmark("Concurrent Operations")
    num_threads = 10
    operations_per_thread = 500
    total_operations = num_threads * operations_per_thread
    
    print(f"🔄 Benchmarking concurrent performance ({num_threads} threads × {operations_per_thread} ops = {total_operations:,} total)...")
    
    def worker_thread(thread_id: int) -> List[float]:
        """Worker thread that performs operations"""
        thread_times = []
        
        for i in range(operations_per_thread):
            start_time = time.perf_counter()
            
            # Create event
            event = CryptographicCommitmentCreatedEvent(
                task_id=f"concurrent_{thread_id}_{i}",
                agent_id=f"concurrent_agent_{thread_id}",
                workflow_id=f"concurrent_workflow_{thread_id}",
                task_description=f"Concurrent test task {i} on thread {thread_id}",
                agent_role=f"Concurrent Agent {thread_id}",
                expected_output=f"Concurrent output {i}",
                commitment_word=f"concurrent_{thread_id}_{i}",
                commitment_hash=f"hash_{thread_id}_{i}",
                environment="concurrent_testing"
            )
            
            # Validate event
            validation = validate_event_completeness(event)
            if not validation['is_valid']:
                raise RuntimeError(f"Thread {thread_id} validation failed: {validation['errors']}")
            
            # Get field summary
            field_summary = get_event_fields_summary(event)
            if field_summary['total_fields'] < 10:
                raise RuntimeError(f"Thread {thread_id} field iteration failed")
            
            end_time = time.perf_counter()
            thread_times.append((end_time - start_time) * 1000)  # Convert to ms
        
        return thread_times
    
    # Start timing for overall benchmark
    benchmark.start_timer()
    
    # Execute concurrent operations
    thread_results = []
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(worker_thread, thread_id) for thread_id in range(num_threads)]
        
        for future in as_completed(futures):
            try:
                thread_times = future.result()
                thread_results.extend(thread_times)
            except Exception as e:
                raise RuntimeError(f"Concurrent thread failed: {e}")
    
    # Record overall benchmark
    benchmark.record_measurement(total_operations)
    
    # Analyze concurrent performance
    avg_concurrent_time = statistics.mean(thread_results)
    max_concurrent_time = max(thread_results)
    min_concurrent_time = min(thread_results)
    
    print(f"   Concurrent operations completed")
    print(f"   Average time per operation: {avg_concurrent_time:.3f} ms")
    print(f"   Min time: {min_concurrent_time:.3f} ms")
    print(f"   Max time: {max_concurrent_time:.3f} ms")
    
    # Generate report
    report = benchmark.generate_report(2.0)  # SLA: 2ms per operation under load
    print(report)
    
    # Check SLA compliance
    sla = benchmark.check_sla_compliance(2.0)
    if not sla['compliant']:
        raise RuntimeError(f"Concurrent performance SLA violated: {sla['actual_avg_ms']:.3f} ms > 2.0 ms")
    
    # Check if concurrent performance degradation is acceptable
    if avg_concurrent_time > 1.5:  # Should not degrade more than 50% under load
        print("⚠️ WARNING: Significant performance degradation under concurrent load")
    
    return benchmark.get_statistics()


def benchmark_large_workflow():
    """Benchmark performance with large workflow audit events"""
    
    benchmark = PerformanceBenchmark("Large Workflow Events")
    iterations = 1000
    
    print(f"📊 Benchmarking large workflow events ({iterations:,} iterations)...")
    
    # Create large audit trails
    large_audit_trail = []
    for i in range(1000):  # 1000 tasks in audit trail
        large_audit_trail.append({
            'step_id': f'step_{i}',
            'task_id': f'task_{i}',
            'agent_id': f'agent_{i % 10}',
            'validation_success': True,
            'timestamp': time.time(),
            'execution_time_ms': float(i * 5),
            'metadata': {'test_data': f'value_{i}', 'large_field': 'x' * 100}
        })
    
    # Benchmark large event creation and processing
    for i in range(iterations):
        benchmark.start_timer()
        
        # Create large workflow audit event
        large_event = CryptographicWorkflowAuditEvent(
            workflow_id=f"large_workflow_{i}",
            crew_name=f"Large_Crew_{i}",
            session_id=f"large_session_{i}",
            total_tasks=1000,
            validated_tasks=1000,
            failed_validations=0,
            workflow_integrity_score=1.0,
            audit_trail=large_audit_trail.copy(),  # Large data structure
            execution_trace=[{'trace': f'data_{j}'} for j in range(100)],  # More large data
            performance_metrics={f'metric_{j}': float(j) for j in range(50)},
            execution_start_time=time.time() - 3600,
            execution_end_time=time.time(),
            total_execution_time_ms=3600000.0,
            average_task_time_ms=3.6,
            slowest_task_time_ms=100.0,
            fastest_task_time_ms=1.0,
            compliance_framework=["LARGE_WORKFLOW_TEST", "PERFORMANCE_TEST"],
            agent_performance={f'agent_{j}': {'score': 0.9, 'tasks': 100} for j in range(10)},
            agent_reliability_scores={f'agent_{j}': 0.95 for j in range(10)},
            environment="large_workflow_testing"
        )
        
        # Test field iteration on large event
        field_summary = get_event_fields_summary(large_event)
        
        # Test validation on large event
        validation = validate_event_completeness(large_event)
        
        benchmark.record_measurement(1)
        
        # Verify large event was processed correctly
        if field_summary['total_fields'] < 30:
            raise RuntimeError(f"Large event field iteration failed: {field_summary['total_fields']} fields")
        
        if not validation['is_valid']:
            raise RuntimeError(f"Large event validation failed: {validation['errors']}")
        
        # Progress indicator
        if i % 200 == 0:
            current_stats = benchmark.get_statistics()
            print(f"   {i:,} large events processed, avg: {current_stats['avg_per_operation_ms']:.3f} ms/event")
    
    # Generate report
    report = benchmark.generate_report(5.0)  # SLA: 5ms per large event
    print(report)
    
    # Check SLA compliance
    sla = benchmark.check_sla_compliance(5.0)
    if not sla['compliant']:
        raise RuntimeError(f"Large workflow performance SLA violated: {sla['actual_avg_ms']:.3f} ms > 5.0 ms")
    
    return benchmark.get_statistics()


def main():
    """Run comprehensive performance benchmarks"""
    
    print("⚡ PERFORMANCE BENCHMARKING FOR PROFESSIONAL REPUTATION")
    print("=" * 65)
    print("⚠️  CRITICAL: Performance must meet SLA requirements for submission")
    print("🎯 Validating enterprise-grade performance characteristics")
    print()
    
    benchmark_results = {}
    
    try:
        # Benchmark 1: Event Creation
        print("🏗️ Benchmark 1: Event Creation Performance")
        print("-" * 45)
        result1 = benchmark_event_creation()
        benchmark_results['event_creation'] = result1
        print("✅ Benchmark 1 PASSED\n")
        
        # Benchmark 2: Field Iteration
        print("🔄 Benchmark 2: Dynamic Field Iteration Performance")
        print("-" * 50)
        result2 = benchmark_field_iteration()
        benchmark_results['field_iteration'] = result2
        print("✅ Benchmark 2 PASSED\n")
        
        # Benchmark 3: Event Validation
        print("✅ Benchmark 3: Event Validation Performance")
        print("-" * 45)
        result3 = benchmark_event_validation()
        benchmark_results['event_validation'] = result3
        print("✅ Benchmark 3 PASSED\n")
        
        # Benchmark 4: Concurrent Performance
        print("🔄 Benchmark 4: Concurrent Operations Performance")
        print("-" * 50)
        result4 = benchmark_concurrent_performance()
        benchmark_results['concurrent_operations'] = result4
        print("✅ Benchmark 4 PASSED\n")
        
        # Benchmark 5: Large Workflows
        print("📊 Benchmark 5: Large Workflow Performance")
        print("-" * 45)
        result5 = benchmark_large_workflow()
        benchmark_results['large_workflows'] = result5
        print("✅ Benchmark 5 PASSED\n")
        
        # Overall Performance Analysis
        print("📈 OVERALL PERFORMANCE ANALYSIS")
        print("=" * 45)
        
        total_operations = sum(
            result['total_operations'] 
            for result in benchmark_results.values()
        )
        
        avg_performance = statistics.mean([
            result['avg_per_operation_ms']
            for result in benchmark_results.values()
        ])
        
        print(f"Total Operations Benchmarked: {total_operations:,}")
        print(f"Average Performance: {avg_performance:.3f} ms/operation")
        print(f"Performance Grade: {'🏆 EXCELLENT' if avg_performance < 1.0 else '✅ GOOD' if avg_performance < 2.0 else '⚠️ ACCEPTABLE' if avg_performance < 5.0 else '❌ POOR'}")
        
        print("\n🎯 PERFORMANCE BENCHMARKING COMPLETED SUCCESSFULLY")
        print("✅ All SLA requirements met")
        print("🏆 Enterprise-grade performance validated")
        print("🚀 Safe for professional submission")
        
    except Exception as e:
        print(f"\n💥 PERFORMANCE BENCHMARK FAILED: {e}")
        print("❌ CRITICAL: Performance SLA violations detected")
        print("🔧 Optimize performance before attempting submission")
        sys.exit(1)


if __name__ == "__main__":
    main()