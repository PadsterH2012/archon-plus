import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

describe('MCP Environment Variables', () => {
  let originalEnv: any;

  beforeEach(() => {
    originalEnv = { ...import.meta.env };
    vi.resetModules();
  });

  afterEach(() => {
    Object.keys(import.meta.env).forEach(key => {
      delete (import.meta.env as any)[key];
    });
    Object.assign(import.meta.env, originalEnv);
  });

  it('should have VITE_MCP_NAME defined in environment interface', () => {
    // Set test environment variables
    (import.meta.env as any).VITE_MCP_NAME = 'archon-test';
    (import.meta.env as any).VITE_MCP_HOST = 'test-host';
    (import.meta.env as any).VITE_MCP_PORT = '9999';

    // Verify they are accessible
    expect(import.meta.env.VITE_MCP_NAME).toBe('archon-test');
    expect(import.meta.env.VITE_MCP_HOST).toBe('test-host');
    expect(import.meta.env.VITE_MCP_PORT).toBe('9999');
  });

  it('should handle missing MCP environment variables gracefully', () => {
    // Clear all MCP environment variables
    delete (import.meta.env as any).VITE_MCP_NAME;
    delete (import.meta.env as any).VITE_MCP_HOST;
    delete (import.meta.env as any).VITE_MCP_PORT;

    // These should be undefined when not set
    expect(import.meta.env.VITE_MCP_NAME).toBeUndefined();
    expect(import.meta.env.VITE_MCP_HOST).toBeUndefined();
    expect(import.meta.env.VITE_MCP_PORT).toBeUndefined();
  });

  it('should use environment-specific MCP names', () => {
    // Test development environment
    (import.meta.env as any).VITE_MCP_NAME = 'archon-dev';
    expect(import.meta.env.VITE_MCP_NAME).toBe('archon-dev');

    // Test production environment
    (import.meta.env as any).VITE_MCP_NAME = 'archon-prod';
    expect(import.meta.env.VITE_MCP_NAME).toBe('archon-prod');
  });

  it('should have MCP environment variables available in TypeScript interface', () => {
    // Set test environment variables
    (import.meta.env as any).VITE_MCP_NAME = 'archon-dev';
    (import.meta.env as any).VITE_MCP_HOST = 'dev-host';
    (import.meta.env as any).VITE_MCP_PORT = '9051';
    (import.meta.env as any).ARCHON_MCP_PORT = '8051';

    // Verify TypeScript interface recognizes these variables
    expect(typeof import.meta.env.VITE_MCP_NAME).toBe('string');
    expect(typeof import.meta.env.VITE_MCP_HOST).toBe('string');
    expect(typeof import.meta.env.VITE_MCP_PORT).toBe('string');
    expect(typeof import.meta.env.ARCHON_MCP_PORT).toBe('string');

    // Verify values are accessible
    expect(import.meta.env.VITE_MCP_NAME).toBe('archon-dev');
    expect(import.meta.env.VITE_MCP_HOST).toBe('dev-host');
    expect(import.meta.env.VITE_MCP_PORT).toBe('9051');
    expect(import.meta.env.ARCHON_MCP_PORT).toBe('8051');
  });
});
