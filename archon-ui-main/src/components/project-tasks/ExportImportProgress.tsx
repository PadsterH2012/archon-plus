import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  CheckCircle, 
  AlertCircle, 
  Download, 
  Upload, 
  X,
  Clock,
  FileText,
  Database,
  Package
} from 'lucide-react';
import { Button } from '../ui/Button';
import { formatFileSize } from '../../services/exportImportService';

interface ProgressStep {
  id: string;
  label: string;
  status: 'pending' | 'active' | 'completed' | 'error';
  message?: string;
  progress?: number;
}

interface ExportImportProgressProps {
  isOpen: boolean;
  onClose: () => void;
  operation: 'export' | 'import';
  projectTitle?: string;
  fileName?: string;
  fileSize?: number;
  steps: ProgressStep[];
  overallProgress: number;
  isComplete: boolean;
  hasError: boolean;
  errorMessage?: string;
  onDownload?: () => void;
  onRetry?: () => void;
  isDarkMode?: boolean;
}

export const ExportImportProgress: React.FC<ExportImportProgressProps> = ({
  isOpen,
  onClose,
  operation,
  projectTitle,
  fileName,
  fileSize,
  steps,
  overallProgress,
  isComplete,
  hasError,
  errorMessage,
  onDownload,
  onRetry,
  isDarkMode = false
}) => {
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [startTime] = useState(Date.now());

  useEffect(() => {
    if (!isOpen || isComplete) return;

    const interval = setInterval(() => {
      setTimeElapsed(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);

    return () => clearInterval(interval);
  }, [isOpen, isComplete, startTime]);

  const formatTime = useCallback((seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }, []);

  const getOperationIcon = () => {
    if (operation === 'export') {
      return <Download className="w-6 h-6 text-blue-600 dark:text-blue-400" />;
    }
    return <Upload className="w-6 h-6 text-green-600 dark:text-green-400" />;
  };

  const getStepIcon = (step: ProgressStep) => {
    switch (step.status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      case 'active':
        return (
          <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
        );
      default:
        return <div className="w-4 h-4 border-2 border-gray-300 dark:border-gray-600 rounded-full" />;
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="relative w-full max-w-md"
        >
          {/* Accent line */}
          <div className={`absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r ${
            operation === 'export' 
              ? 'from-blue-500 to-purple-500 shadow-[0_0_20px_5px_rgba(59,130,246,0.5)]'
              : 'from-green-500 to-blue-500 shadow-[0_0_20px_5px_rgba(34,197,94,0.5)]'
          } z-10 rounded-t-xl`}></div>
          
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${
                  operation === 'export' 
                    ? 'bg-blue-100 dark:bg-blue-900/30' 
                    : 'bg-green-100 dark:bg-green-900/30'
                }`}>
                  {getOperationIcon()}
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                    {operation === 'export' ? 'Exporting Project' : 'Importing Project'}
                  </h2>
                  {projectTitle && (
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {projectTitle}
                    </p>
                  )}
                </div>
              </div>
              {isComplete && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onClose}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                >
                  <X className="w-5 h-5" />
                </Button>
              )}
            </div>

            {/* Progress Content */}
            <div className="p-6 space-y-6">
              {/* Overall Progress */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Overall Progress
                  </span>
                  <span className="text-sm text-gray-500 dark:text-gray-400">
                    {Math.round(overallProgress)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <motion.div
                    className={`h-2 rounded-full ${
                      hasError 
                        ? 'bg-red-500' 
                        : isComplete 
                        ? 'bg-green-500' 
                        : operation === 'export'
                        ? 'bg-blue-500'
                        : 'bg-green-500'
                    }`}
                    initial={{ width: 0 }}
                    animate={{ width: `${overallProgress}%` }}
                    transition={{ duration: 0.5 }}
                  />
                </div>
              </div>

              {/* File Info */}
              {fileName && (
                <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                  <FileText className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                  <div className="flex-1">
                    <div className="text-sm font-medium text-gray-900 dark:text-white">
                      {fileName}
                    </div>
                    {fileSize && (
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        {formatFileSize(fileSize)}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Steps */}
              <div className="space-y-3">
                <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Progress Steps
                </h3>
                <div className="space-y-2">
                  {steps.map((step, index) => (
                    <motion.div
                      key={step.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="flex items-center gap-3 p-2 rounded-lg"
                    >
                      {getStepIcon(step)}
                      <div className="flex-1">
                        <div className={`text-sm ${
                          step.status === 'completed' 
                            ? 'text-green-700 dark:text-green-300' 
                            : step.status === 'error'
                            ? 'text-red-700 dark:text-red-300'
                            : step.status === 'active'
                            ? 'text-blue-700 dark:text-blue-300'
                            : 'text-gray-500 dark:text-gray-400'
                        }`}>
                          {step.label}
                        </div>
                        {step.message && (
                          <div className="text-xs text-gray-500 dark:text-gray-400">
                            {step.message}
                          </div>
                        )}
                        {step.progress !== undefined && step.status === 'active' && (
                          <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-1 mt-1">
                            <div 
                              className="h-1 bg-blue-500 rounded-full transition-all duration-300"
                              style={{ width: `${step.progress}%` }}
                            />
                          </div>
                        )}
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>

              {/* Time Elapsed */}
              {!isComplete && (
                <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                  <Clock className="w-4 h-4" />
                  Time elapsed: {formatTime(timeElapsed)}
                </div>
              )}

              {/* Error Message */}
              {hasError && errorMessage && (
                <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                  <div className="flex items-center gap-2 mb-1">
                    <AlertCircle className="w-4 h-4 text-red-600 dark:text-red-400" />
                    <span className="text-sm font-medium text-red-800 dark:text-red-200">
                      Operation Failed
                    </span>
                  </div>
                  <div className="text-sm text-red-700 dark:text-red-300">
                    {errorMessage}
                  </div>
                </div>
              )}

              {/* Success Message */}
              {isComplete && !hasError && (
                <div className="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                  <div className="flex items-center gap-2 mb-1">
                    <CheckCircle className="w-4 h-4 text-green-600 dark:text-green-400" />
                    <span className="text-sm font-medium text-green-800 dark:text-green-200">
                      {operation === 'export' ? 'Export Complete' : 'Import Complete'}
                    </span>
                  </div>
                  <div className="text-sm text-green-700 dark:text-green-300">
                    {operation === 'export' 
                      ? 'Your project has been exported successfully.' 
                      : 'Your project has been imported successfully.'}
                  </div>
                </div>
              )}
            </div>

            {/* Footer */}
            {(isComplete || hasError) && (
              <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
                {hasError && onRetry && (
                  <Button
                    variant="outline"
                    onClick={onRetry}
                    className="text-red-600 dark:text-red-400 border-red-200 dark:border-red-800"
                  >
                    Retry
                  </Button>
                )}
                {isComplete && !hasError && onDownload && operation === 'export' && (
                  <Button
                    variant="primary"
                    accentColor="blue"
                    onClick={onDownload}
                    icon={<Download className="w-4 h-4" />}
                  >
                    Download
                  </Button>
                )}
                <Button
                  variant={isComplete && !hasError ? "ghost" : "primary"}
                  onClick={onClose}
                >
                  {isComplete || hasError ? 'Close' : 'Cancel'}
                </Button>
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};
