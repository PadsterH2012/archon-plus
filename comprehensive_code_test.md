# Comprehensive Code Extraction Test

This document contains multiple code blocks with substantial length to test the fixed code extraction functionality.

## Large Bash Directory Tree (400+ characters)

```bash
# Complete project structure for a modern web application
enterprise-web-app/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Modal.tsx
│   │   │   │   ├── Input.tsx
│   │   │   │   └── Loading.tsx
│   │   │   ├── layout/
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Footer.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── Navigation.tsx
│   │   │   └── features/
│   │   │       ├── auth/
│   │   │       ├── dashboard/
│   │   │       ├── settings/
│   │   │       └── reports/
│   │   ├── services/
│   │   │   ├── api/
│   │   │   │   ├── auth.ts
│   │   │   │   ├── users.ts
│   │   │   │   ├── data.ts
│   │   │   │   └── config.ts
│   │   │   ├── utils/
│   │   │   │   ├── helpers.ts
│   │   │   │   ├── constants.ts
│   │   │   │   ├── validators.ts
│   │   │   │   └── formatters.ts
│   │   │   └── hooks/
│   │   │       ├── useAuth.ts
│   │   │       ├── useApi.ts
│   │   │       └── useLocalStorage.ts
│   │   ├── styles/
│   │   │   ├── globals.css
│   │   │   ├── components.css
│   │   │   └── themes/
│   │   └── types/
│   │       ├── api.ts
│   │       ├── user.ts
│   │       └── common.ts
│   ├── public/
│   │   ├── images/
│   │   ├── icons/
│   │   └── favicon.ico
│   ├── tests/
│   │   ├── unit/
│   │   │   ├── components/
│   │   │   ├── services/
│   │   │   └── utils/
│   │   ├── integration/
│   │   │   ├── api/
│   │   │   └── workflows/
│   │   └── e2e/
│   │       ├── auth.spec.ts
│   │       ├── dashboard.spec.ts
│   │       └── settings.spec.ts
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── README.md
├── backend/
│   ├── src/
│   │   ├── controllers/
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── data.py
│   │   │   └── health.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── session.py
│   │   │   └── base.py
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── data_service.py
│   │   │   ├── email_service.py
│   │   │   └── cache_service.py
│   │   ├── utils/
│   │   │   ├── helpers.py
│   │   │   ├── validators.py
│   │   │   ├── decorators.py
│   │   │   └── exceptions.py
│   │   ├── config/
│   │   │   ├── settings.py
│   │   │   ├── database.py
│   │   │   └── logging.py
│   │   └── migrations/
│   │       ├── 001_initial.py
│   │       ├── 002_add_users.py
│   │       └── 003_add_sessions.py
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── fixtures/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── README.md
├── infrastructure/
│   ├── docker/
│   │   ├── docker-compose.yml
│   │   ├── docker-compose.prod.yml
│   │   └── nginx/
│   ├── kubernetes/
│   │   ├── deployments/
│   │   ├── services/
│   │   └── ingress/
│   └── terraform/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
├── docs/
│   ├── api/
│   │   ├── authentication.md
│   │   ├── endpoints.md
│   │   └── examples.md
│   ├── deployment/
│   │   ├── local.md
│   │   ├── staging.md
│   │   └── production.md
│   └── development/
│       ├── setup.md
│       ├── guidelines.md
│       └── testing.md
├── scripts/
│   ├── build.sh
│   ├── deploy.sh
│   ├── test.sh
│   └── setup.sh
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── cd.yml
│       └── security.yml
├── .gitignore
├── README.md
├── LICENSE
└── CHANGELOG.md
```

## Comprehensive Python Code Example (500+ characters)

