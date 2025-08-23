{
  "document_type": "prp",
  "title": "VSCode Chat Bridge - IDE Integration Extension",
  "version": "1.0",
  "author": "prp-creator",
  "date": "2025-08-22",
  "status": "draft",

  "goal": "Create a VSCode extension that seamlessly integrates with Archon's existing agent chat system, enabling direct IDE-to-Archon communication using Socket.IO and SSE streaming for real-time AI assistance within the development environment.",

  "why": [
    "Enable developers to access Archon's AI agents directly from their IDE without context switching",
    "Leverage existing robust chat architecture (Socket.IO + SSE) for reliable real-time communication",
    "Provide contextual AI assistance with access to current file, project state, and Archon knowledge base",
    "Integrate with Archon's MCP tools for seamless project and task management from within VSCode",
    "Reduce friction in AI-assisted development workflows by eliminating external tool dependencies"
  ],

  "what": {
    "description": "A VSCode extension that creates a chat panel within the IDE, connecting to Archon's existing agent chat system via Socket.IO and SSE streaming. The extension will provide real-time AI assistance with full access to Archon's knowledge base, project management, and task orchestration capabilities.",
    "success_criteria": [
      "VSCode extension successfully connects to Archon's agent chat system",
      "Real-time streaming chat responses display within VSCode chat panel",
      "Extension can send current file context and project information to Archon agents",
      "Integration with Archon's MCP tools for project and task management from IDE",
      "Chat history persists across VSCode sessions",
      "Extension handles connection failures gracefully with automatic reconnection",
      "Performance impact on VSCode is minimal (<50ms response time for UI interactions)"
    ],
    "user_stories": [
      "As a developer, I want to ask questions about my current code file and get AI assistance without leaving VSCode",
      "As a project manager, I want to create and manage Archon tasks directly from my IDE while reviewing code",
      "As a team member, I want to access our shared knowledge base and documentation from within my development environment",
      "As a developer, I want to get real-time streaming responses from AI agents while maintaining my coding flow",
      "As a user, I want my chat history to persist so I can reference previous conversations across sessions"
    ]
  },

  "context": {
    "documentation": [
      {"source": "docs/docs/agent-chat.mdx", "why": "Existing agent chat architecture with Socket.IO and SSE streaming patterns"},
      {"source": "python/src/server/api_routes/agent_chat_api.py", "why": "Current chat API endpoints and Socket.IO event handling"},
      {"source": "archon-ui-main/src/services/agentChatService.ts", "why": "Frontend chat service implementation patterns for WebSocket management"},
      {"source": "https://code.visualstudio.com/api/extension-guides/chat", "why": "VSCode Chat API documentation for extension development"},
      {"source": "https://code.visualstudio.com/api/extension-guides/webview", "why": "VSCode Webview API for creating custom UI panels"}
    ],
    "existing_code": [
      {"file": "python/src/server/api_routes/agent_chat_api.py", "purpose": "Chat session management and Socket.IO event handlers"},
      {"file": "archon-ui-main/src/services/agentChatService.ts", "purpose": "WebSocket connection management and message handling patterns"},
      {"file": "archon-ui-main/src/components/layouts/ArchonChatPanel.tsx", "purpose": "React chat UI component structure and state management"},
      {"file": "python/src/mcp/modules/project_module.py", "purpose": "MCP tool integration patterns for project management"},
      {"file": "python/src/mcp/modules/task_module.py", "purpose": "Task management MCP tools for IDE integration"}
    ],
    "gotchas": [
      "VSCode extension security model requires careful handling of external connections",
      "Socket.IO connections from VSCode extensions need proper CORS configuration",
      "VSCode Chat API has specific message format requirements for proper rendering",
      "Extension must handle Archon server unavailability gracefully without blocking IDE",
      "WebSocket connections in VSCode extensions require proper cleanup on deactivation",
      "VSCode extension marketplace requires specific packaging and security compliance"
    ],
    "current_state": "Archon has a fully functional agent chat system with Socket.IO and SSE streaming. The system supports multiple agent types (RAG, Document, Task) with real-time communication. VSCode integration does not exist yet.",
    "dependencies": [
      "@vscode/vscode-sdk",
      "socket.io-client",
      "typescript",
      "webpack"
    ],
    "environment_variables": [
      "ARCHON_SERVER_HOST",
      "ARCHON_SERVER_PORT",
      "ARCHON_WEBSOCKET_ENDPOINT"
    ]
  },

  "implementation_blueprint": {
    "phase_1_extension_foundation": {
      "description": "Create VSCode extension structure and basic chat integration",
      "tasks": [
        {
          "title": "Initialize VSCode extension project structure",
          "files": ["vscode-extension/package.json", "vscode-extension/src/extension.ts", "vscode-extension/webpack.config.js"],
          "details": "Set up TypeScript VSCode extension with proper manifest, activation events, and build configuration"
        },
        {
          "title": "Implement Socket.IO connection manager",
          "files": ["vscode-extension/src/services/ArchonConnectionService.ts"],
          "details": "Create service to manage Socket.IO connections to Archon server with reconnection logic and error handling"
        },
        {
          "title": "Create chat webview provider",
          "files": ["vscode-extension/src/providers/ChatWebviewProvider.ts"],
          "details": "Implement VSCode webview provider for chat interface with proper message passing between extension and webview"
        }
      ]
    },
    "phase_2_chat_integration": {
      "description": "Integrate with Archon's existing chat system",
      "tasks": [
        {
          "title": "Implement agent chat service integration",
          "files": ["vscode-extension/src/services/AgentChatService.ts"],
          "details": "Connect to Archon's agent chat API endpoints and handle session management, message sending, and streaming responses"
        },
        {
          "title": "Create chat UI components",
          "files": ["vscode-extension/webview/src/components/ChatPanel.tsx", "vscode-extension/webview/src/components/MessageList.tsx"],
          "details": "Build React components for chat interface within VSCode webview with message rendering and input handling"
        },
        {
          "title": "Implement real-time message streaming",
          "files": ["vscode-extension/src/services/StreamingService.ts"],
          "details": "Handle SSE streaming responses from Archon agents and update chat UI in real-time"
        }
      ]
    },
    "phase_3_context_integration": {
      "description": "Add VSCode context awareness and MCP tool integration",
      "tasks": [
        {
          "title": "Implement context extraction service",
          "files": ["vscode-extension/src/services/ContextService.ts"],
          "details": "Extract current file content, project structure, and workspace information to send as context to Archon agents"
        },
        {
          "title": "Add MCP tool integration",
          "files": ["vscode-extension/src/services/MCPIntegrationService.ts"],
          "details": "Enable project and task management operations from within VSCode using Archon's MCP tools"
        },
        {
          "title": "Implement chat persistence",
          "files": ["vscode-extension/src/services/ChatPersistenceService.ts"],
          "details": "Store and restore chat history across VSCode sessions using extension global state"
        }
      ]
    }
  },

  "validation": {
    "level_1_syntax": [
      "npm run compile",
      "npm run lint",
      "tsc --noEmit"
    ],
    "level_2_unit_tests": [
      "npm test -- --testPathPattern=services",
      "npm test -- --testPathPattern=providers",
      "npm test -- --testPathPattern=components"
    ],
    "level_3_integration": [
      "Test Socket.IO connection to running Archon server",
      "Verify chat session creation and message exchange",
      "Test context extraction from active VSCode workspace",
      "Validate MCP tool integration with project operations"
    ],
    "level_4_end_to_end": [
      "Install extension in VSCode development host",
      "Connect to Archon server and create chat session",
      "Send messages and verify real-time streaming responses",
      "Test context-aware queries with current file content",
      "Verify chat history persistence across VSCode restarts",
      "Test graceful handling of Archon server disconnection"
    ]
  },

  "additional_context": {
    "security_considerations": [
      "Validate all external connections and implement proper CORS handling",
      "Sanitize user input before sending to Archon agents",
      "Implement secure storage for connection credentials",
      "Follow VSCode extension security best practices for webview content",
      "Ensure no sensitive workspace information is logged or transmitted unnecessarily"
    ],
    "testing_strategies": [
      "Mock Archon server responses for unit testing",
      "Use VSCode extension test framework for integration testing",
      "Test with various workspace configurations and file types",
      "Verify performance impact on VSCode startup and operation",
      "Test extension behavior with network connectivity issues"
    ],
    "monitoring_and_logging": [
      "Log connection status and errors to VSCode output channel",
      "Track message exchange metrics for performance monitoring",
      "Implement telemetry for usage patterns and error rates",
      "Monitor WebSocket connection health and reconnection attempts",
      "Log context extraction performance and accuracy"
    ]
  }
}
