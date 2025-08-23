TASK: Verify and Update Documentation Accuracy
Documentation Location: /project_docs/index.md and related files
Frequency: [Weekly/Monthly/Quarterly - as specified]
Agent Responsibility: Systematic verification of documentation against actual codebase

STEP 1: Initial Assessment
1.1 Read Master Documentation Index

 Read /project_docs/index.md completely
 List all documented components/pages/utilities
 Note the last update timestamps for each section
 Identify documentation structure and organization

1.2 Identify Recently Modified Code

 Check git history for files modified since last documentation review
 List components that have been changed but may not have updated docs
 Prioritize review order based on:

Recent modifications
Critical/core components
Frequently used utilities



Output: Create prioritized list of components to verify

STEP 2: Component-by-Component Verification
For each component/page in the documentation:
2.1 Read Current Documentation

 Read existing documentation for the component
 Note all props, methods, dependencies, and examples listed

2.2 Read Actual Code File

 Locate and read the actual component/page source code
 Extract actual props/parameters with their types
 Identify all imports and exports
 List all functions and methods defined

2.3 Compare Documentation vs Reality

 Props/Parameters: Do documented props match actual props?

Check names, types, required/optional status, default values
Note any missing or extra props in documentation


 Functions/Methods: Are all public functions documented?
 Dependencies: Do import/export lists match actual code?
 Usage Examples: Do examples use correct prop names and values?
 File Paths: Are documented file paths accurate?

2.4 Test Documentation Examples

 Copy usage examples from documentation
 Verify examples would actually work with current code
 Check if prop combinations in examples are valid
 Ensure import statements in examples are correct

Output: For each component, create accuracy report

STEP 3: Cross-Reference Verification
3.1 Check Component Relationships

 For each component, verify its relationships with other components
 Check if "Related Files" sections are accurate
 Verify parent-child component relationships documented correctly
 Ensure utility function usage is properly documented

3.2 Verify API Integration Points

 Check documented API endpoints against actual API calls in code
 Verify request/response formats documented correctly
 Ensure error handling patterns match implementation

3.3 Check Navigation and Links

 Verify all internal documentation links work
 Check that master index links to all component docs
 Ensure file path references are accurate

Output: Cross-reference accuracy report

STEP 4: Update Documentation
4.1 Fix Identified Inaccuracies

 Update incorrect prop information
 Fix wrong file paths or component names
 Correct invalid usage examples
 Update dependency lists
 Add missing functions or props

4.2 Add Missing Documentation

 Document any components found in code but not in docs
 Add missing props or methods discovered
 Create documentation for new utility functions
 Update master index with any new components

4.3 Remove Obsolete Documentation

 Remove documentation for deleted components
 Clean up references to removed props or methods
 Update master index to remove deleted components
 Archive deprecated functionality documentation

CRITICAL: Only remove documentation if you can confirm the code was actually deleted

STEP 5: Validation and Quality Check
5.1 Test All Examples

 Copy each usage example from updated documentation
 Verify examples work with current codebase
 Test edge cases mentioned in documentation
 Ensure all prop combinations shown actually work

5.2 Verify Documentation Structure

 Check that master index is complete and organized
 Ensure consistent formatting across all documentation files
 Verify all required sections are present in each doc
 Check that timestamps are updated

5.3 Cross-Reference Final Check

 Verify all "Related Files" sections are accurate
 Check that component dependencies are correctly documented
 Ensure no broken internal links remain

Output: Validation report confirming accuracy

STEP 6: Generate Accuracy Report
6.1 Summary Report
Create a report including:

 Total components reviewed: [number]
 Components with inaccuracies found: [number]
 Components with missing documentation: [number]
 Obsolete documentation removed: [number]
 Examples tested and verified: [number]

6.2 Detailed Findings
For each component with issues:

 Component name and file path
 Specific inaccuracies found
 Changes made to fix issues
 Confidence level in accuracy (High/Medium/Low)

6.3 Recommendations

 Components needing more detailed documentation
 Patterns of documentation drift identified
 Suggestions for preventing future inaccuracies
 Components that should be prioritized in next review

Output: Save report to /project_docs/accuracy_reports/[date]_accuracy_check.md

CRITICAL VERIFICATION RULES
❌ DO NOT:

Remove documentation without confirming code deletion
Make assumptions about component behavior
Update documentation based on what you think it should do
Skip testing examples that look complex

✅ ALWAYS:

Verify every claim in documentation against actual code
Test usage examples before marking them as accurate
Check file paths and component names exactly
Note confidence level when uncertain about interpretation

🔍 WHEN IN DOUBT:

Mark documentation section as "NEEDS REVIEW" rather than guessing
Include specific questions about unclear functionality
Flag for human review rather than making assumptions