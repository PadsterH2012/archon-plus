# knowledgeBaseService

**File Path:** `archon-ui-main/src/services/knowledgeBaseService.ts`
**Last Updated:** 2025-01-22

## Purpose
Service class for managing knowledge base operations including CRUD operations, crawling, document upload, search, and real-time progress tracking.

## Props/Parameters
No props required - this is a service class with methods.

## Dependencies

### Imports
```javascript
// No explicit imports shown in the provided code
// Uses fetch API and standard JavaScript features
```

### Exports
```javascript
export interface KnowledgeItemMetadata;
export interface KnowledgeItem;
export interface KnowledgeItemsResponse;
export interface KnowledgeItemsFilter;
export interface CrawlRequest;
export interface UploadMetadata;
export interface SearchOptions;
export const knowledgeBaseService: KnowledgeBaseService;
```

## Key Functions/Methods
- **getKnowledgeItems**: Retrieves knowledge items with optional filtering and pagination
- **getAvailableTags**: Fetches all available tags from existing knowledge items
- **deleteKnowledgeItem**: Deletes a knowledge item by source ID
- **updateKnowledgeItem**: Updates knowledge item metadata
- **refreshKnowledgeItem**: Re-crawls a knowledge item to update its content
- **uploadDocument**: Uploads documents with metadata and progress tracking
- **crawlUrl**: Initiates URL crawling with specified parameters
- **getKnowledgeItemDetails**: Retrieves detailed information about a specific item
- **searchKnowledgeBase**: Performs search across the knowledge base
- **stopCrawl**: Cancels a running crawl operation
- **getCodeExamples**: Fetches code examples for a specific knowledge item

## Usage Example
```javascript
import { knowledgeBaseService } from '../services/knowledgeBaseService';

// Get knowledge items with filtering
const response = await knowledgeBaseService.getKnowledgeItems({
  knowledge_type: 'technical',
  tags: ['documentation'],
  page: 1,
  per_page: 20
});

// Start crawling a URL
const crawlResult = await knowledgeBaseService.crawlUrl({
  url: 'https://example.com',
  knowledge_type: 'technical',
  tags: ['api', 'documentation'],
  max_depth: 2
});

// Upload a document
const uploadResult = await knowledgeBaseService.uploadDocument(file, {
  knowledge_type: 'business',
  tags: ['policy', 'guidelines']
});
```

## State Management
No state management - stateless service class

## Side Effects
- **API requests**: Makes HTTP requests to backend knowledge API
- **Console logging**: Extensive logging for debugging and monitoring
- **File uploads**: Handles multipart form data for document uploads

## Related Files
- **Parent components:** KnowledgeBasePage, KnowledgeItemCard, KnowledgeTable
- **Child components:** None - this is a service layer
- **Shared utilities:** 
  - apiRequest function for HTTP requests
  - API_BASE_URL configuration

## Notes
- Singleton pattern - exports single instance for app-wide use
- Comprehensive error handling and logging
- Supports both URL crawling and file upload workflows
- Real-time progress tracking for long-running operations
- Flexible filtering and search capabilities
- RESTful API design with proper HTTP methods
- Type-safe interfaces for all data structures

---
*Auto-generated documentation - verify accuracy before use*
