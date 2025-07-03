import os
import json
import requests
from typing import Dict, List, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from utils.prompt_loader import PromptLoader

class ConversationalRAGAgent:
    def __init__(self):
        
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.prompt_loader = PromptLoader()
    
    def conversational_response(self, user_message: str, context: str = "") -> str:
        """Generate conversational response for casual chat"""
        companion_prompt = self.prompt_loader.load_prompt("companion_chat")
        
        prompt = PromptTemplate(
            input_variables=["message", "context"],
            template=companion_prompt
        )
        
        try:
            response = self.llm.invoke(
                prompt.format(message=user_message, context=context)
            )
            return response.content
        
        except Exception as e:
            print(f"Error in conversational response: {e}")
            return "I'm here to chat with you! What would you like to talk about?"
    
    def search_and_respond(self, query: str, context: str = "") -> str:
        """Perform web search and provide summarized response"""
        try:
            # Simulate web search (in production, integrate with actual search API)
            search_results = self._mock_web_search(query)
            
            # Generate response based on search results
            search_prompt = self.prompt_loader.load_prompt("search_summarizer")
            
            prompt = PromptTemplate(
                input_variables=["query", "search_results", "context"],
                template=search_prompt
            )
            
            response = self.llm.invoke(
                prompt.format(
                    query=query,
                    search_results=json.dumps(search_results),
                    context=context
                )
            )
            
            return response.content
        
        except Exception as e:
            print(f"Error in search and respond: {e}")
            return f"I searched for '{query}' but encountered an issue retrieving the information. Could you try rephrasing your question?"
    
    def _mock_web_search(self, query: str) -> List[Dict[str, str]]:
        """Mock web search results for development"""
        # In production, replace with actual search API (Google, Bing, etc.)
        return [
            {
                "title": f"Information about {query}",
                "snippet": f"Here's some relevant information about {query}. This would be actual search results in production.",
                "url": "https://example.com"
            }
        ]

class EmotionalSupportAgent:
    def __init__(self):
        
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.8,  # Higher temperature for more empathetic responses
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.prompt_loader = PromptLoader()
    
    def provide_support(self, user_message: str, context: str = "") -> str:
        """Provide emotional support response"""
        emotion_prompt = self.prompt_loader.load_prompt("emotion_analysis")
        
        # First, analyze the emotional content
        emotion_analysis = self.analyze_emotion(user_message)
        
        # Generate supportive response
        support_prompt = f"""
        You are an empathetic AI companion providing emotional support. 
        
        User's message: {user_message}
        
        Emotional analysis: {json.dumps(emotion_analysis)}
        
        Context: {context}
        
        Provide a warm, empathetic response that:
        1. Acknowledges their feelings
        2. Offers gentle support or encouragement
        3. Suggests helpful coping strategies if appropriate
        4. Maintains a caring, non-judgmental tone
        
        Keep the response personal and conversational, not clinical.
        """
        
        try:
            response = self.llm.invoke(support_prompt)
            return response.content
        
        except Exception as e:
            print(f"Error providing emotional support: {e}")
            return "I can hear that you're going through something difficult. I'm here to listen and support you. Would you like to talk more about what's on your mind?"
    
    def analyze_emotion(self, text: str) -> Dict[str, Any]:
        """Analyze emotional content of text"""
        emotion_prompt = f"""
        Analyze the emotional content of this text and provide a JSON response:
        
        Text: "{text}"
        
        Provide analysis in this format:
        {{
            "primary_emotion": "happy|sad|angry|anxious|neutral|confused|excited|frustrated",
            "intensity": 0.0-1.0,
            "mood_score": 1-5 (1=very negative, 3=neutral, 5=very positive),
            "support_needed": true/false,
            "suggested_response_tone": "empathetic|encouraging|celebratory|calming|motivational",
            "notes": "brief analysis of emotional state"
        }}
        """
        
        try:
            response = self.llm.invoke(
                emotion_prompt,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.content)
        
        except Exception as e:
            print(f"Error analyzing emotion: {e}")
            return {
                "primary_emotion": "neutral",
                "intensity": 0.5,
                "mood_score": 3,
                "support_needed": False,
                "suggested_response_tone": "empathetic",
                "notes": "Unable to analyze emotion"
            }
    
    def generate_coping_strategies(self, emotional_state: str, context: str = "") -> List[str]:
        """Generate personalized coping strategies"""
        strategies_prompt = f"""
        Generate 3-5 personalized coping strategies for someone experiencing: {emotional_state}
        
        Context: {context}
        
        Provide practical, actionable strategies that are:
        1. Simple to implement
        2. Evidence-based
        3. Appropriate for the emotional state
        4. Personalized to the context
        
        Return as a JSON list of strategies.
        """
        
        try:
            response = self.llm.invoke(
                strategies_prompt,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.content)
            return result.get("strategies", [])
        
        except Exception as e:
            print(f"Error generating coping strategies: {e}")
            return [
                "Take a few deep breaths and ground yourself in the present moment",
                "Consider talking to someone you trust about how you're feeling",
                "Engage in a calming activity that you enjoy"
            ]
