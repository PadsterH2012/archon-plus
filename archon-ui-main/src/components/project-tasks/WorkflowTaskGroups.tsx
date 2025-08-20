import React, { useState, useEffect } from 'react';
import { 
  Play, 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  Settings, 
  FileText, 
  Server, 
  Home,
  GitBranch,
  Filter,
  Search
} from 'lucide-react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { TaskGroupService } from '../../services/taskGroupService';
import { WorkflowTaskGroup, WorkflowExecution } from '../../types/workflow';
import type { Project } from '../../types/project';

interface WorkflowTaskGroupsProps {
  project: Project;
  onTaskGroupExecute?: (taskGroup: WorkflowTaskGroup, execution: WorkflowExecution) => void;
}

export const WorkflowTaskGroups: React.FC<WorkflowTaskGroupsProps> = ({
  project,
  onTaskGroupExecute
}) => {
  const [taskGroups, setTaskGroups] = useState<WorkflowTaskGroup[]>([]);
  const [filteredGroups, setFilteredGroups] = useState<WorkflowTaskGroup[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedPhase, setSelectedPhase] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [executions, setExecutions] = useState<WorkflowExecution[]>([]);

  const taskGroupService = TaskGroupService.getInstance();

  useEffect(() => {
    // Load task groups
    const groups = taskGroupService.getTaskGroups();
    setTaskGroups(groups);
    setFilteredGroups(groups);

    // Load existing executions for this project
    const projectExecutions = taskGroupService.getProjectExecutions(project.id);
    setExecutions(projectExecutions);
  }, [project.id]);

  useEffect(() => {
    // Apply filters
    let filtered = taskGroups;

    if (selectedCategory !== 'all') {
      filtered = filtered.filter(group => group.category === selectedCategory);
    }

    if (selectedPhase !== 'all') {
      filtered = filtered.filter(group => 
        group.applicablePhases.includes(selectedPhase as any)
      );
    }

    if (searchQuery) {
      filtered = taskGroupService.searchTaskGroups(searchQuery);
    }

    setFilteredGroups(filtered);
  }, [selectedCategory, selectedPhase, searchQuery, taskGroups]);

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'documentation': return <FileText className="h-4 w-4" />;
      case 'deployment': return <GitBranch className="h-4 w-4" />;
      case 'infrastructure': return <Server className="h-4 w-4" />;
      case 'operations': return <Home className="h-4 w-4" />;
      default: return <Settings className="h-4 w-4" />;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'documentation': return 'blue';
      case 'deployment': return 'green';
      case 'infrastructure': return 'purple';
      case 'operations': return 'orange';
      default: return 'gray';
    }
  };

  const handleExecuteTaskGroup = async (taskGroup: WorkflowTaskGroup) => {
    try {
      const execution = await taskGroupService.createExecution(
        project.id,
        taskGroup.id,
        {
          projectType: 'web-application', // Could be determined from project
          hasAPI: true, // Could be determined from project
          hasDatabase: true, // Could be determined from project
          requiresDeployment: true,
          isHomelabProject: project.title.toLowerCase().includes('homelab')
        }
      );

      setExecutions(prev => [...prev, execution]);
      
      if (onTaskGroupExecute) {
        onTaskGroupExecute(taskGroup, execution);
      }

      // In a real implementation, this would trigger the actual execution
      console.log(`Started execution of task group: ${taskGroup.name}`);
    } catch (error) {
      console.error('Failed to execute task group:', error);
    }
  };

  const getExecutionStatus = (taskGroupId: string) => {
    const execution = executions.find(exec => exec.taskGroupId === taskGroupId);
    return execution?.status || 'not-started';
  };

  const categories = ['all', 'documentation', 'deployment', 'infrastructure', 'operations'];
  const phases = ['all', 'planning', 'development', 'testing', 'deployment', 'maintenance'];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            Workflow Task Groups
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Reusable operational workflows for standardized project tasks
          </p>
        </div>
      </div>

      {/* Filters */}
      <Card className="p-4" accentColor="none">
        <div className="space-y-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search task groups..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
                       bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100
                       focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>

          {/* Category and Phase Filters */}
          <div className="flex flex-wrap gap-4">
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Category:</span>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md
                         bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 text-sm"
              >
                {categories.map(category => (
                  <option key={category} value={category}>
                    {category.charAt(0).toUpperCase() + category.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Phase:</span>
              <select
                value={selectedPhase}
                onChange={(e) => setSelectedPhase(e.target.value)}
                className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md
                         bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 text-sm"
              >
                {phases.map(phase => (
                  <option key={phase} value={phase}>
                    {phase.charAt(0).toUpperCase() + phase.slice(1)}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </Card>

      {/* Task Groups Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredGroups.map(taskGroup => {
          const stats = taskGroupService.getTaskGroupStats(taskGroup.id);
          const executionStatus = getExecutionStatus(taskGroup.id);
          
          return (
            <Card key={taskGroup.id} className="p-6" accentColor={getCategoryColor(taskGroup.category)}>
              <div className="space-y-4">
                {/* Header */}
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    {getCategoryIcon(taskGroup.category)}
                    <div>
                      <h4 className="font-semibold text-gray-900 dark:text-gray-100">
                        {taskGroup.name}
                      </h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        v{taskGroup.version}
                      </p>
                    </div>
                  </div>
                  <Badge 
                    color={executionStatus === 'completed' ? 'green' : 
                           executionStatus === 'running' ? 'blue' :
                           executionStatus === 'failed' ? 'red' : 'gray'}
                    size="sm"
                  >
                    {executionStatus === 'not-started' ? 'Ready' : executionStatus}
                  </Badge>
                </div>

                {/* Description */}
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {taskGroup.description}
                </p>

                {/* Stats */}
                {stats && (
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span className="text-gray-600 dark:text-gray-400">
                        {stats.totalTasks} tasks
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4 text-blue-500" />
                      <span className="text-gray-600 dark:text-gray-400">
                        ~{stats.estimatedDuration}m
                      </span>
                    </div>
                  </div>
                )}

                {/* Required Tools */}
                <div className="flex flex-wrap gap-1">
                  {taskGroup.requiredTools.slice(0, 3).map(tool => (
                    <Badge key={tool} color="gray" size="xs">
                      {tool}
                    </Badge>
                  ))}
                  {taskGroup.requiredTools.length > 3 && (
                    <Badge color="gray" size="xs">
                      +{taskGroup.requiredTools.length - 3} more
                    </Badge>
                  )}
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  <Button
                    onClick={() => handleExecuteTaskGroup(taskGroup)}
                    disabled={executionStatus === 'running'}
                    variant="primary"
                    size="sm"
                    className="flex items-center gap-2"
                  >
                    <Play className="h-3 w-3" />
                    {executionStatus === 'running' ? 'Running...' : 'Execute'}
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      // Show task group details modal
                      console.log('Show details for:', taskGroup.id);
                    }}
                  >
                    Details
                  </Button>
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      {filteredGroups.length === 0 && (
        <Card className="p-8 text-center" accentColor="none">
          <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-600 dark:text-gray-400">
            No task groups found matching your criteria
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-500 mt-1">
            Try adjusting your filters or search query
          </p>
        </Card>
      )}
    </div>
  );
};
