import json
import os
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import deque
import asyncio
import hashlib
import re

from langchain_core.messages import get_buffer_string, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langgraph.store.memory import InMemoryStore
from pinecone import Pinecone, ServerlessSpec

from core.database import DatabaseManager


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


class EpisodicMemoryFramework:
    """Framework for capturing structured episodic memories"""
    
    # Lifestyle spheres from Vision Board
    LIFESTYLE_SPHERES = {
        'self': ['journaling', 'meditation', 'self-care', 'reflection', 'growth', 'mindfulness'],
        'career': ['work', 'job', 'professional', 'business', 'career', 'achievement'],
        'movement': ['exercise', 'fitness', 'dance', 'sports', 'walking', 'yoga'],
        'relationships': ['family', 'friends', 'love', 'partner', 'social', 'community'],
        'environment': ['home', 'space', 'travel', 'nature', 'place', 'location'],
        'exploration': ['learning', 'discovery', 'adventure', 'new', 'experience', 'curiosity']
    }
    
    # Emotional themes
    EMOTIONAL_THEMES = {
        'clarity': ['clear', 'focused', 'certain', 'understood', 'obvious'],
        'healing': ['healing', 'recovery', 'therapy', 'processing', 'emotional'],
        'confidence': ['confident', 'strong', 'capable', 'empowered', 'assured'],
        'freedom': ['free', 'liberated', 'independent', 'autonomous', 'unrestricted']
    }
    
    # Life seasons/energy
    LIFE_SEASONS = {
        'reset': ['fresh start', 'new beginning', 'starting over', 'clean slate'],
        'glow-up': ['transformation', 'improvement', 'upgrade', 'level up'],
        'building': ['creating', 'constructing', 'developing', 'establishing'],
        'exploring': ['discovering', 'investigating', 'trying new', 'experimenting'],
        'healing': ['recovering', 'processing', 'working through', 'therapeutic']
    }
    
    # Mood aesthetics
    MOOD_AESTHETICS = {
        'cozy': ['warm', 'comfortable', 'intimate', 'peaceful', 'soft'],
        'wild': ['adventurous', 'bold', 'fierce', 'untamed', 'rebellious'],
        'soft': ['gentle', 'tender', 'calm', 'soothing', 'delicate'],
        'romantic': ['dreamy', 'passionate', 'loving', 'enchanting', 'beautiful'],
        'quiet': ['still', 'silent', 'peaceful', 'minimal', 'simple'],
        'structured': ['organized', 'planned', 'systematic', 'methodical', 'disciplined']
    }
    
    def __init__(self, llm):
        self.llm = llm
    
    def extract_episodic_data(self, user_message: str, ai_response: str) -> Dict[str, Any]:
        """Extract episodic memory components from conversation"""
        try:
            combined_text = f"{user_message} {ai_response}".lower()
            
            # Detect spheres
            detected_spheres = []
            for sphere, keywords in self.LIFESTYLE_SPHERES.items():
                if any(keyword in combined_text for keyword in keywords):
                    detected_spheres.append(sphere)
            
            # Detect emotions using LLM
            emotion_result = self._classify_with_llm(
                f"User: {user_message}\nAI: {ai_response}",
                "emotion",
                list(self.EMOTIONAL_THEMES.keys())
            )
            
            # Detect season
            season_result = self._classify_with_llm(
                f"User: {user_message}\nAI: {ai_response}",
                "life_season",
                list(self.LIFE_SEASONS.keys())
            )
            
            # Detect mood aesthetic
            mood_result = self._classify_with_llm(
                f"User: {user_message}\nAI: {ai_response}",
                "mood_aesthetic",
                list(self.MOOD_AESTHETICS.keys())
            )
            
            # Generate affirmation
            affirmation = self._generate_affirmation(user_message, ai_response)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'spheres': detected_spheres,
                'emotion': emotion_result,
                'season': season_result,
                'mood': mood_result,
                'affirmation': affirmation,
                'raw_snippet': user_message[:200] + "..." if len(user_message) > 200 else user_message
            }
            
        except Exception as e:
            print(f"Error extracting episodic data: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'spheres': [],
                'emotion': 'neutral',
                'season': 'exploring',
                'mood': 'soft',
                'affirmation': "I'm on a journey of growth and discovery",
                'raw_snippet': user_message[:200] + "..." if len(user_message) > 200 else user_message
            }
    
    def _classify_with_llm(self, text: str, classification_type: str, options: List[str]) -> str:
        """Use LLM to classify text into categories"""
        try:
            prompt = f"""
            Analyze this conversation snippet and classify the {classification_type}:
            
            {text}
            
            Choose the best match from these options: {', '.join(options)}
            
            Respond with just the single word that best matches.
            """
            
            response = self.llm.invoke(prompt)
            result = response.content.strip().lower()
            
            # Validate result is in options
            if result in options:
                return result
            else:
                # Return first option as default
                return options[0]
                
        except Exception as e:
            print(f"Error in LLM classification: {e}")
            return options[0]  # Default to first option
    
    def _generate_affirmation(self, user_message: str, ai_response: str) -> str:
        """Generate a personalized affirmation based on the conversation"""
        try:
            prompt = f"""
            Based on this conversation, create a short, positive affirmation (under 15 words) that captures the user's current theme or journey:
            
            User: {user_message}
            AI: {ai_response}
            
            Format: "I am..." or "I'm learning..." or similar positive statement.
            Make it personal and empowering.
            """
            
            response = self.llm.invoke(prompt)
            affirmation = response.content.strip()
            
            # Ensure it's not too long
            if len(affirmation) > 100:
                affirmation = affirmation[:97] + "..."
            
            return affirmation
            
        except Exception as e:
            print(f"Error generating affirmation: {e}")
            return "I'm growing and learning with each step"


