#!/usr/bin/env python3
"""
Template Performance Benchmarking Script

This script benchmarks the performance of the template injection system
under various load conditions and generates detailed performance reports.
"""

import asyncio
import json
import sys
import time
import statistics
import psutil
import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from server.services.template_injection_service import (
    TemplateInjectionService,
    get_template_injection_service
)
from server.services.projects.task_service import TaskService
from server.config.logfire_config import get_logger

logger = get_logger(__name__)


class TemplatePerformanceBenchmark:
    """Benchmarks template injection system performance"""

    def __init__(self):
        self.template_service = None
        self.task_service = None
        self.benchmark_results = {}

    async def initialize(self):
        """Initialize services for benchmarking"""
        try:
            self.template_service = get_template_injection_service()
            self.task_service = TaskService()
            logger.info("Services initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            raise

    async def benchmark_template_expansion(self, iterations: int = 100) -> Dict[str, Any]:
        """
        Benchmark template expansion performance
        
        Args:
            iterations: Number of expansions to perform
            
        Returns:
            Performance metrics
        """
        logger.info(f"Benchmarking template expansion with {iterations} iterations")
        
        test_descriptions = [
            "Create a REST API endpoint for user management",
            "Fix a critical bug in the payment processing system",
            "Implement OAuth2 authentication with multiple providers",
            "Add comprehensive unit tests for the core business logic",
            "Optimize database queries for better performance",
            "Deploy the application to production environment",
            "Refactor legacy code for improved maintainability",
            "Create documentation for the new API features"
        ]
        
        durations = []
        successes = 0
        errors = []
        
        start_time = time.time()
        
        for i in range(iterations):
            description = test_descriptions[i % len(test_descriptions)]
            
            try:
                expansion_start = time.time()
                response = await self.template_service.expand_task_description(
                    original_description=f"{description} (iteration {i+1})",
                    template_name="workflow_default"
                )
                expansion_duration = (time.time() - expansion_start) * 1000
                
                if response.success:
                    successes += 1
                    durations.append(expansion_duration)
                else:
                    errors.append(f"Iteration {i+1}: {response.error}")
                    
            except Exception as e:
                errors.append(f"Iteration {i+1}: {str(e)}")
        
        total_time = time.time() - start_time
        
        return {
            "test_name": "template_expansion",
            "iterations": iterations,
            "successes": successes,
            "failures": len(errors),
            "success_rate": successes / iterations,
            "total_time_seconds": total_time,
            "throughput_per_second": successes / total_time,
            "durations_ms": durations,
            "avg_duration_ms": statistics.mean(durations) if durations else 0,
            "median_duration_ms": statistics.median(durations) if durations else 0,
            "min_duration_ms": min(durations) if durations else 0,
            "max_duration_ms": max(durations) if durations else 0,
            "p95_duration_ms": statistics.quantiles(durations, n=20)[18] if len(durations) >= 20 else 0,
            "p99_duration_ms": statistics.quantiles(durations, n=100)[98] if len(durations) >= 100 else 0,
            "errors": errors[:10],  # Keep first 10 errors
            "target_met_100ms": all(d < 100 for d in durations),
            "target_met_50ms": all(d < 50 for d in durations)
        }

    async def benchmark_concurrent_load(self, concurrent_users: int = 20, requests_per_user: int = 10) -> Dict[str, Any]:
        """
        Benchmark performance under concurrent load
        
        Args:
            concurrent_users: Number of concurrent users
            requests_per_user: Number of requests per user
            
        Returns:
            Concurrent load performance metrics
        """
        logger.info(f"Benchmarking concurrent load: {concurrent_users} users, {requests_per_user} requests each")
        
        async def user_workload(user_id: int) -> List[float]:
            """Simulate a single user's workload"""
            durations = []
            for i in range(requests_per_user):
                try:
                    start_time = time.time()
                    response = await self.template_service.expand_task_description(
                        original_description=f"User {user_id} task {i+1}: Implement feature",
                        template_name="workflow_default"
                    )
                    duration = (time.time() - start_time) * 1000
                    
                    if response.success:
                        durations.append(duration)
                except Exception as e:
                    logger.error(f"User {user_id} request {i+1} failed: {e}")
            
            return durations
        
        # Record system state before test
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        initial_cpu = process.cpu_percent()
        
        start_time = time.time()
        
        # Run concurrent workloads
        tasks = [user_workload(i) for i in range(concurrent_users)]
        results = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        
        # Record system state after test
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        final_cpu = process.cpu_percent()
        
        # Aggregate results
        all_durations = []
        for user_durations in results:
            all_durations.extend(user_durations)
        
        total_requests = concurrent_users * requests_per_user
        successful_requests = len(all_durations)
        
        return {
            "test_name": "concurrent_load",
            "concurrent_users": concurrent_users,
            "requests_per_user": requests_per_user,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": total_requests - successful_requests,
            "success_rate": successful_requests / total_requests,
            "total_time_seconds": total_time,
            "throughput_per_second": successful_requests / total_time,
            "avg_duration_ms": statistics.mean(all_durations) if all_durations else 0,
            "median_duration_ms": statistics.median(all_durations) if all_durations else 0,
            "p95_duration_ms": statistics.quantiles(all_durations, n=20)[18] if len(all_durations) >= 20 else 0,
            "p99_duration_ms": statistics.quantiles(all_durations, n=100)[98] if len(all_durations) >= 100 else 0,
            "max_duration_ms": max(all_durations) if all_durations else 0,
            "memory_usage": {
                "initial_mb": initial_memory,
                "final_mb": final_memory,
                "growth_mb": final_memory - initial_memory
            },
            "cpu_usage": {
                "initial_percent": initial_cpu,
                "final_percent": final_cpu
            },
            "performance_degradation": {
                "avg_duration_acceptable": statistics.mean(all_durations) < 200 if all_durations else False,
                "p95_duration_acceptable": (statistics.quantiles(all_durations, n=20)[18] < 300) if len(all_durations) >= 20 else False,
                "memory_growth_acceptable": (final_memory - initial_memory) < 100
            }
        }

    async def benchmark_cache_performance(self, cache_test_iterations: int = 50) -> Dict[str, Any]:
        """
        Benchmark cache performance and hit ratios
        
        Args:
            cache_test_iterations: Number of iterations for cache testing
            
        Returns:
            Cache performance metrics
        """
        logger.info(f"Benchmarking cache performance with {cache_test_iterations} iterations")
        
        # Clear cache to start fresh
        self.template_service._template_cache.clear()
        self.template_service._component_cache.clear()
        
        # Test cache miss performance (first request)
        start_time = time.time()
        response = await self.template_service.expand_task_description(
            original_description="Cache miss test",
            template_name="workflow_default"
        )
        cache_miss_duration = (time.time() - start_time) * 1000
        
        # Test cache hit performance (subsequent requests)
        cache_hit_durations = []
        for i in range(cache_test_iterations):
            start_time = time.time()
            response = await self.template_service.expand_task_description(
                original_description=f"Cache hit test {i+1}",
                template_name="workflow_default"
            )
            duration = (time.time() - start_time) * 1000
            cache_hit_durations.append(duration)
        
        avg_cache_hit_duration = statistics.mean(cache_hit_durations)
        cache_improvement_ratio = cache_miss_duration / avg_cache_hit_duration if avg_cache_hit_duration > 0 else 0
        
        return {
            "test_name": "cache_performance",
            "cache_miss_duration_ms": cache_miss_duration,
            "avg_cache_hit_duration_ms": avg_cache_hit_duration,
            "cache_improvement_ratio": cache_improvement_ratio,
            "cache_hit_durations_ms": cache_hit_durations,
            "cache_efficiency": {
                "improvement_ratio_acceptable": cache_improvement_ratio > 2,
                "cache_hit_fast": avg_cache_hit_duration < 10,
                "cache_miss_reasonable": cache_miss_duration < 100
            }
        }

    async def benchmark_task_creation_overhead(self, iterations: int = 50) -> Dict[str, Any]:
        """
        Benchmark task creation overhead with template injection
        
        Args:
            iterations: Number of task creation iterations
            
        Returns:
            Task creation overhead metrics
        """
        logger.info(f"Benchmarking task creation overhead with {iterations} iterations")
        
        project_id = "benchmark-project-" + str(int(time.time()))
        
        # Benchmark task creation with template injection
        with_template_durations = []
        for i in range(iterations):
            try:
                start_time = time.time()
                success, result = await self.task_service.create_task(
                    project_id=project_id,
                    title=f"Benchmark Task {i+1}",
                    description=f"Task with template injection {i+1}",
                    template_name="workflow_default",
                    enable_template_injection=True
                )
                duration = (time.time() - start_time) * 1000
                
                if success:
                    with_template_durations.append(duration)
            except Exception as e:
                logger.error(f"Task creation with template failed: {e}")
        
        # Benchmark task creation without template injection
        without_template_durations = []
        for i in range(iterations):
            try:
                start_time = time.time()
                success, result = await self.task_service.create_task(
                    project_id=project_id,
                    title=f"Benchmark Task No Template {i+1}",
                    description=f"Task without template injection {i+1}",
                    enable_template_injection=False
                )
                duration = (time.time() - start_time) * 1000
                
                if success:
                    without_template_durations.append(duration)
            except Exception as e:
                logger.error(f"Task creation without template failed: {e}")
        
        # Calculate overhead
        avg_with_template = statistics.mean(with_template_durations) if with_template_durations else 0
        avg_without_template = statistics.mean(without_template_durations) if without_template_durations else 0
        overhead_ms = avg_with_template - avg_without_template
        overhead_percentage = (overhead_ms / avg_without_template * 100) if avg_without_template > 0 else 0
        
        return {
            "test_name": "task_creation_overhead",
            "iterations": iterations,
            "with_template_durations_ms": with_template_durations,
            "without_template_durations_ms": without_template_durations,
            "avg_with_template_ms": avg_with_template,
            "avg_without_template_ms": avg_without_template,
            "overhead_ms": overhead_ms,
            "overhead_percentage": overhead_percentage,
            "overhead_acceptable": overhead_ms < 50,
            "performance_impact": {
                "low": overhead_percentage < 20,
                "medium": 20 <= overhead_percentage < 50,
                "high": overhead_percentage >= 50
            }
        }

    async def run_full_benchmark(self) -> Dict[str, Any]:
        """
        Run complete performance benchmark suite
        
        Returns:
            Complete benchmark report
        """
        await self.initialize()
        
        benchmark_report = {
            "benchmark_timestamp": datetime.now().isoformat(),
            "system_info": {
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": psutil.virtual_memory().total / (1024**3),
                "python_version": sys.version
            },
            "benchmarks": {},
            "summary": {}
        }
        
        # Run individual benchmarks
        benchmarks = [
            ("template_expansion", self.benchmark_template_expansion, {}),
            ("concurrent_load", self.benchmark_concurrent_load, {}),
            ("cache_performance", self.benchmark_cache_performance, {}),
            ("task_creation_overhead", self.benchmark_task_creation_overhead, {})
        ]
        
        for benchmark_name, benchmark_func, kwargs in benchmarks:
            logger.info(f"Running benchmark: {benchmark_name}")
            try:
                result = await benchmark_func(**kwargs)
                benchmark_report["benchmarks"][benchmark_name] = result
            except Exception as e:
                logger.error(f"Benchmark {benchmark_name} failed: {e}")
                benchmark_report["benchmarks"][benchmark_name] = {
                    "error": str(e),
                    "success": False
                }
        
        # Generate summary
        benchmark_report["summary"] = self._generate_benchmark_summary(benchmark_report["benchmarks"])
        
        return benchmark_report

    def _generate_benchmark_summary(self, benchmarks: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of benchmark results"""
        summary = {
            "overall_performance": "good",
            "targets_met": {},
            "recommendations": [],
            "critical_issues": []
        }
        
        # Check template expansion performance
        if "template_expansion" in benchmarks:
            te = benchmarks["template_expansion"]
            summary["targets_met"]["template_expansion_100ms"] = te.get("target_met_100ms", False)
            if not te.get("target_met_100ms", False):
                summary["critical_issues"].append("Template expansion exceeds 100ms target")
                summary["overall_performance"] = "needs_improvement"
        
        # Check concurrent load performance
        if "concurrent_load" in benchmarks:
            cl = benchmarks["concurrent_load"]
            summary["targets_met"]["concurrent_load_acceptable"] = cl.get("performance_degradation", {}).get("avg_duration_acceptable", False)
            if not cl.get("performance_degradation", {}).get("avg_duration_acceptable", False):
                summary["critical_issues"].append("Performance degrades significantly under concurrent load")
        
        # Check task creation overhead
        if "task_creation_overhead" in benchmarks:
            tco = benchmarks["task_creation_overhead"]
            summary["targets_met"]["task_overhead_50ms"] = tco.get("overhead_acceptable", False)
            if not tco.get("overhead_acceptable", False):
                summary["critical_issues"].append("Task creation overhead exceeds 50ms target")
        
        # Generate recommendations
        if summary["critical_issues"]:
            summary["overall_performance"] = "critical"
            summary["recommendations"].append("Address critical performance issues immediately")
        
        if not summary["targets_met"].get("template_expansion_100ms", False):
            summary["recommendations"].append("Optimize template expansion to meet 100ms target")
        
        if not summary["targets_met"].get("task_overhead_50ms", False):
            summary["recommendations"].append("Reduce task creation overhead to under 50ms")
        
        return summary


async def main():
    """Main function to run performance benchmarks"""
    benchmark = TemplatePerformanceBenchmark()
    
    try:
        # Run full benchmark suite
        report = await benchmark.run_full_benchmark()
        
        # Print results
        print("\n" + "="*60)
        print("TEMPLATE INJECTION PERFORMANCE BENCHMARK")
        print("="*60)
        
        for benchmark_name, results in report["benchmarks"].items():
            if "error" in results:
                print(f"\n❌ {benchmark_name}: FAILED")
                print(f"   Error: {results['error']}")
                continue
            
            print(f"\n✅ {benchmark_name}:")
            
            if benchmark_name == "template_expansion":
                print(f"   Average Duration: {results['avg_duration_ms']:.1f}ms")
                print(f"   P95 Duration: {results['p95_duration_ms']:.1f}ms")
                print(f"   Success Rate: {results['success_rate']:.1%}")
                print(f"   Target Met (<100ms): {'✅' if results['target_met_100ms'] else '❌'}")
            
            elif benchmark_name == "concurrent_load":
                print(f"   Throughput: {results['throughput_per_second']:.1f} req/sec")
                print(f"   Average Duration: {results['avg_duration_ms']:.1f}ms")
                print(f"   Memory Growth: {results['memory_usage']['growth_mb']:.1f}MB")
                print(f"   Performance Acceptable: {'✅' if results['performance_degradation']['avg_duration_acceptable'] else '❌'}")
            
            elif benchmark_name == "cache_performance":
                print(f"   Cache Improvement: {results['cache_improvement_ratio']:.1f}x")
                print(f"   Cache Hit Duration: {results['avg_cache_hit_duration_ms']:.1f}ms")
                print(f"   Cache Efficiency: {'✅' if results['cache_efficiency']['improvement_ratio_acceptable'] else '❌'}")
            
            elif benchmark_name == "task_creation_overhead":
                print(f"   Overhead: {results['overhead_ms']:.1f}ms ({results['overhead_percentage']:.1f}%)")
                print(f"   Target Met (<50ms): {'✅' if results['overhead_acceptable'] else '❌'}")
        
        # Print summary
        summary = report["summary"]
        print(f"\n📊 Overall Performance: {summary['overall_performance'].upper()}")
        
        if summary["critical_issues"]:
            print("🚨 Critical Issues:")
            for issue in summary["critical_issues"]:
                print(f"   - {issue}")
        
        if summary["recommendations"]:
            print("💡 Recommendations:")
            for rec in summary["recommendations"]:
                print(f"   - {rec}")
        
        # Save detailed report
        report_file = Path(__file__).parent / "performance_benchmark_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        # Exit with appropriate code
        sys.exit(0 if summary["overall_performance"] in ["good", "needs_improvement"] else 1)
        
    except Exception as e:
        logger.error(f"Benchmark failed: {e}")
        print(f"\n❌ Benchmark failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
