import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import deque
from langchain_core.messages import get_buffer_string, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.store.memory import InMemoryStore
from core.database import DatabaseManager

# Modern alternative to deprecated ConversationSummaryMemory
class ModernConversationMemory:
    def __init__(self, llm, max_messages=20):
        self.llm = llm
        self.max_messages = max_messages
        self.messages = []
        self.buffer = ""
        
    def add_user_message(self, content: str):
        """Add a user message"""
        self.messages.append(HumanMessage(content=content))
        self._manage_memory_size()
        
    def add_ai_message(self, content: str):
        """Add an AI message"""
        self.messages.append(AIMessage(content=content))
        self._manage_memory_size()
    
    def _manage_memory_size(self):
        """Manage memory size and create summary if needed"""
        if len(self.messages) > self.max_messages:
            # Create summary of older messages
            older_messages = self.messages[:-self.max_messages//2]
            recent_messages = self.messages[-self.max_messages//2:]
            
            if older_messages:
                # Create summary of older messages
                messages_text = "\n".join([
                    f"{'Human' if isinstance(msg, HumanMessage) else 'AI'}: {msg.content}"
                    for msg in older_messages
                ])
                
                summary_prompt = f"""
                Please create a concise summary of this conversation history:
                
                {messages_text}
                
                Focus on key information, user preferences, and important details that should be remembered.
                """
                
                try:
                    summary_response = self.llm.invoke(summary_prompt)
                    self.buffer = summary_response.content
                except Exception as e:
                    print(f"Error creating summary: {e}")
                    self.buffer = f"Previous conversation included {len(older_messages)} messages."
                
                # Keep only recent messages
                self.messages = recent_messages
    
    @property
    def chat_memory(self):
        """Compatibility property for existing code"""
        return self

class MemoryManager:
    def __init__(self, db_manager: DatabaseManager = None):
        self.db_manager = db_manager or DatabaseManager()
        
        # Check for OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        try:
            
            self.llm = ChatOpenAI(
                model="gpt-4o",
                temperature=0.3,
                api_key=api_key
            )
            
        except Exception as e:
            print(f"Error initializing OpenAI components: {e}")
            raise
        
        # Initialize in-memory store for long-term semantic memory
        self.store = InMemoryStore()
        
        # Per-user memory storage
        self.user_memories = {}
        self.memory_profiles_dir = "user_profiles"
        os.makedirs(self.memory_profiles_dir, exist_ok=True)
    
    def get_user_memory(self, user_id: str) -> Dict[str, Any]:
        """Get or create user memory system"""
        if user_id not in self.user_memories:
            self.user_memories[user_id] = self._initialize_user_memory(user_id)
        return self.user_memories[user_id]
    
    def _initialize_user_memory(self, user_id: str) -> Dict[str, Any]:
        """Initialize memory system for a user"""
        # Load existing memory profile
        memory_profile = self._load_memory_profile(user_id)
        
        # Short-term memory using modern approach
        short_term_memory = ModernConversationMemory(
            llm=self.llm,
            max_messages=20
        )
        
        # Restore short-term memory from profile
        if memory_profile.get('short_term_summary'):
            short_term_memory.buffer = memory_profile['short_term_summary']
        
        # Restore chat history
        if memory_profile.get('recent_messages'):
            for msg in memory_profile['recent_messages']:
                if msg['type'] == 'human':
                    short_term_memory.add_user_message(msg['content'])
                else:
                    short_term_memory.add_ai_message(msg['content'])
        
        # Restore long-term memories to store
        if memory_profile.get('long_term_memories'):
            for memory_item in memory_profile['long_term_memories']:
                self.store.put(
                    (user_id, "memories"),
                    memory_item['key'],
                    {
                        "text": memory_item['text'],
                        "timestamp": memory_item['timestamp'],
                        "importance": memory_item.get('importance', 0.5)
                    }
                )
        
        return {
            'short_term_memory': short_term_memory,
            'short_term_messages': self._get_short_term_messages(short_term_memory),
            'summary_buffer': short_term_memory.buffer if short_term_memory.buffer else "",
            'profile': memory_profile,
            'last_updated': memory_profile.get('last_updated'),
            'conversation_count': memory_profile.get('conversation_count', 0)
        }
    
    def _load_memory_profile(self, user_id: str) -> Dict[str, Any]:
        """Load user memory profile from JSON file"""
        profile_path = os.path.join(self.memory_profiles_dir, f"{user_id}_profile.json")
        
        if os.path.exists(profile_path):
            try:
                with open(profile_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading memory profile for {user_id}: {e}")
        
        # Return default profile structure
        return {
            'user_id': user_id,
            'personality_traits': [],
            'preferences': {},
            'emotional_patterns': {},
            'goals': [],
            'habits': [],
            'conversation_topics': [],
            'recent_messages': [],
            'short_term_summary': '',
            'long_term_memories': [],
            'last_updated': None,
            'conversation_count': 0
        }
    
    def save_memory_profile(self, user_id: str):
        """Save user memory profile to JSON file"""
        if user_id not in self.user_memories:
            return
        
        memory = self.user_memories[user_id]
        profile = memory['profile']
        
        # Update recent messages from short-term memory
        recent_messages = []
        short_term = memory['short_term_memory']
        if hasattr(short_term, 'messages'):
            for msg in short_term.messages[-10:]:  # Keep last 10 messages
                if isinstance(msg, HumanMessage):
                    recent_messages.append({'type': 'human', 'content': msg.content})
                elif isinstance(msg, AIMessage):
                    recent_messages.append({'type': 'ai', 'content': msg.content})
        
        profile['recent_messages'] = recent_messages
        profile['short_term_summary'] = short_term.buffer
        
        # Save long-term memories from store
        long_term_memories = []
        try:
            # Get all memories for this user
            items = self.store.search((user_id, "memories"), query="", limit=100)
            for item in items:
                long_term_memories.append({
                    'key': item.key,
                    'text': item.value.get('text', ''),
                    'timestamp': item.value.get('timestamp'),
                    'importance': item.value.get('importance', 0.5)
                })
        except Exception as e:
            print(f"Warning: Could not save long-term memories for {user_id}: {e}")
        
        profile['long_term_memories'] = long_term_memories
        profile['last_updated'] = datetime.now().isoformat()
        profile['conversation_count'] = memory['conversation_count']
        
        # Save to file
        profile_path = os.path.join(self.memory_profiles_dir, f"{user_id}_profile.json")
        try:
            with open(profile_path, 'w') as f:
                json.dump(profile, f, indent=2)
        except Exception as e:
            print(f"Error saving memory profile for {user_id}: {e}")
    
    def add_interaction(self, user_id: str, human_message: str, ai_message: str, metadata: Dict = None):
        """Add an interaction to user memory"""
        memory = self.get_user_memory(user_id)
        
        # Add to short-term memory
        short_term = memory['short_term_memory']
        short_term.add_user_message(human_message)
        short_term.add_ai_message(ai_message)
        
        # Update conversation count
        memory['conversation_count'] += 1
        
        # Save to database
        try:
            self.db_manager.save_conversation(user_id, 'human', human_message, metadata)
            self.db_manager.save_conversation(user_id, 'ai', ai_message, metadata)
        except Exception as e:
            print(f"Warning: Could not save to database: {e}")
        
        # Save important interactions to long-term memory store
        self._save_to_long_term_memory(user_id, human_message, ai_message, metadata)
        
        # Periodically consolidate memory
        if memory['conversation_count'] % 10 == 0:  # Every 10 interactions
            self._consolidate_memory(user_id)
        
        # Save profile
        self.save_memory_profile(user_id)
    
    def _save_to_long_term_memory(self, user_id: str, human_message: str, ai_message: str, metadata: Dict = None):
        """Save important conversation parts to long-term memory"""
        # Create combined context for better semantic search
        conversation_context = f"Human: {human_message}\nAI: {ai_message}"
        
        # Determine importance based on message characteristics
        importance = self._calculate_importance(human_message, ai_message, metadata)
        
        # Only save if importance is above threshold
        if importance > 0.3:
            memory_key = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            self.store.put(
                (user_id, "memories"),
                memory_key,
                {
                    "text": conversation_context,
                    "timestamp": timestamp,
                    "importance": importance,
                    "human_message": human_message,
                    "ai_message": ai_message
                }
            )
    
    def _calculate_importance(self, human_message: str, ai_message: str, metadata: Dict = None) -> float:
        """Calculate importance score for a conversation"""
        importance = 0.5  # Base importance
        
        # Increase importance for certain keywords
        important_keywords = [
            'remember', 'important', 'preference', 'like', 'dislike', 'goal', 
            'plan', 'schedule', 'appointment', 'birthday', 'anniversary',
            'family', 'work', 'hobby', 'interest', 'problem', 'issue'
        ]
        
        text_to_check = (human_message + " " + ai_message).lower()
        
        for keyword in important_keywords:
            if keyword in text_to_check:
                importance += 0.1
        
        # Increase importance for longer messages (more context)
        if len(human_message) > 50:
            importance += 0.1
        
        # Increase importance if metadata suggests it's important
        if metadata and metadata.get('important', False):
            importance += 0.3
        
        return min(importance, 1.0)  # Cap at 1.0
    
    def _consolidate_memory(self, user_id: str):
        """Consolidate short-term memory into summary"""
        memory = self.get_user_memory(user_id)
        
        try:
            short_term = memory['short_term_memory']
            
            # ModernConversationMemory automatically maintains a summary
            # We just need to trigger an update if there are new messages
            if hasattr(short_term, 'messages') and short_term.messages:
                # The summary is automatically updated by ModernConversationMemory
                # when new messages are added, so we don't need to do anything special
                print(f"✅ Memory consolidated for user {user_id}")
        
        except Exception as e:
            print(f"Error consolidating memory for {user_id}: {e}")
    
    def search_memories(self, user_id: str, query: str, limit: int = 5) -> List[str]:
        """Search for relevant memories using the in-memory store"""
        try:
            # Search in the store for this user's memories
            items = self.store.search((user_id, "memories"), query=query, limit=limit)
            return [item.value["text"] for item in items]
            
        except Exception as e:
            print(f"Error searching memories for {user_id}: {e}")
            return []
    
    def save_recall_memory(self, user_id: str, memory_text: str, memory_type: str = "explicit") -> str:
        """Save a specific memory for later recall"""
        memory_key = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        self.store.put(
            (user_id, "memories"),
            memory_key,
            {
                "text": memory_text,
                "timestamp": timestamp,
                "memory_type": memory_type,
                "importance": 0.8  # High importance for explicitly saved memories
            }
        )
        
        self.save_memory_profile(user_id)
        return memory_text
    
    def get_context_for_conversation(self, user_id: str, current_message: str = "") -> str:
        """Get conversation context from memory"""
        try:
            memory = self.get_user_memory(user_id)
            context_parts = []
            
            # Add short-term summary from ConversationSummaryMemory
            short_term = memory['short_term_memory']
            if short_term.buffer:
                context_parts.append(f"## Recent Conversation Summary\n{short_term.buffer}")
            
            # Add recent conversation history
            if hasattr(short_term, 'messages'):
                recent_messages = short_term.messages[-6:]  # Last 6 messages
                if recent_messages:
                    recent_text = "## Recent Messages\n"
                    for msg in recent_messages:
                        if isinstance(msg, HumanMessage):
                            recent_text += f"Human: {msg.content}\n"
                        elif isinstance(msg, AIMessage):
                            recent_text += f"AI: {msg.content}\n"
                    context_parts.append(recent_text)
            
            # Add relevant memories based on current message (with error handling)
            if current_message:
                try:
                    relevant_memories = self.search_memories(user_id, current_message, limit=3)
                    if relevant_memories:
                        memory_text = "## Relevant Memories\n" + "\n".join(relevant_memories)
                        context_parts.append(memory_text)
                except Exception as e:
                    print(f"Warning: Could not search memories for context: {e}")
            
            # Add personality and preferences
            profile = memory['profile']
            if profile.get('personality_traits'):
                context_parts.append(f"## User Personality\n{', '.join(profile['personality_traits'])}")
            
            if profile.get('preferences'):
                prefs = [f"{k}: {v}" for k, v in profile['preferences'].items()]
                context_parts.append(f"## User Preferences\n{', '.join(prefs)}")
            
            return "\n\n".join(context_parts)
            
        except Exception as e:
            print(f"Error getting conversation context for {user_id}: {e}")
            # Return basic context
            return f"## Basic Context\nUser ID: {user_id}\nCurrent message: {current_message}"
    
    def load_memories_for_conversation(self, user_id: str, messages: List[Dict]) -> List[str]:
        """Load relevant memories based on conversation context"""
        if not messages:
            return []
        
        # Get conversation context from last few messages
        conversation_text = ""
        for msg in messages[-3:]:  # Last 3 messages for context
            content = msg.get('content', '')
            conversation_text += f"{content} "
        
        # Search for relevant memories
        return self.search_memories(user_id, conversation_text.strip(), limit=5)
    
    def update_user_profile(self, user_id: str, updates: Dict[str, Any]):
        """Update user profile with new information"""
        memory = self.get_user_memory(user_id)
        profile = memory['profile']
        
        for key, value in updates.items():
            if key in ['personality_traits', 'conversation_topics']:
                # Append to lists, avoiding duplicates
                if isinstance(value, list):
                    current_list = profile.get(key, [])
                    for item in value:
                        if item not in current_list:
                            current_list.append(item)
                    profile[key] = current_list
                else:
                    current_list = profile.get(key, [])
                    if value not in current_list:
                        current_list.append(value)
                    profile[key] = current_list
            else:
                # Direct update for other fields
                if key == 'preferences' and isinstance(value, dict):
                    current_prefs = profile.get('preferences', {})
                    current_prefs.update(value)
                    profile['preferences'] = current_prefs
                else:
                    profile[key] = value
        
        self.save_memory_profile(user_id)
    
    def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """Export all user data for backup/transfer"""
        try:
            memory = self.get_user_memory(user_id)
            
            # Get conversation history from database
            conversation_history = []
            goals = []
            habits = []
            mood_history = []
            
            try:
                conversation_history = self.db_manager.get_conversation_history(user_id, limit=1000)
                goals = self.db_manager.get_user_goals(user_id)
                habits = self.db_manager.get_user_habits(user_id)
                mood_history = self.db_manager.get_mood_history(user_id, days=365)
            except Exception as e:
                print(f"Warning: Could not get data from database: {e}")
            
            # Get recent messages from short-term memory
            recent_messages = []
            short_term = memory['short_term_memory']
            if hasattr(short_term, 'messages'):
                for msg in short_term.messages:
                    if isinstance(msg, HumanMessage):
                        recent_messages.append({'type': 'human', 'content': msg.content})
                    elif isinstance(msg, AIMessage):
                        recent_messages.append({'type': 'ai', 'content': msg.content})
            
            # Get long-term memories from store
            long_term_memories = []
            try:
                items = self.store.search((user_id, "memories"), query="", limit=100)
                for item in items:
                    long_term_memories.append({
                        'text': item.value.get('text', ''),
                        'timestamp': item.value.get('timestamp'),
                        'importance': item.value.get('importance', 0.5)
                    })
            except Exception as e:
                print(f"Warning: Could not get long-term memories: {e}")
            
            return {
                'user_id': user_id,
                'profile': memory['profile'],
                'conversation_history': conversation_history,
                'goals': goals,
                'habits': habits,
                'mood_history': mood_history,
                'recent_messages': recent_messages,
                'summary_buffer': short_term.buffer,
                'long_term_memories': long_term_memories,
                'export_timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error exporting user data for {user_id}: {e}")
            return {
                'user_id': user_id,
                'error': str(e),
                'export_timestamp': datetime.now().isoformat()
            }
    
    def import_user_data(self, user_data: Dict[str, Any]) -> bool:
        """Import user data from backup"""
        try:
            user_id = user_data['user_id']
            
            # Update memory profile
            if 'profile' in user_data:
                memory = self.get_user_memory(user_id)
                memory['profile'] = user_data['profile']
                
                # Restore recent messages if available
                if 'recent_messages' in user_data:
                    short_term = memory['short_term_memory']
                    for msg in user_data['recent_messages']:
                        if msg['type'] == 'human':
                            short_term.add_user_message(msg['content'])
                        else:
                            short_term.add_ai_message(msg['content'])
                
                # Restore summary buffer
                if 'summary_buffer' in user_data:
                    short_term.buffer = user_data['summary_buffer']
                
                # Restore long-term memories
                if 'long_term_memories' in user_data:
                    for memory_item in user_data['long_term_memories']:
                        memory_key = str(uuid.uuid4())
                        self.store.put(
                            (user_id, "memories"),
                            memory_key,
                            {
                                "text": memory_item.get('text', ''),
                                "timestamp": memory_item.get('timestamp'),
                                "importance": memory_item.get('importance', 0.5)
                            }
                        )
                
                self.save_memory_profile(user_id)
            
            return True
        
        except Exception as e:
            print(f"Error importing user data: {e}")
            return False
    
    def clear_user_memory(self, user_id: str):
        """Clear all memory for a user"""
        if user_id in self.user_memories:
            del self.user_memories[user_id]
        
        # Clear long-term memories from store
        try:
            # Delete all memories for this user from the store
            items = self.store.search((user_id, "memories"), query="", limit=1000)
            for item in items:
                self.store.delete((user_id, "memories"), item.key)
        except Exception as e:
            print(f"Warning: Could not clear memories from store: {e}")
        
        # Delete profile file
        profile_path = os.path.join(self.memory_profiles_dir, f"{user_id}_profile.json")
        if os.path.exists(profile_path):
            os.remove(profile_path)
        
        print(f"✅ Cleared all memory for user {user_id}")
    
    def _get_short_term_messages(self, short_term_memory) -> List[Dict[str, str]]:
        """Extract messages from short-term memory for easier access"""
        messages = []
        if hasattr(short_term_memory, 'messages'):
            for msg in short_term_memory.messages:
                if hasattr(msg, 'content'):
                    msg_type = 'human' if isinstance(msg, HumanMessage) else 'ai'
                    messages.append({
                        'type': msg_type,
                        'content': msg.content
                    })
        return messages
