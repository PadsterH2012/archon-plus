import React, { useState, useCallback } from 'react';
import { 
  Plus, 
  Edit, 
  Trash2, 
  GitBranch, 
  AlertTriangle,
  CheckCircle,
  Clock,
  Target,
  Settings,
  Eye
} from 'lucide-react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { Select } from '../ui/Select';
import type { 
  AssignmentManagerProps,
  TemplateAssignment,
  HierarchyNode,
  AssignmentConflict,
  HierarchyLevel
} from '../../types/templateManagement';

export const AssignmentManager: React.FC<AssignmentManagerProps> = ({
  projectId,
  hierarchyData,
  assignments,
  onAssignmentCreate,
  onAssignmentUpdate,
  onAssignmentDelete,
  onConflictResolve,
  className = ''
}) => {
  const [selectedLevel, setSelectedLevel] = useState<HierarchyLevel | ''>('');
  const [showConflicts, setShowConflicts] = useState(false);
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());

  // Mock conflicts for demonstration
  const mockConflicts: AssignmentConflict[] = [
    {
      entity_id: 'project-1',
      entity_name: 'OAuth Implementation Project',
      hierarchy_level: 'project' as HierarchyLevel,
      conflicting_assignments: assignments.slice(0, 2),
      recommended_resolution: 'use_highest_priority',
      impact_assessment: 'Low impact - templates are compatible'
    }
  ];

  const handleNodeToggle = useCallback((nodeId: string) => {
    setExpandedNodes(prev => {
      const newSet = new Set(prev);
      if (newSet.has(nodeId)) {
        newSet.delete(nodeId);
      } else {
        newSet.add(nodeId);
      }
      return newSet;
    });
  }, []);

  const handleCreateAssignment = useCallback(() => {
    onAssignmentCreate?.({
      template_name: 'workflow_default',
      hierarchy_level: 'project' as HierarchyLevel,
      entity_id: projectId,
      assignment_scope: 'all',
      priority: 0
    });
  }, [onAssignmentCreate, projectId]);

  const handleEditAssignment = useCallback((assignment: TemplateAssignment) => {
    onAssignmentUpdate?.(assignment.id, {
      priority: assignment.priority + 1
    });
  }, [onAssignmentUpdate]);

  const handleDeleteAssignment = useCallback((assignment: TemplateAssignment) => {
    onAssignmentDelete?.(assignment.id);
  }, [onAssignmentDelete]);

  const getAssignmentsByLevel = (level: HierarchyLevel) => {
    return assignments.filter(a => a.hierarchy_level === level);
  };

  const getAssignmentIcon = (level: HierarchyLevel) => {
    switch (level) {
      case 'global': return '🌐';
      case 'project': return '📁';
      case 'milestone': return '🎯';
      case 'phase': return '📋';
      case 'task': return '✅';
      default: return '📄';
    }
  };

  const getPriorityColor = (priority: number) => {
    if (priority >= 20) return 'error';
    if (priority >= 10) return 'warning';
    if (priority >= 5) return 'info';
    return 'secondary';
  };

  const filteredAssignments = selectedLevel 
    ? assignments.filter(a => a.hierarchy_level === selectedLevel)
    : assignments;

  return (
    <div className={`assignment-manager ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">
            Template Assignments
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Manage template assignments across hierarchy levels
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowConflicts(!showConflicts)}
          >
            <AlertTriangle className="h-4 w-4 mr-2" />
            Conflicts ({mockConflicts.length})
          </Button>
          
          <Button
            variant="primary"
            size="sm"
            onClick={handleCreateAssignment}
          >
            <Plus className="h-4 w-4 mr-2" />
            New Assignment
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <div className="p-4">
          <div className="flex items-center gap-4">
            <Select
              value={selectedLevel}
              onChange={(value) => setSelectedLevel(value as HierarchyLevel | '')}
              placeholder="All Levels"
              className="w-48"
            >
              <option value="">All Levels</option>
              <option value="global">Global</option>
              <option value="project">Project</option>
              <option value="milestone">Milestone</option>
              <option value="phase">Phase</option>
              <option value="task">Task</option>
            </Select>
            
            <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
              <span>Total Assignments:</span>
              <Badge variant="secondary">{filteredAssignments.length}</Badge>
            </div>
          </div>
        </div>
      </Card>

      {/* Conflicts Panel */}
      {showConflicts && mockConflicts.length > 0 && (
        <Card className="mb-6" accentColor="yellow">
          <div className="p-4">
            <div className="flex items-center gap-2 mb-3">
              <AlertTriangle className="h-5 w-5 text-yellow-500" />
              <h4 className="font-medium text-gray-900 dark:text-gray-100">
                Assignment Conflicts
              </h4>
            </div>
            
            <div className="space-y-3">
              {mockConflicts.map((conflict, index) => (
                <div key={index} className="border border-yellow-200 dark:border-yellow-800 rounded-md p-3">
                  <div className="flex items-start justify-between">
                    <div>
                      <h5 className="font-medium text-gray-900 dark:text-gray-100">
                        {conflict.entity_name}
                      </h5>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        {conflict.impact_assessment}
                      </p>
                      <div className="flex items-center gap-2 mt-2">
                        <Badge variant="warning" size="sm">
                          {conflict.hierarchy_level}
                        </Badge>
                        <span className="text-xs text-gray-500">
                          {conflict.conflicting_assignments.length} conflicting assignments
                        </span>
                      </div>
                    </div>
                    
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => onConflictResolve?.(conflict)}
                    >
                      Resolve
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </Card>
      )}

      {/* Assignments List */}
      {filteredAssignments.length === 0 ? (
        <Card>
          <div className="p-8 text-center">
            <GitBranch className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
              No assignments found
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              {selectedLevel
                ? `No assignments found for ${selectedLevel} level.`
                : 'No template assignments have been created yet.'
              }
            </p>
            <Button variant="primary" onClick={handleCreateAssignment}>
              <Plus className="h-4 w-4 mr-2" />
              Create Assignment
            </Button>
          </div>
        </Card>
      ) : (
        <div className="space-y-4">
          {filteredAssignments.map((assignment) => (
            <Card key={assignment.id} className="hover:shadow-md transition-shadow">
              <div className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    {/* Assignment Header */}
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-lg">
                        {getAssignmentIcon(assignment.hierarchy_level)}
                      </span>
                      <div>
                        <h4 className="font-medium text-gray-900 dark:text-gray-100">
                          {assignment.template_name}
                        </h4>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {assignment.hierarchy_level} level assignment
                        </p>
                      </div>
                    </div>

                    {/* Assignment Details */}
                    <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400 mb-3">
                      <div className="flex items-center gap-1">
                        <Target className="h-4 w-4" />
                        <span>Priority: {assignment.priority}</span>
                      </div>
                      
                      <div className="flex items-center gap-1">
                        <Settings className="h-4 w-4" />
                        <span>Scope: {assignment.assignment_scope}</span>
                      </div>
                      
                      {assignment.entity_type && (
                        <div className="flex items-center gap-1">
                          <span>Type: {assignment.entity_type}</span>
                        </div>
                      )}
                      
                      {assignment.effective_until && (
                        <div className="flex items-center gap-1">
                          <Clock className="h-4 w-4" />
                          <span>Expires: {new Date(assignment.effective_until).toLocaleDateString()}</span>
                        </div>
                      )}
                    </div>

                    {/* Assignment Badges */}
                    <div className="flex items-center gap-2">
                      <Badge 
                        variant={getPriorityColor(assignment.priority)}
                        size="sm"
                      >
                        Priority {assignment.priority}
                      </Badge>
                      
                      <Badge 
                        variant={assignment.is_active ? 'success' : 'secondary'}
                        size="sm"
                      >
                        {assignment.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                      
                      <Badge variant="info" size="sm">
                        {assignment.hierarchy_level}
                      </Badge>
                      
                      {assignment.inheritance_enabled && (
                        <Badge variant="secondary" size="sm">
                          Inheritable
                        </Badge>
                      )}
                    </div>

                    {/* Entity Information */}
                    {assignment.entity_id && (
                      <div className="mt-3 text-xs text-gray-500">
                        Entity ID: {assignment.entity_id}
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 ml-4">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleEditAssignment(assignment)}
                      title="Edit Assignment"
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDeleteAssignment(assignment)}
                      title="Delete Assignment"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>

                {/* Conditional Logic Preview */}
                {assignment.conditional_logic && Object.keys(assignment.conditional_logic).length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                    <div className="flex items-center gap-2 text-sm">
                      <Eye className="h-4 w-4 text-gray-400" />
                      <span className="text-gray-600 dark:text-gray-400">
                        Has conditional logic
                      </span>
                      <Badge variant="info" size="xs">
                        {Object.keys(assignment.conditional_logic).length} rules
                      </Badge>
                    </div>
                  </div>
                )}

                {/* Metadata Preview */}
                {assignment.metadata && Object.keys(assignment.metadata).length > 0 && (
                  <div className="mt-2">
                    <div className="flex items-center gap-2 text-sm">
                      <span className="text-gray-600 dark:text-gray-400">
                        Additional metadata available
                      </span>
                      <Badge variant="secondary" size="xs">
                        {Object.keys(assignment.metadata).length} fields
                      </Badge>
                    </div>
                  </div>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Summary Stats */}
      <Card className="mt-6">
        <div className="p-4">
          <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-3">
            Assignment Summary
          </h4>
          
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-center">
            {(['global', 'project', 'milestone', 'phase', 'task'] as HierarchyLevel[]).map(level => {
              const levelAssignments = getAssignmentsByLevel(level);
              return (
                <div key={level} className="text-sm">
                  <div className="text-2xl mb-1">
                    {getAssignmentIcon(level)}
                  </div>
                  <div className="font-medium text-gray-900 dark:text-gray-100">
                    {levelAssignments.length}
                  </div>
                  <div className="text-gray-600 dark:text-gray-400 capitalize">
                    {level}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </Card>
    </div>
  );
};
