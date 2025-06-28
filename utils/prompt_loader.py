import os
from typing import Dict, Optional

class PromptLoader:
    def __init__(self, prompts_dir: str = "prompts"):
        self.prompts_dir = prompts_dir
        self._prompt_cache = {}
    
    def load_prompt(self, prompt_name: str) -> str:
        """Load a prompt template from file"""
        if prompt_name in self._prompt_cache:
            return self._prompt_cache[prompt_name]
        
        prompt_path = os.path.join(self.prompts_dir, f"{prompt_name}.txt")
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_content = f.read()
            
            # Cache the prompt
            self._prompt_cache[prompt_name] = prompt_content
            return prompt_content
        
        except FileNotFoundError:
            print(f"Prompt file not found: {prompt_path}")
            return self._get_fallback_prompt(prompt_name)
        
        except Exception as e:
            print(f"Error loading prompt {prompt_name}: {e}")
            return self._get_fallback_prompt(prompt_name)
    
    def _get_fallback_prompt(self, prompt_name: str) -> str:
        """Get fallback prompt if file is not found"""
        fallback_prompts = {
            "intent_classifier": """
            Analyze the user's message and classify their intent. Respond with JSON:
            {
              "intent": "habit|goal|reminder|casual_chat|web_search|emotional_support",
              "confidence": 0.0-1.0,
              "urgency": "low|medium|high",
              "tone": "empathetic|motivational|neutral", 
              "task_required": true/false
            }
            
            User message: {message}
            Context: {context}
            """,
            
            "flow_planner": """
            Create a conversation flow for intent: {intent}
            User message: {message}
            Context: {context}
            
            Respond with JSON containing questions to ask the user:
            {
              "questions": [
                {"text": "Question text", "key": "field_name", "type": "text", "required": true}
              ],
              "flow_description": "What this flow will accomplish"
            }
            """,
            
            "emotion_analysis": """
            Provide empathetic emotional support for this message: {message}
            Context: {context}
            
            Respond with warmth and understanding, acknowledging their feelings and offering support.
            """,
            
            "companion_chat": """
            You are a friendly AI companion. Respond to: {message}
            Context: {context}
            
            Be warm, engaging, and genuinely interested in the user.
            """,
            
            "search_summarizer": """
            Answer the user's query based on search results.
            
            Query: {query}
            Search Results: {search_results}
            Context: {context}
            
            Provide a helpful, conversational response based on the search results.
            """
        }
        
        return fallback_prompts.get(prompt_name, "Please provide more details about what you'd like to discuss.")
    
    def reload_prompts(self):
        """Clear cache and reload all prompts"""
        self._prompt_cache.clear()
    
    def get_available_prompts(self) -> list:
        """Get list of available prompt files"""
        if not os.path.exists(self.prompts_dir):
            return []
        
        prompt_files = []
        for filename in os.listdir(self.prompts_dir):
            if filename.endswith('.txt'):
                prompt_files.append(filename[:-4])  # Remove .txt extension
        
        return prompt_files
    
    def validate_prompts(self) -> Dict[str, bool]:
        """Validate that all expected prompts exist"""
        expected_prompts = [
            "intent_classifier",
            "flow_planner", 
            "emotion_analysis",
            "companion_chat",
            "search_summarizer"
        ]
        
        validation_results = {}
        for prompt_name in expected_prompts:
            prompt_path = os.path.join(self.prompts_dir, f"{prompt_name}.txt")
            validation_results[prompt_name] = os.path.exists(prompt_path)
        
        return validation_results
