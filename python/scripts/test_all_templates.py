#!/usr/bin/env python3
"""
Template Testing Script

This script tests all workflow templates to ensure they expand correctly,
validate component references, and meet performance requirements.
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from server.services.template_injection_service import TemplateInjectionService
from server.services.template_context_selector import template_context_selector, TemplateType
from server.config.database import get_database_connection


@dataclass
class TestResult:
    """Test result for a template or component"""
    name: str
    test_type: str
    success: bool
    duration_ms: float
    error_message: Optional[str] = None
    details: Optional[Dict] = None


@dataclass
class TestSuite:
    """Complete test suite results"""
    total_tests: int
    passed_tests: int
    failed_tests: int
    total_duration_ms: float
    results: List[TestResult]


class TemplateTestRunner:
    """
    Comprehensive template testing framework
    """

    def __init__(self):
        """Initialize the test runner"""
        self.template_service = None
        self.test_tasks = [
            {
                "title": "Fix critical database connection issue",
                "description": "The production database is experiencing connection timeouts causing user login failures. This is a critical P0 issue affecting all users.",
                "expected_template": "workflow_hotfix"
            },
            {
                "title": "Complete Sprint 23 milestone",
                "description": "Finalize all deliverables for Sprint 23 including testing, documentation, and stakeholder sign-off for the new user dashboard feature.",
                "expected_template": "workflow_milestone_pass"
            },
            {
                "title": "Research OAuth2 implementation options",
                "description": "Investigate and analyze different OAuth2 implementation approaches for our authentication system. Compare existing solutions and provide recommendations.",
                "expected_template": "workflow_research"
            },
            {
                "title": "Perform weekly system maintenance",
                "description": "Execute routine weekly maintenance including health checks, backup verification, and monitoring validation for all production systems.",
                "expected_template": "workflow_maintenance"
            },
            {
                "title": "Implement user profile API endpoint",
                "description": "Create a new REST API endpoint for user profile management with proper validation, error handling, and documentation.",
                "expected_template": "workflow_default"
            }
        ]

    async def setup(self):
        """Setup test environment"""
        try:
            # Initialize database connection
            db_connection = await get_database_connection()
            
            # Initialize template service
            self.template_service = TemplateInjectionService(db_connection)
            
            logging.info("Test environment setup completed")
            return True
        except Exception as e:
            logging.error(f"Failed to setup test environment: {e}")
            return False

    async def run_all_tests(self) -> TestSuite:
        """
        Run all template tests
        
        Returns:
            Complete test suite results
        """
        logging.info("Starting comprehensive template testing")
        start_time = time.time()
        
        results = []
        
        # Test template expansion
        expansion_results = await self.test_template_expansion()
        results.extend(expansion_results)
        
        # Test context selection
        selection_results = await self.test_context_selection()
        results.extend(selection_results)
        
        # Test component validation
        component_results = await self.test_component_validation()
        results.extend(component_results)
        
        # Test performance
        performance_results = await self.test_performance()
        results.extend(performance_results)
        
        # Calculate summary
        total_duration = (time.time() - start_time) * 1000
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.success)
        failed_tests = total_tests - passed_tests
        
        test_suite = TestSuite(
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            total_duration_ms=total_duration,
            results=results
        )
        
        logging.info(f"Template testing completed: {passed_tests}/{total_tests} passed")
        return test_suite

    async def test_template_expansion(self) -> List[TestResult]:
        """Test template expansion for all templates"""
        logging.info("Testing template expansion...")
        results = []
        
        templates = [
            "workflow_default",
            "workflow_hotfix", 
            "workflow_milestone_pass",
            "workflow_research",
            "workflow_maintenance"
        ]
        
        for template_name in templates:
            start_time = time.time()
            
            try:
                # Test template expansion
                result = await self.template_service.expand_template(
                    original_description="Test task for template expansion",
                    template_name=template_name,
                    context_data={"test": True}
                )
                
                duration = (time.time() - start_time) * 1000
                
                if result.get("success"):
                    expanded_content = result.get("result", {}).get("expanded_description", "")
                    
                    # Validate expansion
                    if len(expanded_content) > 100:  # Reasonable expansion
                        results.append(TestResult(
                            name=template_name,
                            test_type="expansion",
                            success=True,
                            duration_ms=duration,
                            details={
                                "expansion_length": len(expanded_content),
                                "expansion_time": result.get("result", {}).get("expansion_time_ms", 0)
                            }
                        ))
                    else:
                        results.append(TestResult(
                            name=template_name,
                            test_type="expansion",
                            success=False,
                            duration_ms=duration,
                            error_message="Expansion too short, possible template issue"
                        ))
                else:
                    results.append(TestResult(
                        name=template_name,
                        test_type="expansion",
                        success=False,
                        duration_ms=duration,
                        error_message=result.get("error", "Unknown expansion error")
                    ))
                    
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                results.append(TestResult(
                    name=template_name,
                    test_type="expansion",
                    success=False,
                    duration_ms=duration,
                    error_message=str(e)
                ))
        
        return results

    async def test_context_selection(self) -> List[TestResult]:
        """Test context-aware template selection"""
        logging.info("Testing context selection...")
        results = []
        
        for task in self.test_tasks:
            start_time = time.time()
            
            try:
                # Test template selection
                template_type, confidence, reasoning = template_context_selector.select_template(
                    task["description"], 
                    task["title"]
                )
                
                duration = (time.time() - start_time) * 1000
                
                # Check if selection matches expected
                expected = task["expected_template"]
                actual = template_type.value
                
                success = (actual == expected)
                
                results.append(TestResult(
                    name=f"context_selection_{task['title'][:30]}",
                    test_type="context_selection",
                    success=success,
                    duration_ms=duration,
                    details={
                        "expected_template": expected,
                        "actual_template": actual,
                        "confidence": confidence,
                        "reasoning": reasoning
                    },
                    error_message=None if success else f"Expected {expected}, got {actual}"
                ))
                
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                results.append(TestResult(
                    name=f"context_selection_{task['title'][:30]}",
                    test_type="context_selection",
                    success=False,
                    duration_ms=duration,
                    error_message=str(e)
                ))
        
        return results

    async def test_component_validation(self) -> List[TestResult]:
        """Test component validation and references"""
        logging.info("Testing component validation...")
        results = []
        
        try:
            # Get all template components
            components = await self.template_service._get_all_components()
            
            for component in components:
                start_time = time.time()
                component_name = component.get("name", "unknown")
                
                try:
                    # Validate component structure
                    required_fields = ["name", "instruction_text", "component_type"]
                    missing_fields = [field for field in required_fields if not component.get(field)]
                    
                    if missing_fields:
                        results.append(TestResult(
                            name=component_name,
                            test_type="component_validation",
                            success=False,
                            duration_ms=(time.time() - start_time) * 1000,
                            error_message=f"Missing required fields: {missing_fields}"
                        ))
                        continue
                    
                    # Validate instruction text
                    instruction_text = component.get("instruction_text", "")
                    if len(instruction_text) < 50:
                        results.append(TestResult(
                            name=component_name,
                            test_type="component_validation",
                            success=False,
                            duration_ms=(time.time() - start_time) * 1000,
                            error_message="Instruction text too short"
                        ))
                        continue
                    
                    # Validate tools
                    required_tools = component.get("required_tools", [])
                    if not isinstance(required_tools, list):
                        results.append(TestResult(
                            name=component_name,
                            test_type="component_validation",
                            success=False,
                            duration_ms=(time.time() - start_time) * 1000,
                            error_message="Required tools must be a list"
                        ))
                        continue
                    
                    # Component is valid
                    results.append(TestResult(
                        name=component_name,
                        test_type="component_validation",
                        success=True,
                        duration_ms=(time.time() - start_time) * 1000,
                        details={
                            "instruction_length": len(instruction_text),
                            "tool_count": len(required_tools),
                            "component_type": component.get("component_type")
                        }
                    ))
                    
                except Exception as e:
                    results.append(TestResult(
                        name=component_name,
                        test_type="component_validation",
                        success=False,
                        duration_ms=(time.time() - start_time) * 1000,
                        error_message=str(e)
                    ))
        
        except Exception as e:
            results.append(TestResult(
                name="component_validation_setup",
                test_type="component_validation",
                success=False,
                duration_ms=0,
                error_message=f"Failed to get components: {e}"
            ))
        
        return results

    async def test_performance(self) -> List[TestResult]:
        """Test template expansion performance"""
        logging.info("Testing performance...")
        results = []
        
        # Performance test parameters
        target_expansion_time = 100  # ms
        target_selection_time = 10   # ms
        
        # Test expansion performance
        for template_name in ["workflow_default", "workflow_hotfix", "workflow_milestone_pass"]:
            times = []
            
            for i in range(5):  # Run 5 times for average
                start_time = time.time()
                
                try:
                    result = await self.template_service.expand_template(
                        original_description=f"Performance test task {i}",
                        template_name=template_name
                    )
                    
                    duration = (time.time() - start_time) * 1000
                    times.append(duration)
                    
                except Exception as e:
                    logging.error(f"Performance test failed for {template_name}: {e}")
                    break
            
            if times:
                avg_time = sum(times) / len(times)
                max_time = max(times)
                
                success = avg_time <= target_expansion_time
                
                results.append(TestResult(
                    name=f"performance_expansion_{template_name}",
                    test_type="performance",
                    success=success,
                    duration_ms=avg_time,
                    details={
                        "average_time": avg_time,
                        "max_time": max_time,
                        "target_time": target_expansion_time,
                        "test_runs": len(times)
                    },
                    error_message=None if success else f"Average time {avg_time:.1f}ms exceeds target {target_expansion_time}ms"
                ))
        
        # Test selection performance
        selection_times = []
        for task in self.test_tasks[:3]:  # Test first 3 tasks
            start_time = time.time()
            
            try:
                template_context_selector.select_template(task["description"], task["title"])
                duration = (time.time() - start_time) * 1000
                selection_times.append(duration)
            except Exception as e:
                logging.error(f"Selection performance test failed: {e}")
        
        if selection_times:
            avg_selection_time = sum(selection_times) / len(selection_times)
            success = avg_selection_time <= target_selection_time
            
            results.append(TestResult(
                name="performance_selection",
                test_type="performance",
                success=success,
                duration_ms=avg_selection_time,
                details={
                    "average_time": avg_selection_time,
                    "target_time": target_selection_time,
                    "test_runs": len(selection_times)
                },
                error_message=None if success else f"Average selection time {avg_selection_time:.1f}ms exceeds target {target_selection_time}ms"
            ))
        
        return results

    def generate_report(self, test_suite: TestSuite) -> str:
        """Generate a comprehensive test report"""
        report = []
        report.append("=" * 60)
        report.append("TEMPLATE INJECTION SYSTEM TEST REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Summary
        report.append("SUMMARY:")
        report.append(f"  Total Tests: {test_suite.total_tests}")
        report.append(f"  Passed: {test_suite.passed_tests}")
        report.append(f"  Failed: {test_suite.failed_tests}")
        report.append(f"  Success Rate: {(test_suite.passed_tests/test_suite.total_tests)*100:.1f}%")
        report.append(f"  Total Duration: {test_suite.total_duration_ms:.1f}ms")
        report.append("")
        
        # Group results by test type
        test_types = {}
        for result in test_suite.results:
            if result.test_type not in test_types:
                test_types[result.test_type] = []
            test_types[result.test_type].append(result)
        
        # Report by test type
        for test_type, results in test_types.items():
            passed = sum(1 for r in results if r.success)
            total = len(results)
            
            report.append(f"{test_type.upper()} TESTS ({passed}/{total} passed):")
            report.append("-" * 40)
            
            for result in results:
                status = "PASS" if result.success else "FAIL"
                report.append(f"  [{status}] {result.name} ({result.duration_ms:.1f}ms)")
                
                if not result.success and result.error_message:
                    report.append(f"    Error: {result.error_message}")
                
                if result.details:
                    for key, value in result.details.items():
                        report.append(f"    {key}: {value}")
            
            report.append("")
        
        return "\n".join(report)


async def main():
    """Main test execution function"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    runner = TemplateTestRunner()
    
    # Setup test environment
    if not await runner.setup():
        logging.error("Failed to setup test environment")
        sys.exit(1)
    
    # Run all tests
    test_suite = await runner.run_all_tests()
    
    # Generate and display report
    report = runner.generate_report(test_suite)
    print(report)
    
    # Save report to file
    report_file = Path(__file__).parent.parent.parent / "reports" / f"template_test_report_{int(time.time())}.txt"
    report_file.parent.mkdir(exist_ok=True)
    report_file.write_text(report)
    
    logging.info(f"Test report saved to: {report_file}")
    
    # Exit with appropriate code
    sys.exit(0 if test_suite.failed_tests == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
