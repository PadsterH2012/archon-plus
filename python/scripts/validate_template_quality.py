#!/usr/bin/env python3
"""
Template Quality Validation Script

This script validates the quality and coherence of template expansions
by testing with various user task examples and analyzing the results.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from server.services.template_injection_service import (
    TemplateInjectionService,
    get_template_injection_service
)
from server.config.logfire_config import get_logger

logger = get_logger(__name__)


class TemplateQualityValidator:
    """Validates template expansion quality and coherence"""

    def __init__(self):
        self.template_service = None
        self.validation_results = []

    async def initialize(self):
        """Initialize the template service"""
        try:
            self.template_service = get_template_injection_service()
            logger.info("Template service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize template service: {e}")
            raise

    async def validate_template_quality(self, template_name: str = "workflow_default") -> Dict[str, Any]:
        """
        Validate the quality of a specific template
        
        Args:
            template_name: Name of the template to validate
            
        Returns:
            Dictionary with validation results
        """
        logger.info(f"Validating template quality for: {template_name}")
        
        # Test cases with various user task examples
        test_cases = [
            {
                "description": "Create a REST API endpoint for user authentication",
                "category": "backend_development",
                "complexity": "medium"
            },
            {
                "description": "Fix a memory leak in the image processing module",
                "category": "bug_fix",
                "complexity": "high"
            },
            {
                "description": "Add unit tests for the payment processing service",
                "category": "testing",
                "complexity": "low"
            },
            {
                "description": "Implement OAuth2 integration with Google and GitHub",
                "category": "integration",
                "complexity": "high"
            },
            {
                "description": "Update documentation for the new API endpoints",
                "category": "documentation",
                "complexity": "low"
            },
            {
                "description": "Optimize database queries for the user dashboard",
                "category": "performance",
                "complexity": "medium"
            },
            {
                "description": "Deploy the application to production environment",
                "category": "deployment",
                "complexity": "medium"
            },
            {
                "description": "Refactor the authentication middleware for better maintainability",
                "category": "refactoring",
                "complexity": "high"
            }
        ]
        
        validation_results = {
            "template_name": template_name,
            "timestamp": datetime.now().isoformat(),
            "test_cases": [],
            "overall_metrics": {},
            "issues_found": [],
            "recommendations": []
        }
        
        successful_expansions = 0
        total_expansion_time = 0
        
        for i, test_case in enumerate(test_cases):
            logger.info(f"Testing case {i+1}/{len(test_cases)}: {test_case['description'][:50]}...")
            
            try:
                # Expand the template
                response = await self.template_service.expand_task_description(
                    original_description=test_case["description"],
                    template_name=template_name,
                    context_data={"category": test_case["category"], "complexity": test_case["complexity"]}
                )
                
                if response.success:
                    successful_expansions += 1
                    total_expansion_time += response.result.expansion_time_ms
                    
                    # Analyze the expanded instructions
                    analysis = self._analyze_expansion_quality(
                        test_case["description"],
                        response.result.expanded_instructions,
                        test_case
                    )
                    
                    test_result = {
                        "test_case": test_case,
                        "success": True,
                        "expansion_time_ms": response.result.expansion_time_ms,
                        "expanded_length": len(response.result.expanded_instructions),
                        "analysis": analysis
                    }
                else:
                    test_result = {
                        "test_case": test_case,
                        "success": False,
                        "error": response.error,
                        "analysis": {"quality_score": 0, "issues": ["Expansion failed"]}
                    }
                    validation_results["issues_found"].append(f"Expansion failed for: {test_case['description']}")
                
                validation_results["test_cases"].append(test_result)
                
            except Exception as e:
                logger.error(f"Error testing case {i+1}: {e}")
                test_result = {
                    "test_case": test_case,
                    "success": False,
                    "error": str(e),
                    "analysis": {"quality_score": 0, "issues": ["Exception during expansion"]}
                }
                validation_results["test_cases"].append(test_result)
                validation_results["issues_found"].append(f"Exception for: {test_case['description']}")
        
        # Calculate overall metrics
        validation_results["overall_metrics"] = {
            "success_rate": successful_expansions / len(test_cases),
            "average_expansion_time_ms": total_expansion_time / successful_expansions if successful_expansions > 0 else 0,
            "average_quality_score": sum(tc["analysis"]["quality_score"] for tc in validation_results["test_cases"]) / len(test_cases),
            "total_issues": sum(len(tc["analysis"]["issues"]) for tc in validation_results["test_cases"])
        }
        
        # Generate recommendations
        validation_results["recommendations"] = self._generate_recommendations(validation_results)
        
        return validation_results

    def _analyze_expansion_quality(self, original_description: str, expanded_instructions: str, test_case: Dict) -> Dict[str, Any]:
        """
        Analyze the quality of expanded instructions
        
        Args:
            original_description: Original user task description
            expanded_instructions: Expanded instructions from template
            test_case: Test case metadata
            
        Returns:
            Analysis results with quality score and issues
        """
        analysis = {
            "quality_score": 0,
            "issues": [],
            "strengths": [],
            "metrics": {}
        }
        
        # Check if original task is preserved
        if original_description.lower() in expanded_instructions.lower():
            analysis["quality_score"] += 20
            analysis["strengths"].append("Original task preserved")
        else:
            analysis["issues"].append("Original task not found in expanded instructions")
        
        # Check instruction structure and coherence
        lines = expanded_instructions.split('\n')
        non_empty_lines = [line.strip() for line in lines if line.strip()]
        
        analysis["metrics"]["total_lines"] = len(lines)
        analysis["metrics"]["instruction_lines"] = len(non_empty_lines)
        analysis["metrics"]["character_count"] = len(expanded_instructions)
        
        # Check for reasonable length
        if 500 <= len(expanded_instructions) <= 5000:
            analysis["quality_score"] += 15
            analysis["strengths"].append("Appropriate instruction length")
        else:
            analysis["issues"].append(f"Instruction length ({len(expanded_instructions)} chars) may be too short or too long")
        
        # Check for structured content
        if any(keyword in expanded_instructions.lower() for keyword in ["step", "1.", "2.", "3.", "•", "-"]):
            analysis["quality_score"] += 15
            analysis["strengths"].append("Contains structured steps")
        else:
            analysis["issues"].append("Instructions lack clear structure or steps")
        
        # Check for preparation/setup instructions
        if any(keyword in expanded_instructions.lower() for keyword in ["before", "prepare", "setup", "review", "check"]):
            analysis["quality_score"] += 10
            analysis["strengths"].append("Includes preparation steps")
        else:
            analysis["issues"].append("Missing preparation or setup instructions")
        
        # Check for testing/validation instructions
        if any(keyword in expanded_instructions.lower() for keyword in ["test", "verify", "validate", "check"]):
            analysis["quality_score"] += 15
            analysis["strengths"].append("Includes testing/validation steps")
        else:
            analysis["issues"].append("Missing testing or validation instructions")
        
        # Check for completion/follow-up instructions
        if any(keyword in expanded_instructions.lower() for keyword in ["commit", "deploy", "review", "document"]):
            analysis["quality_score"] += 10
            analysis["strengths"].append("Includes completion steps")
        else:
            analysis["issues"].append("Missing completion or follow-up instructions")
        
        # Check for tool references
        tool_keywords = ["view", "str-replace-editor", "launch-process", "homelab-vault"]
        tools_mentioned = sum(1 for tool in tool_keywords if tool in expanded_instructions.lower())
        if tools_mentioned > 0:
            analysis["quality_score"] += min(15, tools_mentioned * 5)
            analysis["strengths"].append(f"References {tools_mentioned} relevant tools")
        else:
            analysis["issues"].append("No tool references found")
        
        # Check for redundancy or repetition
        words = expanded_instructions.lower().split()
        unique_words = set(words)
        if len(unique_words) / len(words) > 0.7:  # Good word diversity
            analysis["quality_score"] += 10
            analysis["strengths"].append("Good word diversity, minimal redundancy")
        else:
            analysis["issues"].append("High word repetition detected")
        
        # Ensure quality score is within bounds
        analysis["quality_score"] = min(100, max(0, analysis["quality_score"]))
        
        return analysis

    def _generate_recommendations(self, validation_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        metrics = validation_results["overall_metrics"]
        
        if metrics["success_rate"] < 0.9:
            recommendations.append("Improve template reliability - some expansions are failing")
        
        if metrics["average_expansion_time_ms"] > 100:
            recommendations.append("Optimize template expansion performance - exceeding 100ms target")
        
        if metrics["average_quality_score"] < 70:
            recommendations.append("Improve template quality - average score below 70")
        
        if metrics["total_issues"] > len(validation_results["test_cases"]) * 2:
            recommendations.append("Address common quality issues found across test cases")
        
        # Analyze common issues
        all_issues = []
        for test_case in validation_results["test_cases"]:
            all_issues.extend(test_case["analysis"]["issues"])
        
        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        common_issues = [issue for issue, count in issue_counts.items() if count >= 3]
        for issue in common_issues:
            recommendations.append(f"Address common issue: {issue}")
        
        if not recommendations:
            recommendations.append("Template quality is good - no major issues found")
        
        return recommendations

    async def run_validation(self, template_names: List[str] = None) -> Dict[str, Any]:
        """
        Run complete template quality validation
        
        Args:
            template_names: List of template names to validate (default: ["workflow_default"])
            
        Returns:
            Complete validation report
        """
        if template_names is None:
            template_names = ["workflow_default"]
        
        await self.initialize()
        
        validation_report = {
            "validation_timestamp": datetime.now().isoformat(),
            "templates_validated": len(template_names),
            "template_results": {},
            "summary": {}
        }
        
        for template_name in template_names:
            logger.info(f"Validating template: {template_name}")
            try:
                results = await self.validate_template_quality(template_name)
                validation_report["template_results"][template_name] = results
            except Exception as e:
                logger.error(f"Failed to validate template {template_name}: {e}")
                validation_report["template_results"][template_name] = {
                    "error": str(e),
                    "success": False
                }
        
        # Generate summary
        successful_templates = [name for name, result in validation_report["template_results"].items() 
                              if result.get("overall_metrics", {}).get("success_rate", 0) > 0.8]
        
        validation_report["summary"] = {
            "templates_passed": len(successful_templates),
            "templates_failed": len(template_names) - len(successful_templates),
            "overall_success": len(successful_templates) == len(template_names)
        }
        
        return validation_report


async def main():
    """Main function to run template quality validation"""
    validator = TemplateQualityValidator()
    
    try:
        # Run validation for default template
        report = await validator.run_validation(["workflow_default"])
        
        # Print results
        print("\n" + "="*60)
        print("TEMPLATE QUALITY VALIDATION REPORT")
        print("="*60)
        
        for template_name, results in report["template_results"].items():
            if "error" in results:
                print(f"\n❌ {template_name}: FAILED")
                print(f"   Error: {results['error']}")
                continue
                
            metrics = results["overall_metrics"]
            print(f"\n✅ {template_name}: PASSED")
            print(f"   Success Rate: {metrics['success_rate']:.1%}")
            print(f"   Average Quality Score: {metrics['average_quality_score']:.1f}/100")
            print(f"   Average Expansion Time: {metrics['average_expansion_time_ms']:.1f}ms")
            print(f"   Total Issues: {metrics['total_issues']}")
            
            if results["recommendations"]:
                print("   Recommendations:")
                for rec in results["recommendations"]:
                    print(f"   - {rec}")
        
        print(f"\n📊 Summary:")
        print(f"   Templates Passed: {report['summary']['templates_passed']}")
        print(f"   Templates Failed: {report['summary']['templates_failed']}")
        print(f"   Overall Success: {'✅' if report['summary']['overall_success'] else '❌'}")
        
        # Save detailed report
        report_file = Path(__file__).parent / "template_quality_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        # Exit with appropriate code
        sys.exit(0 if report['summary']['overall_success'] else 1)
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        print(f"\n❌ Validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
