"""
Backup Scheduler Service for Archon

This module provides automated backup scheduling functionality using cron-like expressions
and background task management. Supports:
- Cron-based scheduling
- Interval-based scheduling  
- Backup retention policy enforcement
- Health monitoring and alerting
- Schedule management and persistence
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from croniter import croniter

from ...config.logfire_config import get_logger
from ...utils import get_supabase_client
from ..background_task_manager import get_task_manager
from .backup_manager import get_backup_manager

logger = get_logger(__name__)


class BackupScheduler:
    """Manages automated backup scheduling and execution"""
    
    def __init__(self, supabase_client=None):
        self.supabase_client = supabase_client or get_supabase_client()
        self.backup_manager = get_backup_manager()
        self.task_manager = get_task_manager()
        self.active_schedules: Dict[str, asyncio.Task] = {}
        self.is_running = False
        
    async def start_scheduler(self):
        """Start the backup scheduler service"""
        if self.is_running:
            logger.warning("Backup scheduler is already running")
            return
            
        self.is_running = True
        logger.info("Starting backup scheduler service")
        
        # Load existing schedules from database
        await self._load_schedules()
        
        # Start the main scheduler loop
        asyncio.create_task(self._scheduler_loop())
        
        logger.info("Backup scheduler started successfully")
    
    async def stop_scheduler(self):
        """Stop the backup scheduler service"""
        if not self.is_running:
            return
            
        self.is_running = False
        logger.info("Stopping backup scheduler service")
        
        # Cancel all active schedule tasks
        for schedule_id, task in self.active_schedules.items():
            task.cancel()
            logger.info(f"Cancelled schedule task | schedule_id={schedule_id}")
        
        self.active_schedules.clear()
        logger.info("Backup scheduler stopped")
    
    async def create_schedule(
        self,
        project_id: str,
        schedule_type: str = "cron",
        cron_expression: Optional[str] = None,
        interval_minutes: Optional[int] = None,
        backup_type: str = "full",
        enabled: bool = True,
        created_by: str = "system"
    ) -> Tuple[bool, Dict[str, Any]]:
        """Create a new backup schedule"""
        try:
            schedule_id = str(uuid4())
            
            # Validate schedule parameters
            if schedule_type == "cron" and not cron_expression:
                return False, {"error": "Cron expression required for cron schedule"}
            
            if schedule_type == "interval" and not interval_minutes:
                return False, {"error": "Interval minutes required for interval schedule"}
            
            # Validate cron expression
            if schedule_type == "cron":
                try:
                    croniter(cron_expression)
                except Exception as e:
                    return False, {"error": f"Invalid cron expression: {str(e)}"}
            
            # Calculate next run time
            next_run = self._calculate_next_run(schedule_type, cron_expression, interval_minutes)
            
            # Create schedule record
            schedule_data = {
                "id": schedule_id,
                "project_id": project_id,
                "schedule_type": schedule_type,
                "cron_expression": cron_expression,
                "interval_minutes": interval_minutes,
                "backup_type": backup_type,
                "enabled": enabled,
                "created_by": created_by,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "last_run": None,
                "next_run": next_run.isoformat() if next_run else None,
                "run_count": 0,
                "last_status": "pending",
                "last_error": None
            }
            
            # Insert into database
            response = (
                self.supabase_client.table("archon_backup_schedules")
                .insert(schedule_data)
                .execute()
            )
            
            if not response.data:
                return False, {"error": "Failed to create schedule in database"}
            
            # Start the schedule if enabled
            if enabled:
                await self._start_schedule(schedule_id, schedule_data)
            
            logger.info(f"Backup schedule created | schedule_id={schedule_id} | project_id={project_id}")
            
            return True, {
                "schedule_id": schedule_id,
                "schedule": schedule_data,
                "message": "Backup schedule created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating backup schedule | project_id={project_id} | error={str(e)}")
            return False, {"error": f"Failed to create schedule: {str(e)}"}
    
    async def update_schedule(
        self,
        schedule_id: str,
        updates: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Update an existing backup schedule"""
        try:
            # Get current schedule
            response = (
                self.supabase_client.table("archon_backup_schedules")
                .select("*")
                .eq("id", schedule_id)
                .execute()
            )
            
            if not response.data:
                return False, {"error": "Schedule not found"}
            
            current_schedule = response.data[0]
            
            # Validate updates
            if "cron_expression" in updates and updates["cron_expression"]:
                try:
                    croniter(updates["cron_expression"])
                except Exception as e:
                    return False, {"error": f"Invalid cron expression: {str(e)}"}
            
            # Update schedule data
            updates["updated_at"] = datetime.now().isoformat()
            
            # Recalculate next run if schedule parameters changed
            if any(key in updates for key in ["cron_expression", "interval_minutes", "schedule_type"]):
                schedule_type = updates.get("schedule_type", current_schedule["schedule_type"])
                cron_expression = updates.get("cron_expression", current_schedule["cron_expression"])
                interval_minutes = updates.get("interval_minutes", current_schedule["interval_minutes"])
                
                next_run = self._calculate_next_run(schedule_type, cron_expression, interval_minutes)
                updates["next_run"] = next_run.isoformat() if next_run else None
            
            # Update in database
            response = (
                self.supabase_client.table("archon_backup_schedules")
                .update(updates)
                .eq("id", schedule_id)
                .execute()
            )
            
            if not response.data:
                return False, {"error": "Failed to update schedule"}
            
            updated_schedule = response.data[0]
            
            # Restart schedule if it's active
            if schedule_id in self.active_schedules:
                await self._stop_schedule(schedule_id)
                
            if updated_schedule.get("enabled", False):
                await self._start_schedule(schedule_id, updated_schedule)
            
            logger.info(f"Backup schedule updated | schedule_id={schedule_id}")
            
            return True, {
                "schedule_id": schedule_id,
                "schedule": updated_schedule,
                "message": "Schedule updated successfully"
            }
            
        except Exception as e:
            logger.error(f"Error updating backup schedule | schedule_id={schedule_id} | error={str(e)}")
            return False, {"error": f"Failed to update schedule: {str(e)}"}
    
    async def delete_schedule(self, schedule_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Delete a backup schedule"""
        try:
            # Stop the schedule if it's running
            if schedule_id in self.active_schedules:
                await self._stop_schedule(schedule_id)
            
            # Delete from database
            response = (
                self.supabase_client.table("archon_backup_schedules")
                .delete()
                .eq("id", schedule_id)
                .execute()
            )
            
            if response.data:
                logger.info(f"Backup schedule deleted | schedule_id={schedule_id}")
                return True, {"message": "Schedule deleted successfully"}
            else:
                return False, {"error": "Schedule not found"}
                
        except Exception as e:
            logger.error(f"Error deleting backup schedule | schedule_id={schedule_id} | error={str(e)}")
            return False, {"error": f"Failed to delete schedule: {str(e)}"}
    
    async def list_schedules(self, project_id: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """List backup schedules"""
        try:
            query = self.supabase_client.table("archon_backup_schedules").select("*")
            
            if project_id:
                query = query.eq("project_id", project_id)
            
            response = query.execute()
            
            schedules = response.data or []
            
            return True, {
                "schedules": schedules,
                "total_count": len(schedules)
            }
            
        except Exception as e:
            logger.error(f"Error listing backup schedules | error={str(e)}")
            return False, {"error": f"Failed to list schedules: {str(e)}"}
    
    async def _load_schedules(self):
        """Load and start enabled schedules from database"""
        try:
            response = (
                self.supabase_client.table("archon_backup_schedules")
                .select("*")
                .eq("enabled", True)
                .execute()
            )
            
            schedules = response.data or []
            
            for schedule in schedules:
                await self._start_schedule(schedule["id"], schedule)
            
            logger.info(f"Loaded {len(schedules)} backup schedules")
            
        except Exception as e:
            logger.error(f"Error loading backup schedules | error={str(e)}")
    
    async def _start_schedule(self, schedule_id: str, schedule_data: Dict[str, Any]):
        """Start a specific backup schedule"""
        if schedule_id in self.active_schedules:
            return
        
        task = asyncio.create_task(self._schedule_task(schedule_id, schedule_data))
        self.active_schedules[schedule_id] = task
        
        logger.info(f"Started backup schedule | schedule_id={schedule_id}")
    
    async def _stop_schedule(self, schedule_id: str):
        """Stop a specific backup schedule"""
        if schedule_id in self.active_schedules:
            task = self.active_schedules[schedule_id]
            task.cancel()
            del self.active_schedules[schedule_id]
            
            logger.info(f"Stopped backup schedule | schedule_id={schedule_id}")
    
    async def _schedule_task(self, schedule_id: str, schedule_data: Dict[str, Any]):
        """Main task loop for a backup schedule"""
        try:
            while self.is_running:
                # Calculate next run time
                next_run = self._calculate_next_run(
                    schedule_data["schedule_type"],
                    schedule_data.get("cron_expression"),
                    schedule_data.get("interval_minutes")
                )
                
                if not next_run:
                    logger.error(f"Could not calculate next run time | schedule_id={schedule_id}")
                    break
                
                # Wait until next run time
                now = datetime.now()
                if next_run > now:
                    wait_seconds = (next_run - now).total_seconds()
                    await asyncio.sleep(wait_seconds)
                
                # Execute backup
                await self._execute_scheduled_backup(schedule_id, schedule_data)
                
                # Update last run time
                await self._update_schedule_run_time(schedule_id, datetime.now())
                
        except asyncio.CancelledError:
            logger.info(f"Schedule task cancelled | schedule_id={schedule_id}")
        except Exception as e:
            logger.error(f"Error in schedule task | schedule_id={schedule_id} | error={str(e)}")
    
    async def _execute_scheduled_backup(self, schedule_id: str, schedule_data: Dict[str, Any]):
        """Execute a scheduled backup"""
        try:
            project_id = schedule_data["project_id"]
            backup_type = schedule_data["backup_type"]
            
            logger.info(f"Executing scheduled backup | schedule_id={schedule_id} | project_id={project_id}")
            
            # Create backup
            success, result = await self.backup_manager.create_project_backup(
                project_id=project_id,
                backup_type=backup_type,
                created_by="scheduler"
            )
            
            # Update schedule status
            status_update = {
                "last_status": "success" if success else "failed",
                "run_count": schedule_data.get("run_count", 0) + 1,
                "last_error": None if success else result.get("error")
            }
            
            await self._update_schedule_status(schedule_id, status_update)
            
            if success:
                logger.info(f"Scheduled backup completed | schedule_id={schedule_id} | backup_id={result.get('backup_id')}")
            else:
                logger.error(f"Scheduled backup failed | schedule_id={schedule_id} | error={result.get('error')}")
                
        except Exception as e:
            logger.error(f"Error executing scheduled backup | schedule_id={schedule_id} | error={str(e)}")
            
            # Update schedule with error status
            await self._update_schedule_status(schedule_id, {
                "last_status": "error",
                "last_error": str(e)
            })
    
    def _calculate_next_run(
        self,
        schedule_type: str,
        cron_expression: Optional[str] = None,
        interval_minutes: Optional[int] = None
    ) -> Optional[datetime]:
        """Calculate the next run time for a schedule"""
        try:
            now = datetime.now()
            
            if schedule_type == "cron" and cron_expression:
                cron = croniter(cron_expression, now)
                return cron.get_next(datetime)
            
            elif schedule_type == "interval" and interval_minutes:
                return now + timedelta(minutes=interval_minutes)
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculating next run time | error={str(e)}")
            return None
    
    async def _update_schedule_run_time(self, schedule_id: str, run_time: datetime):
        """Update schedule last run time"""
        try:
            self.supabase_client.table("archon_backup_schedules").update({
                "last_run": run_time.isoformat()
            }).eq("id", schedule_id).execute()
            
        except Exception as e:
            logger.error(f"Error updating schedule run time | schedule_id={schedule_id} | error={str(e)}")
    
    async def _update_schedule_status(self, schedule_id: str, status_update: Dict[str, Any]):
        """Update schedule status information"""
        try:
            self.supabase_client.table("archon_backup_schedules").update(status_update).eq("id", schedule_id).execute()
            
        except Exception as e:
            logger.error(f"Error updating schedule status | schedule_id={schedule_id} | error={str(e)}")
    
    async def _scheduler_loop(self):
        """Main scheduler monitoring loop"""
        while self.is_running:
            try:
                # Monitor schedule health and reload if needed
                await asyncio.sleep(300)  # Check every 5 minutes
                
                # Reload schedules to pick up any changes
                await self._reload_schedules()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop | error={str(e)}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _reload_schedules(self):
        """Reload schedules from database"""
        try:
            # Get current enabled schedules
            response = (
                self.supabase_client.table("archon_backup_schedules")
                .select("*")
                .eq("enabled", True)
                .execute()
            )
            
            current_schedules = {s["id"]: s for s in (response.data or [])}
            
            # Stop schedules that are no longer enabled or don't exist
            for schedule_id in list(self.active_schedules.keys()):
                if schedule_id not in current_schedules:
                    await self._stop_schedule(schedule_id)
            
            # Start new or updated schedules
            for schedule_id, schedule_data in current_schedules.items():
                if schedule_id not in self.active_schedules:
                    await self._start_schedule(schedule_id, schedule_data)
                    
        except Exception as e:
            logger.error(f"Error reloading schedules | error={str(e)}")


# Global scheduler instance
_backup_scheduler: Optional[BackupScheduler] = None


def get_backup_scheduler() -> BackupScheduler:
    """Get the global backup scheduler instance"""
    global _backup_scheduler
    if _backup_scheduler is None:
        _backup_scheduler = BackupScheduler()
    return _backup_scheduler
