import schedule
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Callable, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
import json
import os

class NotificationSystem:
    def __init__(self, db_manager=None):
        """Initialize notification system with real-time scheduling"""
        self.db_manager = db_manager
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        
        # In-memory notification queue for real-time processing
        self.notification_queue = []
        self.notification_callbacks = {}
        
        # Start the scheduler
        self._start_background_tasks()
        
    def _start_background_tasks(self):
        """Start background tasks for notifications"""
        # Schedule habit reminders
        self.scheduler.add_job(
            func=self._check_habit_reminders,
            trigger='interval',
            minutes=1,  # Check every minute
            id='habit_reminders'
        )
        
        # Schedule goal deadlines
        self.scheduler.add_job(
            func=self._check_goal_deadlines,
            trigger='interval',
            hours=1,  # Check every hour
            id='goal_deadlines'
        )
        
        # Schedule custom reminders
        self.scheduler.add_job(
            func=self._check_custom_reminders,
            trigger='interval',
            minutes=1,
            id='custom_reminders'
        )
    
    def schedule_habit_reminder(self, user_id: str, habit_data: Dict[str, Any]):
        """Schedule recurring habit reminders"""
        try:
            habit_name = habit_data.get('name', 'Habit')
            reminder_time = habit_data.get('reminder_time')
            frequency = habit_data.get('frequency', 'daily')
            
            if not reminder_time:
                return
            
            # Parse reminder time (assume format "HH:MM")
            try:
                hour, minute = map(int, reminder_time.split(':'))
            except:
                return
            
            job_id = f"habit_{user_id}_{habit_data.get('id', hash(habit_name))}"
            
            if frequency == 'daily':
                self.scheduler.add_job(
                    func=self._send_habit_reminder,
                    trigger=CronTrigger(hour=hour, minute=minute),
                    args=[user_id, habit_name],
                    id=job_id,
                    replace_existing=True
                )
            elif frequency == 'weekly':
                # Schedule for every Monday (can be customized)
                self.scheduler.add_job(
                    func=self._send_habit_reminder,
                    trigger=CronTrigger(day_of_week=0, hour=hour, minute=minute),
                    args=[user_id, habit_name],
                    id=job_id,
                    replace_existing=True
                )
            
        except Exception as e:
            print(f"Error scheduling habit reminder: {e}")
    
    def schedule_goal_reminder(self, user_id: str, goal_data: Dict[str, Any]):
        """Schedule goal deadline reminders"""
        try:
            goal_name = goal_data.get('name', 'Goal')
            target_date = goal_data.get('target_date')
            
            if not target_date:
                return
            
            # Parse target date
            try:
                target_datetime = datetime.fromisoformat(target_date)
            except:
                # Try different date formats
                try:
                    target_datetime = datetime.strptime(target_date, '%Y-%m-%d')
                except:
                    return
            
            # Schedule reminder 1 day before deadline
            reminder_datetime = target_datetime - timedelta(days=1)
            
            if reminder_datetime > datetime.now():
                job_id = f"goal_{user_id}_{goal_data.get('id', hash(goal_name))}"
                
                self.scheduler.add_job(
                    func=self._send_goal_reminder,
                    trigger=DateTrigger(run_date=reminder_datetime),
                    args=[user_id, goal_name, target_date],
                    id=job_id,
                    replace_existing=True
                )
            
        except Exception as e:
            print(f"Error scheduling goal reminder: {e}")
    
    def schedule_custom_reminder(self, user_id: str, reminder_data: Dict[str, Any]):
        """Schedule one-time custom reminders"""
        try:
            reminder_text = reminder_data.get('text', 'Reminder')
            reminder_time = reminder_data.get('time')
            
            if not reminder_time:
                return
            
            # Parse reminder time
            try:
                reminder_datetime = datetime.fromisoformat(reminder_time)
            except:
                try:
                    # Try parsing different formats
                    reminder_datetime = datetime.strptime(reminder_time, '%Y-%m-%d %H:%M')
                except:
                    return
            
            if reminder_datetime > datetime.now():
                job_id = f"reminder_{user_id}_{reminder_data.get('id', hash(reminder_text))}"
                
                self.scheduler.add_job(
                    func=self._send_custom_reminder,
                    trigger=DateTrigger(run_date=reminder_datetime),
                    args=[user_id, reminder_text],
                    id=job_id,
                    replace_existing=True
                )
            
        except Exception as e:
            print(f"Error scheduling custom reminder: {e}")
    
    def _send_habit_reminder(self, user_id: str, habit_name: str):
        """Send habit reminder notification"""
        notification = {
            'type': 'habit_reminder',
            'user_id': user_id,
            'title': 'Habit Reminder',
            'message': f"Time to work on your habit: {habit_name}",
            'timestamp': datetime.now().isoformat(),
            'data': {'habit_name': habit_name}
        }
        self._queue_notification(notification)
    
    def _send_goal_reminder(self, user_id: str, goal_name: str, target_date: str):
        """Send goal deadline reminder"""
        notification = {
            'type': 'goal_reminder',
            'user_id': user_id,
            'title': 'Goal Deadline Approaching',
            'message': f"Your goal '{goal_name}' is due tomorrow ({target_date})",
            'timestamp': datetime.now().isoformat(),
            'data': {'goal_name': goal_name, 'target_date': target_date}
        }
        self._queue_notification(notification)
    
    def _send_custom_reminder(self, user_id: str, reminder_text: str):
        """Send custom reminder notification"""
        notification = {
            'type': 'custom_reminder',
            'user_id': user_id,
            'title': 'Reminder',
            'message': reminder_text,
            'timestamp': datetime.now().isoformat(),
            'data': {'reminder_text': reminder_text}
        }
        self._queue_notification(notification)
    
    def _check_habit_reminders(self):
        """Background task to check for habit reminders"""
        if not self.db_manager:
            return
        
        try:
            # This would check database for habits that need reminders
            # Implementation depends on database schema
            pass
        except Exception as e:
            print(f"Error checking habit reminders: {e}")
    
    def _check_goal_deadlines(self):
        """Background task to check for goal deadlines"""
        if not self.db_manager:
            return
        
        try:
            # This would check database for approaching goal deadlines
            pass
        except Exception as e:
            print(f"Error checking goal deadlines: {e}")
    
    def _check_custom_reminders(self):
        """Background task to check for custom reminders"""
        if not self.db_manager:
            return
        
        try:
            # This would check database for scheduled reminders
            pass
        except Exception as e:
            print(f"Error checking custom reminders: {e}")
    
    def _queue_notification(self, notification: Dict[str, Any]):
        """Add notification to queue for processing"""
        self.notification_queue.append(notification)
        
        # Trigger callback if registered
        user_id = notification.get('user_id')
        if user_id in self.notification_callbacks:
            try:
                self.notification_callbacks[user_id](notification)
            except Exception as e:
                print(f"Error executing notification callback: {e}")
    
    def register_notification_callback(self, user_id: str, callback: Callable):
        """Register callback function for user notifications"""
        self.notification_callbacks[user_id] = callback
    
    def get_pending_notifications(self, user_id: str) -> List[Dict[str, Any]]:
        """Get pending notifications for user"""
        user_notifications = [
            notif for notif in self.notification_queue 
            if notif.get('user_id') == user_id
        ]
        
        # Remove returned notifications from queue
        self.notification_queue = [
            notif for notif in self.notification_queue 
            if notif.get('user_id') != user_id
        ]
        
        return user_notifications
    
    def cancel_scheduled_notification(self, job_id: str):
        """Cancel a scheduled notification"""
        try:
            self.scheduler.remove_job(job_id)
        except Exception as e:
            print(f"Error canceling notification {job_id}: {e}")
    
    def get_scheduled_jobs(self) -> List[Dict[str, Any]]:
        """Get list of scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        return jobs
    
    def shutdown(self):
        """Shutdown the notification system"""
        try:
            self.scheduler.shutdown()
        except Exception as e:
            print(f"Error shutting down notification system: {e}")