```python
"""
Advanced code extraction and processing system for handling multiple content types.
This module provides comprehensive functionality for extracting, validating, and storing
code examples from various document formats including markdown, HTML, and plain text.
"""

import re
import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import hashlib
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CodeLanguage(Enum):
    """Enumeration of supported programming languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    BASH = "bash"
    SQL = "sql"
    HTML = "html"
    CSS = "css"
    JSON = "json"
    YAML = "yaml"
    MARKDOWN = "markdown"
    UNKNOWN = "unknown"

@dataclass
class CodeBlock:
    """Represents a single code block with metadata."""
    content: str
    language: CodeLanguage
    start_line: int
    end_line: int
    char_count: int = field(init=False)
    word_count: int = field(init=False)
    hash_value: str = field(init=False)
    
    def __post_init__(self):
        """Calculate derived fields after initialization."""
        self.char_count = len(self.content)
        self.word_count = len(self.content.split())
        self.hash_value = hashlib.md5(self.content.encode()).hexdigest()

@dataclass
class ExtractionResult:
    """Results from code extraction operation."""
    code_blocks: List[CodeBlock]
    total_blocks: int = field(init=False)
    total_characters: int = field(init=False)
    languages_found: List[CodeLanguage] = field(init=False)
    
    def __post_init__(self):
        """Calculate summary statistics."""
        self.total_blocks = len(self.code_blocks)
        self.total_characters = sum(block.char_count for block in self.code_blocks)
        self.languages_found = list(set(block.language for block in self.code_blocks))

class AdvancedCodeExtractor:
    """
    Advanced code extraction system with support for multiple formats and languages.
    
    Features:
    - Multi-format support (Markdown, HTML, plain text)
    - Language detection and validation
    - Configurable filtering and validation rules
    - Async processing for large documents
    - Comprehensive error handling and logging
    """
    
    def __init__(self, min_length: int = 250, max_length: int = 5000):
        """
        Initialize the code extractor with configuration parameters.
        
        Args:
            min_length: Minimum character count for valid code blocks
            max_length: Maximum character count for valid code blocks
        """
        self.min_length = min_length
        self.max_length = max_length
        self.patterns = self._compile_patterns()
        logger.info(f"Initialized AdvancedCodeExtractor with min_length={min_length}, max_length={max_length}")
    
    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for different code block formats."""
        return {
            'markdown_fenced': re.compile(r'```(\w*)\n(.*?)```', re.DOTALL),
            'markdown_indented': re.compile(r'^( {4}|\t)(.+)$', re.MULTILINE),
            'html_pre': re.compile(r'<pre[^>]*><code[^>]*>(.*?)</code></pre>', re.DOTALL),
            'html_code': re.compile(r'<code[^>]*>(.*?)</code>', re.DOTALL),
        }
    
    def detect_language(self, code_content: str, declared_language: str = "") -> CodeLanguage:
        """
        Detect programming language from code content and declared language.
        
        Args:
            code_content: The actual code content to analyze
            declared_language: Language declared in code block (if any)
            
        Returns:
            Detected CodeLanguage enum value
        """
        # First try declared language
        if declared_language:
            try:
                return CodeLanguage(declared_language.lower())
            except ValueError:
                pass
        
        # Fallback to content-based detection
        content_lower = code_content.lower()
        
        # Python indicators
        if any(keyword in content_lower for keyword in ['def ', 'import ', 'from ', 'class ', '__init__']):
            return CodeLanguage.PYTHON
        
        # JavaScript/TypeScript indicators
        if any(keyword in content_lower for keyword in ['function', 'const ', 'let ', 'var ', '=>']):
            if 'interface ' in content_lower or ': string' in content_lower:
                return CodeLanguage.TYPESCRIPT
            return CodeLanguage.JAVASCRIPT
        
        # SQL indicators
        if any(keyword in content_lower for keyword in ['select ', 'insert ', 'update ', 'delete ', 'create table']):
            return CodeLanguage.SQL
        
        # Bash indicators
        if any(indicator in content_lower for indicator in ['#!/bin/bash', '#!/bin/sh', 'echo ', 'cd ', 'ls ']):
            return CodeLanguage.BASH
        
        return CodeLanguage.UNKNOWN
    
    async def extract_from_markdown(self, content: str) -> ExtractionResult:
        """
        Extract code blocks from markdown content.
        
        Args:
            content: Markdown content to process
            
        Returns:
            ExtractionResult containing extracted code blocks
        """
        code_blocks = []
        
        # Extract fenced code blocks
        for match in self.patterns['markdown_fenced'].finditer(content):
            declared_lang = match.group(1)
            code_content = match.group(2).strip()
            
            if self.min_length <= len(code_content) <= self.max_length:
                language = self.detect_language(code_content, declared_lang)
                start_line = content[:match.start()].count('\n') + 1
                end_line = content[:match.end()].count('\n') + 1
                
                code_block = CodeBlock(
                    content=code_content,
                    language=language,
                    start_line=start_line,
                    end_line=end_line
                )
                code_blocks.append(code_block)
                logger.debug(f"Extracted {language.value} code block ({len(code_content)} chars)")
        
        return ExtractionResult(code_blocks=code_blocks)
    
    async def process_document(self, file_path: Union[str, Path]) -> ExtractionResult:
        """
        Process a document file and extract all code blocks.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            ExtractionResult containing all extracted code blocks
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")
        
        logger.info(f"Processing document: {path.name}")
        
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Determine processing method based on file extension
        if path.suffix.lower() in ['.md', '.markdown']:
            return await self.extract_from_markdown(content)
        else:
            # Fallback to markdown processing for other text files
            return await self.extract_from_markdown(content)
    
    def generate_summary_report(self, result: ExtractionResult) -> Dict[str, Any]:
        """
        Generate a comprehensive summary report of extraction results.
        
        Args:
            result: ExtractionResult to summarize
            
        Returns:
            Dictionary containing summary statistics and details
        """
        language_stats = {}
        for block in result.code_blocks:
            lang = block.language.value
            if lang not in language_stats:
                language_stats[lang] = {'count': 0, 'total_chars': 0}
            language_stats[lang]['count'] += 1
            language_stats[lang]['total_chars'] += block.char_count
        
        return {
            'total_blocks': result.total_blocks,
            'total_characters': result.total_characters,
            'languages_found': [lang.value for lang in result.languages_found],
            'language_statistics': language_stats,
            'average_block_size': result.total_characters / result.total_blocks if result.total_blocks > 0 else 0,
            'extraction_timestamp': asyncio.get_event_loop().time()
        }

# Example usage and testing
async def main():
    """Main function demonstrating the code extraction system."""
    extractor = AdvancedCodeExtractor(min_length=100, max_length=10000)
    
    # Example markdown content
    sample_content = '''
    # Sample Document
    
    Here's some Python code:
    
    ```python
    def hello_world():
        print("Hello, World!")
        return True
    ```
    
    And some JavaScript:
    
    ```javascript
    function greet(name) {
        console.log(`Hello, ${name}!`);
        return name.toUpperCase();
    }
    ```
    '''
    
    # Extract code blocks
    result = await extractor.extract_from_markdown(sample_content)
    
    # Generate report
    report = extractor.generate_summary_report(result)
    
    print("Code Extraction Report:")
    print(json.dumps(report, indent=2))
    
    for i, block in enumerate(result.code_blocks):
        print(f"\nBlock {i+1}:")
        print(f"  Language: {block.language.value}")
        print(f"  Lines: {block.start_line}-{block.end_line}")
        print(f"  Characters: {block.char_count}")
        print(f"  Hash: {block.hash_value[:8]}...")

if __name__ == "__main__":
    asyncio.run(main())
```

