import json
import os
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from core.serp_search import SerpAPISearchRun, SerpAPISearchWrapper
from core.database import DatabaseManager
from core.memory import MemoryManager
from core.vision_board_generator import VisionBoardGenerator
from datetime import datetime
import re
import asyncio
import time
import random
import traceback

class SmartAgent:
    def __init__(self, db_manager: DatabaseManager, memory_manager: MemoryManager):
        self.db_manager = db_manager
        self.memory_manager = memory_manager
        
        # Initialize vision board generator
        self.vision_board_generator = VisionBoardGenerator(db_manager, memory_manager)
        
        # Initialize vision board intake manager
        from core.vision_board_intake import VisionBoardIntakeManager
        self.vision_board_intake = VisionBoardIntakeManager(db_manager, memory_manager)
        
        # Initializing prompt loader with direct file reading as fallback
        self.prompt_loader = None
        self.prompts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prompts")
        
        
        try:
            import importlib.util
            prompt_loader_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "utils", "prompt_loader.py")
            
            if os.path.exists(prompt_loader_path):
                spec = importlib.util.spec_from_file_location("prompt_loader", prompt_loader_path)
                prompt_loader_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(prompt_loader_module)
                self.prompt_loader = prompt_loader_module.PromptLoader()
                print("✅ PromptLoader initialized successfully")
            else:
                print("Warning: PromptLoader file not found, using direct file reading")
        except Exception as e:
            print(f"Warning: Error with PromptLoader ({e}), using direct file reading")
            self.prompt_loader = None
        
        # Check for OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable not set. Please add it to your .env file or system environment variables.")
        
        
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.3,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def process_message(self, user_id: str, message: str) -> str:
        """Process user message with optimized performance and selective memory retrieval"""
        try:
            # FIRST: Check if message requires web search for current information
            if self._requires_web_search(message):
                print(f"🔍 Detected web search query: {message}")
                return self.search_and_respond(user_id, message)
            
            # Check if user is in vision board intake flow
            intake_status = self.vision_board_intake.get_intake_status(user_id)
            
            if intake_status.get("status") == "in_progress":
                # User is answering vision board intake questions
                return self._handle_vision_board_answer(user_id, message, "")
            
            # Check for vision board confirmation intent ONLY if intake is completed
            if self._check_for_vision_board_confirmation(message):
                # If intake is completed and user wants to proceed, generate vision board
                if intake_status.get("status") == "completed":
                    return self._generate_vision_board_from_intake(user_id, "")
                # If no completed intake, check if user can skip
                else:
                    can_skip, skip_explanation = self.vision_board_intake.can_skip_intake(user_id)
                    if can_skip:
                        # If they can skip and confirmed, generate the vision board
                        return self._generate_vision_board_from_intake(user_id, "")
                    else:
                        # If they can't skip, start the intake
                        return self.vision_board_intake.start_intake_flow(user_id)
            
            # Check for vision board creation intent ONLY if not just completed intake
            if self.check_for_vision_board_intent(message) and intake_status.get("status") != "completed":
                return self._handle_vision_board_flow(user_id, "")

            # OPTIMIZED CONTEXT RETRIEVAL - Only when needed
            session_context = {"has_context": False, "conversation_count": 0}
            memory_context = ""
            vision_context = ""
            
            # Categorize message type for smart memory retrieval
            message_lower = message.lower()
            
            # Check for conversation history queries
            conversation_history_keywords = [
                'yesterday', 'last time', 'what did we talk', 'what we discussed',
                'our conversation', 'we talked about', 'remember when',
                'what did i tell you', 'what did i say', 'did i mention'
            ]
            
            needs_conversation_history = any(keyword in message_lower for keyword in conversation_history_keywords)
            
            # Only search memory for complex queries or vision-related topics
            needs_memory_search = (
                len(message.split()) > 5 or  # Complex messages
                any(keyword in message_lower for keyword in [
                    'remember', 'mentioned', 'told', 'said', 'before',
                    'vision', 'goal', 'dream', 'habit', 'reminder',
                    'what did', 'you know', 'recall'
                ]) or
                needs_conversation_history
            )
            
            # Get lightweight session context for continuity
            try:
                session_context = self.memory_manager.get_lightweight_session_context(user_id)
            except:
                # Fallback to basic conversation count
                session_context = {"has_context": True, "conversation_count": 3, "summary": "Ongoing conversation"}
            
            # Smart memory retrieval - only when needed
            if needs_memory_search:
                try:
                    # Check if they're asking about conversation history
                    if needs_conversation_history:
                        conversation_memory = self.memory_manager.search_conversation_history(user_id, message)
                        if conversation_memory and "No relevant" not in conversation_memory:
                            memory_context = conversation_memory
                        else:
                            # Fallback to semantic memory search
                            relevant_memories = self.memory_manager.search_memories(user_id, message, limit=3)
                            memory_context = "\n".join(relevant_memories[:2])
                    else:
                        # Use cached context if available
                        memory_context = self.memory_manager.get_fast_context(user_id, message)
                except:
                    # Fallback to limited memory search
                    try:
                        relevant_memories = self.memory_manager.search_memories(user_id, message, limit=2)
                        memory_context = "\n".join(relevant_memories[:2])
                    except:
                        memory_context = ""
            
            # Vision context only for vision-related queries
            if any(keyword in message_lower for keyword in ['vision', 'board', 'goal', 'dream', 'aspiration']):
                try:
                    vision_context = self.memory_manager.get_vision_board_context(user_id)
                except:
                    vision_context = ""
            
            # Get cached user profile for speed
            user_profile = self.memory_manager.get_cached_user_profile(user_id)
            
            # Create minimal context for faster processing
            context_parts = []
            
            # Add session context summary only if meaningful
            if session_context.get('has_context') and session_context.get('conversation_count', 0) > 0:
                context_parts.append(f"� Ongoing conversation (#{session_context['conversation_count']})")
            
            # Add memory context only if found
            if memory_context and len(memory_context) > 20:
                context_parts.append(f"🧠 Relevant: {memory_context[:150]}...")
            
            # Add vision context only if relevant and exists
            if vision_context and "No previous vision board" not in vision_context:
                context_parts.append(f"🎨 Vision: {vision_context[:100]}...")
            
            context = "\n".join(context_parts) if context_parts else "Fresh conversation."
            
            # Check for pending flows
            try:
                pending_flows = self.db_manager.get_pending_flows(user_id)
            except Exception as e:
                print(f"Error getting pending flows: {e}")
                pending_flows = []
            
            # Create enhanced system prompt
            system_prompt = self._create_enhanced_system_prompt(user_profile, pending_flows, session_context)
            
            # Process message with LLM
            prompt = PromptTemplate(
                input_variables=["system_prompt", "context", "user_message"],
                template="""{system_prompt}

ENHANCED CONVERSATION CONTEXT:
{context}

USER MESSAGE: {user_message}

RESPONSE GUIDELINES:
- Use the context to provide personalized, continuous conversations
- Reference past conversations naturally when relevant
- Avoid repeating information the user has already shared
- Build on previous insights and maintain relationship depth
- For vision board topics, leverage existing vision board context
- Maintain natural conversation flow while being contextually aware

Respond naturally and conversationally, showing that you remember and understand this user."""
            )
            
            # Generate response
            formatted_prompt = prompt.format(
                system_prompt=system_prompt,
                context=context,
                user_message=message
            )
            
            response = self.llm.invoke(formatted_prompt)
            generated_response = response.content
            
            # OPTIMIZED MEMORY STORAGE - Only store important interactions
            should_store_enhanced = (
                len(message.split()) > 8 or  # Complex messages
                any(keyword in message.lower() for keyword in [
                    'goal', 'habit', 'reminder', 'vision', 'dream', 'important',
                    'remember', 'help me', 'i want', 'i need'
                ]) or
                session_context.get('conversation_count', 0) < 3  # First few conversations
            )
            
            if should_store_enhanced:
                # Full enhanced memory storage for important interactions
                self.memory_manager.add_interaction(
                    user_id, 
                    message, 
                    generated_response,
                    metadata={
                        'interaction_type': 'enhanced_conversation',
                        'has_session_context': session_context.get('has_context', False),
                        'conversation_count': session_context.get('conversation_count', 0),
                        'timestamp': datetime.now().isoformat()
                    }
                )
            else:
                # Lightweight memory storage for simple interactions
                try:
                    self.memory_manager.add_lightweight_interaction(user_id, message, generated_response)
                except:
                    # Fallback to regular storage if lightweight method doesn't exist
                    self.memory_manager.add_interaction(user_id, message, generated_response)
            
            print(f"✅ Enhanced conversation processing completed for user {user_id}")
            print(f"   📊 Session context: {session_context.get('has_context', False)}")
            print(f"   💬 Conversation #: {session_context.get('conversation_count', 0) + 1}")
            print(f"   🧠 Memory context: {len(context)} chars")
            
            return generated_response
            
        except Exception as e:
            print(f"Error in enhanced message processing: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback to basic processing
            try:
                return self._fallback_message_processing(user_id, message)
            except:
                return "I apologize, but I'm having trouble processing your message right now. Could you please try again?"
    
    def _fallback_message_processing(self, user_id: str, message: str) -> str:
        """Fallback message processing when enhanced system fails"""
        try:
            # Basic system prompt
            system_prompt = "You are a helpful AI assistant. Respond naturally and helpfully."
            
            # Generate basic response
            response = self.llm.invoke(f"{system_prompt}\n\nUser: {message}\n\nAssistant:")
            generated_response = response.content
            
            # Basic memory save
            try:
                self.memory_manager.add_interaction(user_id, message, generated_response)
            except:
                pass  # Don't fail if memory save fails
            
            return generated_response
            
        except Exception as e:
            print(f"Error in fallback processing: {e}")
            return "I'm having technical difficulties. Please try again shortly."
    
    def _create_enhanced_system_prompt(self, user_profile: Dict, pending_flows: List, session_context: Dict) -> str:
        """Create enhanced system prompt with session awareness"""
        base_prompt = """You are NowwClub AI, a sophisticated personal companion focused on helping users with vision boards, goals, habits, and personal growth.

ENHANCED CONVERSATION CAPABILITIES:
- You maintain deep context across sessions and remember previous conversations
- You build relationships over time and reference past insights naturally
- You avoid asking users to repeat information they've already shared
- You provide personalized responses based on accumulated understanding

SESSION AWARENESS:"""
        
        # Add session-specific context
        if session_context.get('has_context'):
            conversation_count = session_context.get('conversation_count', 0)
            if conversation_count > 0:
                base_prompt += f"""
- This user has had {conversation_count} previous conversations with you
- You know this user well and should reference past conversations naturally
- Build on previous insights and maintain relationship continuity"""
            else:
                base_prompt += """
- This is a new user - be welcoming and start building the relationship"""
        else:
            base_prompt += """
- Building context with this user - be attentive to details for future reference"""
        
        # Add vision board awareness
        base_prompt += """

VISION BOARD EXPERTISE:
- Specializes in helping users create personalized vision boards through thoughtful intake
- Uses 10-question intake flow for deep personalization when users want vision boards
- Remembers user's vision board preferences and style from previous sessions
- Can skip intake if user already has sufficient vision board data"""
        
        return base_prompt
    
    def _handle_vision_board_flow(self, user_id: str) -> str:
        """Handle vision board flow - check intake status and proceed accordingly"""
        try:
            # First check if user can skip intake (has sufficient data)
            can_skip, skip_explanation = self.vision_board_intake.can_skip_intake(user_id)
            
            if can_skip:
                # User has sufficient data, offer to generate immediately or update
                return skip_explanation
            
            # Check current intake status
            intake_status = self.vision_board_intake.get_intake_status(user_id)
            
            if intake_status["status"] == "not_started":
                # Start new intake flow
                return self.vision_board_intake.start_intake_flow(user_id)
            
            elif intake_status["status"] == "in_progress":
                # Continue existing intake
                current_q = intake_status.get("current_question", 1)
                question = self.vision_board_intake._format_question(current_q)
                progress = f"({current_q}/10)"
                return f"🎨 **Vision Board Intake {progress}**\n\nLet's continue where we left off!\n\n{question}"
            
            elif intake_status["status"] == "completed":
                # Generate vision board using existing data
                return self._generate_vision_board_from_intake(user_id)
            
            else:
                # Fallback - start intake
                return skip_explanation
                
        except Exception as e:
            print(f"Error in vision board flow: {e}")
            return "❌ I encountered an error setting up your vision board. Please try again."
        """Create comprehensive system prompt"""
        return f"""You are Noww Club AI, a helpful personal assistant that engages in natural conversation and can help with productivity when asked.

USER PROFILE:
- User preferences: {user_profile.get('preferences', {})}
- Recent topics: {user_profile.get('conversation_topics', [])}
- Current habits: {len(user_profile.get('habits', []))} habits
- Current goals: {len(user_profile.get('goals', []))} goals

PENDING FLOWS: {len(pending_flows)} pending items

CORE BEHAVIOR:
- Engage in natural, helpful conversation on any topic
- Be empathetic, supportive, and genuinely interested in what the user shares
- Answer questions, provide information, and offer assistance as needed
- Remember context from previous conversations to maintain continuity

PRODUCTIVITY FEATURES (Only mention when relevant):
When users specifically ask about or express interest in:
1. **Habit Creation**: Help extract habit name, frequency, type, motivation, reminder time
2. **Goal Setting**: Help extract goal name, target date, tracking method, motivation  
3. **Reminder Setup**: Help extract reminder text, time, notification method
4. **Vision Board Creation**: Generate personalized vision boards based on user profile and conversation history
5. **Web Search**: Provide current information on topics

CONVERSATION APPROACH:
- Respond naturally to greetings, questions, and casual conversation
- Focus on what the user is actually discussing
- Don't mention productivity features unless the user brings them up
- If user expresses wanting to track, improve, or organize something, then offer relevant help
- Use step-by-step questioning ONLY when creating habits/goals/reminders
- Be conversational and helpful, never robotic or scripted

WHEN TO OFFER PRODUCTIVITY HELP:
✅ User says: "I want to start exercising", "I need to drink more water", "Help me track something", "Create a vision board", "I want a vision board", "Show me my dreams"
❌ Don't mention for: "Hi", "How are you?", "What's the weather?", general questions

VISION BOARD FEATURE:
- When user asks for vision board: First check if they've completed the intake flow
- If they have sufficient data but want to proceed: Generate immediately
- If they want to update their info: Start intake or update existing
- If intake completed: Generate the vision board
- Phrases that trigger vision board: "vision board", "dream board", "visualize my goals", "show my future", "create my vision"
- Phrases that confirm generation: "proceed", "yes generate", "create it now", "go ahead", "yes let's do it"

Always prioritize natural conversation over feature promotion."""

    def _extract_action_data(self, response: str) -> Optional[Dict]:
        """Extract JSON action data from response"""
        try:
            # Look for JSON code blocks
            json_pattern = r'```json\s*(\{.*?\})\s*```'
            match = re.search(json_pattern, response, re.DOTALL)
            
            if match:
                json_str = match.group(1)
                return json.loads(json_str)
            
            return None
        except Exception as e:
            print(f"Error extracting action data: {e}")
            return None
    
    def _handle_action(self, user_id: str, action_data: Dict, response_content: str) -> str:
        """Handle the extracted action"""
        action = action_data.get("action")
        data = action_data.get("data", {})
        needs_more_info = action_data.get("needs_more_info", [])
        
        # Remove JSON from response
        clean_response = re.sub(r'```json.*?```', '', response_content, flags=re.DOTALL).strip()
        
        try:
            if action == "create_habit" and not needs_more_info:
                habit_id = self.db_manager.save_habit(
                    user_id,
                    data.get('name', data.get('habit_name', 'New Habit')),
                    data.get('description', ''),
                    data.get('frequency', 'daily')
                )
                return clean_response + f"\n\n✅ Great! I've created your habit: '{data.get('name', data.get('habit_name', 'New Habit'))}'. You can track it in your dashboard."
            
            elif action == "create_goal" and not needs_more_info:
                goal_id = self.db_manager.save_goal(
                    user_id,
                    data.get('name', data.get('goal_name', 'New Goal')),
                    data.get('description', ''),
                    data.get('target_date', '')
                )
                return clean_response + f"\n\n🎯 Perfect! I've set up your goal: '{data.get('name', data.get('goal_name', 'New Goal'))}'. You can track your progress in the dashboard."
            
            elif action == "create_reminder" and not needs_more_info:
                reminder_id = self.db_manager.save_reminder(
                    user_id,
                    data.get('text', data.get('reminder_text', 'New Reminder')),
                    data.get('description', ''),
                    data.get('time', data.get('reminder_time', ''))
                )
                return clean_response + f"\n\n⏰ Done! I've set up your reminder: '{data.get('text', data.get('reminder_text', 'New Reminder'))}' for {data.get('time', data.get('reminder_time', 'the specified time'))}."
            
            elif action == "vision_board_flow":
                # Handle vision board request with intake flow
                return self._handle_vision_board_flow(user_id, clean_response)
            
            elif action == "vision_board_answer":
                # Handle vision board intake answer
                answer = data.get("answer", "")
                return self._handle_vision_board_answer(user_id, answer, clean_response)
            
            elif action == "generate_vision_board_now":
                # User confirmed they want to generate vision board with existing data
                return self._generate_vision_board_from_intake(user_id, clean_response)
            
            elif action == "create_vision_board":
                # Legacy support - redirect to flow
                return self._handle_vision_board_flow(user_id, clean_response)
            
            elif action == "web_search":
                query = data.get('query', data.get('search_query', ''))
                if query:
                    search_response = self.search_and_respond(user_id, query)
                    return search_response
                else:
                    return clean_response
            
            elif action == "continue_flow":
                # Save partial data and continue step-by-step flow
                flow_data = {
                    "collected_data": data,
                    "needs_info": needs_more_info,
                    "flow_type": self._determine_flow_type(action_data),
                    "status": "pending"
                }
                
                try:
                    flow_id = self.db_manager.save_flow(user_id, flow_data.get("flow_type", "unknown"), flow_data)
                except Exception as e:
                    print(f"Error saving flow: {e}")
                
                return clean_response
            
            else:
                return clean_response
                
        except Exception as e:
            print(f"Error handling action: {e}")
            return clean_response + "\n\nI encountered an error while saving. Please try again."
    
    def _determine_flow_type(self, action_data: Dict) -> str:
        """Determine flow type from action data"""
        action = action_data.get("action", "")
        data = action_data.get("data", {})
        
        if "habit" in action or any(key in data for key in ["habit_name", "name", "frequency"]):
            return "habit"
        elif "goal" in action or any(key in data for key in ["goal_name", "name", "target_date"]):
            return "goal"
        elif "reminder" in action or any(key in data for key in ["reminder_text", "text", "reminder_time", "time"]):
            return "reminder"
        else:
            return "unknown"
    
    def handle_emotional_support(self, user_id: str, message: str) -> str:
        """Handle emotional support specifically"""
        context = self.memory_manager.get_context_for_conversation(user_id, message)
        
        prompt = PromptTemplate(
            input_variables=["context", "message"],
            template="""You are a compassionate AI companion providing emotional support. 

CONTEXT: {context}
USER MESSAGE: {message}

Provide empathetic, supportive response. Acknowledge their feelings, offer comfort, and suggest helpful coping strategies if appropriate. Be warm but professional."""
        )
        
        response = self.llm.invoke(prompt.format(context=context, message=message))
        
        # Analyze mood for tracking
        mood_analysis = self._analyze_mood(message)
        if mood_analysis.get("mood_score"):
            self.db_manager.save_mood_entry(
                user_id,
                mood_analysis["mood_score"],
                mood_analysis.get("notes", message)
            )
        
        return response.content
    
    def _analyze_mood(self, message: str) -> Dict:
        """Analyze mood from message"""
        try:
            prompt = PromptTemplate(
                input_variables=["message"],
                template="""Analyze the emotional content and mood from this message: "{message}"

Respond with JSON only:
{{
    "mood_score": 1-5 (1=very negative, 3=neutral, 5=very positive),
    "emotions": ["emotion1", "emotion2"],
    "notes": "brief analysis"
}}"""
            )
            
            response = self.llm.invoke(
                prompt.format(message=message),
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.content)
        except Exception as e:
            print(f"Error analyzing mood: {e}")
            return {"mood_score": 3, "emotions": [], "notes": ""}
    
    def _requires_web_search(self, message: str) -> bool:
        """
        Advanced detection for web search requirements with contextual analysis.
        Handles ambiguous keywords and reduces false positives for production use.
        """
        message_lower = message.lower().strip()
        
        # PHASE 1: Immediate exclusions - personal/conversational patterns
        personal_patterns = [
            # Personal greetings and check-ins
            r'\b(how are you|how have you been|how\'s it going|how\'s everything)\b',
            r'\b(good morning|good afternoon|good evening|hello|hi|hey)\b',
            r'\b(thank you|thanks|please|sorry|excuse me)\b',
            
            # Personal states and feelings  
            r'\b(i am|i\'m|i feel|i need|i want|i like|i love|i hate|i have)\b',
            r'\b(my (day|life|mood|feelings|goals?|habits?|progress|productivity|status|routine|activities))\b',
            r'\b(how am i|help me|can you help|assist me|motivate me)\b',
            
            # Memory and conversation references
            r'\b(remember|recall|we talked|we discussed|you said|i told you)\b',
            r'\b(yesterday|last time|before|previously|earlier|conversation|chat)\b',
            
            # App-specific functionality
            r'\b(vision board|habit|goal|reminder|schedule|meditation|track|create|set up)\b',
            r'\b((show|tell) me (my|about my)|(what\'s|what are) my)\b',
            r'\b(focus on|work on|plan my|organize my)\b',
            
            # Personal temporal references
            r'\b(plan my day|my day|help me.*today|i.*today|today i|today has been)\b',
            r'\b(my.*current|current.*my|my.*latest|latest.*my|my.*recent|recent.*my)\b'
        ]
        
        import re
        for pattern in personal_patterns:
            if re.search(pattern, message_lower):
                return False
        
        # PHASE 2: Strong web search indicators - high confidence patterns
        strong_web_indicators = [
            # News and breaking information with location/global context
            r'\b(latest news|breaking news|recent news|news today|current events)\b',
            r'\b(what happened (in|to|with|during)|what\'s happening (in|to|with|around))\b',
            r'\b(headlines|reports|updates) (today|now|recent)\b',
            r'\b(developments in|updates on|news about)\b',
            
            # Weather with specific locations or times
            r'\b(weather (in|for|today|tomorrow|forecast)|temperature (in|for|today|now))\b',
            r'\b(forecast|rain today|sunny today|cloudy today|climate in)\b',
            r'\b(is it raining|will it rain|weather like)\b',
            
            # Sports scores and results
            r'\b(cricket score|match result|live score|sports (score|result|news))\b',
            r'\b((who won|winner of) (the|today\'s|yesterday\'s)|match today|game result)\b',
            r'\b(tournament|championship|league) (result|score|update)\b',
            r'\b(latest.*(score|match)|recent.*(match|result)|current.*(result|score))\b',
            
            # Financial/market data
            r'\b(stock price|market (today|now|trends)|exchange rate|bitcoin price)\b',
            r'\b(current price of|how much is.*worth|market doing)\b',
            r'\b(cryptocurrency|trading|stocks today|market trends)\b',
            r'\b(latest.*market|recent.*market|current.*market)\b',
            
            # Real-time events with global context
            r'\b(election result|voting result|government policy|political)\b',
            r'\b(pandemic|covid|restrictions|policy changes)\b',
            r'\b(economy (today|now|doing)|economic (situation|conditions))\b',
            r'\b(happening.*disasters|natural disasters|major headlines)\b'
        ]
        
        for pattern in strong_web_indicators:
            if re.search(pattern, message_lower):
                return True
        
        # PHASE 3: Global vs Personal context differentiation
        # Check for global/location indicators vs personal indicators
        
        global_context_indicators = [
            r'\b(in (delhi|mumbai|london|new york|tokyo|bangalore|india|usa|uk|world))\b',
            r'\b(around the world|globally|worldwide|international)\b',
            r'\b(the (economy|market|country|government|situation))\b',
            r'\b(happening (in|around|across|worldwide))\b'
        ]
        
        has_global_context = any(re.search(pattern, message_lower) for pattern in global_context_indicators)
        
        # PHASE 4: Contextual analysis for time-sensitive keywords
        # Only trigger web search if combined with global context or specific patterns
        
        if has_global_context:
            time_keywords = ['today', 'current', 'latest', 'recent', 'now']
            if any(keyword in message_lower for keyword in time_keywords):
                return True
        
        # PHASE 5: Specific domain patterns that usually need web search
        web_domains = [
            # Weather patterns
            r'\b(temperature|weather|forecast|rain|snow|storm|climate)\b.*\b(today|now|current)\b',
            r'\b(today|now|current)\b.*\b(temperature|weather|forecast)\b',
            
            # News patterns  
            r'\b(news|headlines|reports|updates|developments)\b.*\b(about|on|regarding)\b',
            r'\b(what.*happened|what\'s.*happening)\b.*\b(in|to|with)\b',
            r'\b(trending.*today|today.*headlines|major.*headlines)\b',
            
            # Sports patterns
            r'\b(score|result|match|game)\b.*\b(today|live|current|latest)\b',
            r'\b(who won|winner)\b.*\b(match|game|tournament)\b',
            r'\b(latest.*cricket|recent.*football|current.*basketball)\b',
            
            # Financial patterns
            r'\b(price|market|stock|trading)\b.*\b(today|current|latest|now)\b',
            r'\b(how much.*worth|current.*price)\b',
            
            # Technology and industry
            r'\b(new.*tech|latest.*technology|developments.*industry)\b',
            r'\b(what\'s new.*industry|trending.*social media)\b'
        ]
        
        for pattern in web_domains:
            if re.search(pattern, message_lower):
                return True
        
        # PHASE 6: Question patterns for external information
        information_question_patterns = [
            r'\b(what is the.*price|what are the.*rates)\b',
            r'\b(how much (is|does|costs?).*in)\b',  # Location-based pricing
            r'\b(when (is|was|will).*\b(election|event|match|game))\b',
            r'\b(who (won|is winning|will win).*\b(election|match|tournament))\b',
            r'\b(where.*happened.*\b(incident|event|disaster))\b'
        ]
        
        for pattern in information_question_patterns:
            if re.search(pattern, message_lower):
                return True
        
        # PHASE 7: High-priority entities that almost always need web search
        priority_entities = [
            'covid', 'pandemic', 'election', 'stock market', 'cryptocurrency',
            'weather forecast', 'breaking news', 'live score', 'match result'
        ]
        
        if any(entity in message_lower for entity in priority_entities):
            return True
        
        # PHASE 8: Final safety check - default to no web search for ambiguous cases
        return False
    
    def search_and_respond(self, user_id: str, query: str) -> str:
        """Handle web search requests with rate limiting and fallback providers"""
        try:
            print(f"🔍 Performing web search for query: {query}")
            
            # Try different search strategies with rate limiting
            search_results = self._perform_search_with_fallback(query)
            
            if not search_results:
                print("⚠️ All search providers failed, using knowledge-based response")
                return self._generate_knowledge_based_response(user_id, query)
            
            print(f"✅ Search completed. Results length: {len(search_results)}")
            
            # Get user context for personalized responses
            user_context = self.memory_manager.get_context_for_conversation(user_id, query)
            
            # Load the search summarizer prompt or use fallback
            if self.prompt_loader:
                try:
                    prompt_template = self.prompt_loader.load_prompt("search_summarizer")
                    summary_prompt = PromptTemplate(
                        input_variables=["query", "search_results", "context"],
                        template=prompt_template
                    )
                except Exception as e:
                    print(f"Error loading search_summarizer prompt: {e}")
                    # Fallback to enhanced inline prompt
                    summary_prompt = self._get_fallback_search_prompt()
            else:
                # Try direct file reading first
                prompt_template = self._load_prompt_direct("search_summarizer")
                if prompt_template:
                    summary_prompt = PromptTemplate(
                        input_variables=["query", "search_results", "context"],
                        template=prompt_template
                    )
                else:
                    # Use enhanced fallback prompt
                    summary_prompt = self._get_fallback_search_prompt()
            
            # Generate summary using the LLM
            print("🤖 Generating response with LLM...")
            summary_response = self.llm.invoke(
                summary_prompt.format(
                    query=query, 
                    search_results=search_results,
                    context=user_context[:500] if user_context else "No previous context"
                )
            )
            
            print("✅ Response generated successfully")
            return summary_response.content
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            traceback.print_exc()
            return f"I apologize, but I'm currently unable to perform web searches. Error: {str(e)}. Please try again later or rephrase your question."
    
    def _load_prompt_direct(self, prompt_name: str) -> Optional[str]:
        """Load prompt directly from file if PromptLoader is not available"""
        try:
            prompt_path = os.path.join(self.prompts_dir, f"{prompt_name}.txt")
            if os.path.exists(prompt_path):
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                print(f"Prompt file not found: {prompt_path}")
                return None
        except Exception as e:
            print(f"Error reading prompt file {prompt_name}: {e}")
            return None

    def _get_fallback_search_prompt(self) -> PromptTemplate:
        """Fallback search prompt with enhanced formatting"""
        return PromptTemplate(
            input_variables=["query", "search_results", "context"],
            template="""You are a helpful AI assistant providing current information from web search results.

User Query: {query}

Search Results: {search_results}

Context: {context}

**Instructions:**
1. Analyze the search results and provide a comprehensive answer to the user's query
2. Use the most current and relevant information from the search results
3. Structure your response clearly with proper formatting
4. Include specific details, numbers, dates, and facts when available
5. Cite sources when mentioning specific information
6. Be conversational and helpful

**Response Format:**
- Start with a direct answer to the query
- Include key details and specifics from the search results  
- Use clear formatting (bullet points, sections as needed)
- End with a helpful summary or next steps if relevant

**Important:** 
- Only use information from the provided search results
- If the search results don't fully answer the query, acknowledge the limitations
- Provide the most current information available in the search results
- Be accurate and fact-based

Provide a helpful, well-structured response:"""
        )
    
    def _perform_search_with_fallback(self, query: str) -> Optional[str]:
        """Perform search with SERP API Google Search and fallback strategies"""
        
        # Strategy 1: Try SERP API Google Search
        try:
            print("📡 Trying SERP API Google Search...")
            
            # Create SERP API search tool
            search_tool = SerpAPISearchRun(
                api_wrapper=SerpAPISearchWrapper(),
                max_results=5  # Get top 5 results for concise response
            )
            
            results = search_tool.run(query)
            if results and len(results) > 100 and "error" not in results.lower():
                print("✅ SERP API Google Search successful")
                return results
            else:
                print("⚠️ SERP API returned limited or error results")
                
        except Exception as e:
            print(f"⚠️ SERP API search failed: {e}")
            
        # Strategy 2: Try SERP API with simpler query
        try:
            print("📡 Trying SERP API with simplified query...")
            
            # Simplify query (remove special characters, limit words)
            simplified_query = " ".join(query.split()[:5])  # Use first 5 words
            simplified_query = ''.join(c for c in simplified_query if c.isalnum() or c.isspace())
            
            search_tool = SerpAPISearchRun(
                api_wrapper=SerpAPISearchWrapper(),
                max_results=3  # Even fewer results
            )
            
            results = search_tool.run(simplified_query)
            if results and len(results) > 50:
                print("✅ SERP API simplified search successful")
                return results
                
        except Exception as e:
            print(f"⚠️ SERP API simplified search failed: {e}")
            
        # Strategy 3: Use cached/simulated search for common topics
        cached_result = self._get_cached_search_response(query)
        if cached_result:
            print("✅ Using cached search response")
            return cached_result
            
        print("❌ All search strategies failed")
        return None
    
    def _get_cached_search_response(self, query: str) -> Optional[str]:
        """Provide cached responses for common search topics"""
        query_lower = query.lower()
        
        # AI/Technology topics
        if any(term in query_lower for term in ['ai', 'artificial intelligence', 'machine learning', 'technology']):
            return """Recent AI developments include advances in large language models, computer vision improvements, 
            and increased focus on AI safety. Key trends include multimodal AI, smaller specialized models, 
            and integration of AI into everyday applications. Major companies continue investing heavily in AI research."""
            
        # Health/Fitness topics
        if any(term in query_lower for term in ['health', 'fitness', 'exercise', 'workout', 'nutrition']):
            return """Current health and fitness trends emphasize sustainable lifestyle changes, functional fitness, 
            mindful nutrition, and mental health awareness. Popular approaches include HIIT workouts, 
            Mediterranean diet principles, and holistic wellness practices combining physical and mental health."""
            
        # Productivity topics
        if any(term in query_lower for term in ['productivity', 'time management', 'efficiency', 'organization']):
            return """Modern productivity strategies focus on deep work principles, digital minimalism, 
            and sustainable work practices. Popular methods include time blocking, the Pomodoro Technique, 
            and tools that minimize distractions while maximizing focus and output."""
            
        # Weather topics
        if any(term in query_lower for term in ['weather', 'temperature', 'forecast']):
            return """For current weather information, I recommend checking reliable sources like Weather.com, 
            AccuWeather, or your local meteorological service. Weather patterns vary by location and season, 
            so real-time data from official sources provides the most accurate forecasts."""
            
        # Recipe/Food topics
        if any(term in query_lower for term in ['recipe', 'cooking', 'food', 'meal', 'breakfast', 'lunch', 'dinner']):
            return """Healthy cooking trends emphasize whole foods, minimal processing, and balanced nutrition. 
            Popular approaches include meal prep, plant-based options, and cooking methods that preserve nutrients. 
            Consider seasonal ingredients and simple techniques for sustainable healthy eating."""
            
        return None
    
    def _generate_knowledge_based_response(self, user_id: str, query: str) -> str:
        """Generate a helpful response based on general knowledge when search fails"""
        user_context = self.memory_manager.get_context_for_conversation(user_id, query)
        
        knowledge_prompt = f"""
        The user asked: {query}
        
        User context: {user_context[:300] if user_context else "No previous context"}
        
        Since Google search via SERP API is temporarily unavailable, provide a helpful response based on your knowledge.
        Be honest about limitations but offer valuable insights, suggestions, or guidance.
        Format your response to be engaging and actionable.
        """
        
        try:
            response = self.llm.invoke(knowledge_prompt)
            return f"💡 While I can't search the web right now, here's what I can share based on my knowledge:\n\n{response.content}"
        except Exception as e:
            print(f"Error generating knowledge-based response: {e}")
            return self._get_generic_helpful_response(query)
    
    def _get_generic_helpful_response(self, query: str) -> str:
        """Provide a generic but helpful response when all else fails"""
        return f"""I understand you're looking for information about "{query}". While I'm currently unable to search the web, I'd be happy to help in other ways:

🔄 **Alternative approaches:**
• I can share general knowledge on the topic
• Help you break down your question into specific areas
• Suggest reliable sources where you might find current information
• Assist with related questions I can answer directly

💡 **What would be most helpful for you right now?**

Feel free to rephrase your question or let me know what specific aspect interests you most!"""

    def _handle_vision_board_flow(self, user_id: str, clean_response: str) -> str:
        """Handle vision board flow - check intake status and proceed accordingly"""
        try:
            # First check if user can skip intake (has sufficient data)
            can_skip, skip_explanation = self.vision_board_intake.can_skip_intake(user_id)
            
            if can_skip:
                # User has sufficient data, offer to generate immediately or update
                return f"{clean_response}\n\n{skip_explanation}"
            
            # Check current intake status
            intake_status = self.vision_board_intake.get_intake_status(user_id)
            
            if intake_status["status"] == "not_started":
                # Start new intake flow
                question = self.vision_board_intake.start_intake_flow(user_id)
                return f"{clean_response}\n\n{question}"
            
            elif intake_status["status"] == "in_progress":
                # Continue existing intake
                current_q = intake_status.get("current_question", 1)
                question = self.vision_board_intake._format_question(current_q)
                progress = f"({current_q}/10)"
                return f"{clean_response}\n\n🎨 **Vision Board Intake {progress}**\n\nLet's continue where we left off!\n\n{question}"
            
            elif intake_status["status"] == "completed":
                # Generate vision board using existing data
                return self._generate_vision_board_from_intake(user_id, clean_response)
            
            else:
                # Fallback - start intake
                return f"{clean_response}\n\n{skip_explanation}"
                
        except Exception as e:
            print(f"Error in vision board flow: {e}")
            return f"{clean_response}\n\n❌ I encountered an error setting up your vision board. Please try again."
    
    def _handle_vision_board_answer(self, user_id: str, answer: str, clean_response: str) -> str:
        """Handle a vision board intake answer"""
        try:
            # Process the answer
            result = self.vision_board_intake.process_answer(user_id, answer)
            return f"{clean_response}\n\n{result}"
            
        except Exception as e:
            print(f"Error processing vision board answer: {e}")
            return f"{clean_response}\n\n❌ I had trouble processing your answer. Please try again."
    
    def _generate_vision_board_from_intake(self, user_id: str, clean_response: str) -> str:
        """Generate vision board using completed intake data"""
        try:
            # Check if user has sufficient data for vision board generation
            if not self.vision_board_intake.has_sufficient_data_for_vision_board(user_id):
                return f"{clean_response}\n\n❌ I need more information to create your vision board. Please complete the intake process first."
            
            # Get the intake data for vision board generation
            intake_data = self.vision_board_intake.get_intake_data_for_vision_board(user_id)
            
            if not intake_data:
                return f"{clean_response}\n\n❌ I couldn't retrieve your intake data. Please try the intake process again."
            
            # Generate the vision board using the intake data
            try:
                vision_board_result = self.vision_board_generator.generate_vision_board(user_id, intake_data)
                
                if vision_board_result and "image_path" in vision_board_result:
                    image_path = vision_board_result["image_path"]
                    template_used = vision_board_result.get("template_used", "custom")
                    
                    # Save to memory
                    self.memory_manager.add_interaction(
                        user_id,
                        "vision_board_generated",
                        f"Generated vision board using template {template_used} based on completed intake data"
                    )
                    
                    return f"""{clean_response}

🎉 **Your Vision Board is Ready!**

I've created a personalized vision board that captures your dreams, values, and aspirations based on our thoughtful conversation.

✨ **Template Used:** {template_used}
🎨 **Image Path:** {image_path}

Your vision board reflects everything you shared - your emotions, goals, visual preferences, and the energy you want to manifest. Place it somewhere you'll see it daily as a powerful reminder of the life you're creating! 🌟

*Remember: Vision boards work best when you connect with them emotionally and take inspired action toward your dreams.*"""
                
                else:
                    return f"{clean_response}\n\n❌ I encountered an issue generating your vision board image. Please try again or contact support."
                    
            except Exception as gen_error:
                print(f"Vision board generation error: {gen_error}")
                return f"{clean_response}\n\n❌ I encountered an error while creating your vision board: {str(gen_error)}. Please try again."
            
        except Exception as e:
            print(f"Error in vision board generation: {e}")
            return f"{clean_response}\n\n❌ I encountered an error generating your vision board. Please try again."
    
    def check_for_vision_board_intent(self, message: str) -> bool:
        """Check if the message contains vision board creation intent"""
        vision_keywords = [
            'vision board', 'dream board', 'visualize my goals', 'show my future', 
            'create my vision', 'vision', 'dreams visualization', 'goal board',
            'my dreams', 'visualize dreams', 'show my goals', 'future board',
            'destiny', 'aspirations board', 'i want to create a vision board'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in vision_keywords)
    
    def _check_for_vision_board_confirmation(self, message: str) -> bool:
        """Check if the message contains confirmation to proceed with vision board"""
        confirmation_keywords = [
            'yes', 'yeah', 'sure', 'go ahead', 'proceed', 'start', 'begin',
            'let\'s do it', 'ok', 'okay', 'alright', 'yes go ahead', 'continue',
            'let\'s start', 'let\'s begin', 'i\'m ready', 'ready'
        ]
        
        message_lower = message.lower().strip()
        return any(keyword in message_lower for keyword in confirmation_keywords)

