# Test Code Extraction

This is a test document to verify code extraction functionality.

## Python Example

```python
def hello_world():
    """A simple hello world function."""
    print("Hello, World!")
    return "success"

class TestClass:
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        return f"Hello, {self.name}!"
```

## JavaScript Example

```javascript
function calculateSum(a, b) {
    return a + b;
}

const user = {
    name: "John",
    age: 30,
    greet: function() {
        console.log(`Hello, I'm ${this.name}`);
    }
};
```

## Bash Script

```bash
#!/bin/bash
echo "Starting deployment..."
docker build -t myapp .
docker run -d -p 8080:8080 myapp
echo "Deployment complete!"
```

## SQL Query

```sql
SELECT u.name, u.email, p.title
FROM users u
JOIN posts p ON u.id = p.user_id
WHERE u.active = true
ORDER BY p.created_at DESC;
```

This document contains multiple code blocks that should be extracted and stored in the archon_code_examples table.