## Complex SQL Database Schema (400+ characters)

```sql
-- Comprehensive database schema for enterprise application
-- This schema supports user management, content organization, and analytics

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create custom types
CREATE TYPE user_role AS ENUM ('admin', 'moderator', 'user', 'guest');
CREATE TYPE content_status AS ENUM ('draft', 'published', 'archived', 'deleted');
CREATE TYPE notification_type AS ENUM ('info', 'warning', 'error', 'success');

-- Users table with comprehensive profile information
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role user_role DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    profile_image_url TEXT,
    bio TEXT,
    location VARCHAR(255),
    website_url TEXT,
    social_links JSONB DEFAULT '{}',
    preferences JSONB DEFAULT '{}',
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User sessions for authentication management
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    refresh_token VARCHAR(255) UNIQUE,
    ip_address INET,
    user_agent TEXT,
    is_active BOOLEAN DEFAULT true,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Content categories for organization
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    parent_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Main content table
CREATE TABLE content (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    excerpt TEXT,
    author_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    category_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    status content_status DEFAULT 'draft',
    featured BOOLEAN DEFAULT false,
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    tags TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Comments system
CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID NOT NULL REFERENCES content(id) ON DELETE CASCADE,
    author_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES comments(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    is_approved BOOLEAN DEFAULT false,
    like_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User notifications
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type notification_type NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    data JSONB DEFAULT '{}',
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Analytics events
CREATE TABLE analytics_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    referrer TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_categories_parent_id ON categories(parent_id);
CREATE INDEX idx_categories_slug ON categories(slug);
CREATE INDEX idx_content_author_id ON content(author_id);
CREATE INDEX idx_content_category_id ON content(category_id);
CREATE INDEX idx_content_status ON content(status);
CREATE INDEX idx_content_published_at ON content(published_at);
CREATE INDEX idx_content_tags ON content USING GIN(tags);
CREATE INDEX idx_comments_content_id ON comments(content_id);
CREATE INDEX idx_comments_author_id ON comments(author_id);
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_analytics_events_user_id ON analytics_events(user_id);
CREATE INDEX idx_analytics_events_type ON analytics_events(event_type);

-- Create full-text search indexes
CREATE INDEX idx_content_search ON content USING GIN(to_tsvector('english', title || ' ' || content));
CREATE INDEX idx_users_search ON users USING GIN(to_tsvector('english', username || ' ' || first_name || ' ' || last_name));

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_categories_updated_at BEFORE UPDATE ON categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_content_updated_at BEFORE UPDATE ON content
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_comments_updated_at BEFORE UPDATE ON comments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data
INSERT INTO users (username, email, password_hash, first_name, last_name, role) VALUES
('admin', 'admin@example.com', crypt('admin123', gen_salt('bf')), 'System', 'Administrator', 'admin'),
('john_doe', 'john@example.com', crypt('password123', gen_salt('bf')), 'John', 'Doe', 'user'),
('jane_smith', 'jane@example.com', crypt('password123', gen_salt('bf')), 'Jane', 'Smith', 'moderator');

INSERT INTO categories (name, slug, description) VALUES
('Technology', 'technology', 'Articles about technology and programming'),
('Business', 'business', 'Business insights and strategies'),
('Lifestyle', 'lifestyle', 'Lifestyle and personal development content');

-- Grant appropriate permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;
```

This comprehensive test document contains multiple substantial code blocks that should all be extracted by the fixed code extraction system.