class LocalMemoryStore:
    """Local file-based memory store as fallback when Pinecone is unavailable"""
    
    def __init__(self, storage_dir: str = "vector_stores"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        
        try:
            # Initialize OpenAI embeddings for local storage
            self.embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small",
                api_key=os.getenv("OPENAI_API_KEY")
            )
            self.has_embeddings = True
            print("✅ Local memory store initialized with OpenAI embeddings")
        except Exception as e:
            print(f"⚠️  Local memory store initialized without embeddings: {e}")
            self.has_embeddings = False
    
    def _get_user_file(self, user_id: str) -> str:
        """Get file path for user memories"""
        return os.path.join(self.storage_dir, f"user_{user_id}_memories.json")
    
    def store_memory(self, user_id: str, memory_text: str, metadata: Dict[str, Any] = None) -> str:
        """Store memory locally"""
        try:
            memory_id = str(uuid.uuid4())
            
            # Create memory record
            memory_record = {
                'id': memory_id,
                'text': memory_text,
                'metadata': metadata or {},
                'timestamp': datetime.now().isoformat()
            }
            
            # Load existing memories
            file_path = self._get_user_file(user_id)
            memories = []
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        memories = json.load(f)
                except:
                    memories = []
            
            # Add new memory
            memories.append(memory_record)
            
            # Keep only last 1000 memories to prevent file bloat
            if len(memories) > 1000:
                memories = memories[-1000:]
            
            # Save back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(memories, f, indent=2, ensure_ascii=False)
            
            return memory_id
            
        except Exception as e:
            print(f"Error storing local memory: {e}")
            return ""
    
    def search_memories(self, user_id: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search memories locally (simple text matching when no embeddings)"""
        try:
            file_path = self._get_user_file(user_id)
            if not os.path.exists(file_path):
                return []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                memories = json.load(f)
            
            # Simple keyword matching if no embeddings available
            query_lower = query.lower()
            scored_memories = []
            
            for memory in memories:
                text_lower = memory['text'].lower()
                # Simple scoring based on keyword matches
                score = 0
                for word in query_lower.split():
                    if word in text_lower:
                        score += 1
                
                if score > 0:
                    scored_memories.append({
                        'text': memory['text'],
                        'metadata': memory.get('metadata', {}),
                        'score': score / len(query_lower.split())
                    })
            
            # Sort by score and return top results
            scored_memories.sort(key=lambda x: x['score'], reverse=True)
            return scored_memories[:top_k]
            
        except Exception as e:
            print(f"Error searching local memories: {e}")
            return []
    
    def get_user_memory_count(self, user_id: str) -> int:
        """Get count of stored memories for user"""
        try:
            file_path = self._get_user_file(user_id)
            if not os.path.exists(file_path):
                return 0
            
            with open(file_path, 'r', encoding='utf-8') as f:
                memories = json.load(f)
            return len(memories)
        except:
            return 0
    
    def get_memory_stats(self, user_id: str) -> Dict[str, Any]:
        """Get memory statistics for user"""
        try:
            count = self.get_user_memory_count(user_id)
            return {
                'total_memories': count,
                'storage_type': 'local_file',
                'has_embeddings': self.has_embeddings
            }
        except:
            return {'total_memories': 0, 'storage_type': 'local_file', 'has_embeddings': False}
    
    def delete_user_memories(self, user_id: str) -> bool:
        """Delete all memories for a user"""
        try:
            file_path = self._get_user_file(user_id)
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except:
            return False


class PineconeMemoryStore:
    """Pinecone-based vector store for user memories"""
    
    def __init__(self, api_key: str, index_name: str = "nowwclubchatbot"):
        self.api_key = api_key
        self.index_name = index_name
        
        # Initialize Pinecone client
        self.pc = Pinecone(api_key=api_key)
        
        
        try:
            # Use OpenAI text-embedding-3-small (1536 dimensions) and truncate to 1024
            self.embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small",
                api_key=os.getenv("OPENAI_API_KEY")
            )
            self.embedding_dimension = 1536  
            self.target_dimension = 1024  
            print("✅ Using OpenAI text-embedding-3-small (cloud-based)")
            print(f"   Original: {self.embedding_dimension} dims → Target: {self.target_dimension} dims")
        except Exception as e:
            print(f"❌ Error initializing OpenAI embeddings: {e}")
            print("Please ensure OPENAI_API_KEY is set correctly")
            raise
        
        # Get or create index
        try:
            # Check if index exists
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if index_name not in existing_indexes:
                print(f"Index {index_name} not found. Available indexes: {existing_indexes}")
                # Create index if it doesn't exist
                print(f"Creating index {index_name}...")
                self.pc.create_index(
                    name=index_name,
                    dimension=1024,  
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                print(f"✅ Created Pinecone index: {index_name}")
            
            # Connect to index
            self.index = self.pc.Index(index_name)
            print(f"✅ Connected to Pinecone index: {index_name}")
            
        except Exception as e:
            print(f"❌ Error connecting to Pinecone index: {e}")
            raise
    
    def _get_user_namespace(self, user_id: str) -> str:
        """Get namespace for user"""
        return f"user-{user_id}"
    
    def _create_embedding(self, text: str) -> List[float]:
        """Create embedding for text and ensure it matches the 1024-dimension target"""
        try:
            # Get embedding from OpenAI
            embedding = self.embeddings.embed_query(text)
            
            # Ensure we have the right dimension for the Pinecone index (1024)
            if len(embedding) == self.target_dimension:
                return embedding
            elif len(embedding) > self.target_dimension:
                # Truncate to target dimension (1024)
                return embedding[:self.target_dimension]
            else:
                # Pad with zeros if somehow smaller
                return embedding + [0.0] * (self.target_dimension - len(embedding))
                
        except Exception as e:
            print(f"Error creating embedding: {e}")
            # Return zero vector with correct dimension (1024)
            return [0.0] * self.target_dimension
    
    def store_memory(self, user_id: str, memory_text: str, metadata: Dict[str, Any] = None) -> str:
        """Store a memory in Pinecone"""
        try:
            # Create unique ID
            memory_id = str(uuid.uuid4())
            
            # Create embedding
            embedding = self._create_embedding(memory_text)
            
            # Prepare metadata
            meta = {
                'text': memory_text,
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                **(metadata or {})
            }
            
            # Store in Pinecone with user namespace
            self.index.upsert(
                vectors=[(memory_id, embedding, meta)],
                namespace=self._get_user_namespace(user_id)
            )
            
            return memory_id
            
        except Exception as e:
            print(f"Error storing memory in Pinecone: {e}")
            return ""
    
    def search_memories(self, user_id: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar memories"""
        try:
            # Create query embedding
            query_embedding = self._create_embedding(query)
            
            # Search in user's namespace
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                namespace=self._get_user_namespace(user_id)
            )
            
            # Format results
            memories = []
            for match in results.matches:
                memories.append({
                    'id': match.id,
                    'score': match.score,
                    'text': match.metadata.get('text', ''),
                    'timestamp': match.metadata.get('timestamp', ''),
                    'metadata': match.metadata
                })
            
            return memories
            
        except Exception as e:
            print(f"Error searching memories in Pinecone: {e}")
            return []
    
    def delete_user_memories(self, user_id: str):
        """Delete all memories for a user"""
        try:
            # Delete entire namespace
            self.index.delete(delete_all=True, namespace=self._get_user_namespace(user_id))
            print(f"✅ Deleted all memories for user {user_id}")
        except Exception as e:
            print(f"Error deleting user memories: {e}")
    
    def get_memory_stats(self, user_id: str) -> Dict[str, Any]:
        """Get statistics about user's memories"""
        try:
            # Get namespace stats
            stats = self.index.describe_index_stats()
            user_namespace = self._get_user_namespace(user_id)
            
            if user_namespace in stats.namespaces:
                return {
                    'total_memories': stats.namespaces[user_namespace].vector_count,
                    'namespace': user_namespace
                }
            else:
                return {
                    'total_memories': 0,
                    'namespace': user_namespace
                }
                
        except Exception as e:
            print(f"Error getting memory stats: {e}")
            return {'total_memories': 0, 'namespace': self._get_user_namespace(user_id)}

