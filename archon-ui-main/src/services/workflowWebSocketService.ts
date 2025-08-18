/**
 * Workflow WebSocket Service
 * 
 * Real-time communication service for workflow execution monitoring
 * Provides live updates, progress streaming, and log tailing
 */

import { WorkflowExecution, StepExecution, ExecutionLogEntry } from '../components/workflow/types/workflow.types';

export interface WebSocketMessage {
  type: 'execution_update' | 'step_update' | 'log_entry' | 'progress_update' | 'error' | 'heartbeat';
  data: any;
  timestamp: string;
  execution_id?: string;
  step_id?: string;
}

export interface ExecutionUpdateData {
  execution: WorkflowExecution;
  step_executions: StepExecution[];
}

export interface ProgressUpdateData {
  execution_id: string;
  current_step_index: number;
  total_steps: number;
  progress_percentage: number;
  status: string;
}

export interface LogEntryData {
  execution_id: string;
  step_id?: string;
  entry: ExecutionLogEntry;
}

export interface WebSocketEventHandlers {
  onExecutionUpdate?: (data: ExecutionUpdateData) => void;
  onStepUpdate?: (stepExecution: StepExecution) => void;
  onLogEntry?: (data: LogEntryData) => void;
  onProgressUpdate?: (data: ProgressUpdateData) => void;
  onError?: (error: string) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onReconnect?: () => void;
}

class WorkflowWebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second
  private maxReconnectDelay = 30000; // Max 30 seconds
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private subscriptions = new Set<string>();
  private handlers: WebSocketEventHandlers = {};
  private isConnecting = false;
  private shouldReconnect = true;

  constructor() {
    this.connect();
  }

  /**
   * Connect to WebSocket server
   */
  private connect(): void {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    this.isConnecting = true;
    
    try {
      // Determine WebSocket URL based on current location
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.host;
      const wsUrl = `${protocol}//${host}/ws/workflows`;
      
      this.ws = new WebSocket(wsUrl);
      
      this.ws.onopen = this.handleOpen.bind(this);
      this.ws.onmessage = this.handleMessage.bind(this);
      this.ws.onclose = this.handleClose.bind(this);
      this.ws.onerror = this.handleError.bind(this);
      
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      this.isConnecting = false;
      this.scheduleReconnect();
    }
  }

  /**
   * Handle WebSocket open event
   */
  private handleOpen(): void {
    console.log('WebSocket connected');
    this.isConnecting = false;
    this.reconnectAttempts = 0;
    this.reconnectDelay = 1000;
    
    // Start heartbeat
    this.startHeartbeat();
    
    // Resubscribe to all previous subscriptions
    this.subscriptions.forEach(executionId => {
      this.sendMessage({
        type: 'subscribe',
        execution_id: executionId
      });
    });
    
    this.handlers.onConnect?.();
  }

  /**
   * Handle WebSocket message
   */
  private handleMessage(event: MessageEvent): void {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);
      
      switch (message.type) {
        case 'execution_update':
          this.handlers.onExecutionUpdate?.(message.data as ExecutionUpdateData);
          break;
          
        case 'step_update':
          this.handlers.onStepUpdate?.(message.data as StepExecution);
          break;
          
        case 'log_entry':
          this.handlers.onLogEntry?.(message.data as LogEntryData);
          break;
          
        case 'progress_update':
          this.handlers.onProgressUpdate?.(message.data as ProgressUpdateData);
          break;
          
        case 'error':
          this.handlers.onError?.(message.data);
          break;
          
        case 'heartbeat':
          // Respond to heartbeat
          this.sendMessage({ type: 'heartbeat_response' });
          break;
          
        default:
          console.warn('Unknown WebSocket message type:', message.type);
      }
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
    }
  }

  /**
   * Handle WebSocket close event
   */
  private handleClose(event: CloseEvent): void {
    console.log('WebSocket disconnected:', event.code, event.reason);
    this.isConnecting = false;
    this.stopHeartbeat();
    
    this.handlers.onDisconnect?.();
    
    if (this.shouldReconnect && event.code !== 1000) { // 1000 = normal closure
      this.scheduleReconnect();
    }
  }

  /**
   * Handle WebSocket error event
   */
  private handleError(event: Event): void {
    console.error('WebSocket error:', event);
    this.isConnecting = false;
    this.handlers.onError?.('WebSocket connection error');
  }

  /**
   * Schedule reconnection attempt
   */
  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      this.handlers.onError?.('Failed to reconnect after maximum attempts');
      return;
    }

    this.reconnectAttempts++;
    const delay = Math.min(this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1), this.maxReconnectDelay);
    
    console.log(`Scheduling reconnection attempt ${this.reconnectAttempts} in ${delay}ms`);
    
    setTimeout(() => {
      if (this.shouldReconnect) {
        console.log(`Reconnection attempt ${this.reconnectAttempts}`);
        this.handlers.onReconnect?.();
        this.connect();
      }
    }, delay);
  }

  /**
   * Start heartbeat to keep connection alive
   */
  private startHeartbeat(): void {
    this.stopHeartbeat();
    this.heartbeatInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.sendMessage({ type: 'heartbeat' });
      }
    }, 30000); // Send heartbeat every 30 seconds
  }

  /**
   * Stop heartbeat
   */
  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  /**
   * Send message to WebSocket server
   */
  private sendMessage(message: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        ...message,
        timestamp: new Date().toISOString()
      }));
    } else {
      console.warn('WebSocket not connected, cannot send message:', message);
    }
  }

  /**
   * Set event handlers
   */
  setHandlers(handlers: WebSocketEventHandlers): void {
    this.handlers = { ...this.handlers, ...handlers };
  }

  /**
   * Subscribe to execution updates
   */
  subscribeToExecution(executionId: string): void {
    this.subscriptions.add(executionId);
    this.sendMessage({
      type: 'subscribe',
      execution_id: executionId
    });
  }

  /**
   * Unsubscribe from execution updates
   */
  unsubscribeFromExecution(executionId: string): void {
    this.subscriptions.delete(executionId);
    this.sendMessage({
      type: 'unsubscribe',
      execution_id: executionId
    });
  }

  /**
   * Subscribe to all executions
   */
  subscribeToAllExecutions(): void {
    this.sendMessage({
      type: 'subscribe_all'
    });
  }

  /**
   * Unsubscribe from all executions
   */
  unsubscribeFromAllExecutions(): void {
    this.subscriptions.clear();
    this.sendMessage({
      type: 'unsubscribe_all'
    });
  }

  /**
   * Get connection status
   */
  getConnectionStatus(): 'connecting' | 'connected' | 'disconnected' | 'error' {
    if (this.isConnecting) return 'connecting';
    if (!this.ws) return 'disconnected';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting';
      case WebSocket.OPEN:
        return 'connected';
      case WebSocket.CLOSING:
      case WebSocket.CLOSED:
        return 'disconnected';
      default:
        return 'error';
    }
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  /**
   * Manually reconnect
   */
  reconnect(): void {
    this.shouldReconnect = true;
    this.reconnectAttempts = 0;
    this.disconnect();
    setTimeout(() => this.connect(), 100);
  }

  /**
   * Disconnect WebSocket
   */
  disconnect(): void {
    this.shouldReconnect = false;
    this.stopHeartbeat();
    
    if (this.ws) {
      this.ws.close(1000, 'Manual disconnect');
      this.ws = null;
    }
  }

  /**
   * Cleanup resources
   */
  destroy(): void {
    this.disconnect();
    this.subscriptions.clear();
    this.handlers = {};
  }
}

// Export singleton instance
export const workflowWebSocketService = new WorkflowWebSocketService();
export default workflowWebSocketService;
