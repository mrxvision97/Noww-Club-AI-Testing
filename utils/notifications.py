import os
import json
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

class NotificationManager:
    def __init__(self, db_manager=None):
        self.db_manager = db_manager
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Notification scheduling (mock cron for development)
        self.scheduled_notifications = {}
        self.notification_handlers = {}
        self.is_running = False
        self.scheduler_thread = None
        
        # Default notification types
        self.notification_types = {
            "reminder": "Scheduled reminders",
            "mood_checkin": "Daily mood check-ins", 
            "habit_reminder": "Habit tracking reminders",
            "goal_update": "Goal progress updates",
            "proactive_message": "Proactive engagement messages"
        }
        
        # Initialize scheduler
        self.start_scheduler()
    
    def start_scheduler(self):
        """Start the notification scheduler (mock cron implementation)"""
        if not self.is_running:
            self.is_running = True
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self.scheduler_thread.start()
    
    def stop_scheduler(self):
        """Stop the notification scheduler"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=1)
    
    def _scheduler_loop(self):
        """Main scheduler loop - checks for notifications every minute"""
        while self.is_running:
            try:
                self._process_scheduled_notifications()
                time.sleep(60)  # Check every minute
            except Exception as e:
                print(f"Error in scheduler loop: {e}")
                time.sleep(60)
    
    def _process_scheduled_notifications(self):
        """Process all scheduled notifications"""
        current_time = datetime.now()
        
        # Check scheduled notifications
        for notification_id, notification in list(self.scheduled_notifications.items()):
            try:
                scheduled_time = datetime.fromisoformat(notification["scheduled_time"])
                
                if current_time >= scheduled_time:
                    # Trigger notification
                    self._trigger_notification(notification)
                    
                    # Remove one-time notifications or reschedule recurring ones
                    if notification.get("recurring"):
                        self._reschedule_notification(notification_id, notification)
                    else:
                        del self.scheduled_notifications[notification_id]
            
            except Exception as e:
                print(f"Error processing notification {notification_id}: {e}")
    
    def _trigger_notification(self, notification: Dict[str, Any]):
        """Trigger a notification"""
        notification_type = notification.get("type", "reminder")
        user_id = notification.get("user_id")
        
        # Get notification handler
        handler = self.notification_handlers.get(notification_type)
        if handler:
            try:
                handler(notification)
            except Exception as e:
                print(f"Error in notification handler for type {notification_type}: {e}")
        else:
            # Default handler - just log the notification
            print(f"Notification triggered: {notification.get('title', 'No title')} for user {user_id}")
    
    def _reschedule_notification(self, notification_id: str, notification: Dict[str, Any]):
        """Reschedule a recurring notification"""
        try:
            current_time = datetime.fromisoformat(notification["scheduled_time"])
            recurring_pattern = notification.get("recurring_pattern", "daily")
            
            if recurring_pattern == "daily":
                next_time = current_time + timedelta(days=1)
            elif recurring_pattern == "weekly":
                next_time = current_time + timedelta(weeks=1)
            elif recurring_pattern == "hourly":
                next_time = current_time + timedelta(hours=1)
            else:
                # Default to daily
                next_time = current_time + timedelta(days=1)
            
            notification["scheduled_time"] = next_time.isoformat()
            self.scheduled_notifications[notification_id] = notification
        
        except Exception as e:
            print(f"Error rescheduling notification {notification_id}: {e}")
    
    def schedule_notification(self, user_id: str, notification_type: str, title: str, 
                            message: str, scheduled_time: datetime, 
                            recurring: bool = False, recurring_pattern: str = "daily") -> str:
        """Schedule a new notification"""
        notification_id = f"{user_id}_{notification_type}_{int(time.time())}"
        
        notification = {
            "id": notification_id,
            "user_id": user_id,
            "type": notification_type,
            "title": title,
            "message": message,
            "scheduled_time": scheduled_time.isoformat(),
            "recurring": recurring,
            "recurring_pattern": recurring_pattern,
            "created_at": datetime.now().isoformat()
        }
        
        self.scheduled_notifications[notification_id] = notification
        return notification_id
    
    def cancel_notification(self, notification_id: str) -> bool:
        """Cancel a scheduled notification"""
        if notification_id in self.scheduled_notifications:
            del self.scheduled_notifications[notification_id]
            return True
        return False
    
    def get_user_notifications(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all scheduled notifications for a user"""
        user_notifications = []
        for notification in self.scheduled_notifications.values():
            if notification.get("user_id") == user_id:
                user_notifications.append(notification)
        
        return sorted(user_notifications, key=lambda x: x["scheduled_time"])
    
    def register_notification_handler(self, notification_type: str, handler: Callable):
        """Register a handler for a notification type"""
        self.notification_handlers[notification_type] = handler
    
    def generate_proactive_message(self, user_id: str, context: Dict[str, Any]) -> Optional[str]:
        """Generate a proactive message based on user context"""
        try:
            # Analyze user activity and generate appropriate message
            proactive_prompt = self._build_proactive_prompt(context)
            
            response = self.llm.invoke(proactive_prompt)
            return response.content
        
        except Exception as e:
            print(f"Error generating proactive message: {e}")
            return None
    
    def _build_proactive_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for proactive message generation"""
        prompt = f"""
        You are an AI companion generating a proactive, helpful message for a user.
        
        User Context:
        - Last activity: {context.get('last_activity', 'Unknown')}
        - Pending flows: {context.get('pending_flows', [])}
        - Active goals: {context.get('active_goals', [])}
        - Active habits: {context.get('active_habits', [])}
        - Recent mood: {context.get('recent_mood', 'Unknown')}
        - Time since last interaction: {context.get('time_since_last', 'Unknown')}
        
        Generate a brief, helpful proactive message that:
        1. Feels natural and caring, not robotic
        2. References relevant context
        3. Offers specific help or encouragement
        4. Is appropriate for the time and situation
        5. Encourages engagement without being pushy
        
        Keep it to 1-2 sentences. Make it feel like a friend checking in.
        """
        
        return prompt
    
    def check_user_inactivity(self, user_id: str, threshold_hours: int = 24) -> bool:
        """Check if user has been inactive beyond threshold"""
        if not self.db_manager:
            return False
        
        try:
            # Get last conversation
            conversations = self.db_manager.get_conversation_history(user_id, limit=1)
            
            if not conversations:
                return True  # No conversations yet
            
            last_conversation = conversations[0]
            last_time = datetime.fromisoformat(last_conversation['timestamp'])
            
            # Check if inactive beyond threshold
            hours_since_last = (datetime.now() - last_time).total_seconds() / 3600
            return hours_since_last > threshold_hours
        
        except Exception as e:
            print(f"Error checking user inactivity: {e}")
            return False
    
    def suggest_proactive_content(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Suggest proactive content based on user profile and activity"""
        if not self.db_manager:
            return None
        
        try:
            # Gather user context
            context = self._gather_user_context(user_id)
            
            # Generate suggestion based on context
            if context.get('pending_flows'):
                return {
                    "type": "flow_resumption",
                    "message": "I noticed you have an incomplete task. Would you like to continue where we left off?",
                    "action": "resume_flow"
                }
            
            elif context.get('inactive_days', 0) > 1:
                message = self.generate_proactive_message(user_id, context)
                return {
                    "type": "check_in",
                    "message": message or "How are you doing today? I'm here if you need anything!",
                    "action": "general_checkin"
                }
            
            elif context.get('mood_trend') == 'declining':
                return {
                    "type": "emotional_support",
                    "message": "I noticed you might be going through a tough time. Would you like to talk about it?",
                    "action": "emotional_checkin"
                }
            
            elif len(context.get('active_goals', [])) > 0:
                return {
                    "type": "goal_encouragement", 
                    "message": "How are your goals coming along? I'd love to hear about your progress!",
                    "action": "goal_checkin"
                }
            
            return None
        
        except Exception as e:
            print(f"Error suggesting proactive content: {e}")
            return None
    
    def _gather_user_context(self, user_id: str) -> Dict[str, Any]:
        """Gather comprehensive user context for proactive messaging"""
        context = {}
        
        try:
            if self.db_manager:
                # Get pending flows
                pending_flows = self.db_manager.get_pending_flows(user_id)
                context['pending_flows'] = pending_flows
                
                # Get active goals and habits
                context['active_goals'] = self.db_manager.get_user_goals(user_id)
                context['active_habits'] = self.db_manager.get_user_habits(user_id)
                
                # Get recent mood data
                mood_history = self.db_manager.get_mood_history(user_id, days=7)
                if mood_history:
                    recent_moods = [m['mood_score'] for m in mood_history]
                    context['recent_mood'] = sum(recent_moods) / len(recent_moods)
                    
                    # Determine mood trend
                    if len(recent_moods) >= 3:
                        first_half = recent_moods[:len(recent_moods)//2]
                        second_half = recent_moods[len(recent_moods)//2:]
                        
                        first_avg = sum(first_half) / len(first_half)
                        second_avg = sum(second_half) / len(second_half)
                        
                        if second_avg < first_avg - 0.5:
                            context['mood_trend'] = 'declining'
                        elif second_avg > first_avg + 0.5:
                            context['mood_trend'] = 'improving'
                        else:
                            context['mood_trend'] = 'stable'
                
                # Get last activity
                conversations = self.db_manager.get_conversation_history(user_id, limit=1)
                if conversations:
                    last_conversation = conversations[0]
                    last_time = datetime.fromisoformat(last_conversation['timestamp'])
                    context['last_activity'] = last_time.isoformat()
                    
                    hours_since = (datetime.now() - last_time).total_seconds() / 3600
                    context['time_since_last'] = f"{hours_since:.1f} hours"
                    context['inactive_days'] = hours_since / 24
        
        except Exception as e:
            print(f"Error gathering user context: {e}")
        
        return context
    
    def schedule_daily_mood_checkin(self, user_id: str, hour: int = 20) -> str:
        """Schedule daily mood check-in notification"""
        # Calculate next occurrence
        now = datetime.now()
        next_checkin = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        
        if next_checkin <= now:
            next_checkin += timedelta(days=1)
        
        return self.schedule_notification(
            user_id=user_id,
            notification_type="mood_checkin",
            title="Daily Mood Check-in",
            message="How are you feeling today? Take a moment to log your mood.",
            scheduled_time=next_checkin,
            recurring=True,
            recurring_pattern="daily"
        )
    
    def schedule_habit_reminder(self, user_id: str, habit_title: str, 
                              reminder_time: datetime, frequency: str = "daily") -> str:
        """Schedule habit reminder notification"""
        return self.schedule_notification(
            user_id=user_id,
            notification_type="habit_reminder",
            title=f"Habit Reminder: {habit_title}",
            message=f"Time for your '{habit_title}' habit! You've got this!",
            scheduled_time=reminder_time,
            recurring=True,
            recurring_pattern=frequency
        )
    
    def schedule_goal_update(self, user_id: str, goal_title: str, 
                           reminder_date: datetime) -> str:
        """Schedule goal progress update notification"""
        return self.schedule_notification(
            user_id=user_id,
            notification_type="goal_update",
            title=f"Goal Check: {goal_title}",
            message=f"How is your progress on '{goal_title}' coming along? I'd love to hear an update!",
            scheduled_time=reminder_date,
            recurring=False
        )
    
    def get_notification_stats(self, user_id: str) -> Dict[str, Any]:
        """Get notification statistics for a user"""
        user_notifications = self.get_user_notifications(user_id)
        
        stats = {
            "total_scheduled": len(user_notifications),
            "by_type": {},
            "recurring_count": 0,
            "next_notification": None
        }
        
        for notification in user_notifications:
            # Count by type
            notif_type = notification.get("type", "unknown")
            stats["by_type"][notif_type] = stats["by_type"].get(notif_type, 0) + 1
            
            # Count recurring
            if notification.get("recurring"):
                stats["recurring_count"] += 1
            
            # Find next notification
            scheduled_time = datetime.fromisoformat(notification["scheduled_time"])
            if scheduled_time > datetime.now():
                if not stats["next_notification"] or scheduled_time < datetime.fromisoformat(stats["next_notification"]["scheduled_time"]):
                    stats["next_notification"] = notification
        
        return stats
    
    def cleanup_expired_notifications(self, days_old: int = 30):
        """Clean up old, expired notifications"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        expired_ids = []
        for notification_id, notification in self.scheduled_notifications.items():
            created_at = datetime.fromisoformat(notification.get("created_at", datetime.now().isoformat()))
            scheduled_time = datetime.fromisoformat(notification["scheduled_time"])
            
            # Remove if old and not recurring, or if scheduled time is way past and failed
            if (created_at < cutoff_date and not notification.get("recurring")) or \
               (scheduled_time < cutoff_date and not notification.get("recurring")):
                expired_ids.append(notification_id)
        
        for notification_id in expired_ids:
            del self.scheduled_notifications[notification_id]
        
        return len(expired_ids)
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.stop_scheduler()
