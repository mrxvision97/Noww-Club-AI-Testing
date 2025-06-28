import json
import os
import asyncio
from typing import Dict, List, Any, Optional, TypedDict
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from core.database import DatabaseManager
from core.memory import MemoryManager
from core.agents import ConversationalRAGAgent, EmotionalSupportAgent
from core.flow_manager import DynamicFlowManager, FlowStep
from utils.prompt_loader import PromptLoader

class GraphState(TypedDict):
    user_id: str
    messages: List[Dict[str, str]]
    current_intent: Optional[str]
    intent_confidence: float
    current_flow: Optional[Dict[str, Any]]
    flow_step: int
    pending_confirmation: Optional[Dict[str, Any]]
    context: str
    error_message: Optional[str]

class StateGraphManager:
    def __init__(self, db_manager: DatabaseManager, memory_manager: MemoryManager):
        self.db_manager = db_manager
        self.memory_manager = memory_manager
        self.prompt_loader = PromptLoader()
        
       
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.3,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.rag_agent = ConversationalRAGAgent()
        self.emotion_agent = EmotionalSupportAgent()
        
        # Initialize checkpointer before building graph
        self.checkpointer = MemorySaver()
        
        # Initialize state graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the conversation flow state graph"""
        workflow = StateGraph(GraphState)
        
        # Add nodes
        workflow.add_node("route_to_start", self.route_to_start)
        workflow.add_node("interrupt_detector", self.interrupt_detector)
        workflow.add_node("intent_router", self.intent_router)
        workflow.add_node("flow_generator", self.flow_generator)
        workflow.add_node("question_asker", self.question_asker)
        workflow.add_node("answer_collector", self.answer_collector)
        workflow.add_node("confirmation_handler", self.confirmation_handler)
        workflow.add_node("conversational_rag_agent", self.conversational_rag_node)
        workflow.add_node("emotional_support_agent", self.emotional_support_node)
        workflow.add_node("fallback_handler", self.fallback_handler)
        
        # Set entry point
        workflow.set_entry_point("route_to_start")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "route_to_start",
            self.should_resume_flow,
            {
                "resume_flow": "interrupt_detector",
                "resume_confirmation": "confirmation_handler",
                "new_conversation": "intent_router"
            }
        )
        
        workflow.add_conditional_edges(
            "interrupt_detector",
            self.check_for_interrupt,
            {
                "handle_interrupt": "intent_router",
                "continue_flow": "answer_collector",
                "new_intent": "intent_router"
            }
        )
        
        workflow.add_conditional_edges(
            "intent_router",
            self.route_by_intent,
            {
                "habit": "flow_generator",
                "goal": "flow_generator", 
                "reminder": "flow_generator",
                "emotional_support": "emotional_support_agent",
                "web_search": "conversational_rag_agent",
                "casual_chat": "conversational_rag_agent",
                "fallback": "fallback_handler"
            }
        )
        
        workflow.add_conditional_edges(
            "flow_generator",
            self.check_flow_completion,
            {
                "continue_flow": "question_asker",
                "flow_complete": "confirmation_handler",
                "error": "fallback_handler"
            }
        )
        
        workflow.add_edge("question_asker", "answer_collector")
        
        workflow.add_conditional_edges(
            "answer_collector",
            self.check_answer_completion,
            {
                "continue_flow": "flow_generator",
                "flow_complete": "confirmation_handler",
                "error": "fallback_handler"
            }
        )
        
        workflow.add_conditional_edges(
            "confirmation_handler",
            self.handle_confirmation,
            {
                "confirmed": END,
                "rejected": "intent_router",
                "error": "fallback_handler"
            }
        )
        
        workflow.add_edge("conversational_rag_agent", END)
        workflow.add_edge("emotional_support_agent", END)
        workflow.add_edge("fallback_handler", END)
        
        return workflow.compile(checkpointer=self.checkpointer)
    
    def route_to_start(self, state: GraphState) -> GraphState:
        """Entry point - determine where to route based on current state"""
        user_id = state["user_id"]
        
        # Check for pending flows
        pending_flows = self.db_manager.get_pending_flows(user_id)
        
        if pending_flows:
            # Check if there's an active flow with pending questions
            for flow in pending_flows:
                flow_data = flow['flow_data']
                if flow_data.get('current_step', 0) < len(flow_data.get('questions', [])):
                    state["current_flow"] = flow_data
                    state["flow_step"] = flow_data.get('current_step', 0)
                    return state
                elif flow_data.get('awaiting_confirmation'):
                    state["pending_confirmation"] = flow_data
                    return state
        
        # Add conversation context
        current_message = ""
        if state.get("messages") and len(state["messages"]) > 0:
            current_message = state["messages"][-1].get("content", "")
        
        context = self.memory_manager.get_context_for_conversation(user_id, current_message)
        state["context"] = context
        
        return state
    
    def should_resume_flow(self, state: GraphState) -> str:
        """Decide whether to resume a flow or start new conversation"""
        if state.get("current_flow") and state.get("flow_step", 0) >= 0:
            return "resume_flow"
        elif state.get("pending_confirmation"):
            return "resume_confirmation"
        else:
            return "new_conversation"
    
    def intent_router(self, state: GraphState) -> GraphState:
        """Classify user intent and route accordingly"""
        if not state.get("messages"):
            state["error_message"] = "No messages to process"
            return state
        
        latest_message = state["messages"][-1]["content"]
        context = state.get("context", "")
        
        # Load intent classification prompt
        intent_prompt = self.prompt_loader.load_prompt("intent_classifier")
        
        prompt = PromptTemplate(
            input_variables=["message", "context"],
            template=intent_prompt
        )
        
        try:
            response = self.llm.invoke(
                prompt.format(message=latest_message, context=context),
                response_format={"type": "json_object"}
            )
            
            intent_data = json.loads(response.content)
            
            state["current_intent"] = intent_data.get("intent", "casual_chat")
            state["intent_confidence"] = intent_data.get("confidence", 0.5)
            
            # Update user profile with conversation topic
            if intent_data.get("intent") != "casual_chat":
                self.memory_manager.update_user_profile(
                    state["user_id"],
                    {"conversation_topics": [intent_data.get("intent")]}
                )
            
        except Exception as e:
            print(f"Error in intent classification: {e}")
            state["current_intent"] = "casual_chat"
            state["intent_confidence"] = 0.3
            state["error_message"] = f"Intent classification failed: {str(e)}"
        
        return state
    
    def route_by_intent(self, state: GraphState) -> str:
        """Route based on classified intent"""
        intent = state.get("current_intent", "casual_chat")
        confidence = state.get("intent_confidence", 0.0)
        
        # If confidence is too low, go to fallback
        if confidence < 0.4:
            return "fallback"
        
        intent_routing = {
            "habit": "habit",
            "goal": "goal", 
            "reminder": "reminder",
            "emotional_support": "emotional_support",
            "web_search": "web_search",
            "casual_chat": "casual_chat"
        }
        
        return intent_routing.get(intent, "fallback")
    
    def flow_generator(self, state: GraphState) -> GraphState:
        """Generate dynamic flow based on intent"""
        intent = state["current_intent"]
        user_message = state["messages"][-1]["content"]
        
        # Initialize flow manager
        flow_manager = DynamicFlowManager(state["user_id"], self.db_manager)
        
        try:
            # Create event loop if none exists
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Generate flow using async call
            if loop.is_running():
                # If loop is already running, use thread executor
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, flow_manager.load_flow(intent, user_message))
                    flow_plan = future.result()
            else:
                flow_plan = loop.run_until_complete(flow_manager.load_flow(intent, user_message))
            
            # Save flow to database
            flow_id = self.db_manager.save_flow(
                state["user_id"],
                intent,
                flow_manager.get_flow_data()
            )
            
            # Create flow structure (don't store flow_manager object directly due to serialization)
            state["current_flow"] = {
                "id": flow_id,
                "flow_type": intent,
                "current_step": 0,
                "status": "active",
                "flow_data": flow_manager.get_flow_data(),
                "answers": flow_manager.answers
            }
            
            state["flow_step"] = 0
            
        except Exception as e:
            print(f"Error generating flow: {e}")
            # Fallback to simple flow
            fallback_questions = {
                "habit": ["What habit would you like to build?", "How often do you want to do this?", "When would you like to be reminded?"],
                "goal": ["What goal would you like to set?", "When would you like to achieve this?", "How will you track progress?"],
                "reminder": ["What would you like to be reminded about?", "When should I remind you?"]
            }
            
            questions = fallback_questions.get(intent, ["How can I help you?"])
            
            flow_id = self.db_manager.save_flow(
                state["user_id"],
                intent,
                {
                    "questions": questions,
                    "current_step": 0,
                    "collected_data": {},
                    "flow_type": intent,
                    "status": "active"
                }
            )
            
            state["current_flow"] = {
                "id": flow_id,
                "questions": questions,
                "current_step": 0,
                "collected_data": {},
                "flow_type": intent,
                "status": "active"
            }
            
            state["flow_step"] = 0
        
        return state
    
    def check_flow_completion(self, state: GraphState) -> str:
        """Check if flow should continue or is complete"""
        if state.get("error_message"):
            return "error"
        
        current_flow = state.get("current_flow")
        if not current_flow:
            return "error"
        
        questions = current_flow.get("questions", [])
        current_step = current_flow.get("current_step", 0)
        
        if current_step >= len(questions):
            return "flow_complete"
        else:
            return "continue_flow"
    
    def question_asker(self, state: GraphState) -> GraphState:
        """Ask the next question in the flow"""
        current_flow = state["current_flow"]
        
        # Recreate flow manager from stored data
        flow_data = current_flow.get("flow_data", {})
        if flow_data and flow_data.get("flow_type"):
            # Recreate flow manager
            flow_manager = DynamicFlowManager(state["user_id"], self.db_manager)
            flow_manager.flow_type = flow_data.get("flow_type")
            flow_manager.answers = current_flow.get("answers", {})
            flow_manager.current_index = current_flow.get("current_step", 0)
            flow_manager.stack = [FlowStep(**step) for step in flow_data.get("stack", [])]
            
            next_step = flow_manager.get_next_question()
            if next_step:
                question = next_step.question
                
                # Add context for first question
                if flow_manager.current_index == 0:
                    intro = f"Great! Let's set up your {current_flow.get('flow_type', 'request')}. "
                    question = intro + question
                
                # Add options for choice questions
                if next_step.type == "choice" and next_step.options:
                    question += "\n\nOptions:\n"
                    for i, option in enumerate(next_step.options, 1):
                        question += f"{i}. {option}\n"
                
                state["messages"].append({
                    "role": "assistant",
                    "content": question
                })
            else:
                # Flow complete, show summary
                summary = f"Perfect! Here's what I have:\n\n"
                for key, value in flow_manager.answers.items():
                    summary += f"{key.replace('_', ' ').title()}: {value}\n"
                summary += "\nWould you like me to create this for you?"
                
                state["messages"].append({
                    "role": "assistant",
                    "content": summary
                })
                current_flow["status"] = "confirmation"
                state["current_flow"] = current_flow
        else:
            # Fallback to simple flow
            questions = current_flow.get("questions", [])
            current_step = current_flow.get("current_step", 0)
            
            if current_step < len(questions):
                question = questions[current_step]
                
                if current_step == 0:
                    intro = f"Great! Let's set up your {current_flow.get('flow_type', 'request')}. "
                    question = intro + question
                
                state["messages"].append({
                    "role": "assistant",
                    "content": question
                })
            else:
                state["messages"].append({
                    "role": "assistant",
                    "content": "I have all the information I need. Would you like me to create this for you?"
                })
                current_flow["status"] = "confirmation"
                state["current_flow"] = current_flow
        
        return state
    
    def answer_collector(self, state: GraphState) -> GraphState:
        """Collect and store user's answer"""
        if not state.get("messages"):
            state["error_message"] = "No answer to collect"
            return state
        
        current_flow = state["current_flow"]
        if not current_flow:
            state["error_message"] = "No active flow to collect answer for"
            return state
        
        # Get the latest user message (answer)
        user_messages = [msg for msg in state["messages"] if msg["role"] == "user"]
        if not user_messages:
            state["error_message"] = "No user answer found"
            return state
        
        latest_answer = user_messages[-1]["content"]
        current_step = current_flow.get("current_step", 0)
        questions = current_flow.get("questions", [])
        
        # Store the answer
        collected_data = current_flow.get("collected_data", {})
        
        if current_step < len(questions):
            question = questions[current_step]
            question_key = question.get("key", f"question_{current_step}") if isinstance(question, dict) else f"question_{current_step}"
            collected_data[question_key] = latest_answer
        
        # Update flow state
        current_flow["collected_data"] = collected_data
        current_flow["current_step"] = current_step + 1
        
        # Update in database
        self.db_manager.update_flow(
            current_flow.get("id"),
            current_flow
        )
        
        state["current_flow"] = current_flow
        state["flow_step"] = current_flow["current_step"]
        
        return state
    
    def check_answer_completion(self, state: GraphState) -> str:
        """Check if more answers are needed or flow is complete"""
        if state.get("error_message"):
            return "error"
        
        current_flow = state.get("current_flow")
        if not current_flow:
            return "error"
        
        questions = current_flow.get("questions", [])
        current_step = current_flow.get("current_step", 0)
        
        if current_step >= len(questions):
            return "flow_complete"
        else:
            return "continue_flow"
    
    def confirmation_handler(self, state: GraphState) -> GraphState:
        """Handle flow confirmation and saving"""
        current_flow = state.get("current_flow")
        
        if not current_flow:
            # Check for pending confirmation
            if state.get("pending_confirmation"):
                current_flow = state["pending_confirmation"]
            else:
                state["error_message"] = "No flow to confirm"
                return state
        
        collected_data = current_flow.get("collected_data", {})
        flow_type = current_flow.get("flow_type", "unknown")
        
        # Generate confirmation summary
        confirmation_text = self._generate_confirmation_summary(flow_type, collected_data)
        
        # Check if this is a confirmation response
        if state.get("messages"):
            latest_message = state["messages"][-1]["content"].lower()
            
            if any(word in latest_message for word in ["yes", "confirm", "save", "correct"]):
                # Save the flow data
                success = self._save_flow_data(state["user_id"], flow_type, collected_data)
                
                if success:
                    # Mark flow as completed
                    if current_flow.get("id"):
                        self.db_manager.update_flow(
                            current_flow["id"],
                            current_flow,
                            status="completed"
                        )
                    
                    state["messages"].append({
                        "role": "assistant",
                        "content": "Great! I've saved that information for you. Is there anything else I can help you with?"
                    })
                    
                    # Clear current flow
                    state["current_flow"] = None
                    state["pending_confirmation"] = None
                    
                else:
                    state["error_message"] = "Failed to save flow data"
            
            elif any(word in latest_message for word in ["no", "cancel", "wrong", "incorrect"]):
                # Cancel the flow
                if current_flow.get("id"):
                    self.db_manager.update_flow(
                        current_flow["id"],
                        current_flow,
                        status="cancelled"
                    )
                
                state["messages"].append({
                    "role": "assistant",
                    "content": "No problem! Let me know if you'd like to try again or if there's something else I can help you with."
                })
                
                # Clear current flow
                state["current_flow"] = None
                state["pending_confirmation"] = None
        
        else:
            # First time showing confirmation
            state["messages"].append({
                "role": "assistant",
                "content": f"{confirmation_text}\n\nWould you like me to save this information? (Yes/No)"
            })
            
            # Mark as awaiting confirmation
            current_flow["awaiting_confirmation"] = True
            state["pending_confirmation"] = current_flow
            
            # Update in database
            if current_flow.get("id"):
                self.db_manager.update_flow(
                    current_flow["id"],
                    current_flow
                )
        
        return state
    
    def handle_confirmation(self, state: GraphState) -> str:
        """Route based on confirmation response"""
        if state.get("error_message"):
            return "error"
        
        if state.get("current_flow") is None and state.get("pending_confirmation") is None:
            return "confirmed"
        
        if state.get("messages"):
            latest_message = state["messages"][-1]["content"].lower()
            
            if any(word in latest_message for word in ["yes", "confirm", "save", "correct"]):
                return "confirmed"
            elif any(word in latest_message for word in ["no", "cancel", "wrong", "incorrect"]):
                return "rejected"
        
        return "confirmed"  # Default to confirmed if unclear
    
    def conversational_rag_node(self, state: GraphState) -> GraphState:
        """Handle conversational RAG for general chat and web search"""
        user_message = state["messages"][-1]["content"]
        context = state.get("context", "")
        intent = state.get("current_intent", "casual_chat")
        
        try:
            if intent == "web_search":
                response = self.rag_agent.search_and_respond(user_message, context)
            else:
                response = self.rag_agent.conversational_response(user_message, context)
            
            # Check if there's a paused flow to offer resumption
            paused_flows = self.db_manager.get_pending_flows(state["user_id"])
            paused_flow = next((f for f in paused_flows if f.get('flow_data', {}).get('status') == 'paused'), None)
            
            if paused_flow and state.get("flow_interrupt"):
                flow_type = paused_flow.get('flow_type', 'task')
                response += f"\n\nWould you like to continue where we left off with your {flow_type}?"
            
            state["messages"].append({
                "role": "assistant",
                "content": response
            })
            
        except Exception as e:
            print(f"Error in conversational RAG: {e}")
            state["messages"].append({
                "role": "assistant", 
                "content": "I'm having trouble processing that request right now. Could you try rephrasing it?"
            })
        
        return state
    
    def emotional_support_node(self, state: GraphState) -> GraphState:
        """Handle emotional support conversations"""
        user_message = state["messages"][-1]["content"]
        context = state.get("context", "")
        
        try:
            response = self.emotion_agent.provide_support(user_message, context)
            
            # Check if there's a paused flow to offer resumption
            paused_flows = self.db_manager.get_pending_flows(state["user_id"])
            paused_flow = next((f for f in paused_flows if f.get('flow_data', {}).get('status') == 'paused'), None)
            
            if paused_flow and state.get("flow_interrupt"):
                flow_type = paused_flow.get('flow_type', 'task')
                response += f"\n\nWould you like to continue where we left off with your {flow_type}?"
            
            state["messages"].append({
                "role": "assistant",
                "content": response
            })
            
            # Extract mood information and save it
            mood_info = self.emotion_agent.analyze_emotion(user_message)
            if mood_info.get("mood_score"):
                self.db_manager.save_mood_entry(
                    state["user_id"],
                    mood_info["mood_score"],
                    mood_info.get("notes", user_message)
                )
            
            # Add to memory
            self.memory_manager.add_interaction(
                state["user_id"],
                user_message,
                response
            )
            
        except Exception as e:
            print(f"Error in emotional support: {e}")
            response = "I'm here to listen and support you. Sometimes it helps just to talk about what's on your mind."
            
            state["messages"].append({
                "role": "assistant", 
                "content": response
            })
        
        return state
    
    def interrupt_detector(self, state: GraphState) -> GraphState:
        """Detect if the user's message interrupts the current flow"""
        current_flow = state.get("current_flow")
        if not current_flow:
            return state
        
        latest_message = state["messages"][-1]["content"] if state.get("messages") else ""
        
        # Check if this is a continuation signal
        continuation_signals = ["yes", "continue", "go on", "proceed", "next", "sure", "ok", "okay"]
        if any(signal in latest_message.lower() for signal in continuation_signals):
            state["flow_interrupt"] = False
            return state
        
        # Use LLM to detect if this is an interruption
        interrupt_prompt = f"""
        You are a flow-aware conversational agent managing user intents.

        The user is currently in the middle of a structured flow for: {current_flow.get('flow_type', 'unknown')}
        Current step: {current_flow.get('current_step', 0)} of {len(current_flow.get('questions', []))}

        User's latest message: "{latest_message}"

        Determine if this message is:
        1. An answer to the current flow question (continue flow)
        2. An unrelated request that interrupts the flow (emotional, casual, general, or web search)
        3. A request to cancel/stop the current flow

        Respond with JSON only:
        {{
            "is_interruption": true/false,
            "interrupt_type": "emotional_support" | "casual_chat" | "web_search" | "cancel_flow" | "none",
            "confidence": 0.0-1.0
        }}
        """
        
        try:
            response = self.llm.invoke(
                interrupt_prompt,
                response_format={"type": "json_object"}
            )
            
            interrupt_data = json.loads(response.content)
            state["interrupt_analysis"] = interrupt_data
            
            if interrupt_data.get("is_interruption", False) and interrupt_data.get("confidence", 0) > 0.6:
                # Pause the current flow
                current_flow["status"] = "paused"
                self.db_manager.update_flow(
                    current_flow.get("id"),
                    current_flow
                )
                state["flow_interrupt"] = True
                state["current_intent"] = interrupt_data.get("interrupt_type", "casual_chat")
            else:
                state["flow_interrupt"] = False
        
        except Exception as e:
            print(f"Error in interrupt detection: {e}")
            state["flow_interrupt"] = False
        
        return state
    
    def check_for_interrupt(self, state: GraphState) -> str:
        """Route based on interrupt detection"""
        if state.get("flow_interrupt", False):
            interrupt_type = state.get("interrupt_analysis", {}).get("interrupt_type", "casual_chat")
            if interrupt_type == "cancel_flow":
                # Clear the flow
                if state.get("current_flow"):
                    self.db_manager.update_flow(
                        state["current_flow"].get("id"),
                        state["current_flow"],
                        status="cancelled"
                    )
                    state["current_flow"] = None
                return "new_intent"
            else:
                return "handle_interrupt"
        else:
            return "continue_flow"
    
    def fallback_handler(self, state: GraphState) -> GraphState:
        """Handle fallback cases and errors"""
        error_message = state.get("error_message", "")
        
        if error_message:
            response = f"I encountered an issue: {error_message}. Let me try to help you in a different way."
        else:
            response = "I'm not sure I understood that correctly. Could you please rephrase your request?"
        
        state["messages"].append({
            "role": "assistant",
            "content": response
        })
        
        # Clear error state
        state["error_message"] = None
        
        return state
    
    def _generate_confirmation_summary(self, flow_type: str, collected_data: Dict[str, Any]) -> str:
        """Generate a summary for confirmation"""
        if flow_type == "habit":
            return f"I understand you want to create a habit: {collected_data.get('habit_name', 'New Habit')}. " + \
                   f"Frequency: {collected_data.get('frequency', 'daily')}. " + \
                   f"Description: {collected_data.get('description', 'No description provided')}."
        
        elif flow_type == "goal":
            return f"I understand you want to set a goal: {collected_data.get('goal_name', 'New Goal')}. " + \
                   f"Target date: {collected_data.get('target_date', 'No deadline set')}. " + \
                   f"Description: {collected_data.get('description', 'No description provided')}."
        
        elif flow_type == "reminder":
            return f"I understand you want to set a reminder: {collected_data.get('reminder_title', 'New Reminder')}. " + \
                   f"Time: {collected_data.get('reminder_time', 'Time not specified')}. " + \
                   f"Description: {collected_data.get('description', 'No description provided')}."
        
        else:
            return f"Here's what I collected: {json.dumps(collected_data, indent=2)}"
    
    def _save_flow_data(self, user_id: str, flow_type: str, collected_data: Dict[str, Any]) -> bool:
        """Save the collected flow data to appropriate tables"""
        try:
            if flow_type == "habit":
                self.db_manager.save_habit(
                    user_id,
                    collected_data.get('habit_name', 'New Habit'),
                    collected_data.get('description'),
                    collected_data.get('frequency', 'daily')
                )
            
            elif flow_type == "goal":
                self.db_manager.save_goal(
                    user_id,
                    collected_data.get('goal_name', 'New Goal'),
                    collected_data.get('description'),
                    collected_data.get('target_date')
                )
            
            elif flow_type == "reminder":
                self.db_manager.save_reminder(
                    user_id,
                    collected_data.get('reminder_title', 'New Reminder'),
                    collected_data.get('description'),
                    collected_data.get('reminder_time')
                )
            
            return True
        
        except Exception as e:
            print(f"Error saving flow data: {e}")
            return False
    
    def process_message(self, user_id: str, message: str, session_id: str = None) -> Dict[str, Any]:
        """Process a user message through the state graph"""
        session_id = session_id or f"session_{user_id}"
        
        # Initialize state
        initial_state = GraphState(
            user_id=user_id,
            messages=[{"role": "user", "content": message}],
            current_intent=None,
            intent_confidence=0.0,
            current_flow=None,
            flow_step=0,
            pending_confirmation=None,
            context="",
            error_message=None
        )
        
        try:
            # Run the graph
            result = self.graph.invoke(
                initial_state,
                config={"configurable": {"thread_id": session_id}}
            )
            
            # Extract AI response
            ai_messages = [msg for msg in result["messages"] if msg["role"] == "assistant"]
            ai_response = ai_messages[-1]["content"] if ai_messages else "I'm sorry, I couldn't process that."
            
            # Update memory
            self.memory_manager.add_interaction(user_id, message, ai_response)
            
            return {
                "response": ai_response,
                "current_flow": result.get("current_flow"),
                "pending_confirmation": result.get("pending_confirmation"),
                "error": result.get("error_message")
            }
        
        except Exception as e:
            print(f"Error processing message: {e}")
            return {
                "response": "I'm sorry, I encountered an error processing your message. Please try again.",
                "current_flow": None,
                "pending_confirmation": None,
                "error": str(e)
            }
