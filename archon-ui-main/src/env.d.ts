/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_HOST: string;
  readonly VITE_PORT: string;
  readonly VITE_MCP_HOST: string;
  readonly VITE_MCP_PORT: string;
  readonly VITE_MCP_NAME: string;
  readonly ARCHON_MCP_PORT: string;
  // Add other environment variables here as needed
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
