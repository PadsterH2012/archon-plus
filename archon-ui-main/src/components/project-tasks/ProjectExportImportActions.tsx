import React, { useState, useCallback } from 'react';
import { Download, Upload, MoreHorizontal, Package, History } from 'lucide-react';
import { Button } from '../ui/Button';
import { ExportDialog } from './ExportDialog';
import { ImportDialog } from './ImportDialog';
import { useToast } from '../../contexts/ToastContext';
import { listExports, type ExportListItem } from '../../services/exportImportService';

interface ProjectExportImportActionsProps {
  projectId: string;
  projectTitle: string;
  onProjectImported?: (projectId: string) => void;
  isDarkMode?: boolean;
  className?: string;
}

export const ProjectExportImportActions: React.FC<ProjectExportImportActionsProps> = ({
  projectId,
  projectTitle,
  onProjectImported,
  isDarkMode = false,
  className = ''
}) => {
  const { addToast } = useToast();
  const [showExportDialog, setShowExportDialog] = useState(false);
  const [showImportDialog, setShowImportDialog] = useState(false);
  const [showExportHistory, setShowExportHistory] = useState(false);
  const [exportHistory, setExportHistory] = useState<ExportListItem[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);

  const handleShowExportHistory = useCallback(async () => {
    try {
      setIsLoadingHistory(true);
      const response = await listExports(projectId);
      setExportHistory(response.exports);
      setShowExportHistory(true);
    } catch (error) {
      console.error('Failed to load export history:', error);
      addToast({
        type: 'error',
        title: 'Failed to Load History',
        message: error instanceof Error ? error.message : 'Could not load export history'
      });
    } finally {
      setIsLoadingHistory(false);
    }
  }, [projectId, addToast]);

  const handleImportSuccess = useCallback((newProjectId: string) => {
    addToast({
      type: 'success',
      title: 'Import Successful',
      message: 'Project has been imported successfully'
    });
    
    if (onProjectImported) {
      onProjectImported(newProjectId);
    }
  }, [addToast, onProjectImported]);

  return (
    <>
      <div className={`flex items-center gap-2 ${className}`}>
        {/* Export Button */}
        <Button
          variant="outline"
          size="sm"
          accentColor="blue"
          onClick={() => setShowExportDialog(true)}
          icon={<Download className="w-4 h-4" />}
          className="text-blue-600 dark:text-blue-400 border-blue-200 dark:border-blue-800 hover:bg-blue-50 dark:hover:bg-blue-900/20"
        >
          Export
        </Button>

        {/* Import Button */}
        <Button
          variant="outline"
          size="sm"
          accentColor="green"
          onClick={() => setShowImportDialog(true)}
          icon={<Upload className="w-4 h-4" />}
          className="text-green-600 dark:text-green-400 border-green-200 dark:border-green-800 hover:bg-green-50 dark:hover:bg-green-900/20"
        >
          Import
        </Button>

        {/* Export History Button */}
        <Button
          variant="ghost"
          size="sm"
          onClick={handleShowExportHistory}
          disabled={isLoadingHistory}
          icon={isLoadingHistory ? undefined : <History className="w-4 h-4" />}
          className="text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
          title="View export history"
        >
          {isLoadingHistory ? (
            <div className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
          ) : (
            'History'
          )}
        </Button>
      </div>

      {/* Export Dialog */}
      <ExportDialog
        isOpen={showExportDialog}
        onClose={() => setShowExportDialog(false)}
        projectId={projectId}
        projectTitle={projectTitle}
        isDarkMode={isDarkMode}
      />

      {/* Import Dialog */}
      <ImportDialog
        isOpen={showImportDialog}
        onClose={() => setShowImportDialog(false)}
        onImportSuccess={handleImportSuccess}
        isDarkMode={isDarkMode}
      />

      {/* Export History Modal */}
      {showExportHistory && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 w-full max-w-2xl max-h-[80vh] overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                  <History className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Export History
                  </h2>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {projectTitle}
                  </p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowExportHistory(false)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                ×
              </Button>
            </div>

            {/* Content */}
            <div className="p-6">
              {exportHistory.length === 0 ? (
                <div className="text-center py-8">
                  <Package className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                    No Exports Yet
                  </h3>
                  <p className="text-gray-500 dark:text-gray-400">
                    Export this project to see the history here.
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {exportHistory.map((exportItem) => (
                    <div
                      key={exportItem.export_id}
                      className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50"
                    >
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                          <Package className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                        </div>
                        <div>
                          <div className="text-sm font-medium text-gray-900 dark:text-white">
                            {exportItem.export_type.charAt(0).toUpperCase() + exportItem.export_type.slice(1)} Export
                          </div>
                          <div className="text-xs text-gray-500 dark:text-gray-400">
                            {new Date(exportItem.created_at).toLocaleDateString()} • {Math.round(exportItem.file_size / 1024)} KB
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          exportItem.status === 'completed' 
                            ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200'
                            : exportItem.status === 'failed'
                            ? 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200'
                            : 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-200'
                        }`}>
                          {exportItem.status}
                        </span>
                        {exportItem.status === 'completed' && (
                          <Button
                            variant="ghost"
                            size="sm"
                            icon={<Download className="w-3 h-3" />}
                            className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300"
                            onClick={() => {
                              // Download logic would go here
                              window.open(`/api/projects/exports/${exportItem.export_id}/download`, '_blank');
                            }}
                          >
                            Download
                          </Button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

// Standalone Export/Import Buttons for use in different contexts
export const ExportButton: React.FC<{
  projectId: string;
  projectTitle: string;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}> = ({ projectId, projectTitle, variant = 'outline', size = 'sm', className = '' }) => {
  const [showDialog, setShowDialog] = useState(false);

  return (
    <>
      <Button
        variant={variant}
        size={size}
        accentColor="blue"
        onClick={() => setShowDialog(true)}
        icon={<Download className="w-4 h-4" />}
        className={className}
      >
        Export
      </Button>
      
      <ExportDialog
        isOpen={showDialog}
        onClose={() => setShowDialog(false)}
        projectId={projectId}
        projectTitle={projectTitle}
      />
    </>
  );
};

export const ImportButton: React.FC<{
  onImportSuccess?: (projectId: string) => void;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}> = ({ onImportSuccess, variant = 'outline', size = 'sm', className = '' }) => {
  const [showDialog, setShowDialog] = useState(false);

  return (
    <>
      <Button
        variant={variant}
        size={size}
        accentColor="green"
        onClick={() => setShowDialog(true)}
        icon={<Upload className="w-4 h-4" />}
        className={className}
      >
        Import
      </Button>
      
      <ImportDialog
        isOpen={showDialog}
        onClose={() => setShowDialog(false)}
        onImportSuccess={onImportSuccess}
      />
    </>
  );
};
