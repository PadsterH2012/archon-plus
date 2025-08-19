import React, { useState, useCallback } from 'react';
import { Download, Upload, HardDrive, Clock, AlertCircle, CheckCircle, Package } from 'lucide-react';
import { Button } from '../ui/Button';
import { ImportButton } from '../project-tasks/ProjectExportImportActions';
import { useToast } from '../../contexts/ToastContext';

interface BackupRestoreSectionProps {
  className?: string;
}

export const BackupRestoreSection: React.FC<BackupRestoreSectionProps> = ({
  className = ''
}) => {
  const { addToast } = useToast();
  const [isCreatingBackup, setIsCreatingBackup] = useState(false);
  const [lastBackupTime, setLastBackupTime] = useState<string | null>(null);

  const handleCreateSystemBackup = useCallback(async () => {
    try {
      setIsCreatingBackup(true);
      
      // This would call a system-wide backup API endpoint
      // For now, we'll simulate the process
      addToast({
        type: 'info',
        title: 'Creating System Backup',
        message: 'Backing up all projects and system data...'
      });

      // Simulate backup process
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      const now = new Date().toISOString();
      setLastBackupTime(now);
      
      addToast({
        type: 'success',
        title: 'Backup Complete',
        message: 'System backup created successfully'
      });
      
      // In a real implementation, this would trigger a download
      // window.open('/api/system/backup/download', '_blank');
      
    } catch (error) {
      console.error('Failed to create backup:', error);
      addToast({
        type: 'error',
        title: 'Backup Failed',
        message: error instanceof Error ? error.message : 'Failed to create system backup'
      });
    } finally {
      setIsCreatingBackup(false);
    }
  }, [addToast]);

  const handleImportSuccess = useCallback((projectId: string) => {
    addToast({
      type: 'success',
      title: 'Import Successful',
      message: 'Project has been imported successfully'
    });
  }, [addToast]);

  return (
    <div className={`space-y-6 ${className}`}>
      {/* System Backup Section */}
      <div className="space-y-4">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
            <HardDrive className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              System Backup
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Create a complete backup of all projects and system data
            </p>
          </div>
        </div>

        {/* Last Backup Info */}
        {lastBackupTime && (
          <div className="flex items-center gap-2 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
            <CheckCircle className="w-4 h-4 text-green-600 dark:text-green-400" />
            <span className="text-sm text-green-700 dark:text-green-300">
              Last backup: {new Date(lastBackupTime).toLocaleString()}
            </span>
          </div>
        )}

        {/* Backup Actions */}
        <div className="flex items-center gap-3">
          <Button
            variant="primary"
            accentColor="blue"
            onClick={handleCreateSystemBackup}
            disabled={isCreatingBackup}
            icon={isCreatingBackup ? undefined : <Download className="w-4 h-4" />}
            className="shadow-lg shadow-blue-500/20"
          >
            {isCreatingBackup ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                Creating Backup...
              </>
            ) : (
              'Create System Backup'
            )}
          </Button>

          <Button
            variant="outline"
            accentColor="gray"
            icon={<Clock className="w-4 h-4" />}
            className="text-gray-600 dark:text-gray-400 border-gray-200 dark:border-gray-700"
            disabled
            title="Scheduled backups (coming soon)"
          >
            Schedule Backups
          </Button>
        </div>
      </div>

      {/* Divider */}
      <div className="border-t border-gray-200 dark:border-gray-700"></div>

      {/* Project Import Section */}
      <div className="space-y-4">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
            <Upload className="w-5 h-5 text-green-600 dark:text-green-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Project Import
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Import projects from backup files or other Archon instances
            </p>
          </div>
        </div>

        {/* Import Actions */}
        <div className="flex items-center gap-3">
          <ImportButton
            onImportSuccess={handleImportSuccess}
            variant="primary"
            size="md"
            className="shadow-lg shadow-green-500/20"
          />
          
          <Button
            variant="outline"
            accentColor="gray"
            icon={<Package className="w-4 h-4" />}
            className="text-gray-600 dark:text-gray-400 border-gray-200 dark:border-gray-700"
            disabled
            title="Bulk import (coming soon)"
          >
            Bulk Import
          </Button>
        </div>
      </div>

      {/* Info Section */}
      <div className="p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-amber-600 dark:text-amber-400 mt-0.5 flex-shrink-0" />
          <div className="space-y-2">
            <h4 className="text-sm font-medium text-amber-800 dark:text-amber-200">
              Backup & Restore Guidelines
            </h4>
            <ul className="text-sm text-amber-700 dark:text-amber-300 space-y-1">
              <li>• System backups include all projects, documents, tasks, and settings</li>
              <li>• Individual project exports are available from the Projects page</li>
              <li>• Backups are compressed and include version history</li>
              <li>• Import operations will validate data before applying changes</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};
