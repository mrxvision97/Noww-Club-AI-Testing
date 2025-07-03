import json
import os
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from core.database import DatabaseManager
from core.memory import MemoryManager
from datetime import datetime
import re
import asyncio

class SmartAgent:
    def __init__(self, db_manager: DatabaseManager, memory_manager: MemoryManager):
        self.db_manager = db_manager
        self.memory_manager = memory_manager
        
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
        """Process user message and generate appropriate response"""
        try:
            # Get comprehensive context for natural conversation
            memory_context = self.memory_manager.get_context_for_conversation(user_id, message)
            user_profile = self.memory_manager.get_user_memory(user_id)
            
            # Prioritize memory context for better recall
            context = f"{memory_context}"
            
            # Check for pending flows
            try:
                pending_flows = self.db_manager.get_pending_flows(user_id)
            except Exception as e:
                print(f"Error getting pending flows: {e}")
                pending_flows = []
            
            # Create comprehensive prompt for the LLM
            system_prompt = self._create_system_prompt(user_profile, pending_flows)
            
            # Process message with LLM
            prompt = PromptTemplate(
                input_variables=["system_prompt", "context", "user_message"],
                template="""{system_prompt}

CONVERSATION CONTEXT:
{context}

USER MESSAGE: {user_message}

Respond naturally and conversationally. Focus on what the user is actually asking about or discussing.

IMPORTANT RESPONSE GUIDELINES:
- For casual conversation, greetings, questions about past topics, or general chat: Respond naturally without mentioning habits/goals/reminders unless the user brings them up
- For emotional support or personal sharing: Focus on empathy and understanding
- For information requests: Provide helpful answers or use web search if needed
- ONLY mention creating habits/goals/reminders if the user specifically asks about them or expresses interest in tracking something

ONLY include JSON if the user specifically wants to create habits, goals, or reminders, or asks for web search:

**For creating things:**
```json
{{
    "action": "create_habit|create_goal|create_reminder|continue_flow",
    "data": {{ extracted_data }},
    "needs_more_info": ["field_name"] // only if needed
}}
```

**For web search:**
```json
{{
    "action": "web_search",
    "data": {{ "query": "search_query" }}
}}
```

For all other conversations: Respond naturally without any JSON. Be conversational, helpful, and focus on what the user is actually talking about."""
            )
            
            # Add timeout to LLM call to prevent hanging
            try:
                print(f"Processing message with LLM for user {user_id}...")
                response = self.llm.invoke(
                    prompt.format(
                        system_prompt=system_prompt,
                        context=context,
                        user_message=message
                    )
                )
                print(f"✅ LLM response received for user {user_id}")
                
            except Exception as llm_error:
                print(f"Error with LLM call: {llm_error}")
                return "I'm sorry, I'm having trouble connecting to my language processing service. Please try again in a moment."
            
            response_content = response.content
            
            # Parse JSON action if present
            action_data = self._extract_action_data(response_content)
            
            # Handle actions
            if action_data:
                final_response = self._handle_action(user_id, action_data, response_content)
            else:
                final_response = response_content
            
            # Update memory with error handling
            try:
                self.memory_manager.add_interaction(user_id, message, final_response)
                print(f"✅ Memory updated for user {user_id}")
            except Exception as memory_error:
                print(f"Warning: Could not update memory for {user_id}: {memory_error}")
            
            # Save conversation to database for memory
            try:
                self.db_manager.save_conversation(user_id, "user", message)
                self.db_manager.save_conversation(user_id, "assistant", final_response)
                print(f"✅ Conversation saved to database for user {user_id}")
            except Exception as db_error:
                print(f"Warning: Could not save conversation to database for {user_id}: {db_error}")
            
            return final_response
            
        except Exception as e:
            print(f"Error processing message: {e}")
            return "I'm sorry, I encountered an error. Please try again."
    
    def _create_system_prompt(self, user_profile: Dict, pending_flows: List) -> str:
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
4. **Web Search**: Provide current information on topics

CONVERSATION APPROACH:
- Respond naturally to greetings, questions, and casual conversation
- Focus on what the user is actually discussing
- Don't mention productivity features unless the user brings them up
- If user expresses wanting to track, improve, or organize something, then offer relevant help
- Use step-by-step questioning ONLY when creating habits/goals/reminders
- Be conversational and helpful, never robotic or scripted

WHEN TO OFFER PRODUCTIVITY HELP:
✅ User says: "I want to start exercising", "I need to drink more water", "Help me track something"
❌ Don't mention for: "Hi", "How are you?", "What's the weather?", general questions

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
    
    def search_and_respond(self, user_id: str, query: str) -> str:
        """Handle web search requests using real DuckDuckGo search"""
        try:
            print(f"🔍 Performing web search for query: {query}")
            
            # Use LangChain DuckDuckGo tool for real search results
            search_tool = DuckDuckGoSearchRun(
                api_wrapper=DuckDuckGoSearchAPIWrapper(
                    max_results=5,
                    time="d"  # last day
                )
            )
            
            # Perform the actual search
            print("📡 Executing search...")
            search_results = search_tool.run(query)
            print(f"✅ Search completed. Results length: {len(search_results) if search_results else 0}")
            
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
            import traceback
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
            template="""You are an enthusiastic AI research assistant who loves helping users discover amazing information! 🌟

User Query: {query}

Search Results: {search_results}

Context: {context}

Your mission is to make information discovery exciting and engaging! 

**Response Style Guidelines:**
- Start with an enthusiastic opener that shows you found great info
- Use bullet points, numbered lists, or clear sections for easy reading
- Include relevant emojis to make it visually appealing (but not overwhelming)
- Break information into digestible chunks
- End with an encouraging note or next steps

**Structure your response like this:**
🎯 **Here's what I discovered:**

• **Key Point 1:** [Main finding with details]
• **Key Point 2:** [Supporting information]
• **Key Point 3:** [Additional insights]

💡 **Quick Takeaway:** [Summary in one line]

**Formatting Rules:**
- Use bullet points for multiple facts
- Use **bold** for important terms
- Add emojis strategically 
- Keep paragraphs short (2-3 sentences max)
- Create visual breaks between sections

**Tone:** Excited, helpful, and genuinely interested in sharing knowledge
**Goal:** Make the user feel like they just learned something awesome!

If search results are limited:
- Stay positive and share what you found
- Suggest creative ways to explore the topic further
- Offer to help with related questions

Always format your response to be visually appealing and easy to scan!"""
        )

