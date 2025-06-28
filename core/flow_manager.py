import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from difflib import get_close_matches
from pydantic import BaseModel, Field, ValidationError
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import os

class FlowStep(BaseModel):
    field: str
    question: str
    type: str = Field(..., pattern="^(text|date|time|choice)$")
    options: Optional[List[str]] = None

class FlowPlan(BaseModel):
    intent: str
    steps: List[FlowStep]

class DynamicFlowManager:
    def __init__(self, user_id: str, db_manager=None):
        self.user_id = user_id
        self.db_manager = db_manager
        self.stack: List[FlowStep] = []
        self.answers: Dict = {}
        self.current_index: int = 0
        self.flow_type: Optional[str] = None
        self.model = ChatOpenAI(
            model="gpt-4o", 
            api_key=os.getenv("OPENAI_API_KEY"), 
            temperature=0.3
        )

    async def load_flow(self, flow_type: str, user_message: str) -> FlowPlan:
        """Load a dynamic flow based on user intent and message"""
        flow_planner_prompt = PromptTemplate(
            input_variables=["intent", "user_message"],
            template="""You are FlowAgent, an expert digital assistant for Noww Club AI. Your role is to understand the user's needs and create a comprehensive flow for their {intent}.

User's request: "{user_message}"

Based on this request for a {intent}, create a flow that collects ALL necessary information. Follow these requirements:

FOR HABITS:
Required fields: habit_name, habit_type, frequency, motivation, reminder_time, notification_method
Optional: specific_days (if frequency is weekly), goal

FOR GOALS:
Required fields: goal_name, target_date, tracking_method, motivation, notification_method
Optional: reminder_time, milestones

FOR REMINDERS:
Required fields: reminder_text, reminder_time, notification_method

NOTIFICATION METHODS: Always ask for one of: "Email", "SMS", "WhatsApp", "Push Notification", "Slack"

Create questions that are:
- Natural and conversational
- Context-aware based on what the user mentioned
- One concept per question
- Include specific examples for choices

Respond with ONLY a valid JSON object:
{{
  "intent": "{intent}",
  "steps": [
    {{
      "field": "field_name",
      "question": "Natural, contextual question here",
      "type": "text" | "date" | "time" | "choice",
      "options": ["option1", "option2", ...] // only for choice type
    }}
  ]
}}"""
        )
        
        try:
            chain = flow_planner_prompt | self.model
            response = await chain.ainvoke({"intent": flow_type, "user_message": user_message})
            
            # Clean response to extract JSON
            content = response.content.strip()
            if content.startswith('```json'):
                content = content[7:-3].strip()
            elif content.startswith('```'):
                content = content[3:-3].strip()
            
            flow_plan = FlowPlan.model_validate_json(content)
            
        except (json.JSONDecodeError, ValidationError) as e:
            print(f"Error creating dynamic flow, using fallback: {e}")
            # Fallback flow plans
            flow_plan = self._get_fallback_flow(flow_type)
        
        self.flow_type = flow_type
        self.stack = flow_plan.steps
        self.answers = {}
        self.current_index = 0
        return flow_plan

    def _get_fallback_flow(self, flow_type: str) -> FlowPlan:
        """Get fallback flow plans with comprehensive questions"""
        fallback_flows = {
            "habit": FlowPlan(
                intent="habit",
                steps=[
                    FlowStep(field="habit_name", question="What habit would you like to build?", type="text"),
                    FlowStep(field="habit_type", question="What type of habit is this?", type="choice", 
                            options=["Health & Fitness", "Learning", "Productivity", "Mindfulness", "Social", "Creative", "Other"]),
                    FlowStep(field="frequency", question="How often do you want to do this?", type="choice", 
                            options=["Daily", "Weekly", "Every few days", "Monthly"]),
                    FlowStep(field="motivation", question="What's your main motivation for this habit?", type="text"),
                    FlowStep(field="reminder_time", question="What time would you like to be reminded? (e.g., 8:00 AM)", type="time"),
                    FlowStep(field="notification_method", question="How would you like to receive reminders?", type="choice", 
                            options=["Email", "SMS", "WhatsApp", "Push Notification", "Slack"])
                ]
            ),
            "goal": FlowPlan(
                intent="goal",
                steps=[
                    FlowStep(field="goal_name", question="What goal would you like to set?", type="text"),
                    FlowStep(field="target_date", question="When would you like to achieve this by? (e.g., in 3 months, by December)", type="date"),
                    FlowStep(field="tracking_method", question="How would you like to track progress?", type="choice", 
                            options=["Daily check-ins", "Weekly reviews", "Milestone tracking", "Progress photos", "Metrics/Numbers"]),
                    FlowStep(field="motivation", question="What's driving you to achieve this goal?", type="text"),
                    FlowStep(field="notification_method", question="How would you like to receive progress reminders?", type="choice", 
                            options=["Email", "SMS", "WhatsApp", "Push Notification", "Slack"])
                ]
            ),
            "reminder": FlowPlan(
                intent="reminder",
                steps=[
                    FlowStep(field="reminder_text", question="What would you like to be reminded about?", type="text"),
                    FlowStep(field="reminder_time", question="When should I remind you? (e.g., 2:00 PM, in 1 hour)", type="time"),
                    FlowStep(field="notification_method", question="How would you like to receive this reminder?", type="choice", 
                            options=["Email", "SMS", "WhatsApp", "Push Notification", "Slack"])
                ]
            )
        }
        return fallback_flows.get(flow_type, FlowPlan(intent=flow_type, steps=[]))

    def get_next_question(self) -> Optional[FlowStep]:
        """Get the next question in the flow"""
        if self.current_index < len(self.stack):
            return self.stack[self.current_index]
        return None

    def submit_answer(self, answer: str) -> bool:
        """Submit answer for current question and move to next"""
        if self.current_index >= len(self.stack):
            return False
            
        current_step = self.stack[self.current_index]
        field = current_step.field
        
        # Process answer based on type
        if current_step.type == "time":
            extracted_time = self._extract_time(answer)
            self.answers[field] = extracted_time if extracted_time else answer
        elif current_step.type == "choice" and current_step.options:
            extracted_option = self._extract_option(answer, current_step.options)
            self.answers[field] = extracted_option if extracted_option else answer
        elif current_step.type == "date":
            extracted_date = self._extract_date_time(answer)
            self.answers[field] = extracted_date if extracted_date else answer
        else:
            self.answers[field] = answer
            
        self.current_index += 1
        return True

    def is_complete(self) -> bool:
        """Check if flow is complete"""
        return self.current_index >= len(self.stack)

    def get_completion_summary(self) -> str:
        """Generate summary of collected information"""
        if not self.is_complete():
            return "Flow not yet complete"
            
        summary_parts = []
        if self.flow_type == "habit":
            summary_parts.append(f"Habit: {self.answers.get('habit_name', 'Unknown')}")
            summary_parts.append(f"Type: {self.answers.get('habit_type', 'Not specified')}")
            summary_parts.append(f"Frequency: {self.answers.get('frequency', 'Not specified')}")
            summary_parts.append(f"Reminder: {self.answers.get('reminder_time', 'Not set')}")
            summary_parts.append(f"Notification: {self.answers.get('notification_method', 'Not specified')}")
        elif self.flow_type == "goal":
            summary_parts.append(f"Goal: {self.answers.get('goal_name', 'Unknown')}")
            summary_parts.append(f"Target Date: {self.answers.get('target_date', 'Not specified')}")
            summary_parts.append(f"Tracking: {self.answers.get('tracking_method', 'Not specified')}")
            summary_parts.append(f"Notification: {self.answers.get('notification_method', 'Not specified')}")
        elif self.flow_type == "reminder":
            summary_parts.append(f"Reminder: {self.answers.get('reminder_text', 'Unknown')}")
            summary_parts.append(f"Time: {self.answers.get('reminder_time', 'Not specified')}")
            summary_parts.append(f"Notification: {self.answers.get('notification_method', 'Not specified')}")
            
        return "\n".join(summary_parts)

    def _extract_time(self, input_text: str) -> Optional[str]:
        """Extract time from user input"""
        time_patterns = [
            r'(\d{1,2}:\d{2}\s+(?:AM|PM|am|pm))',
            r'(\d{1,2}:\d{2}(?:AM|PM|am|pm))',
            r'(\d{1,2}:\d{2})',
            r'(\d{1,2}\s+(?:AM|PM|am|pm))',
            r'(\d{1,2}(?:AM|PM|am|pm))',
            r'(?:at|remind me at|set for|scheduled for|reminder at)\s+(\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm)?)',
            r'(?:at|remind me at|set for|scheduled for|reminder at)\s+(\d{1,2}(?::\d{2})?)'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, input_text.upper())
            if match:
                time_str = match.group(1).strip()
                try:
                    for fmt in ["%I:%M %p", "%I:%M%p", "%H:%M", "%I:%M", "%I %p", "%I%p"]:
                        try:
                            parsed_time = datetime.strptime(time_str.upper(), fmt)
                            return parsed_time.strftime("%I:%M %p")
                        except ValueError:
                            continue
                    if re.match(r'^\d{1,2}$', time_str):
                        hour = int(time_str)
                        if 0 <= hour <= 23:
                            return datetime.strptime(f"{hour}:00", "%H:%M").strftime("%I:%M %p")
                except Exception:
                    continue
        return None

    def _extract_option(self, input_text: str, options: List[str]) -> Optional[str]:
        """Extract option from user input"""
        if not input_text or not options:
            return None
            
        input_lower = input_text.lower().strip()
        options_lower = [opt.lower() for opt in options]
        
        # Exact match
        if input_lower in options_lower:
            return options[options_lower.index(input_lower)]
        
        # Number word matching
        number_words = {'first': 1, 'second': 2, 'third': 3, 'fourth': 4, 'fifth': 5, 
                       '1st': 1, '2nd': 2, '3rd': 3, '4th': 4, '5th': 5}
        for word, num in number_words.items():
            if word in input_lower and num <= len(options):
                return options[num - 1]
        
        # Number matching
        try:
            num = int(input_lower)
            if 1 <= num <= len(options):
                return options[num - 1]
        except ValueError:
            pass
        
        # Partial matching
        for i, opt in enumerate(options_lower):
            if input_lower in opt or opt in input_lower:
                return options[i]
        
        # Word intersection matching
        input_words = set(input_lower.split())
        for i, opt in enumerate(options_lower):
            opt_words = set(opt.split())
            if input_words.intersection(opt_words):
                return options[i]
        
        # Fuzzy matching
        matches = get_close_matches(input_lower, options_lower, n=1, cutoff=0.6)
        if matches:
            return options[options_lower.index(matches[0])]
        
        return None

    def _extract_date_time(self, text: str) -> Optional[str]:
        """Extract date/time from user input"""
        patterns = [
            r'(in \d+\s*(?:days?|hours?|weeks?|months?))',
            r'(by\s(?:next\s)?(?:week|month|semester|year|\w+))',
            r'([A-Z][a-z]+\s\d{1,2}(?:st|nd|rd|th)?,\s?\d{4})',
            r'([A-Z][a-z]+\s\d{1,2}(?:st|nd|rd|th)?)',
            r'(\d{1,2}/\d{1,2}/\d{2,4})',
            r'(\d{4}-\d{2}-\d{2})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def get_flow_data(self) -> Dict[str, Any]:
        """Get all flow data for saving"""
        return {
            "flow_type": self.flow_type,
            "answers": self.answers,
            "current_index": self.current_index,
            "stack": [step.dict() for step in self.stack],
            "is_complete": self.is_complete()
        }