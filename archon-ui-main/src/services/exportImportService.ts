/**
 * Export/Import Service Layer
 * Handles project export/import operations with the backend API
 */

import { apiRequest, retry } from './api';

// Types for export/import operations
export interface ExportOptions {
  export_type?: 'full' | 'selective' | 'incremental';
  include_versions?: boolean;
  include_sources?: boolean;
  include_attachments?: boolean;
  version_limit?: number;
  date_range?: [string, string];
  selective_components?: string[];
}

export interface ImportOptions {
  import_type?: 'full' | 'selective' | 'merge';
  conflict_resolution?: 'merge' | 'overwrite' | 'skip' | 'fail';
  target_project_id?: string;
  selective_components?: string[];
  dry_run?: boolean;
}

export interface ExportResponse {
  success: boolean;
  export_id?: string;
  download_url?: string;
  file_size?: number;
  message: string;
  error?: string;
}

export interface ImportResponse {
  success: boolean;
  project_id?: string;
  import_summary?: {
    project_created?: boolean;
    project_updated?: boolean;
    tasks_imported?: number;
    documents_imported?: number;
    versions_imported?: number;
    sources_imported?: number;
    conflicts_resolved?: any[];
  };
  conflicts_resolved?: any[];
  message: string;
  error?: string;
}

export interface ValidationResponse {
  valid: boolean;
  project_title?: string;
  project_id?: string;
  task_count?: number;
  document_count?: number;
  version_count?: number;
  source_count?: number;
  export_timestamp?: string;
  exported_by?: string;
  error?: string;
}

export interface ExportStatus {
  export_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress?: number;
  message?: string;
  created_at?: string;
  completed_at?: string;
  error?: string;
}

export interface ExportListItem {
  export_id: string;
  project_id: string;
  project_title: string;
  export_type: string;
  file_size: number;
  created_at: string;
  status: string;
}

// Error classes
export class ExportImportError extends Error {
  constructor(message: string, public code?: string, public statusCode?: number) {
    super(message);
    this.name = 'ExportImportError';
  }
}

export class ValidationError extends ExportImportError {
  constructor(message: string) {
    super(message, 'VALIDATION_ERROR', 400);
    this.name = 'ValidationError';
  }
}

/**
 * Export a project with specified options
 */
export async function exportProject(
  projectId: string, 
  options: ExportOptions = {}
): Promise<ExportResponse> {
  try {
    const response = await retry(() => 
      apiRequest<ExportResponse>(`/projects/${projectId}/export`, {
        method: 'POST',
        body: JSON.stringify(options),
      })
    );

    if (!response.success) {
      throw new ExportImportError(response.error || 'Export failed');
    }

    return response;
  } catch (error) {
    if (error instanceof ExportImportError) {
      throw error;
    }
    throw new ExportImportError(`Failed to export project: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

/**
 * Import a project from a file
 */
export async function importProject(
  file: File,
  options: ImportOptions = {}
): Promise<ImportResponse> {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    // Add options as form fields
    if (options.import_type) formData.append('import_type', options.import_type);
    if (options.conflict_resolution) formData.append('conflict_resolution', options.conflict_resolution);
    if (options.target_project_id) formData.append('target_project_id', options.target_project_id);
    if (options.selective_components) {
      formData.append('selective_components', JSON.stringify(options.selective_components));
    }
    if (options.dry_run !== undefined) formData.append('dry_run', options.dry_run.toString());

    const response = await retry(() => 
      apiRequest<ImportResponse>('/projects/import', {
        method: 'POST',
        body: formData,
        headers: {}, // Let browser set Content-Type for FormData
      })
    );

    if (!response.success) {
      throw new ExportImportError(response.error || 'Import failed');
    }

    return response;
  } catch (error) {
    if (error instanceof ExportImportError) {
      throw error;
    }
    throw new ExportImportError(`Failed to import project: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

/**
 * Validate an import file without importing
 */
export async function validateImportFile(file: File): Promise<ValidationResponse> {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await retry(() => 
      apiRequest<ValidationResponse>('/projects/import/validate', {
        method: 'POST',
        body: formData,
        headers: {}, // Let browser set Content-Type for FormData
      })
    );

    return response;
  } catch (error) {
    throw new ValidationError(`Failed to validate import file: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

/**
 * Download an exported project file
 */
export async function downloadExport(exportId: string): Promise<Blob> {
  try {
    const response = await fetch(`/api/projects/exports/${exportId}/download`);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Download failed' }));
      throw new ExportImportError(errorData.error || `Download failed with status ${response.status}`);
    }

    return await response.blob();
  } catch (error) {
    if (error instanceof ExportImportError) {
      throw error;
    }
    throw new ExportImportError(`Failed to download export: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

/**
 * Get export status for a project
 */
export async function getExportStatus(projectId: string): Promise<ExportStatus[]> {
  try {
    return await retry(() => 
      apiRequest<ExportStatus[]>(`/projects/${projectId}/export/status`)
    );
  } catch (error) {
    throw new ExportImportError(`Failed to get export status: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

/**
 * List all available exports
 */
export async function listExports(projectId?: string): Promise<{ exports: ExportListItem[]; total_count: number }> {
  try {
    const endpoint = projectId ? `/projects/exports?project_id=${projectId}` : '/projects/exports';
    return await retry(() => 
      apiRequest<{ exports: ExportListItem[]; total_count: number }>(endpoint)
    );
  } catch (error) {
    throw new ExportImportError(`Failed to list exports: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

/**
 * Trigger download of a file with proper filename
 */
export function triggerDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * Format file size for display
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Validate file type for import
 */
export function validateImportFileType(file: File): boolean {
  return file.type === 'application/zip' || file.name.endsWith('.zip');
}

/**
 * Get conflict resolution display text
 */
export function getConflictResolutionText(strategy: string): string {
  switch (strategy) {
    case 'merge':
      return 'Merge with existing data';
    case 'overwrite':
      return 'Overwrite existing data';
    case 'skip':
      return 'Skip conflicting items';
    case 'fail':
      return 'Fail on conflicts';
    default:
      return strategy;
  }
}

/**
 * Get import type display text
 */
export function getImportTypeText(type: string): string {
  switch (type) {
    case 'full':
      return 'Full project import';
    case 'selective':
      return 'Selective component import';
    case 'merge':
      return 'Merge into existing project';
    default:
      return type;
  }
}
