import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { createPortal } from 'react-dom';
import { 
  Download, 
  X, 
  Settings, 
  Calendar, 
  Database, 
  FileText, 
  GitBranch,
  Package,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import { Button } from '../ui/Button';
import { useToast } from '../../contexts/ToastContext';
import { 
  exportProject, 
  downloadExport, 
  triggerDownload, 
  formatFileSize,
  type ExportOptions 
} from '../../services/exportImportService';

interface ExportDialogProps {
  isOpen: boolean;
  onClose: () => void;
  projectId: string;
  projectTitle: string;
  isDarkMode?: boolean;
}

export const ExportDialog: React.FC<ExportDialogProps> = ({
  isOpen,
  onClose,
  projectId,
  projectTitle,
  isDarkMode = false
}) => {
  const { addToast } = useToast();
  const [isExporting, setIsExporting] = useState(false);
  const [exportOptions, setExportOptions] = useState<ExportOptions>({
    export_type: 'full',
    include_versions: true,
    include_sources: true,
    include_attachments: false,
    version_limit: undefined,
    date_range: undefined,
    selective_components: []
  });

  const [showAdvanced, setShowAdvanced] = useState(false);
  const [dateRange, setDateRange] = useState({ start: '', end: '' });

  const handleExport = useCallback(async () => {
    try {
      setIsExporting(true);

      // Prepare export options
      const options: ExportOptions = {
        ...exportOptions,
        date_range: dateRange.start && dateRange.end ? [dateRange.start, dateRange.end] : undefined
      };

      // Start export
      const exportResponse = await exportProject(projectId, options);

      if (exportResponse.success && exportResponse.export_id) {
        addToast({
          type: 'success',
          title: 'Export Started',
          message: 'Project export is being prepared...'
        });

        // Download the file
        const blob = await downloadExport(exportResponse.export_id);
        const filename = `${projectTitle.replace(/[^a-zA-Z0-9]/g, '_')}_export_${new Date().toISOString().split('T')[0]}.zip`;
        
        triggerDownload(blob, filename);

        addToast({
          type: 'success',
          title: 'Export Complete',
          message: `Project exported successfully${exportResponse.file_size ? ` (${formatFileSize(exportResponse.file_size)})` : ''}`
        });

        onClose();
      } else {
        throw new Error(exportResponse.error || 'Export failed');
      }
    } catch (error) {
      console.error('Export error:', error);
      addToast({
        type: 'error',
        title: 'Export Failed',
        message: error instanceof Error ? error.message : 'Failed to export project'
      });
    } finally {
      setIsExporting(false);
    }
  }, [projectId, projectTitle, exportOptions, dateRange, addToast, onClose]);

  const handleOptionChange = useCallback((key: keyof ExportOptions, value: any) => {
    setExportOptions(prev => ({ ...prev, [key]: value }));
  }, []);

  const handleComponentToggle = useCallback((component: string) => {
    setExportOptions(prev => ({
      ...prev,
      selective_components: prev.selective_components?.includes(component)
        ? prev.selective_components.filter(c => c !== component)
        : [...(prev.selective_components || []), component]
    }));
  }, []);

  if (!isOpen) return null;

  return createPortal(
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="relative w-full max-w-lg"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Accent line */}
          <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-blue-500 to-purple-500 shadow-[0_0_20px_5px_rgba(59,130,246,0.5)] z-10 rounded-t-xl"></div>
          
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                  <Download className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Export Project
                  </h2>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {projectTitle}
                  </p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <X className="w-5 h-5" />
              </Button>
            </div>

            {/* Content */}
            <div className="p-6 space-y-6">
              {/* Export Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                  Export Type
                </label>
                <div className="grid grid-cols-1 gap-2">
                  {[
                    { value: 'full', label: 'Full Export', desc: 'Complete project with all data', icon: Package },
                    { value: 'selective', label: 'Selective Export', desc: 'Choose specific components', icon: CheckCircle },
                    { value: 'incremental', label: 'Incremental Export', desc: 'Only recent changes', icon: GitBranch }
                  ].map(({ value, label, desc, icon: Icon }) => (
                    <label key={value} className="flex items-center p-3 border border-gray-200 dark:border-gray-600 rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50">
                      <input
                        type="radio"
                        name="exportType"
                        value={value}
                        checked={exportOptions.export_type === value}
                        onChange={(e) => handleOptionChange('export_type', e.target.value)}
                        className="sr-only"
                      />
                      <div className={`w-4 h-4 rounded-full border-2 mr-3 ${
                        exportOptions.export_type === value 
                          ? 'border-blue-500 bg-blue-500' 
                          : 'border-gray-300 dark:border-gray-600'
                      }`}>
                        {exportOptions.export_type === value && (
                          <div className="w-2 h-2 bg-white rounded-full mx-auto mt-0.5" />
                        )}
                      </div>
                      <Icon className="w-4 h-4 text-gray-400 mr-3" />
                      <div className="flex-1">
                        <div className="text-sm font-medium text-gray-900 dark:text-white">{label}</div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">{desc}</div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              {/* Include Options */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                  Include in Export
                </label>
                <div className="space-y-2">
                  {[
                    { key: 'include_versions', label: 'Version History', icon: GitBranch },
                    { key: 'include_sources', label: 'Knowledge Sources', icon: Database },
                    { key: 'include_attachments', label: 'File Attachments', icon: FileText }
                  ].map(({ key, label, icon: Icon }) => (
                    <label key={key} className="flex items-center p-2 hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded-lg cursor-pointer">
                      <input
                        type="checkbox"
                        checked={exportOptions[key as keyof ExportOptions] as boolean}
                        onChange={(e) => handleOptionChange(key as keyof ExportOptions, e.target.checked)}
                        className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      />
                      <Icon className="w-4 h-4 text-gray-400 ml-3 mr-2" />
                      <span className="text-sm text-gray-700 dark:text-gray-300">{label}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Selective Components */}
              {exportOptions.export_type === 'selective' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    Select Components
                  </label>
                  <div className="space-y-2">
                    {['tasks', 'documents', 'versions', 'sources'].map((component) => (
                      <label key={component} className="flex items-center p-2 hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded-lg cursor-pointer">
                        <input
                          type="checkbox"
                          checked={exportOptions.selective_components?.includes(component)}
                          onChange={() => handleComponentToggle(component)}
                          className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                        />
                        <span className="text-sm text-gray-700 dark:text-gray-300 ml-3 capitalize">{component}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}

              {/* Advanced Options */}
              <div>
                <button
                  onClick={() => setShowAdvanced(!showAdvanced)}
                  className="flex items-center text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300"
                >
                  <Settings className="w-4 h-4 mr-1" />
                  Advanced Options
                </button>
                
                {showAdvanced && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="mt-3 space-y-4"
                  >
                    {/* Version Limit */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Version Limit
                      </label>
                      <input
                        type="number"
                        placeholder="All versions"
                        value={exportOptions.version_limit || ''}
                        onChange={(e) => handleOptionChange('version_limit', e.target.value ? parseInt(e.target.value) : undefined)}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                    </div>

                    {/* Date Range */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Date Range
                      </label>
                      <div className="grid grid-cols-2 gap-2">
                        <input
                          type="date"
                          value={dateRange.start}
                          onChange={(e) => setDateRange(prev => ({ ...prev, start: e.target.value }))}
                          className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                        <input
                          type="date"
                          value={dateRange.end}
                          onChange={(e) => setDateRange(prev => ({ ...prev, end: e.target.value }))}
                          className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                      </div>
                    </div>
                  </motion.div>
                )}
              </div>
            </div>

            {/* Footer */}
            <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
              <Button
                variant="ghost"
                onClick={onClose}
                disabled={isExporting}
              >
                Cancel
              </Button>
              <Button
                variant="primary"
                accentColor="blue"
                onClick={handleExport}
                disabled={isExporting}
                icon={isExporting ? undefined : <Download className="w-4 h-4" />}
              >
                {isExporting ? 'Exporting...' : 'Export Project'}
              </Button>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>,
    document.body
  );
};
