import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from core.database import DatabaseManager

class UserProfileManager:
    def __init__(self, db_manager: DatabaseManager = None):
        self.db_manager = db_manager or DatabaseManager()
    
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user profile"""
        # Get basic profile data
        profile_data = self._get_profile_data(user_id)
        
        # Get goals, habits, and mood data
        goals = self.db_manager.get_user_goals(user_id)
        habits = self.db_manager.get_user_habits(user_id)
        mood_history = self.db_manager.get_mood_history(user_id, days=30)
        
        # Calculate statistics
        stats = self._calculate_user_stats(goals, habits, mood_history)
        
        return {
            "user_id": user_id,
            "profile": profile_data,
            "goals": goals,
            "habits": habits,
            "mood_history": mood_history,
            "statistics": stats,
            "last_updated": datetime.now().isoformat()
        }
    
    def _get_profile_data(self, user_id: str) -> Dict[str, Any]:
        """Get user profile data from database"""
        conn = self.db_manager.db_path
        import sqlite3
        
        connection = sqlite3.connect(conn)
        cursor = connection.cursor()
        
        cursor.execute('''
            SELECT profile_data FROM user_profiles WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        connection.close()
        
        if result:
            return json.loads(result[0])
        else:
            # Create default profile
            default_profile = {
                "name": "",
                "preferences": {},
                "notification_settings": {
                    "reminders_enabled": True,
                    "mood_check_ins": True,
                    "habit_reminders": True,
                    "goal_updates": True
                },
                "privacy_settings": {
                    "data_sharing": False,
                    "analytics": True
                },
                "created_at": datetime.now().isoformat()
            }
            
            self._save_profile_data(user_id, default_profile)
            return default_profile
    
    def _save_profile_data(self, user_id: str, profile_data: Dict[str, Any]):
        """Save user profile data to database"""
        conn = self.db_manager.db_path
        import sqlite3
        
        connection = sqlite3.connect(conn)
        cursor = connection.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_profiles (user_id, profile_data, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, json.dumps(profile_data)))
        
        connection.commit()
        connection.close()
    
    def update_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user profile with new data"""
        try:
            current_profile = self._get_profile_data(user_id)
            current_profile.update(updates)
            current_profile["updated_at"] = datetime.now().isoformat()
            
            self._save_profile_data(user_id, current_profile)
            return True
        
        except Exception as e:
            print(f"Error updating profile for {user_id}: {e}")
            return False
    
    def _calculate_user_stats(self, goals: List[Dict], habits: List[Dict], mood_history: List[Dict]) -> Dict[str, Any]:
        """Calculate user statistics"""
        stats = {
            "total_goals": len(goals),
            "active_goals": len([g for g in goals if g["status"] == "active"]),
            "total_habits": len(habits),
            "active_habits": len([h for h in habits if h["status"] == "active"]),
            "mood_entries_count": len(mood_history),
            "average_mood": 0,
            "mood_trend": "stable"
        }
        
        # Calculate mood statistics
        if mood_history:
            mood_scores = [entry["mood_score"] for entry in mood_history]
            stats["average_mood"] = sum(mood_scores) / len(mood_scores)
            
            # Calculate trend (comparing first half to second half)
            mid_point = len(mood_scores) // 2
            if mid_point > 0:
                first_half_avg = sum(mood_scores[:mid_point]) / mid_point
                second_half_avg = sum(mood_scores[mid_point:]) / (len(mood_scores) - mid_point)
                
                if second_half_avg > first_half_avg + 0.3:
                    stats["mood_trend"] = "improving"
                elif second_half_avg < first_half_avg - 0.3:
                    stats["mood_trend"] = "declining"
                else:
                    stats["mood_trend"] = "stable"
        
        return stats
    
    def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """Export all user data for download"""
        try:
            profile = self.get_user_profile(user_id)
            
            # Get conversation history
            conversation_history = self.db_manager.get_conversation_history(user_id, limit=1000)
            
            # Get all flows
            import sqlite3
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT flow_type, flow_data, status, created_at FROM flows
                WHERE user_id = ?
                ORDER BY created_at DESC
            ''', (user_id,))
            
            flows = []
            for row in cursor.fetchall():
                flows.append({
                    "flow_type": row[0],
                    "flow_data": json.loads(row[1]),
                    "status": row[2],
                    "created_at": row[3]
                })
            
            conn.close()
            
            export_data = {
                "export_info": {
                    "user_id": user_id,
                    "export_timestamp": datetime.now().isoformat(),
                    "export_version": "1.0"
                },
                "profile": profile,
                "conversation_history": conversation_history,
                "flows": flows
            }
            
            return export_data
        
        except Exception as e:
            print(f"Error exporting data for {user_id}: {e}")
            return {"error": f"Failed to export data: {str(e)}"}
    
    def import_user_data(self, user_id: str, import_data: Dict[str, Any]) -> bool:
        """Import user data from uploaded file"""
        try:
            if "profile" in import_data:
                profile_data = import_data["profile"].get("profile", {})
                self._save_profile_data(user_id, profile_data)
            
            # Import goals
            if "profile" in import_data and "goals" in import_data["profile"]:
                for goal in import_data["profile"]["goals"]:
                    self.db_manager.save_goal(
                        user_id,
                        goal.get("title", "Imported Goal"),
                        goal.get("description"),
                        goal.get("target_date")
                    )
            
            # Import habits  
            if "profile" in import_data and "habits" in import_data["profile"]:
                for habit in import_data["profile"]["habits"]:
                    self.db_manager.save_habit(
                        user_id,
                        habit.get("title", "Imported Habit"),
                        habit.get("description"),
                        habit.get("frequency", "daily")
                    )
            
            # Import mood history
            if "profile" in import_data and "mood_history" in import_data["profile"]:
                for mood_entry in import_data["profile"]["mood_history"]:
                    # Save mood entry with original timestamp if available
                    import sqlite3
                    conn = sqlite3.connect(self.db_manager.db_path)
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        INSERT INTO mood_entries (user_id, mood_score, notes, timestamp)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        user_id,
                        mood_entry.get("mood_score", 3),
                        mood_entry.get("notes"),
                        mood_entry.get("timestamp", datetime.now().isoformat())
                    ))
                    
                    conn.commit()
                    conn.close()
            
            return True
        
        except Exception as e:
            print(f"Error importing data for {user_id}: {e}")
            return False
    
    def delete_user_data(self, user_id: str) -> bool:
        """Delete all user data"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            # Delete from all tables
            tables = [
                "user_profiles", "flows", "conversations", 
                "goals", "habits", "reminders", "mood_entries"
            ]
            
            for table in tables:
                cursor.execute(f'DELETE FROM {table} WHERE user_id = ?', (user_id,))
            
            conn.commit()
            conn.close()
            
            # Delete memory profile file
            memory_profiles_dir = "user_profiles"
            profile_path = os.path.join(memory_profiles_dir, f"{user_id}_profile.json")
            if os.path.exists(profile_path):
                os.remove(profile_path)
            
            return True
        
        except Exception as e:
            print(f"Error deleting data for {user_id}: {e}")
            return False
    
    def get_notification_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user notification preferences"""
        profile_data = self._get_profile_data(user_id)
        return profile_data.get("notification_settings", {
            "reminders_enabled": True,
            "mood_check_ins": True,
            "habit_reminders": True,
            "goal_updates": True
        })
    
    def update_notification_preferences(self, user_id: str, preferences: Dict[str, bool]) -> bool:
        """Update user notification preferences"""
        try:
            current_profile = self._get_profile_data(user_id)
            current_profile["notification_settings"] = preferences
            self._save_profile_data(user_id, current_profile)
            return True
        
        except Exception as e:
            print(f"Error updating notification preferences for {user_id}: {e}")
            return False
