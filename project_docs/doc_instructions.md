TASK: Create comprehensive documentation for our codebase by analyzing each file systematically.

STEPS:
1. Create master index at /project_docs/index.md with navigation to all pages and components
2. For each page in /src/pages/, create documentation at /project_docs/pages/[filename].md
3. For each component in /src/components/, create documentation at /project_docs/components/[filename].md
4. For utility files, create documentation at /project_docs/utils/[filename].md
5. Use the exact template provided below for every documentation file

CRITICAL RULES:
- Only document what actually exists in the code
- Do not add, remove, or modify any functionality descriptions
- Include actual code snippets from the files
- List all props/parameters with their actual types from the code
- Verify all imports/exports are accurate

Use this exact template for each file: doc_template.md