# Layout & Navigation Components Documentation

**File Path:** `archon-ui-main/src/components/layouts/` directory and related components
**Last Updated:** 2025-08-23

## Purpose
Documentation for the core layout and navigation components that provide the structural foundation of the Archon application. These components handle routing patterns, state management, responsive design, and user interface organization.

## Core Layout Components

### 1. MainLayout
**File:** `layouts/MainLayout.tsx`
**Purpose:** Primary application layout wrapper that orchestrates the overall page structure

**Key Features:**
- **Responsive Grid Layout:** Fixed neon grid background with floating navigation
- **Chat Panel Integration:** Slidable chat panel with state management
- **Backend Health Monitoring:** Automatic health checks with retry logic
- **Onboarding Flow:** Redirects to onboarding when LM not configured
- **Toast Notifications:** Integrated error and status messaging
- **Z-Index Management:** Proper layering of UI elements

**Props Interface:**
```typescript
interface MainLayoutProps {
  children: React.ReactNode;
}
```

**Layout Structure:**
```jsx
<MainLayout>
  {/* Fixed neon grid background */}
  <div className="fixed inset-0 neon-grid" />
  
  {/* Floating side navigation */}
  <div className="fixed left-6 top-1/2">
    <SideNavigation />
  </div>
  
  {/* Main content area */}
  <div className="pl-[100px]">
    {children}
  </div>
  
  {/* Slidable chat panel */}
  <ArchonChatPanel />
</MainLayout>
```

**State Management:**
- `isChatOpen` - Controls chat panel visibility
- `backendReady` - Tracks backend health status
- Health check with exponential backoff retry logic
- Automatic navigation to onboarding when needed

**Responsive Design:**
- Mobile-first approach with adaptive spacing
- Fixed positioning for navigation and chat
- Flexible content area with proper margins
- Grid background that doesn't interfere with content

### 2. SideNavigation
**File:** `layouts/SideNavigation.tsx`
**Purpose:** Vertical navigation sidebar with icon-based menu system

**Key Features:**
- **Icon-Based Navigation:** Clean, minimal design with tooltips
- **Active Route Highlighting:** Visual feedback for current page
- **Conditional Navigation:** Projects menu based on feature flags
- **Hover Effects:** Smooth transitions and visual feedback
- **Logo Integration:** Clickable logo with special projects styling

**Props Interface:**
```typescript
interface SideNavigationProps {
  className?: string;
  'data-id'?: string;
}

interface NavigationItem {
  path: string;
  icon: React.ReactNode;
  label: string;
}
```

**Navigation Items:**
```typescript
const navigationItems: NavigationItem[] = [
  {
    path: '/knowledge-base',
    icon: <BookOpen className="h-5 w-5" />,
    label: 'Knowledge Base'
  },
  {
    path: '/workflows',
    icon: <Workflow className="h-5 w-5" />,
    label: 'Workflows'
  },
  {
    path: '/mcp',
    icon: <HardDrive className="h-5 w-5" />,
    label: 'MCP Clients'
  },
  {
    path: '/settings',
    icon: <Settings className="h-5 w-5" />,
    label: 'Settings'
  }
];
```

**State Management:**
- `activeTooltip` - Controls which tooltip is currently visible
- Uses `useLocation()` for active route detection
- Integrates with `useSettings()` for feature flags

**Styling Features:**
- Gradient backgrounds for active states
- Neon glow effects on hover
- Smooth transitions and animations
- Tooltip positioning and timing

### 3. ArchonChatPanel
**File:** `layouts/ArchonChatPanel.tsx`
**Purpose:** AI chat interface panel with resizable functionality

**Key Features:**
- **Resizable Panel:** Drag-to-resize functionality with constraints
- **Message History:** Persistent chat session management
- **Real-time Communication:** WebSocket integration for live responses
- **Loading States:** Visual feedback during AI processing
- **Session Management:** Automatic session creation and restoration

**Props Interface:**
```typescript
interface ArchonChatPanelProps {
  'data-id'?: string;
}

interface ChatMessage {
  id: string;
  content: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
}
```

**State Management:**
- `messages` - Chat message history array
- `sessionId` - Current chat session identifier
- `isInitialized` - Panel initialization status
- `inputValue` - Current input field value
- `width` - Panel width (resizable, default: 416px)
- `isTyping` - User typing indicator
- `isDragging` - Resize handle drag state
- `connectionError` - Error message for connection issues
- `streamingMessage` - Real-time streaming message content
- `isStreaming` - Streaming response indicator
- `connectionStatus` - 'online' | 'offline' | 'connecting'
- `isReconnecting` - Reconnection attempt status

**WebSocket Integration:**
```typescript
// Initialize WebSocket connection
const initializeChat = async () => {
  const sessionId = await agentChatService.createSession();
  await agentChatService.connectWebSocket(
    sessionId,
    onMessage,      // Message handler
    onChunk,        // Streaming chunk handler
    onComplete,     // Stream completion handler
    onError,        // Error handler
    onClose         // Connection close handler
  );
};
```

**Resizing System:**
- Minimum width: 280px
- Maximum width: 600px
- Default width: 416px
- Drag handle with visual feedback
- Mouse cursor changes during resize
- Prevents text selection during drag
- Real-time width updates with constraints

## Overlay Components

