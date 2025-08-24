/**
 * Unified API Configuration
 * 
 * This module provides centralized configuration for API endpoints
 * and handles different environments (development, Docker, production)
 */

// Get the API URL from environment or construct it
export function getApiUrl(): string {
  // Check if VITE_API_URL is provided (set by docker-compose)
  if (import.meta.env.VITE_API_URL) {
    console.log('🔍 [API Config] Using VITE_API_URL:', import.meta.env.VITE_API_URL);
    return import.meta.env.VITE_API_URL;
  }

  // For development, construct from window location
  const protocol = window.location.protocol;
  const host = window.location.hostname;
  const port = import.meta.env.ARCHON_SERVER_PORT;

  if (port) {
    const constructedUrl = `${protocol}//${host}:${port}`;
    console.log('🔍 [API Config] Constructed URL from ARCHON_SERVER_PORT:', constructedUrl);
    return constructedUrl;
  }

  // Fallback: try to determine backend port based on current frontend port
  const currentPort = window.location.port;
  let backendPort = '8181'; // Default backend port

  if (currentPort === '4737') {
    // Development frontend -> development backend
    backendPort = '9181';
  } else if (currentPort === '3737') {
    // Production frontend -> production backend
    backendPort = '8181';
  }

  const fallbackUrl = `${protocol}//${host}:${backendPort}`;
  console.log('🔍 [API Config] Using fallback URL based on frontend port:', {
    frontendPort: currentPort,
    backendPort,
    fallbackUrl
  });

  return fallbackUrl;
}

// Get the base path for API endpoints
export function getApiBasePath(): string {
  const apiUrl = getApiUrl();
  const basePath = `${apiUrl}/api`;

  console.log('🔍 [API Config] API Base Path:', basePath);
  return basePath;
}

// Get WebSocket URL for real-time connections
export function getWebSocketUrl(): string {
  const apiUrl = getApiUrl();
  
  // If using relative URLs, construct from current location
  if (!apiUrl) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    return `${protocol}//${host}`;
  }
  
  // Convert http/https to ws/wss
  return apiUrl.replace(/^http/, 'ws');
}

// Export commonly used values
export const API_BASE_URL = '/api';  // Always use relative URL for API calls
export const API_FULL_URL = getApiUrl();
export const WS_URL = getWebSocketUrl();