class MemoryManager:
    """Enhanced Memory Manager with Pinecone integration and local fallback"""
    
    def __init__(self, db_manager: DatabaseManager = None):
        self.db_manager = db_manager or DatabaseManager()
        
        # Check for required API keys
        openai_key = os.getenv("OPENAI_API_KEY")
        pinecone_key = os.getenv("PINECONE_API_KEY")
        
        if not openai_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        try:
            # Initialize LLM
            self.llm = ChatOpenAI(
                model="gpt-4o",
                temperature=0.3,
                api_key=openai_key
            )
            print("✅ LLM initialized successfully")
            
            # Try to initialize Pinecone, fallback to local storage if fails
            self.memory_store = None
            self.using_pinecone = False
            
            if pinecone_key:
                try:
                    self.memory_store = PineconeMemoryStore(
                        api_key=pinecone_key.strip('"'),
                        index_name="nowwclubchatbot"
                    )
                    self.using_pinecone = True
                    print("✅ Memory system initialized with Pinecone integration")
                except Exception as pinecone_error:
                    print(f"⚠️  Pinecone initialization failed: {pinecone_error}")
                    print("📂 Falling back to local memory storage")
                    self.memory_store = LocalMemoryStore()
                    self.using_pinecone = False
            else:
                print("⚠️  PINECONE_API_KEY not found, using local storage")
                self.memory_store = LocalMemoryStore()
                self.using_pinecone = False
            
            # Initialize episodic memory framework
            self.episodic_framework = EpisodicMemoryFramework(self.llm)
            
        except Exception as e:
            print(f"❌ Critical error initializing memory components: {e}")
            # Create minimal fallback
            self.memory_store = LocalMemoryStore()
            self.using_pinecone = False
            self.episodic_framework = None
            print("📂 Using minimal local storage fallback")
        
        # Initialize in-memory store for session data
        self.store = InMemoryStore()
        
        # Per-user memory storage
        self.user_memories = {}
        self.memory_profiles_dir = "user_profiles"
        os.makedirs(self.memory_profiles_dir, exist_ok=True)
        
        # Episodic memory storage
        self.episodic_dir = os.path.join(self.memory_profiles_dir, "episodic")
        os.makedirs(self.episodic_dir, exist_ok=True)
        
        # Performance optimization - lightweight caches
        self._lightweight_cache = {}
        self._profile_cache = {}
        self._fast_context_cache = {}
    
    def get_lightweight_session_context(self, user_id: str) -> Dict[str, Any]:
        """Get lightweight session context for faster processing"""
        try:
            # Check cache first
            cache_key = f"session_{user_id}"
            if cache_key in self._lightweight_cache:
                cached_time = self._lightweight_cache[cache_key].get('timestamp', 0)
                if time.time() - cached_time < 300:  # 5 minute cache
                    return self._lightweight_cache[cache_key]['data']
            
            memory = self.get_user_memory(user_id)
            context = {
                'has_context': True,
                'conversation_count': memory.get('conversation_count', 0),
                'summary': memory.get('summary_buffer', '')[:100] if memory.get('summary_buffer') else ''
            }
            
            # Cache the result
            self._lightweight_cache[cache_key] = {
                'data': context,
                'timestamp': time.time()
            }
            
            return context
        except:
            return {'has_context': False, 'conversation_count': 0}
    
    def get_fast_context(self, user_id: str, message: str) -> str:
        """Get fast context without heavy vector search when possible"""
        try:
            # Check fast context cache
            cache_key = f"context_{user_id}_{hash(message[:50])}"
            if cache_key in self._fast_context_cache:
                cached_time = self._fast_context_cache[cache_key].get('timestamp', 0)
                if time.time() - cached_time < 180:  # 3 minute cache
                    return self._fast_context_cache[cache_key]['data']
            
            memory = self.get_user_memory(user_id)
            context_parts = []
            
            # Quick summary from buffer
            if memory.get('summary_buffer'):
                context_parts.append(f"Summary: {memory['summary_buffer'][:100]}")
            
            # Recent messages (without vector search)
            short_term = memory['short_term_memory']
            if hasattr(short_term, 'messages') and short_term.messages:
                recent = short_term.messages[-2:]  # Just last 2 messages
                for msg in recent:
                    if hasattr(msg, 'content'):
                        content = msg.content[:80]
                        context_parts.append(content)
            
            context = " | ".join(context_parts)
            
            # Cache the result
            self._fast_context_cache[cache_key] = {
                'data': context,
                'timestamp': time.time()
            }
            
            return context
        except:
            return ""
    
    def get_cached_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get cached user profile for faster access"""
        try:
            # Check profile cache
            if user_id in self._profile_cache:
                cached_time = self._profile_cache[user_id].get('timestamp', 0)
                if time.time() - cached_time < 600:  # 10 minute cache
                    return self._profile_cache[user_id]['data']
            
            memory = self.get_user_memory(user_id)
            profile = memory.get('profile', {})
            
            # Cache the profile
            self._profile_cache[user_id] = {
                'data': profile,
                'timestamp': time.time()
            }
            
            return profile
        except:
            return {}
    
    def _save_memory_profile(self, user_id: str, profile_data: Dict[str, Any]):
        """Save user memory profile to disk"""
        try:
            profile_path = os.path.join(self.memory_profiles_dir, f"{user_id}_profile.json")
            
            # Update timestamp
            profile_data['last_updated'] = datetime.now().isoformat()
            
            # Save to file
            with open(profile_path, 'w', encoding='utf-8') as file:
                json.dump(profile_data, file, indent=2, ensure_ascii=False)
            
            # Update in-memory cache
            if user_id in self.user_memories:
                self.user_memories[user_id]['profile'] = profile_data
                
        except Exception as e:
            print(f"Warning: Could not save memory profile for {user_id}: {e}")
    
    def add_lightweight_interaction(self, user_id: str, human_message: str, ai_message: str):
        """Add interaction with minimal memory processing for performance"""
        try:
            memory = self.get_user_memory(user_id)
            
            # Add to short-term memory only
            short_term = memory['short_term_memory']
            short_term.add_user_message(human_message)
            short_term.add_ai_message(ai_message)
            
            # Update conversation count
            memory['conversation_count'] = memory.get('conversation_count', 0) + 1
            
            # Save profile update only (skip heavy Pinecone operations)
            self._save_memory_profile(user_id, memory['profile'])
            
            print(f"✅ Lightweight interaction stored for {user_id}")
            
        except Exception as e:
            print(f"Warning: Could not store lightweight interaction: {e}")
            # Fallback to regular add_interaction
            self.add_interaction(user_id, human_message, ai_message)
    
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
        
        # Load episodic memories
        episodic_memories = self._load_episodic_memories(user_id)
        
        return {
            'short_term_memory': short_term_memory,
            'short_term_messages': self._get_short_term_messages(short_term_memory),
            'summary_buffer': short_term_memory.buffer if short_term_memory.buffer else "",
            'profile': memory_profile,
            'episodic_memories': episodic_memories,
            'last_updated': memory_profile.get('last_updated'),
            'conversation_count': memory_profile.get('conversation_count', 0),
            'interaction_count': 0  # Count for episodic memory capture
        }
    
    def add_interaction(self, user_id: str, human_message: str, ai_message: str, metadata: Dict = None):
        """Add an interaction to user memory with Pinecone and episodic capture"""
        memory = self.get_user_memory(user_id)
        
        # Add to short-term memory
        short_term = memory['short_term_memory']
        short_term.add_user_message(human_message)
        short_term.add_ai_message(ai_message)
        
        # Update conversation count
        memory['conversation_count'] += 1
        memory['interaction_count'] += 1
        
        # Store conversation in database for long-term access
        self._store_conversation_in_database(user_id, human_message, ai_message, metadata)
        
        # Store in Pinecone for semantic search
        self._store_semantic_memory(user_id, human_message, ai_message, metadata)
        
        # Capture episodic memory every 3-5 interactions
        if memory['interaction_count'] >= 3:
            self._capture_episodic_memory(user_id, human_message, ai_message)
            memory['interaction_count'] = 0  # Reset counter
        
        # Periodically consolidate memory
        if memory['conversation_count'] % 10 == 0:  # Every 10 interactions
            self._consolidate_memory(user_id)
        
        # Save profile
        self.save_memory_profile(user_id)
    
    def _store_conversation_in_database(self, user_id: str, human_message: str, ai_message: str, metadata: Dict = None):
        """Store conversation in database for complete history"""
        try:
            # Store human message
            self.db_manager.save_conversation(
                user_id=user_id,
                message_type="human",
                content=human_message,
                metadata={
                    'timestamp': datetime.now().isoformat(),
                    'session_id': metadata.get('session_id', 'default') if metadata else 'default',
                    **(metadata or {})
                }
            )
            
            # Store AI message
            self.db_manager.save_conversation(
                user_id=user_id,
                message_type="ai",
                content=ai_message,
                metadata={
                    'timestamp': datetime.now().isoformat(),
                    'session_id': metadata.get('session_id', 'default') if metadata else 'default',
                    **(metadata or {})
                }
            )
            
        except Exception as e:
            print(f"Error storing conversation in database: {e}")
    
    def get_conversation_memory(self, user_id: str, query: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        """Get conversation history for memory recall"""
        try:
            # Get recent conversations from database
            conversations = self.db_manager.get_conversation_history(user_id, limit * 2)  # Get more to filter
            
            # If no query, return recent conversations
            if not query:
                return conversations[:limit]
            
            # Search for relevant conversations
            query_lower = query.lower()
            relevant_conversations = []
            
            for conv in conversations:
                content = conv.get('content', '').lower()
                if any(word in content for word in query_lower.split()):
                    relevant_conversations.append(conv)
                
                if len(relevant_conversations) >= limit:
                    break
            
            return relevant_conversations[:limit]
            
        except Exception as e:
            print(f"Error getting conversation memory: {e}")
            return []
    
    def search_conversation_history(self, user_id: str, query: str, days_back: int = 7) -> str:
        """Search conversation history for relevant context"""
        try:
            # Get conversations from the last N days
            conversations = self.db_manager.get_conversation_history(user_id, limit=100)
            
            # Filter by date if needed
            from datetime import datetime, timedelta
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            query_lower = query.lower()
            relevant_parts = []
            
            current_pair = {"human": None, "ai": None}
            
            for conv in conversations:
                # Parse timestamp
                try:
                    conv_time = datetime.fromisoformat(conv['timestamp'])
                    if conv_time < cutoff_date:
                        continue
                except:
                    continue  # Skip if can't parse timestamp
                
                content = conv.get('content', '')
                msg_type = conv.get('message_type', '')
                
                # Build conversation pairs
                if msg_type == 'human':
                    current_pair["human"] = content
                elif msg_type == 'ai' and current_pair["human"]:
                    current_pair["ai"] = content
                    
                    # Check if this pair is relevant
                    combined_content = f"{current_pair['human']} {current_pair['ai']}".lower()
                    if any(word in combined_content for word in query_lower.split()):
                        relevant_parts.append(f"User: {current_pair['human']}\nAssistant: {current_pair['ai']}")
                    
                    # Reset for next pair
                    current_pair = {"human": None, "ai": None}
                
                if len(relevant_parts) >= 5:  # Limit results
                    break
            
            if relevant_parts:
                return f"🧠 Previous conversations:\n" + "\n\n".join(relevant_parts[-3:])  # Last 3 relevant
            else:
                return "No relevant previous conversations found."
                
        except Exception as e:
            print(f"Error searching conversation history: {e}")
            return "Unable to search conversation history."
    
    def _store_semantic_memory(self, user_id: str, human_message: str, ai_message: str, metadata: Dict = None):
        """Store conversation in Pinecone for semantic search"""
        try:
            # Create conversation context for better semantic search
            conversation_context = f"User: {human_message}\nAssistant: {ai_message}"
            
            # Determine importance
            importance = self._calculate_importance(human_message, ai_message, metadata)
            
            # Store in Pinecone if important enough
            if importance > 0.3:
                memory_metadata = {
                    'importance': importance,
                    'human_message': human_message,
                    'ai_message': ai_message,
                    'conversation_type': 'chat',
                    **(metadata or {})
                }
                
                memory_id = self.memory_store.store_memory(
                    user_id, 
                    conversation_context, 
                    memory_metadata
                )
                
                if memory_id:
                    print(f"✅ Stored semantic memory for user {user_id}")
                
        except Exception as e:
            print(f"Error storing semantic memory: {e}")
    
    def _capture_episodic_memory(self, user_id: str, human_message: str, ai_message: str):
        """Capture structured episodic memory"""
        try:
            # Extract episodic components
            episodic_data = self.episodic_framework.extract_episodic_data(human_message, ai_message)
            episodic_data['user_id'] = user_id
            
            # Load existing episodic memories
            memory = self.get_user_memory(user_id)
            episodic_memories = memory['episodic_memories']
            
            # Add new episodic memory
            episodic_memories.append(episodic_data)
            
            # Keep only last 100 episodic memories
            if len(episodic_memories) > 100:
                episodic_memories = episodic_memories[-100:]
                memory['episodic_memories'] = episodic_memories
            
            # Save episodic memories
            self._save_episodic_memories(user_id, episodic_memories)
            
            # Store episodic summary in vector store
            episodic_summary = self._create_episodic_summary(episodic_data)
            self.memory_store.store_memory(
                user_id,
                episodic_summary,
                {
                    'type': 'episodic',
                    'spheres': episodic_data['spheres'],
                    'emotion': episodic_data['emotion'],
                    'season': episodic_data['season'],
                    'mood': episodic_data['mood'],
                    'affirmation': episodic_data['affirmation']
                }
            )
            
            print(f"✅ Captured episodic memory for user {user_id}")
            
        except Exception as e:
            print(f"Error capturing episodic memory: {e}")
    
    def _create_episodic_summary(self, episodic_data: Dict[str, Any]) -> str:
        """Create a text summary of episodic data for storage"""
        spheres = ", ".join(episodic_data.get('spheres', []))
        return f"""
        Lifestyle focus: {spheres}
        Emotional theme: {episodic_data.get('emotion', 'neutral')}
        Life season: {episodic_data.get('season', 'exploring')}
        Mood aesthetic: {episodic_data.get('mood', 'soft')}
        Affirmation: {episodic_data.get('affirmation', '')}
        Context: {episodic_data.get('raw_snippet', '')}
        """.strip()
    
    def search_semantic_memories(self, user_id: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant memories using Pinecone"""
        try:
            return self.memory_store.search_memories(user_id, query, top_k=limit)
        except Exception as e:
            print(f"Error searching semantic memories: {e}")
            return []
    
    def get_context_for_conversation(self, user_id: str, current_message: str = "") -> str:
        """Get enhanced conversation context from all memory sources"""
        try:
            memory = self.get_user_memory(user_id)
            context_parts = []
            
            # Add short-term summary
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
                            recent_text += f"User: {msg.content}\n"
                        elif isinstance(msg, AIMessage):
                            recent_text += f"Assistant: {msg.content}\n"
                    context_parts.append(recent_text)
            
            # Add semantic memories from Pinecone
            if current_message:
                try:
                    semantic_memories = self.search_semantic_memories(user_id, current_message, limit=3)
                    if semantic_memories:
                        memory_text = "## Relevant Past Conversations\n"
                        for mem in semantic_memories:
                            memory_text += f"- {mem['text'][:200]}...\n"
                        context_parts.append(memory_text)
                except Exception as e:
                    print(f"Warning: Could not search semantic memories: {e}")
            
            # Add episodic memory insights
            episodic_insights = self._get_episodic_insights(user_id)
            if episodic_insights:
                context_parts.append(f"## User's Journey Insights\n{episodic_insights}")
            
            # Add user profile
            profile = memory['profile']
            if profile.get('personality_traits'):
                context_parts.append(f"## User Personality\n{', '.join(profile['personality_traits'])}")
            
            if profile.get('preferences'):
                prefs = [f"{k}: {v}" for k, v in profile['preferences'].items()]
                context_parts.append(f"## User Preferences\n{', '.join(prefs)}")
            
            return "\n\n".join(context_parts)
            
        except Exception as e:
            print(f"Error getting conversation context for {user_id}: {e}")
            return f"## Basic Context\nUser ID: {user_id}\nCurrent message: {current_message}"
    
    def _get_episodic_insights(self, user_id: str) -> str:
        """Get insights from episodic memories"""
        try:
            memory = self.get_user_memory(user_id)
            episodic_memories = memory['episodic_memories']
            
            if not episodic_memories:
                return ""
            
            # Get recent episodic memories (last 10)
            recent_episodes = episodic_memories[-10:]
            
            # Aggregate insights
            spheres = []
            emotions = []
            seasons = []
            moods = []
            affirmations = []
            
            for episode in recent_episodes:
                spheres.extend(episode.get('spheres', []))
                emotions.append(episode.get('emotion', ''))
                seasons.append(episode.get('season', ''))
                moods.append(episode.get('mood', ''))
                affirmations.append(episode.get('affirmation', ''))
            
            # Create insights
            insights = []
            
            # Most common spheres
            if spheres:
                sphere_counts = {}
                for sphere in spheres:
                    sphere_counts[sphere] = sphere_counts.get(sphere, 0) + 1
                top_spheres = sorted(sphere_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                insights.append(f"Focus areas: {', '.join([s[0] for s in top_spheres])}")
            
            # Current emotional theme
            if emotions:
                recent_emotion = emotions[-1]
                insights.append(f"Current emotional theme: {recent_emotion}")
            
            # Current season
            if seasons:
                recent_season = seasons[-1]
                insights.append(f"Life season: {recent_season}")
            
            # Latest affirmation
            if affirmations:
                recent_affirmation = affirmations[-1]
                insights.append(f"Personal affirmation: {recent_affirmation}")
            
            return "\n".join(insights)
            
        except Exception as e:
            print(f"Error getting episodic insights: {e}")
            return ""
    
    def generate_vision_story_card(self, user_id: str) -> Dict[str, Any]:
        """Generate a vision story card based on episodic memory"""
        try:
            memory = self.get_user_memory(user_id)
            episodic_memories = memory['episodic_memories']
            
            if not episodic_memories:
                return self._default_vision_card(user_id)
            
            # Aggregate data from recent memories (last 20)
            recent_episodes = episodic_memories[-20:]
            
            spheres = []
            emotions = []
            seasons = []
            moods = []
            affirmations = []
            
            for episode in recent_episodes:
                spheres.extend(episode.get('spheres', []))
                emotions.append(episode.get('emotion', ''))
                seasons.append(episode.get('season', ''))
                moods.append(episode.get('mood', ''))
                affirmations.append(episode.get('affirmation', ''))
            
            # Get most frequent items
            def get_most_common(items):
                if not items:
                    return None
                counts = {}
                for item in items:
                    if item:
                        counts[item] = counts.get(item, 0) + 1
                return max(counts.items(), key=lambda x: x[1])[0] if counts else None
            
            # Create vision card
            vision_card = {
                'user_id': user_id,
                'generated_at': datetime.now().isoformat(),
                'lifestyle_season': get_most_common(seasons) or 'exploring',
                'emotional_theme': get_most_common(emotions) or 'clarity',
                'mood_aesthetic': get_most_common(moods) or 'soft',
                'top_spheres': list(set(spheres))[:3],
                'affirmations': list(set([a for a in affirmations if a]))[:3],
                'vibe_quote': self._generate_vibe_quote(recent_episodes)
            }
            
            return vision_card
            
        except Exception as e:
            print(f"Error generating vision story card: {e}")
            return self._default_vision_card(user_id)
    
    def _default_vision_card(self, user_id: str) -> Dict[str, Any]:
        """Default vision card for new users"""
        return {
            'user_id': user_id,
            'generated_at': datetime.now().isoformat(),
            'lifestyle_season': 'exploring',
            'emotional_theme': 'clarity',
            'mood_aesthetic': 'soft',
            'top_spheres': ['self', 'growth'],
            'affirmations': ['I am on a journey of discovery', 'I embrace growth and change'],
            'vibe_quote': 'Every conversation is a step toward understanding myself better.'
        }
    
    def _generate_vibe_quote(self, episodes: List[Dict[str, Any]]) -> str:
        """Generate a vibe quote from episodic memories"""
        try:
            if not episodes:
                return "Every moment is an opportunity for growth."
            
            # Get recent themes
            recent_snippets = [ep.get('raw_snippet', '') for ep in episodes[-5:]]
            combined_text = " ".join(recent_snippets)
            
            prompt = f"""
            Based on these conversation themes, create an inspiring, personal vibe quote (under 20 words):
            
            {combined_text[:500]}
            
            Make it uplifting, personal, and reflective of their current journey.
            """
            
            response = self.llm.invoke(prompt)
            quote = response.content.strip()
            
            # Clean up quote
            quote = quote.strip('"').strip("'")
            if len(quote) > 100:
                quote = quote[:97] + "..."
            
            return quote
            
        except Exception as e:
            print(f"Error generating vibe quote: {e}")
            return "I am writing my own story, one conversation at a time."
    
    def _load_memory_profile(self, user_id: str) -> Dict[str, Any]:
        """Load user memory profile from JSON file"""
        profile_path = os.path.join(self.memory_profiles_dir, f"{user_id}_profile.json")
        
        if os.path.exists(profile_path):
            try:
                with open(profile_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading memory profile for {user_id}: {e}")
                # Try with different encoding as fallback
                try:
                    with open(profile_path, 'r', encoding='latin-1') as f:
                        return json.load(f)
                except Exception as e2:
                    print(f"Fallback encoding also failed for {user_id}: {e2}")
                    # Create a backup and start fresh
                    import shutil
                    backup_path = profile_path + '.backup'
                    shutil.move(profile_path, backup_path)
                    print(f"Corrupted profile backed up to {backup_path}")
                    
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
            'last_updated': None,
            'conversation_count': 0
        }
    
    def _load_episodic_memories(self, user_id: str) -> List[Dict[str, Any]]:
        """Load episodic memories from JSON file"""
        episodic_path = os.path.join(self.episodic_dir, f"{user_id}_episodic.json")
        
        if os.path.exists(episodic_path):
            try:
                with open(episodic_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading episodic memories for {user_id}: {e}")
        
        return []
    
    def _save_episodic_memories(self, user_id: str, episodic_memories: List[Dict[str, Any]]):
        """Save episodic memories to JSON file"""
        episodic_path = os.path.join(self.episodic_dir, f"{user_id}_episodic.json")
        
        try:
            with open(episodic_path, 'w') as f:
                json.dump(episodic_memories, f, indent=2)
        except Exception as e:
            print(f"Error saving episodic memories for {user_id}: {e}")
    
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
        profile['last_updated'] = datetime.now().isoformat()
        profile['conversation_count'] = memory['conversation_count']
        
        # Save to file
        profile_path = os.path.join(self.memory_profiles_dir, f"{user_id}_profile.json")
        try:
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(profile, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving memory profile for {user_id}: {e}")
    
    def _calculate_importance(self, human_message: str, ai_message: str, metadata: Dict = None) -> float:
        """Calculate importance score for a conversation"""
        importance = 0.5  # Base importance
        
        # Increase importance for certain keywords
        important_keywords = [
            'remember', 'important', 'preference', 'like', 'dislike', 'goal', 
            'plan', 'schedule', 'appointment', 'birthday', 'anniversary',
            'family', 'work', 'hobby', 'interest', 'problem', 'issue',
            'feel', 'emotion', 'stress', 'anxiety', 'happy', 'sad'
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
                print(f"✅ Memory consolidated for user {user_id}")
        
        except Exception as e:
            print(f"Error consolidating memory for {user_id}: {e}")
    
    def search_memories(self, user_id: str, query: str, limit: int = 5) -> List[str]:
        """Search for relevant memories (legacy compatibility)"""
        try:
            # Use Pinecone search
            semantic_memories = self.search_semantic_memories(user_id, query, limit)
            return [mem['text'] for mem in semantic_memories]
            
        except Exception as e:
            print(f"Error searching memories for {user_id}: {e}")
            return []
    
    def save_recall_memory(self, user_id: str, memory_text: str, memory_type: str = "explicit") -> str:
        """Save a specific memory for later recall"""
        try:
            memory_id = self.pinecone_store.store_memory(
                user_id,
                memory_text,
                {
                    'memory_type': memory_type,
                    'importance': 0.8,
                    'explicit_save': True
                }
            )
            
            self.save_memory_profile(user_id)
            return memory_text
            
        except Exception as e:
            print(f"Error saving recall memory: {e}")
            return memory_text
    
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
    
    def get_memory_stats(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        try:
            memory = self.get_user_memory(user_id)
            
            # Pinecone stats
            memory_stats = self.memory_store.get_memory_stats(user_id)
            
            # Episodic memory stats
            episodic_memories = memory['episodic_memories']
            
            # Profile stats
            profile = memory['profile']
            
            return {
                'user_id': user_id,
                'total_conversations': memory['conversation_count'],
                'semantic_memories': memory_stats.get('total_memories', 0),
                'episodic_memories': len(episodic_memories),
                'personality_traits': len(profile.get('personality_traits', [])),
                'preferences': len(profile.get('preferences', {})),
                'last_updated': memory.get('last_updated'),
                'storage_type': memory_stats.get('storage_type', 'unknown')
            }
            
        except Exception as e:
            print(f"Error getting memory stats: {e}")
            return {'user_id': user_id, 'error': str(e)}
    
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
            
            # Get semantic memories from Pinecone
            semantic_memories = []
            try:
                # Search for all memories (use broad query)
                all_memories = self.search_semantic_memories(user_id, "", limit=100)
                semantic_memories = all_memories
            except Exception as e:
                print(f"Warning: Could not get semantic memories: {e}")
            
            # Get episodic memories
            episodic_memories = memory['episodic_memories']
            
            # Generate vision card
            vision_card = self.generate_vision_story_card(user_id)
            
            return {
                'user_id': user_id,
                'profile': memory['profile'],
                'conversation_history': conversation_history,
                'goals': goals,
                'habits': habits,
                'mood_history': mood_history,
                'recent_messages': recent_messages,
                'summary_buffer': short_term.buffer,
                'semantic_memories': semantic_memories,
                'episodic_memories': episodic_memories,
                'vision_card': vision_card,
                'memory_stats': self.get_memory_stats(user_id),
                'export_timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error exporting user data for {user_id}: {e}")
            return {
                'user_id': user_id,
                'error': str(e),
                'export_timestamp': datetime.now().isoformat()
            }
    
    def clear_user_memory(self, user_id: str):
        """Clear all memory for a user"""
        try:
            # Clear in-memory data
            if user_id in self.user_memories:
                del self.user_memories[user_id]
            
            # Clear Pinecone memories
            self.pinecone_store.delete_user_memories(user_id)
            
            # Delete profile file
            profile_path = os.path.join(self.memory_profiles_dir, f"{user_id}_profile.json")
            if os.path.exists(profile_path):
                os.remove(profile_path)
            
            # Delete episodic memory file
            episodic_path = os.path.join(self.episodic_dir, f"{user_id}_episodic.json")
            if os.path.exists(episodic_path):
                os.remove(episodic_path)
            
            print(f"✅ Cleared all memory for user {user_id}")
            
        except Exception as e:
            print(f"Error clearing user memory: {e}")
    
    def get_reflection_prompts(self, user_id: str) -> List[str]:
        """Generate reflection prompts based on user's episodic memory"""
        try:
            memory = self.get_user_memory(user_id)
            episodic_memories = memory['episodic_memories']
            
            if not episodic_memories:
                return [
                    "How are you feeling about your current journey?",
                    "What's one thing you're grateful for today?",
                    "What would you like to focus on this week?"
                ]
            
            # Get recent episode data
            recent_episodes = episodic_memories[-5:]
            
            # Extract themes
            recent_spheres = []
            recent_emotions = []
            recent_seasons = []
            
            for episode in recent_episodes:
                recent_spheres.extend(episode.get('spheres', []))
                recent_emotions.append(episode.get('emotion', ''))
                recent_seasons.append(episode.get('season', ''))
            
            # Generate tailored prompts
            prompts = []
            
            # Sphere-based prompts
            if 'self' in recent_spheres:
                prompts.append("You've been focusing on self-discovery. What insights have you gained about yourself recently?")
            
            if 'career' in recent_spheres:
                prompts.append("How is your professional journey aligning with your personal goals?")
            
            if 'relationships' in recent_spheres:
                prompts.append("What connections in your life are bringing you the most joy?")
            
            # Season-based prompts
            if recent_seasons and recent_seasons[-1] == 'reset':
                prompts.append("You're in your Reset season. What old patterns are you ready to release?")
            elif recent_seasons and recent_seasons[-1] == 'glow-up':
                prompts.append("You're in transformation mode. What positive changes do you want to celebrate?")
            
            # Emotion-based prompts
            if recent_emotions and recent_emotions[-1] == 'clarity':
                prompts.append("You're seeking clarity. What questions are most important to you right now?")
            
            # Default prompts if none generated
            if not prompts:
                prompts = [
                    "What's been on your mind lately?",
                    "How would you describe your current energy?",
                    "What's one small win you'd like to celebrate?"
                ]
            
            return prompts[:3]  # Return max 3 prompts
            
        except Exception as e:
            print(f"Error generating reflection prompts: {e}")
            return [
                "How are you feeling right now?",
                "What's one thing you're looking forward to?",
                "What would make today feel successful?"
            ]
    
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
    
    def restore_session_context(self, user_id: str) -> Dict[str, Any]:
        """Restore complete session context for seamless conversation continuity"""
        try:
            memory = self.get_user_memory(user_id)
            
            # Get recent conversation history
            recent_messages = self._get_short_term_messages(memory['short_term_memory'])
            
            # Get conversation summary
            summary = memory.get('summary_buffer', '')
            
            # Search for recent important memories
            recent_memories = self.search_semantic_memories(
                user_id, 
                "recent conversation important preferences goals",
                limit=5
            )
            
            # Get episodic memory highlights
            episodic_memories = memory.get('episodic_memories', [])
            recent_episodes = episodic_memories[-5:] if episodic_memories else []
            
            # Create context summary
            context_summary = f"""📚 **Session Context for {user_id}**

🔄 **Conversation History:**
- Total conversations: {memory.get('conversation_count', 0)}
- Last updated: {memory.get('last_updated', 'Unknown')}
- Recent messages: {len(recent_messages)}

💭 **Memory Summary:**
{summary if summary else 'No previous session summary available.'}

🎯 **Recent Important Memories:**
{chr(10).join([f"• {mem.get('text', '')[:100]}..." for mem in recent_memories[:3]])}

🌟 **Recent Emotional Themes:**
{chr(10).join([f"• {ep.get('emotion', 'neutral').title()}: {ep.get('affirmation', '')}" for ep in recent_episodes[-3:]])}"""

            return {
                'has_context': True,
                'recent_messages': recent_messages[-10:],  # Last 10 messages
                'summary': summary,
                'recent_memories': [mem.get('text', '') for mem in recent_memories],
                'episodic_highlights': recent_episodes,
                'context_summary': context_summary,
                'conversation_count': memory.get('conversation_count', 0),
                'last_session': memory.get('last_updated')
            }
            
        except Exception as e:
            print(f"Error restoring session context: {e}")
            return {
                'has_context': False,
                'error': str(e),
                'recent_messages': [],
                'summary': '',
                'recent_memories': [],
                'episodic_highlights': [],
                'context_summary': f'Starting a new session with {user_id}! 🌟',
                'conversation_count': 0,
                'last_session': None
            }
    
    def add_vision_board_intake_to_episodic_memory(self, user_id: str, question_num: int, question_data: Dict, raw_answer: str, analyzed_data: Dict) -> None:
        """Store vision board intake response as detailed episodic memory for authentic personalization"""
        try:
            print(f"💾 Storing vision board intake Q{question_num} as episodic memory...")
            
            # Create rich episodic memory entry
            episodic_entry = {
                'timestamp': datetime.now().isoformat(),
                'memory_type': 'vision_board_intake',
                'question_number': question_num,
                'question_theme': question_data.get('theme', ''),
                'question_text': question_data.get('question', ''),
                'question_context': question_data.get('context', ''),
                'raw_user_response': raw_answer,
                'spheres': ['self', 'exploration', 'vision'],
                'emotion': analyzed_data.get('emotional_tone', 'reflective'),
                'season': 'building',
                'mood': analyzed_data.get('core_emotions', ['thoughtful'])[0] if analyzed_data.get('core_emotions') else 'thoughtful',
                'affirmation': f"I shared my authentic truth about {question_data.get('theme', 'my vision')}",
                'raw_snippet': raw_answer[:200],
                
                # Deep analysis data for personalization
                'vision_analysis': {
                    'core_emotions': analyzed_data.get('core_emotions', []),
                    'visual_metaphors': analyzed_data.get('visual_metaphors', []),
                    'color_palette': analyzed_data.get('color_palette', []),
                    'lifestyle_elements': analyzed_data.get('lifestyle_elements', []),
                    'values_revealed': analyzed_data.get('values_revealed', []),
                    'aspirations': analyzed_data.get('aspirations', []),
                    'personality_traits': analyzed_data.get('personality_traits', []),
                    'essence_keywords': analyzed_data.get('essence_keywords', []),
                    'specific_mentions': analyzed_data.get('specific_mentions', []),
                    'visual_style_preference': analyzed_data.get('visual_style_preference', 'natural'),
                    'energy_level': analyzed_data.get('energy_level', 'medium'),
                    'authenticity_score': analyzed_data.get('authenticity_score', '8'),
                    'manifestation_focus': analyzed_data.get('manifestation_focus', []),
                    'symbolic_elements': analyzed_data.get('symbolic_elements', [])
                }
            }
            
            # Load existing episodic memories
            episodic_memories = self._load_episodic_memories(user_id)
            
            # Add new entry
            episodic_memories.append(episodic_entry)
            
            # Keep only last 100 episodic memories to prevent excessive storage
            if len(episodic_memories) > 100:
                episodic_memories = episodic_memories[-100:]
            
            # Save updated episodic memories
            self._save_episodic_memories(user_id, episodic_memories)
            
            # Also store as high-importance semantic memory for easy retrieval
            semantic_memory_text = f"""Vision Board Intake Q{question_num}: {question_data.get('theme', '').title()}

Question: {question_data.get('question', '')}
User Response: "{raw_answer}"

Key Insights:
• Emotions: {', '.join(analyzed_data.get('core_emotions', [])[:3])}
• Visual Style: {analyzed_data.get('visual_style_preference', 'natural')}
• Values: {', '.join(analyzed_data.get('values_revealed', [])[:3])}
• Aspirations: {', '.join(analyzed_data.get('aspirations', [])[:3])}
• Symbols: {', '.join(analyzed_data.get('visual_metaphors', [])[:3])}
• Colors: {', '.join(analyzed_data.get('color_palette', [])[:3])}
• Energy: {analyzed_data.get('energy_level', 'medium')}
• Authenticity: {analyzed_data.get('authenticity_score', '8')}/10

This represents authentic user data for personalized vision board generation."""
            
            self.pinecone_store.store_memory(
                user_id,
                semantic_memory_text,
                {
                    'memory_type': 'vision_board_intake',
                    'question_number': question_num,
                    'theme': question_data.get('theme', ''),
                    'importance': 0.9,
                    'permanent': True,
                    'session_type': 'vision_board_intake'
                }
            )
            
            print(f"✅ Vision board intake Q{question_num} stored in episodic & semantic memory")
            print(f"   🧠 Episodic entry with full analysis data")
            print(f"   💾 Semantic memory for easy retrieval")
            print(f"   🎨 Ready for authentic vision board personalization")
            
        except Exception as e:
            print(f"❌ Error storing vision board intake in episodic memory: {e}")
    
    def get_vision_board_intake_memories(self, user_id: str) -> List[Dict[str, Any]]:
        """Retrieve all vision board intake episodic memories for personalization"""
        try:
            # First try to get from episodic memories
            episodic_memories = self._load_episodic_memories(user_id)
            
            # Filter for vision board intake memories
            intake_memories = [
                memory for memory in episodic_memories 
                if memory.get('memory_type') == 'vision_board_intake'
            ]
            
            # If no episodic memories found, get from database as fallback
            if not intake_memories:
                print(f"⚠️ No episodic intake memories found, checking database...")
                intake_memories = self._get_vision_board_intake_from_database(user_id)
            
            # Sort by question number
            intake_memories.sort(key=lambda x: x.get('question_number', 0))
            
            print(f"📖 Retrieved {len(intake_memories)} vision board intake memories for user {user_id}")
            
            return intake_memories
            
        except Exception as e:
            print(f"❌ Error retrieving vision board intake memories: {e}")
            return []
    
    def _get_vision_board_intake_from_database(self, user_id: str) -> List[Dict[str, Any]]:
        """Fallback method to get vision board intake data from database"""
        try:
            # Get intake data from database
            db_intake = self.db_manager.get_vision_board_intake(user_id)
            
            if not db_intake or db_intake.get('status') != 'completed':
                return []
            
            answers = db_intake.get('answers', {})
            
            # Convert database format to episodic memory format
            intake_memories = []
            
            for q_num_str, answer_data in answers.items():
                q_num = int(q_num_str)
                
                memory_entry = {
                    'timestamp': answer_data.get('analyzed_at', db_intake.get('completed_at', '')),
                    'memory_type': 'vision_board_intake',
                    'question_number': q_num,
                    'question_theme': answer_data.get('theme', ''),
                    'raw_user_response': answer_data.get('answer', ''),
                    'vision_analysis': {
                        'core_emotions': answer_data.get('core_emotions', []),
                        'visual_metaphors': answer_data.get('visual_metaphors', []),
                        'color_palette': answer_data.get('color_palette', []),
                        'lifestyle_elements': answer_data.get('lifestyle_elements', []),
                        'values_revealed': answer_data.get('values_revealed', []),
                        'aspirations': answer_data.get('aspirations', []),
                        'personality_traits': answer_data.get('personality_traits', []),
                        'essence_keywords': answer_data.get('essence_keywords', []),
                        'specific_mentions': [],  # Extract from answer if needed
                        'visual_style_preference': answer_data.get('visual_style_preference', 'natural'),
                        'energy_level': answer_data.get('energy_level', 'medium'),
                        'authenticity_score': answer_data.get('authenticity_score', '8'),
                    }
                }
                
                intake_memories.append(memory_entry)
            
            print(f"📝 Converted {len(intake_memories)} database entries to memory format")
            return intake_memories
            
        except Exception as e:
            print(f"❌ Error getting intake data from database: {e}")
            return []

    def enhance_vision_board_memory(self, user_id: str, vision_board_data: Dict[str, Any]) -> None:
        """Enhance memory specifically for vision board context and cross-session persistence"""
        try:
            # Create comprehensive vision board memory entry
            vision_memory = f"""🎨 **VISION BOARD PROFILE CREATED**

📊 **User Profile Summary:**
• Template: {vision_board_data.get('template_name', 'Unknown')}
• Core Values: {', '.join(vision_board_data.get('personal_values', [])[:5])}
• Primary Goals: {', '.join(vision_board_data.get('user_goals', [])[:5])}
• Emotional Tone: {', '.join(vision_board_data.get('emotional_tone', [])[:5])}
• Visual Style: {vision_board_data.get('visual_style', 'Natural')}
• Energy Level: {vision_board_data.get('energy_level', 'Medium')}

🎯 **Key Aspirations:**
{chr(10).join([f"• {goal}" for goal in vision_board_data.get('aspirations', [])[:5]])}

🎨 **Visual Elements:**
{chr(10).join([f"• {element}" for element in vision_board_data.get('visual_elements', [])[:5]])}

🏠 **Lifestyle Context:**
{chr(10).join([f"• {context}" for context in vision_board_data.get('lifestyle_context', [])[:5]])}

🎨 **Color Preferences:**
{', '.join(vision_board_data.get('color_preferences', [])[:5])}

💫 **Personality Traits:**
{', '.join(vision_board_data.get('personality_traits', [])[:5])}

This vision board profile represents the user's authentic self and deepest aspirations. Reference this for all future vision board conversations and updates."""

            # Store as high-importance semantic memory
            self.pinecone_store.store_memory(
                user_id,
                vision_memory,
                {
                    'memory_type': 'vision_board_profile',
                    'importance': 1.0,
                    'template': vision_board_data.get('template_name', 'Unknown'),
                    'session_type': 'vision_board_completion',
                    'permanent': True
                }
            )
            
            # Save to episodic memory
            episodic_data = {
                'timestamp': datetime.now().isoformat(),
                'spheres': ['self', 'exploration', 'growth'],
                'emotion': 'achievement',
                'season': 'building',
                'mood': 'inspired',
                'affirmation': 'I have created a clear vision for my future',
                'raw_snippet': f"Completed vision board with {vision_board_data.get('template_name', 'personalized')} template"
            }
            
            memory = self.get_user_memory(user_id)
            memory['episodic_memories'].append(episodic_data)
            self._save_episodic_memories(user_id, memory['episodic_memories'])
            
            # Update user profile with vision board insights
            profile_updates = {
                'vision_board_template': vision_board_data.get('template_name'),
                'core_values': vision_board_data.get('personal_values', [])[:5],
                'primary_goals': vision_board_data.get('user_goals', [])[:5],
                'visual_style_preference': vision_board_data.get('visual_style'),
                'energy_level': vision_board_data.get('energy_level'),
                'last_vision_board_created': datetime.now().isoformat()
            }
            
            self.update_user_profile(user_id, profile_updates)
            
            print(f"✅ Enhanced vision board memory for user {user_id}")
            print(f"   💾 Stored: Comprehensive profile, episodic memory, profile updates")
            
        except Exception as e:
            print(f"❌ Error enhancing vision board memory: {e}")
    
    def get_vision_board_context(self, user_id: str) -> str:
        """Get vision board specific context for conversations"""
        try:
            # Search for vision board related memories
            vision_memories = self.search_semantic_memories(
                user_id,
                "vision board template values goals aspirations personality visual style",
                limit=5
            )
            
            if not vision_memories:
                return "No previous vision board context found. Ready to explore your vision! 🎨"
            
            # Create context from memories
            context = "🎨 **Your Vision Board Journey So Far:**\n\n"
            
            for i, memory in enumerate(vision_memories, 1):
                # Extract key information
                text = memory.get('text', '')
                metadata = memory.get('metadata', {})
                
                # Show template info if available
                if metadata.get('template'):
                    context += f"• Template: {metadata['template']}\n"
                
                # Show condensed memory
                short_text = text[:100] + "..." if len(text) > 100 else text
                context += f"• {short_text}\n"
                
                if i >= 3:  # Limit to 3 most relevant memories
                    break
            
            context += "\n*This helps me understand your vision and provide consistent guidance.*"
            return context
            
        except Exception as e:
            print(f"Error getting vision board context: {e}")
            return "Ready to continue your vision board journey! ✨"