### 4. DisconnectScreenOverlay
**File:** `DisconnectScreenOverlay.tsx`
**Purpose:** Full-screen overlay displayed when backend connection is lost

**Key Features:**
- **Aurora Animation:** Beautiful animated background with canvas effects
- **Frosted Glass Design:** Modern glassmorphism aesthetic
- **Auto-dismiss Controls:** Mouse interaction reveals dismiss button
- **Health Integration:** Automatic show/hide based on server status
- **Configurable Behavior:** Settings-controlled enable/disable

**Props Interface:**
```typescript
interface DisconnectScreenOverlayProps {
  isActive: boolean;
  onDismiss?: () => void;
}
```

**Animation System:**
```typescript
// Aurora borealis effect with multiple wave layers
const colors = [
  { r: 34, g: 211, b: 238, a: 0.4 },  // Cyan
  { r: 168, g: 85, b: 247, a: 0.4 },  // Purple
  { r: 236, g: 72, b: 153, a: 0.4 },  // Pink
  { r: 59, g: 130, b: 246, a: 0.4 },  // Blue
  { r: 16, g: 185, b: 129, a: 0.4 },  // Green
];

// Wave animation with varying speeds and heights
const waveHeight = 250;
const speed = 0.001 + index * 0.0002;
const y = canvas.height / 2 +
  Math.sin(x * 0.003 + time * speed) * waveHeight +
  Math.sin(x * 0.005 + time * speed * 1.5) * (waveHeight / 2) +
  Math.sin(x * 0.002 + time * speed * 0.5) * (waveHeight / 3);
```

**Visual Effects:**
- **Radial Gradient Background:** Dark vignette effect
- **Multi-layer Waves:** 5 animated wave layers with different colors
- **Dynamic Opacity:** Sine wave-based opacity animation
- **Glow Effects:** Shadow blur and color effects
- **Frosted Glass Medallion:** Central focus with glassmorphism
- **Performance Optimization:** RequestAnimationFrame loop

**State Management:**
- `showControls` - Controls visibility of dismiss button
- Mouse interaction detection for control visibility
- Automatic timeout for control hiding (3 seconds)
- Canvas resize handling for responsive design

**Integration:**
- Connected to `serverHealthService` for status monitoring
- Configurable through settings panel
- Z-index management for proper overlay behavior

## Routing Patterns

### Application Routing Structure
```typescript
// Main App.tsx routing configuration
<Routes>
  <Route path="/" element={<KnowledgeBasePage />} />
  <Route path="/knowledge-base" element={<KnowledgeBasePage />} />
  <Route path="/onboarding" element={<OnboardingPage />} />
  <Route path="/settings" element={<SettingsPage />} />
  <Route path="/mcp" element={<MCPPage />} />
  <Route path="/workflows" element={<WorkflowPage />} />
  <Route path="/workflows/*" element={<WorkflowPage />} />
  {projectsEnabled ? (
    <Route path="/projects" element={<ProjectPage />} />
  ) : (
    <Route path="/projects" element={<Navigate to="/" replace />} />
  )}
</Routes>
```

### Route Protection
- **Feature Flags:** Projects route protected by `projectsEnabled` setting
- **Onboarding Flow:** Automatic redirect when LM not configured
- **Fallback Routes:** Default redirects for invalid paths

### Navigation State
- **Active Route Detection:** Uses `useLocation()` hook
- **Conditional Rendering:** Menu items based on feature availability
- **Visual Feedback:** Highlighting and styling for current route

## State Management Patterns

### Context Integration
- **Settings Context:** Feature flags and user preferences
- **Toast Context:** Error and notification messaging
- **Theme Context:** Dark/light mode management

### Health Monitoring
- **Backend Health Checks:** Automatic monitoring with retry logic
- **Connection Status:** Real-time status updates
- **Error Recovery:** Automatic reconnection and page refresh

### Chat State
- **Session Persistence:** Maintains chat history across navigation
- **Real-time Updates:** WebSocket integration for live responses
- **Loading Management:** Visual feedback during AI processing

## Responsive Design Considerations

### Breakpoint Strategy
- **Mobile First:** Base styles for mobile devices
- **Progressive Enhancement:** Additional features for larger screens
- **Flexible Layouts:** Adaptive spacing and sizing

### Layout Adaptations
- **Navigation:** Fixed positioning with responsive spacing
- **Content Area:** Flexible margins and padding
- **Chat Panel:** Resizable with minimum/maximum constraints
- **Overlay:** Full-screen coverage on all devices

### Performance Optimizations
- **Lazy Loading:** Components loaded on demand
- **Efficient Rendering:** Minimal re-renders with proper state management
- **Animation Performance:** Hardware-accelerated CSS transforms
- **Memory Management:** Proper cleanup of event listeners and timers

## Integration Notes

### Service Dependencies
- **credentialsService:** Authentication and configuration
- **serverHealthService:** Backend monitoring and status
- **agentChatService:** AI chat functionality
- **socketService:** Real-time communication

### Component Relationships
- **MainLayout** wraps all page content
- **SideNavigation** provides primary navigation
- **ArchonChatPanel** offers AI assistance
- **DisconnectScreenOverlay** handles connection issues

### Error Handling
- **Graceful Degradation:** Fallbacks for failed services
- **User Feedback:** Clear error messages and recovery options
- **Automatic Recovery:** Retry logic and reconnection attempts
