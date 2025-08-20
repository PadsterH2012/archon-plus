#!/usr/bin/env python3
"""
Validate Default Template Script

This script validates the default workflow template and its components
to ensure they work correctly for template injection.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from server.services.template_injection_service import TemplateInjectionService
from server.models.template_injection_models import TemplateExpansionRequest


async def validate_template_expansion():
    """Test template expansion with sample user tasks."""
    
    print("🔍 VALIDATING DEFAULT TEMPLATE EXPANSION")
    print("=" * 50)
    
    # Sample user tasks to test with
    test_tasks = [
        "Implement OAuth2 authentication with Google provider",
        "Create REST API endpoint for user management", 
        "Add unit tests for payment processing module",
        "Fix bug in email notification system",
        "Deploy application to production environment"
    ]
    
    try:
        # Create template injection service
        service = TemplateInjectionService()
        print("✅ TemplateInjectionService created successfully")
        
        # Test each sample task
        for i, task in enumerate(test_tasks, 1):
            print(f"\n📋 TEST {i}: {task}")
            print("-" * 40)
            
            try:
                # Expand the task description
                result = await service.expand_task_description(
                    original_description=task,
                    template_name="workflow_default"
                )
                
                if result.success and result.result:
                    expansion = result.result
                    print(f"✅ Expansion successful")
                    print(f"   Original length: {len(task)} chars")
                    print(f"   Expanded length: {len(expansion.expanded_instructions)} chars")
                    print(f"   Expansion time: {expansion.expansion_time_ms}ms")
                    print(f"   Template: {expansion.template_name}")
                    
                    # Validate that user task is preserved
                    if task in expansion.expanded_instructions:
                        print(f"   ✅ User task preserved in expansion")
                    else:
                        print(f"   ❌ User task NOT found in expansion")
                        return False
                    
                    # Check for key components
                    expected_components = [
                        "homelab environment",
                        "coding standards", 
                        "naming conventions",
                        "testing strategy",
                        "documentation",
                        "create tests",
                        "test locally",
                        "commit",
                        "jenkins",
                        "review"
                    ]
                    
                    found_components = []
                    for component in expected_components:
                        if component.lower() in expansion.expanded_instructions.lower():
                            found_components.append(component)
                    
                    print(f"   ✅ Found {len(found_components)}/{len(expected_components)} expected components")
                    
                    if len(found_components) < len(expected_components) * 0.8:  # 80% threshold
                        print(f"   ⚠️  Missing components: {set(expected_components) - set(found_components)}")
                
                else:
                    print(f"   ❌ Expansion failed: {result.error}")
                    return False
                    
            except Exception as e:
                print(f"   ❌ Exception during expansion: {e}")
                return False
        
        print(f"\n🎉 ALL TEMPLATE EXPANSION TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create template service: {e}")
        return False


async def validate_template_components():
    """Validate individual template components."""
    
    print(f"\n🧩 VALIDATING TEMPLATE COMPONENTS")
    print("=" * 50)
    
    expected_components = [
        "group::understand_homelab_env",
        "group::guidelines_coding", 
        "group::naming_conventions",
        "group::testing_strategy",
        "group::documentation_strategy",
        "group::create_tests",
        "group::test_locally", 
        "group::commit_push_to_git",
        "group::check_jenkins_build",
        "group::send_task_to_review"
    ]
    
    try:
        service = TemplateInjectionService()
        
        for component_name in expected_components:
            print(f"\n🔍 Testing component: {component_name}")
            
            try:
                component = await service.get_component(component_name)
                
                if component:
                    print(f"   ✅ Component found")
                    print(f"   Type: {component.component_type}")
                    print(f"   Category: {component.category}")
                    print(f"   Duration: {component.estimated_duration} min")
                    print(f"   Priority: {component.priority}")
                    print(f"   Instruction length: {len(component.instruction_text)} chars")
                    
                    # Validate instruction quality
                    if len(component.instruction_text) < 50:
                        print(f"   ⚠️  Instruction text seems too short")
                    elif len(component.instruction_text) > 2000:
                        print(f"   ⚠️  Instruction text seems too long")
                    else:
                        print(f"   ✅ Instruction length appropriate")
                        
                    # Check for required tools
                    if component.required_tools:
                        print(f"   ✅ Required tools: {component.required_tools}")
                    else:
                        print(f"   ℹ️  No required tools specified")
                        
                else:
                    print(f"   ❌ Component not found")
                    return False
                    
            except Exception as e:
                print(f"   ❌ Error retrieving component: {e}")
                return False
        
        print(f"\n🎉 ALL COMPONENT VALIDATION TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to validate components: {e}")
        return False


async def validate_workflow_template():
    """Validate the workflow template definition."""
    
    print(f"\n📋 VALIDATING WORKFLOW TEMPLATE")
    print("=" * 50)
    
    try:
        service = TemplateInjectionService()
        
        # Get the workflow template
        template_response = await service.get_template("workflow_default")
        
        if template_response.success and template_response.template:
            template = template_response.template
            print(f"✅ Template found: {template.name}")
            print(f"   Title: {template.title}")
            print(f"   Type: {template.template_type}")
            print(f"   Category: {template.category}")
            
            # Validate template data
            template_data = template.template_data
            if "template_content" in template_data:
                content = template_data["template_content"]
                print(f"   ✅ Template content found ({len(content)} chars)")
                
                # Check for USER_TASK placeholder
                if "{{USER_TASK}}" in content:
                    print(f"   ✅ USER_TASK placeholder found")
                else:
                    print(f"   ❌ USER_TASK placeholder missing")
                    return False
                
                # Count component placeholders
                import re
                placeholders = re.findall(r'\{\{([^}]+)\}\}', content)
                component_placeholders = [p for p in placeholders if p.startswith("group::")]
                print(f"   ✅ Found {len(component_placeholders)} component placeholders")
                
                # Validate template
                is_valid = await service.validate_template(template)
                if is_valid:
                    print(f"   ✅ Template validation passed")
                else:
                    print(f"   ❌ Template validation failed")
                    return False
                    
            else:
                print(f"   ❌ Template content missing")
                return False
                
        else:
            print(f"❌ Template not found: {template_response.error}")
            return False
        
        print(f"\n🎉 WORKFLOW TEMPLATE VALIDATION PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to validate workflow template: {e}")
        return False


async def main():
    """Run all validation tests."""
    
    print("🚀 STARTING TEMPLATE INJECTION VALIDATION")
    print("=" * 60)
    
    # Run all validation tests
    tests = [
        ("Workflow Template", validate_workflow_template),
        ("Template Components", validate_template_components), 
        ("Template Expansion", validate_template_expansion)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 RUNNING TEST: {test_name}")
        try:
            if await test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print(f"\n📊 VALIDATION SUMMARY")
    print("=" * 30)
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print(f"\n🎉 ALL VALIDATION TESTS PASSED!")
        print(f"✅ Default template is ready for production use!")
        return True
    else:
        print(f"\n❌ SOME VALIDATION TESTS FAILED!")
        print(f"⚠️  Template needs fixes before production use!")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
