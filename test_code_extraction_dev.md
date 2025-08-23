# Test Code Extraction for Dev Environment

This document tests the fixed code extraction functionality.

## Bash Directory Tree (Previously Filtered Out)

```bash
project-structure/
├── src/
│   ├── components/
│   │   ├── Button.tsx
│   │   └── Modal.tsx
│   ├── services/
│   │   ├── api.ts
│   │   └── auth.ts
│   └── utils/
│       ├── helpers.ts
│       └── constants.ts
├── tests/
│   ├── unit/
│   └── integration/
└── docs/
    ├── README.md
    └── API.md
```

## Python Code Example

```python
def extract_code_blocks(content: str) -> list:
    """Extract code blocks from markdown content."""
    import re
    
    pattern = r'```(\w*)\n(.*?)```'
    matches = re.findall(pattern, content, re.DOTALL)
    
    code_blocks = []
    for language, code in matches:
        if len(code.strip()) >= 250:  # Minimum length check
            code_blocks.append({
                'language': language or 'text',
                'code': code.strip(),
                'length': len(code.strip())
            })
    
    return code_blocks
```

## SQL Example

```sql
-- Create table for code examples
CREATE TABLE code_examples (
    id SERIAL PRIMARY KEY,
    language VARCHAR(50),
    content TEXT NOT NULL,
    source_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Insert sample data
INSERT INTO code_examples (language, content, source_url) 
VALUES ('python', 'def hello(): return "world"', 'test.md');
```

This document should now have its code blocks properly extracted!
