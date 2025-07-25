import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

class DatabaseManager:
    def __init__(self, db_path: str = "noww_club.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Flows table for persistent state management
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                flow_type TEXT NOT NULL,
                flow_data TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                profile_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Conversations table for memory management
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                message_type TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Goals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'active',
                target_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        ''')
        
        # Habits table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                frequency TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Reminders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                reminder_time TIMESTAMP NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Mood entries table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mood_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                mood_score INTEGER NOT NULL,
                notes TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Vision board intake table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vision_board_intake (
                user_id TEXT PRIMARY KEY,
                intake_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_flow(self, user_id: str, flow_type: str, flow_data: Dict[str, Any]) -> int:
        """Save a flow to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO flows (user_id, flow_type, flow_data, status)
            VALUES (?, ?, ?, 'pending')
        ''', (user_id, flow_type, json.dumps(flow_data)))
        
        flow_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return flow_id
    
    def update_flow(self, flow_id: int, flow_data: Dict[str, Any], status: str = None):
        """Update an existing flow"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if status:
            cursor.execute('''
                UPDATE flows SET flow_data = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (json.dumps(flow_data), status, flow_id))
        else:
            cursor.execute('''
                UPDATE flows SET flow_data = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (json.dumps(flow_data), flow_id))
        
        conn.commit()
        conn.close()
    
    def get_pending_flows(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all pending flows for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, flow_type, flow_data, created_at FROM flows
            WHERE user_id = ? AND (status = 'pending' OR status = 'paused')
            ORDER BY created_at DESC
        ''', (user_id,))
        
        flows = []
        for row in cursor.fetchall():
            flows.append({
                'id': row[0],
                'flow_type': row[1],
                'flow_data': json.loads(row[2]),
                'created_at': row[3]
            })
        
        conn.close()
        return flows
    
    def clear_pending_flows(self, user_id: str):
        """Clear all pending flows for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE flows SET status = 'cancelled'
            WHERE user_id = ? AND status = 'pending'
        ''', (user_id,))
        
        conn.commit()
        conn.close()
    
    def save_conversation(self, user_id: str, message_type: str, content: str, metadata: Dict = None):
        """Save a conversation message"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute('''
            INSERT INTO conversations (user_id, message_type, content, metadata)
            VALUES (?, ?, ?, ?)
        ''', (user_id, message_type, content, metadata_json))
        
        conn.commit()
        conn.close()
    
    def get_conversation_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get conversation history for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT message_type, content, metadata, timestamp FROM conversations
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user_id, limit))
        
        history = []
        for row in cursor.fetchall():
            metadata = json.loads(row[2]) if row[2] else {}
            history.append({
                'message_type': row[0],
                'content': row[1],
                'metadata': metadata,
                'timestamp': row[3]
            })
        
        conn.close()
        return list(reversed(history))  # Return in chronological order
    
    def save_goal(self, user_id: str, title: str, description: str = None, target_date: str = None) -> int:
        """Save a goal"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO goals (user_id, title, description, target_date)
            VALUES (?, ?, ?, ?)
        ''', (user_id, title, description, target_date))
        
        goal_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return goal_id
    
    def save_habit(self, user_id: str, title: str, description: str = None, frequency: str = "daily") -> int:
        """Save a habit"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO habits (user_id, title, description, frequency)
            VALUES (?, ?, ?, ?)
        ''', (user_id, title, description, frequency))
        
        habit_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return habit_id
    
    def save_reminder(self, user_id: str, title: str, description: str = None, reminder_time: str = None) -> int:
        """Save a reminder"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO reminders (user_id, title, description, reminder_time)
            VALUES (?, ?, ?, ?)
        ''', (user_id, title, description, reminder_time))
        
        reminder_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return reminder_id
    
    def save_mood_entry(self, user_id: str, mood_score: int, notes: str = None):
        """Save a mood entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO mood_entries (user_id, mood_score, notes)
            VALUES (?, ?, ?)
        ''', (user_id, mood_score, notes))
        
        conn.commit()
        conn.close()
    
    def get_user_goals(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user goals"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, description, status, target_date, created_at FROM goals
            WHERE user_id = ? AND status = 'active'
            ORDER BY created_at DESC
        ''', (user_id,))
        
        goals = []
        for row in cursor.fetchall():
            goals.append({
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'status': row[3],
                'target_date': row[4],
                'created_at': row[5]
            })
        
        conn.close()
        return goals
    
    def get_user_habits(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user habits"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, description, frequency, status, created_at FROM habits
            WHERE user_id = ? AND status = 'active'
            ORDER BY created_at DESC
        ''', (user_id,))
        
        habits = []
        for row in cursor.fetchall():
            habits.append({
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'frequency': row[3],
                'status': row[4],
                'created_at': row[5]
            })
        
        conn.close()
        return habits
    
    def get_user_reminders(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user reminders"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, description, reminder_time, status, created_at FROM reminders
            WHERE user_id = ? AND status = 'active'
            ORDER BY created_at DESC
        ''', (user_id,))
        
        reminders = []
        for row in cursor.fetchall():
            reminders.append({
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'reminder_time': row[3],
                'status': row[4],
                'created_at': row[5]
            })
        
        conn.close()
        return reminders
    
    def get_mood_history(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get mood history for the last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT mood_score, notes, timestamp FROM mood_entries
            WHERE user_id = ? AND timestamp >= datetime('now', '-{} days')
            ORDER BY timestamp DESC
        '''.format(days), (user_id,))
        
        moods = []
        for row in cursor.fetchall():
            moods.append({
                'mood_score': row[0],
                'notes': row[1],
                'timestamp': row[2]
            })
        
        conn.close()
        return moods

    def get_mood_entries(self, user_id: str, limit: int = 7) -> List[Dict[str, Any]]:
        """Get mood entries for a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT mood_score, notes, timestamp FROM mood_entries
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user_id, limit))
        
        entries = []
        for row in cursor.fetchall():
            entries.append({
                'mood_score': row[0],
                'notes': row[1],
                'timestamp': row[2]
            })
            
        conn.close()
        return entries

    def save_vision_board_intake(self, user_id: str, intake_data: Dict[str, Any]):
        """Save vision board intake data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert or replace intake data
        cursor.execute('''
            INSERT OR REPLACE INTO vision_board_intake (user_id, intake_data, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, json.dumps(intake_data)))
        
        conn.commit()
        conn.close()
    
    def get_vision_board_intake(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get vision board intake data for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT intake_data FROM vision_board_intake
            WHERE user_id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return json.loads(row[0])
        return None
    
    def clear_vision_board_intake(self, user_id: str):
        """Clear vision board intake data for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM vision_board_intake WHERE user_id = ?
        ''', (user_id,))
        
        conn.commit()
        conn.close()

    def get_recent_conversations(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent conversations for a user"""
        return self.get_conversation_history(user_id, limit)
    
    def save_vision_board_creation(self, user_id: str, vision_board_data: Dict[str, Any]):
        """Save vision board creation record with enhanced metadata"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Ensure vision board creations table exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vision_board_creations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                template_number INTEGER NOT NULL,
                template_name TEXT NOT NULL,
                image_url TEXT,
                persona_data TEXT,
                intake_summary TEXT,
                status TEXT DEFAULT 'completed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        ''')
        
        # Insert vision board creation record
        cursor.execute('''
            INSERT INTO vision_board_creations 
            (user_id, template_number, template_name, image_url, persona_data, status, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            vision_board_data.get('template_number', 1),
            vision_board_data.get('template_name', 'Unknown'),
            vision_board_data.get('image_url', ''),
            vision_board_data.get('persona_data', '{}'),
            vision_board_data.get('status', 'completed'),
            json.dumps(vision_board_data)
        ))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Saved vision board creation record for user {user_id}")
    
    def get_user_vision_boards(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's vision board creation history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT template_number, template_name, image_url, created_at, status, metadata
                FROM vision_board_creations
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (user_id, limit))
            
            vision_boards = []
            for row in cursor.fetchall():
                metadata = {}
                try:
                    metadata = json.loads(row[5]) if row[5] else {}
                except:
                    pass
                
                vision_boards.append({
                    'template_number': row[0],
                    'template_name': row[1],
                    'image_url': row[2],
                    'created_at': row[3],
                    'status': row[4],
                    'metadata': metadata
                })
            
            conn.close()
            return vision_boards
            
        except sqlite3.OperationalError:
            # Table doesn't exist yet
            conn.close()
            return []
    
    def enhance_conversation_metadata(self, user_id: str, conversation_id: int, metadata: Dict[str, Any]):
        """Enhance conversation with additional metadata for better memory management"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Update the metadata for the conversation
            cursor.execute('''
                UPDATE conversations 
                SET metadata = ?
                WHERE id = ? AND user_id = ?
            ''', (json.dumps(metadata), conversation_id, user_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error enhancing conversation metadata: {e}")
            conn.close()
