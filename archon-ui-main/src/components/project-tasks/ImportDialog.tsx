import React, { useState, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { createPortal } from 'react-dom';
import { 
  Upload, 
  X, 
  FileText, 
  CheckCircle, 
  AlertTriangle,
  Info,
  Package,
  Merge,
  Settings
} from 'lucide-react';
import { Button } from '../ui/Button';
import { useToast } from '../../contexts/ToastContext';
import { 
  importProject, 
  validateImportFile, 
  validateImportFileType,
  getConflictResolutionText,
  getImportTypeText,
  formatFileSize,
  type ImportOptions,
  type ValidationResponse 
} from '../../services/exportImportService';

interface ImportDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onImportSuccess?: (projectId: string) => void;
  isDarkMode?: boolean;
}

export const ImportDialog: React.FC<ImportDialogProps> = ({
  isOpen,
  onClose,
  onImportSuccess,
  isDarkMode = false
}) => {
  const { addToast } = useToast();
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isValidating, setIsValidating] = useState(false);
  const [isImporting, setIsImporting] = useState(false);
  const [validation, setValidation] = useState<ValidationResponse | null>(null);
  const [importOptions, setImportOptions] = useState<ImportOptions>({
    import_type: 'full',
    conflict_resolution: 'merge',
    dry_run: false
  });
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleFileSelect = useCallback(async (file: File) => {
    if (!validateImportFileType(file)) {
      addToast({
        type: 'error',
        title: 'Invalid File Type',
        message: 'Please select a ZIP file exported from Archon'
      });
      return;
    }

    setSelectedFile(file);
    setValidation(null);

    // Validate the file
    try {
      setIsValidating(true);
      const validationResult = await validateImportFile(file);
      setValidation(validationResult);

      if (!validationResult.valid) {
        addToast({
          type: 'error',
          title: 'Invalid Import File',
          message: validationResult.error || 'The selected file is not a valid Archon export'
        });
      }
    } catch (error) {
      console.error('Validation error:', error);
      addToast({
        type: 'error',
        title: 'Validation Failed',
        message: error instanceof Error ? error.message : 'Failed to validate import file'
      });
    } finally {
      setIsValidating(false);
    }
  }, [addToast]);

  const handleFileChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  }, [handleFileSelect]);

  const handleDrop = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file) {
      handleFileSelect(file);
    }
  }, [handleFileSelect]);

  const handleImport = useCallback(async () => {
    if (!selectedFile || !validation?.valid) return;

    try {
      setIsImporting(true);

      const response = await importProject(selectedFile, importOptions);

      if (response.success) {
        addToast({
          type: 'success',
          title: 'Import Complete',
          message: response.message || 'Project imported successfully'
        });

        if (response.project_id && onImportSuccess) {
          onImportSuccess(response.project_id);
        }

        onClose();
      } else {
        throw new Error(response.error || 'Import failed');
      }
    } catch (error) {
      console.error('Import error:', error);
      addToast({
        type: 'error',
        title: 'Import Failed',
        message: error instanceof Error ? error.message : 'Failed to import project'
      });
    } finally {
      setIsImporting(false);
    }
  }, [selectedFile, validation, importOptions, addToast, onImportSuccess, onClose]);

  const handleOptionChange = useCallback((key: keyof ImportOptions, value: any) => {
    setImportOptions(prev => ({ ...prev, [key]: value }));
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
          <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-green-500 to-blue-500 shadow-[0_0_20px_5px_rgba(34,197,94,0.5)] z-10 rounded-t-xl"></div>
          
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
                  <Upload className="w-5 h-5 text-green-600 dark:text-green-400" />
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Import Project
                  </h2>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Import from Archon export file
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
              {/* File Upload */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                  Select Export File
                </label>
                
                <div
                  onDrop={handleDrop}
                  onDragOver={(e) => e.preventDefault()}
                  onClick={() => fileInputRef.current?.click()}
                  className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center cursor-pointer hover:border-green-400 dark:hover:border-green-500 transition-colors"
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".zip"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                  
                  {selectedFile ? (
                    <div className="space-y-2">
                      <FileText className="w-8 h-8 text-green-500 mx-auto" />
                      <div className="text-sm font-medium text-gray-900 dark:text-white">
                        {selectedFile.name}
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        {formatFileSize(selectedFile.size)}
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <Upload className="w-8 h-8 text-gray-400 mx-auto" />
                      <div className="text-sm text-gray-600 dark:text-gray-400">
                        Click to select or drag and drop
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-500">
                        ZIP files only
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Validation Results */}
              {selectedFile && (
                <div className="space-y-3">
                  {isValidating ? (
                    <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                      <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                      Validating file...
                    </div>
                  ) : validation ? (
                    <div className={`p-3 rounded-lg border ${
                      validation.valid 
                        ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800' 
                        : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
                    }`}>
                      <div className="flex items-center gap-2 mb-2">
                        {validation.valid ? (
                          <CheckCircle className="w-4 h-4 text-green-600 dark:text-green-400" />
                        ) : (
                          <AlertTriangle className="w-4 h-4 text-red-600 dark:text-red-400" />
                        )}
                        <span className={`text-sm font-medium ${
                          validation.valid 
                            ? 'text-green-800 dark:text-green-200' 
                            : 'text-red-800 dark:text-red-200'
                        }`}>
                          {validation.valid ? 'Valid Export File' : 'Invalid Export File'}
                        </span>
                      </div>
                      
                      {validation.valid && (
                        <div className="text-xs text-green-700 dark:text-green-300 space-y-1">
                          <div>Project: {validation.project_title}</div>
                          <div>Tasks: {validation.task_count || 0} | Documents: {validation.document_count || 0}</div>
                          {validation.export_timestamp && (
                            <div>Exported: {new Date(validation.export_timestamp).toLocaleDateString()}</div>
                          )}
                        </div>
                      )}
                      
                      {!validation.valid && validation.error && (
                        <div className="text-xs text-red-700 dark:text-red-300">
                          {validation.error}
                        </div>
                      )}
                    </div>
                  ) : null}
                </div>
              )}

              {/* Import Options */}
              {validation?.valid && (
                <div className="space-y-4">
                  {/* Import Type */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                      Import Type
                    </label>
                    <div className="space-y-2">
                      {[
                        { value: 'full', label: 'Full Import', desc: 'Create new project', icon: Package },
                        { value: 'merge', label: 'Merge Import', desc: 'Merge into existing project', icon: Merge }
                      ].map(({ value, label, desc, icon: Icon }) => (
                        <label key={value} className="flex items-center p-3 border border-gray-200 dark:border-gray-600 rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50">
                          <input
                            type="radio"
                            name="importType"
                            value={value}
                            checked={importOptions.import_type === value}
                            onChange={(e) => handleOptionChange('import_type', e.target.value)}
                            className="sr-only"
                          />
                          <div className={`w-4 h-4 rounded-full border-2 mr-3 ${
                            importOptions.import_type === value 
                              ? 'border-green-500 bg-green-500' 
                              : 'border-gray-300 dark:border-gray-600'
                          }`}>
                            {importOptions.import_type === value && (
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

                  {/* Conflict Resolution */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Conflict Resolution
                    </label>
                    <select
                      value={importOptions.conflict_resolution}
                      onChange={(e) => handleOptionChange('conflict_resolution', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    >
                      <option value="merge">Merge with existing data</option>
                      <option value="overwrite">Overwrite existing data</option>
                      <option value="skip">Skip conflicting items</option>
                      <option value="fail">Fail on conflicts</option>
                    </select>
                  </div>

                  {/* Dry Run Option */}
                  <label className="flex items-center p-2 hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded-lg cursor-pointer">
                    <input
                      type="checkbox"
                      checked={importOptions.dry_run}
                      onChange={(e) => handleOptionChange('dry_run', e.target.checked)}
                      className="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
                    />
                    <Info className="w-4 h-4 text-gray-400 ml-3 mr-2" />
                    <span className="text-sm text-gray-700 dark:text-gray-300">
                      Dry run (validate only, don't import)
                    </span>
                  </label>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
              <Button
                variant="ghost"
                onClick={onClose}
                disabled={isImporting}
              >
                Cancel
              </Button>
              <Button
                variant="primary"
                accentColor="green"
                onClick={handleImport}
                disabled={!selectedFile || !validation?.valid || isImporting}
                icon={isImporting ? undefined : <Upload className="w-4 h-4" />}
              >
                {isImporting ? 'Importing...' : importOptions.dry_run ? 'Validate Import' : 'Import Project'}
              </Button>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>,
    document.body
  );
};
