import json
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from core.database import DatabaseManager
from core.memory import MemoryManager
from openai import OpenAI


class VisionBoardIntakeManager:
    """
    Manages the 10-question intake flow for vision board creation.
    Users must complete this flow before generating a vision board.
    """
    
    def __init__(self, db_manager: DatabaseManager, memory_manager: MemoryManager):
        self.db_manager = db_manager
        self.memory_manager = memory_manager
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # 10 High-Impact Questions for Vision Board Creation - Conversational & Engaging
        self.questions = {
            1: {
                "theme": "emotional_anchor",
                "question": "If you had to bring more of just one feeling into your life right now — what would it be?",
                "follow_up": "What would that feeling change about your daily life?",
                "context": "This helps me understand the emotional energy you want to manifest"
            },
            2: {
                "theme": "identity_legacy",
                "question": "Three years from now — what do you want people to know you for?",
                "follow_up": "What impact do you want to have on the world around you?",
                "context": "Your legacy shapes how we'll visualize your future self"
            },
            3: {
                "theme": "growth_craft",
                "question": "What's a skill you're building (or dreaming of building) that excites you?",
                "follow_up": "What draws you to this particular skill?",
                "context": "Learning about your growth helps me capture your aspirational energy"
            },
            4: {
                "theme": "self_care_wellness",
                "question": "Right now, what does 'taking care of yourself' look like for you? Be honest — it might be saying no, taking walks, eating better, sleeping in...",
                "follow_up": "How does this make you feel when you actually do it?",
                "context": "Self-care reveals your relationship with yourself"
            },
            5: {
                "theme": "relationships_community",
                "question": "What kind of people do you want to attract, grow with, or be surrounded by?",
                "follow_up": "What energy do these people bring that you crave?",
                "context": "Your ideal community shows me the energy you want to cultivate"
            },
            6: {
                "theme": "authentic_presence",
                "question": "Who or what makes you feel most 'you' when you're around them? Think of people, places, activities — what feels most like 'home' in you?",
                "follow_up": "What is it about these moments that feels so right?",
                "context": "These authentic moments reveal your truest self"
            },
            7: {
                "theme": "space_environment",
                "question": "If you closed your eyes and stepped into your dream living space — what does it FEEL like? Not what it looks like, but the vibe, emotion, rhythm?",
                "follow_up": "How would you spend a perfect morning in this space?",
                "context": "Your ideal environment reflects your inner world"
            },
            8: {
                "theme": "unleashed_expression",
                "question": "What part of you is ready to be expressed more? Is it your creativity, softness, boldness, ambition, weirdness?",
                "follow_up": "What would expressing this part of you more fully look like?",
                "context": "This shows me what wants to emerge in your life"
            },
            9: {
                "theme": "secret_desire",
                "question": "What's something you secretly want to try, create, or learn? Think of something playful, thrilling, or 'not for others'",
                "follow_up": "What stops you from pursuing this right now?",
                "context": "Secret desires often hold the keys to our deepest fulfillment"
            },
            10: {
                "theme": "brave_wish",
                "question": "What's one thing you're a little scared to admit you want — but you do want it? Dare to say it.",
                "follow_up": "What would having this change about your life?",
                "context": "This brave wish will be the most powerful element in your vision board"
            }
        }
        
        # Template matching based on responses (updated names)
        self.template_mappings = {
            1: {
                "name": "Disciplined Achiever",
                "keywords": ["discipline", "strength", "focus", "achievement", "leadership", "fitness", "success", "performance", "goals", "determination"],
                "themes": ["ambition", "growth", "mastery", "confidence", "achievement"]
            },
            2: {
                "name": "Creative Visionary", 
                "keywords": ["creativity", "design", "art", "beauty", "style", "expression", "vision", "elegance", "create", "aesthetic"],
                "themes": ["creativity", "lifestyle", "leadership", "aesthetics", "expression"]
            },
            3: {
                "name": "Bold Success",
                "keywords": ["luxury", "success", "money", "recognition", "bold", "attraction", "wealth", "business", "power", "confident"],
                "themes": ["success", "luxury", "confidence", "ambition", "recognition"]
            },
            4: {
                "name": "Mindful Balance",
                "keywords": ["peace", "wellness", "mindfulness", "balance", "nature", "healing", "calm", "spiritual", "harmony", "centered"],
                "themes": ["wellness", "peace", "mindfulness", "balance", "authenticity"]
            }
        }
    
    def start_intake_flow(self, user_id: str) -> str:
        """Start the vision board intake flow for a user"""
        try:
            # Clear any existing intake data
            self._clear_intake_data(user_id)
            
            # Set flow status
            intake_data = {
                "user_id": user_id,
                "status": "in_progress",
                "current_question": 1,
                "started_at": datetime.now().isoformat(),
                "answers": {},
                "completed_at": None
            }
            
            self._save_intake_data(user_id, intake_data)
            
            # Create engaging introduction
            intro = """🎨 **Let's create your perfect vision board!**

I'm so excited to dive deep with you and understand what makes your heart sing. This isn't just about pretty pictures — this is about capturing the essence of who you're becoming.

I have 10 thoughtful questions that will help me understand your dreams, values, and the energy you want to manifest. Each answer you give helps me create something truly personalized for YOU.

Ready? Let's start with something beautiful..."""

            question = self._format_question(1)
            return f"{intro}\n\n{question}"
            
        except Exception as e:
            print(f"Error starting intake flow: {e}")
            return "I'm sorry, I encountered an error starting the vision board intake. Please try again."
    
    def process_answer(self, user_id: str, answer: str) -> str:
        """Process a user's answer and move to next question or complete flow"""
        try:
            intake_data = self._load_intake_data(user_id)
            
            if not intake_data or intake_data.get("status") != "in_progress":
                return "It looks like you haven't started the vision board intake yet. Would you like to begin?"
            
            current_q = intake_data.get("current_question", 1)
            
            # Analyze and categorize the answer
            categorized_answer = self._analyze_answer(current_q, answer)
            
            # Save the answer
            intake_data["answers"][str(current_q)] = categorized_answer
            self._save_intake_data(user_id, intake_data)
            
            # Save to episodic memory for long-term retention
            self._save_to_memory(user_id, current_q, answer, categorized_answer)
            
            # Create encouraging response
            encouragement = self._get_encouraging_response(current_q, answer)
            
            # Move to next question or complete
            if current_q < 10:
                intake_data["current_question"] = current_q + 1
                self._save_intake_data(user_id, intake_data)
                next_question = self._format_question(current_q + 1)
                return f"{encouragement}\n\n{next_question}"
            else:
                # Complete the intake
                completion_message = self._complete_intake(user_id, intake_data)
                return f"{encouragement}\n\n{completion_message}"
                
        except Exception as e:
            print(f"Error processing answer: {e}")
            return "I encountered an error processing your answer. Please try again."
    
    def get_intake_status(self, user_id: str) -> Dict[str, Any]:
        """Get the current intake status for a user"""
        intake_data = self._load_intake_data(user_id)
        
        if not intake_data:
            return {"status": "not_started"}
        
        return {
            "status": intake_data.get("status"),
            "current_question": intake_data.get("current_question"),
            "total_questions": 10,
            "answers_count": len(intake_data.get("answers", {})),
            "started_at": intake_data.get("started_at"),
            "completed_at": intake_data.get("completed_at")
        }
    
    def is_intake_complete(self, user_id: str) -> bool:
        """Check if user has completed the intake flow"""
        intake_data = self._load_intake_data(user_id)
        return intake_data and intake_data.get("status") == "completed"
    
    def get_completed_answers(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get completed intake answers for vision board generation"""
        if not self.is_intake_complete(user_id):
            return None
        
        intake_data = self._load_intake_data(user_id)
        return intake_data.get("answers", {})
    
    def recommend_template(self, user_id: str) -> Tuple[int, str]:
        """Recommend a template based on completed intake answers with enhanced analysis"""
        intake_data = self.db_manager.get_vision_board_intake(user_id)
        if not intake_data or not intake_data.get('analyzed_responses'):
            return 1, "Disciplined Achiever"  # Default
        
        # Analyze the combined responses for template matching
        analyzed_responses = intake_data['analyzed_responses']
        
        # Template characteristics enhanced:
        # 1. Disciplined Achiever: Structure, goals, discipline, success, organization
        # 2. Creative Visionary: Creativity, innovation, artistic, imagination, expression
        # 3. Bold Success: Confidence, leadership, ambition, power, strength
        # 4. Mindful Balance: Peace, wellness, harmony, mindfulness, nature
        
        template_scores = {1: 0, 2: 0, 3: 0, 4: 0}
        
        # Enhanced keywords that indicate each template preference
        template_keywords = {
            1: ['structure', 'goal', 'discipline', 'organized', 'plan', 'system', 'achievement', 'focused', 'methodical', 'consistent', 'success', 'productive', 'efficient'],
            2: ['creative', 'artistic', 'imagination', 'innovation', 'expression', 'beauty', 'inspire', 'vision', 'unique', 'original', 'design', 'colorful', 'expressive'],
            3: ['bold', 'confident', 'leadership', 'success', 'power', 'ambitious', 'strong', 'fearless', 'commanding', 'influential', 'dynamic', 'assertive', 'winning'],
            4: ['peaceful', 'balance', 'mindful', 'harmony', 'wellness', 'calm', 'serene', 'natural', 'gentle', 'centered', 'tranquil', 'spiritual', 'grounded']
        }
        
        # Analyze all responses
        all_keywords = []
        energy_levels = []
        visual_styles = []
        
        for response in analyzed_responses:
            # Collect keywords from multiple sources
            all_keywords.extend(response.get('essence_keywords', []))
            all_keywords.extend(response.get('values_revealed', []))
            all_keywords.extend(response.get('aspirations', []))
            all_keywords.extend(response.get('personality_traits', []))
            all_keywords.extend(response.get('core_emotions', []))
            
            # Energy level influences template choice
            energy = response.get('energy_level', 'medium')
            energy_levels.append(energy)
            
            # Visual style preferences
            visual_style = response.get('visual_style_preference', 'natural')
            visual_styles.append(visual_style)
        
        # Convert to lowercase for matching
        all_keywords = [kw.lower().strip() for kw in all_keywords if kw]
        
        # Score templates based on keyword matches
        for template_num, keywords in template_keywords.items():
            for keyword in keywords:
                for user_keyword in all_keywords:
                    if keyword in user_keyword or user_keyword in keyword:
                        template_scores[template_num] += 1
        
        # Additional scoring based on energy and style patterns
        high_energy_count = energy_levels.count('high')
        medium_energy_count = energy_levels.count('medium') 
        low_energy_count = energy_levels.count('low')
        
        # High energy -> Bold Success or Disciplined Achiever
        if high_energy_count >= 3:
            template_scores[3] += 4  # Bold Success gets preference
            template_scores[1] += 2  # Disciplined Achiever secondary
        elif high_energy_count >= 1:
            template_scores[3] += 2
            template_scores[1] += 1
        
        # Low energy -> Mindful Balance
        if low_energy_count >= 2:
            template_scores[4] += 5
        elif low_energy_count >= 1:
            template_scores[4] += 2
        
        # Visual style influences
        for style in visual_styles:
            if style in ['artistic', 'creative', 'expressive']:
                template_scores[2] += 3
            elif style in ['minimalist', 'natural', 'gentle']:
                template_scores[4] += 3
            elif style in ['bold', 'luxury', 'commanding']:
                template_scores[3] += 3
            else:  # balanced styles
                template_scores[1] += 1
        
        # Find the template with highest score
        recommended_template = max(template_scores, key=template_scores.get)
        template_name = self.template_mappings[recommended_template]["name"]
        
        print(f"✅ Template analysis for user {user_id}:")
        print(f"   Scores: {template_scores}")
        print(f"   Energy levels: High={high_energy_count}, Medium={medium_energy_count}, Low={low_energy_count}")
        print(f"   Visual styles: {visual_styles}")
        print(f"   Recommended: Template {recommended_template} - {template_name}")
        
        return recommended_template, template_name
    
    def start_intake_flow(self, user_id: str) -> str:
        """Start the vision board intake flow for a user"""
        try:
            # Clear any existing intake data
            self._clear_intake_data(user_id)
            
            # Set flow status
            intake_data = {
                "user_id": user_id,
                "status": "in_progress",
                "current_question": 1,
                "started_at": datetime.now().isoformat(),
                "answers": {},
                "completed_at": None
            }
            
            self._save_intake_data(user_id, intake_data)
            
            # Create engaging introduction
            intro = """🎨 **Let's create your perfect vision board!**

I'm so excited to dive deep with you and understand what makes your heart sing. This isn't just about pretty pictures — this is about capturing the essence of who you're becoming.

I have 10 thoughtful questions that will help me understand your dreams, values, and the energy you want to manifest. Each answer you give helps me create something truly personalized for YOU.

Ready? Let's start with something beautiful..."""

            question = self._format_question(1)
            return f"{intro}\n\n{question}"
            
        except Exception as e:
            print(f"Error starting intake flow: {e}")
            return "I'm sorry, I encountered an error starting the vision board intake. Please try again."
    
    def process_answer(self, user_id: str, answer: str) -> str:
        """Process a user's answer and move to next question or complete flow"""
        try:
            intake_data = self._load_intake_data(user_id)
            
            if not intake_data or intake_data.get("status") != "in_progress":
                return "It looks like you haven't started the vision board intake yet. Would you like to begin?"
            
            current_q = intake_data.get("current_question", 1)
            
            # Analyze and categorize the answer
            categorized_answer = self._analyze_answer(current_q, answer)
            
            # Save the answer
            intake_data["answers"][str(current_q)] = categorized_answer
            self._save_intake_data(user_id, intake_data)
            
            # Save to episodic memory for long-term retention
            self._save_to_memory(user_id, current_q, answer, categorized_answer)
            
            # Create encouraging response
            encouragement = self._get_encouraging_response(current_q, answer)
            
            # Move to next question or complete
            if current_q < 10:
                intake_data["current_question"] = current_q + 1
                self._save_intake_data(user_id, intake_data)
                next_question = self._format_question(current_q + 1)
                return f"{encouragement}\n\n{next_question}"
            else:
                # Complete the intake
                completion_message = self._complete_intake(user_id, intake_data)
                return f"{encouragement}\n\n{completion_message}"
                
        except Exception as e:
            print(f"Error processing answer: {e}")
            return "I encountered an error processing your answer. Please try again."
    
    def get_intake_status(self, user_id: str) -> Dict[str, Any]:
        """Get the current intake status for a user"""
        intake_data = self._load_intake_data(user_id)
        
        if not intake_data:
            return {"status": "not_started"}
        
        return {
            "status": intake_data.get("status"),
            "current_question": intake_data.get("current_question"),
            "total_questions": 10,
            "answers_count": len(intake_data.get("answers", {})),
            "started_at": intake_data.get("started_at"),
            "completed_at": intake_data.get("completed_at")
        }
    
    def is_intake_complete(self, user_id: str) -> bool:
        """Check if user has completed the intake flow"""
        intake_data = self._load_intake_data(user_id)
        return intake_data and intake_data.get("status") == "completed"
    
    def get_completed_answers(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get completed intake answers for vision board generation"""
        if not self.is_intake_complete(user_id):
            return None
        
        intake_data = self._load_intake_data(user_id)
        return intake_data.get("answers", {})
    
    def recommend_template(self, user_id: str) -> Tuple[int, str]:
        """Recommend a template based on completed intake answers with enhanced analysis"""
        intake_data = self.db_manager.get_vision_board_intake(user_id)
        if not intake_data or not intake_data.get('analyzed_responses'):
            return 1, "Disciplined Achiever"  # Default
        
        # Analyze the combined responses for template matching
        analyzed_responses = intake_data['analyzed_responses']
        
        # Template characteristics enhanced:
        # 1. Disciplined Achiever: Structure, goals, discipline, success, organization
        # 2. Creative Visionary: Creativity, innovation, artistic, imagination, expression
        # 3. Bold Success: Confidence, leadership, ambition, power, strength
        # 4. Mindful Balance: Peace, wellness, harmony, mindfulness, nature
        
        template_scores = {1: 0, 2: 0, 3: 0, 4: 0}
        
        # Enhanced keywords that indicate each template preference
        template_keywords = {
            1: ['structure', 'goal', 'discipline', 'organized', 'plan', 'system', 'achievement', 'focused', 'methodical', 'consistent', 'success', 'productive', 'efficient'],
            2: ['creative', 'artistic', 'imagination', 'innovation', 'expression', 'beauty', 'inspire', 'vision', 'unique', 'original', 'design', 'colorful', 'expressive'],
            3: ['bold', 'confident', 'leadership', 'success', 'power', 'ambitious', 'strong', 'fearless', 'commanding', 'influential', 'dynamic', 'assertive', 'winning'],
            4: ['peaceful', 'balance', 'mindful', 'harmony', 'wellness', 'calm', 'serene', 'natural', 'gentle', 'centered', 'tranquil', 'spiritual', 'grounded']
        }
        
        # Analyze all responses
        all_keywords = []
        energy_levels = []
        visual_styles = []
        
        for response in analyzed_responses:
            # Collect keywords from multiple sources
            all_keywords.extend(response.get('essence_keywords', []))
            all_keywords.extend(response.get('values_revealed', []))
            all_keywords.extend(response.get('aspirations', []))
            all_keywords.extend(response.get('personality_traits', []))
            all_keywords.extend(response.get('core_emotions', []))
            
            # Energy level influences template choice
            energy = response.get('energy_level', 'medium')
            energy_levels.append(energy)
            
            # Visual style preferences
            visual_style = response.get('visual_style_preference', 'natural')
            visual_styles.append(visual_style)
        
        # Convert to lowercase for matching
        all_keywords = [kw.lower().strip() for kw in all_keywords if kw]
        
        # Score templates based on keyword matches
        for template_num, keywords in template_keywords.items():
            for keyword in keywords:
                for user_keyword in all_keywords:
                    if keyword in user_keyword or user_keyword in keyword:
                        template_scores[template_num] += 1
        
        # Additional scoring based on energy and style patterns
        high_energy_count = energy_levels.count('high')
        medium_energy_count = energy_levels.count('medium') 
        low_energy_count = energy_levels.count('low')
        
        # High energy -> Bold Success or Disciplined Achiever
        if high_energy_count >= 3:
            template_scores[3] += 4  # Bold Success gets preference
            template_scores[1] += 2  # Disciplined Achiever secondary
        elif high_energy_count >= 1:
            template_scores[3] += 2
            template_scores[1] += 1
        
        # Low energy -> Mindful Balance
        if low_energy_count >= 2:
            template_scores[4] += 5
        elif low_energy_count >= 1:
            template_scores[4] += 2
        
        # Visual style influences
        for style in visual_styles:
            if style in ['artistic', 'creative', 'expressive']:
                template_scores[2] += 3
            elif style in ['minimalist', 'natural', 'gentle']:
                template_scores[4] += 3
            elif style in ['bold', 'luxury', 'commanding']:
                template_scores[3] += 3
            else:  # balanced styles
                template_scores[1] += 1
        
        # Find the template with highest score
        recommended_template = max(template_scores, key=template_scores.get)
        template_name = self.template_mappings[recommended_template]["name"]
        
        print(f"✅ Template analysis for user {user_id}:")
        print(f"   Scores: {template_scores}")
        print(f"   Energy levels: High={high_energy_count}, Medium={medium_energy_count}, Low={low_energy_count}")
        print(f"   Visual styles: {visual_styles}")
        print(f"   Recommended: Template {recommended_template} - {template_name}")
        
        return recommended_template, template_name
    
    def _format_question(self, question_num: int) -> str:
        """Format a question for display in an engaging way"""
        q_data = self.questions[question_num]
        
        progress = f"Question {question_num} of 10"
        question = q_data["question"]
        context = q_data["context"]
        
        # Add variety to question presentation
        if question_num <= 3:
            style = "🌟"
        elif question_num <= 6:
            style = "💫"
        elif question_num <= 8:
            style = "✨"
        else:
            style = "🔥"
        
        return f"""{style} **{progress}**

{question}

*{context}*

Take your time and share what feels true for you..."""
    
    def _analyze_answer(self, question_num: int, answer: str) -> Dict[str, Any]:
        """Analyze and categorize an answer using AI with comprehensive extraction for personalization"""
        try:
            q_data = self.questions[question_num]
            
            # Comprehensive analysis prompt for deep personalization
            prompt = f"""
            Perform a comprehensive analysis of this vision board intake response for highly personalized vision board creation:
            
            Question Theme: {q_data['theme']}
            Question Context: {q_data['context']}
            Question Asked: {q_data['question']}
            User's Response: "{answer}"
            
            Extract ALL elements that would help create a deeply personalized vision board:
            
            1. EMOTIONAL CORE: What emotions, feelings, and energy does this reveal?
            2. VISUAL SYMBOLS: What images, symbols, or metaphors would represent this?
            3. COLOR PSYCHOLOGY: What colors match the mood and energy expressed?
            4. LIFESTYLE ELEMENTS: What environments, spaces, or contexts are mentioned or implied?
            5. VALUES & PRIORITIES: What core values and life priorities are revealed?
            6. ASPIRATIONS & DREAMS: What specific goals, dreams, or aspirations are mentioned?
            7. PERSONALITY TRAITS: What personality characteristics come through?
            8. ESSENCE KEYWORDS: Key words that capture the essence of their response
            9. VISUAL STYLE: What aesthetic or visual style would resonate with them?
            10. SPECIFIC DETAILS: Any specific mentions of activities, places, people, objects, etc.
            
            Provide comprehensive analysis in JSON format:
            {{
                "answer": "{answer}",
                "theme": "{q_data['theme']}",
                "core_emotions": ["list 4-6 specific emotions expressed or implied"],
                "visual_metaphors": ["list 6-8 specific symbols/images that represent this"],
                "color_palette": ["list 4-6 colors that match the mood/energy"],
                "lifestyle_elements": ["list 4-6 specific environments/contexts mentioned or implied"],
                "values_revealed": ["list 3-5 core values shown through this response"],
                "aspirations": ["list 3-5 specific goals/dreams mentioned or implied"],
                "personality_traits": ["list 4-6 personality traits revealed"],
                "essence_keywords": ["list 8-10 keywords that capture the essence"],
                "specific_mentions": ["list any specific activities, places, objects, people mentioned"],
                "visual_style_preference": "minimalist/bold/artistic/natural/luxury/eclectic",
                "energy_level": "high/medium/low",
                "authenticity_score": "1-10 (how genuine and deep this response feels)",
                "manifestation_focus": ["what they're trying to manifest or attract"],
                "symbolic_elements": ["deeper symbols that represent their journey/growth"],
                "emotional_tone": "overall emotional tone of their response"
            }}
            
            Be specific and detailed. Extract everything that could personalize a vision board.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.4  # Balanced creativity for comprehensive analysis
            )
            
            analyzed_data = json.loads(response.choices[0].message.content)
            
            # Add metadata
            analyzed_data["analyzed_at"] = datetime.now().isoformat()
            analyzed_data["question_number"] = question_num
            analyzed_data["analysis_depth"] = "comprehensive"
            
            print(f"   🧠 Deep analysis complete: {len(analyzed_data.get('essence_keywords', []))} keywords, {len(analyzed_data.get('visual_metaphors', []))} symbols")
            
            return analyzed_data
            
        except Exception as e:
            print(f"❌ Error in comprehensive analysis: {e}")
            
            # Enhanced fallback analysis that still extracts useful info
            try:
                # Basic analysis using keywords and sentiment
                answer_lower = answer.lower()
                
                # Extract basic emotional indicators
                positive_emotions = ["happy", "excited", "confident", "peaceful", "grateful", "inspired", "motivated"]
                growth_emotions = ["determined", "focused", "ambitious", "hopeful", "driven"]
                
                detected_emotions = []
                for emotion in positive_emotions + growth_emotions:
                    if emotion in answer_lower:
                        detected_emotions.append(emotion)
                
                # Extract basic visual cues
                visual_words = ["beautiful", "bright", "clear", "strong", "flowing", "organized", "natural", "bold"]
                detected_visuals = [word for word in visual_words if word in answer_lower]
                
                # Basic color associations
                color_mapping = {
                    "peace": ["blue", "soft green", "white"],
                    "energy": ["orange", "red", "yellow"],
                    "growth": ["green", "earth tones"],
                    "confidence": ["bold colors", "black", "gold"],
                    "calm": ["pastels", "muted tones"]
                }
                
                suggested_colors = []
                for mood, colors in color_mapping.items():
                    if mood in answer_lower:
                        suggested_colors.extend(colors)
                
                return {
                    "answer": answer,
                    "theme": q_data["theme"],
                    "core_emotions": detected_emotions[:4] or ["hopeful", "motivated"],
                    "visual_metaphors": detected_visuals[:6] or ["growth", "journey", "strength"],
                    "color_palette": suggested_colors[:4] or ["inspiring blues", "warm earth tones"],
                    "lifestyle_elements": ["meaningful spaces", "growth environments"],
                    "values_revealed": ["authenticity", "growth", "purpose"],
                    "aspirations": ["personal development", "meaningful life"],
                    "personality_traits": ["thoughtful", "genuine", "growth-oriented"],
                    "essence_keywords": answer.split()[:8],  # First 8 words as keywords
                    "specific_mentions": [],
                    "visual_style_preference": "natural",
                    "energy_level": "medium",
                    "authenticity_score": "7",
                    "manifestation_focus": ["personal growth"],
                    "symbolic_elements": ["transformation", "journey"],
                    "emotional_tone": "hopeful and authentic",
                    "analyzed_at": datetime.now().isoformat(),
                    "question_number": question_num,
                    "analysis_depth": "basic_fallback"
                }
                
            except Exception as fallback_error:
                print(f"❌ Even fallback analysis failed: {fallback_error}")
                # Absolute minimal fallback
                return {
                    "answer": answer,
                    "theme": q_data["theme"],
                    "core_emotions": ["hopeful"],
                    "visual_metaphors": ["growth"],
                    "color_palette": ["inspiring"],
                    "lifestyle_elements": ["meaningful"],
                    "values_revealed": ["authenticity"],
                    "aspirations": ["growth"],
                    "personality_traits": ["genuine"],
                    "essence_keywords": ["authentic", "growth"],
                    "visual_style_preference": "natural",
                    "energy_level": "medium",
                    "authenticity_score": "5",
                    "analyzed_at": datetime.now().isoformat(),
                    "question_number": question_num
                }
    
    def _get_encouraging_response(self, question_num: int, answer: str) -> str:
        """Generate an encouraging, personalized response to keep user engaged"""
        
        encouragements = [
            "Beautiful! I can already feel the energy of your vision taking shape.",
            "Love this insight! Your authentic voice is coming through so clearly.",
            "This is gold! I'm getting such a clear picture of who you're becoming.",
            "Wow, this tells me so much about your beautiful soul.",
            "Perfect! This adds such depth to your vision board story.",
            "I'm loving how honest and real you're being with yourself.",
            "This is exactly the kind of insight that makes magic happen.",
            "Your self-awareness is incredible - this will make your board so powerful.",
            "Yes! This energy is exactly what we need to capture.",
            "This final piece is going to be the heart of your vision board! 🔥"
        ]
        
        # Select encouragement based on question number
        encouragement_index = min(question_num - 1, len(encouragements) - 1)
        base_encouragement = encouragements[encouragement_index]
        
        # Add specific acknowledgment for later questions
        if question_num >= 8:
            base_encouragement += " Your courage in sharing these deeper truths is inspiring."
        elif question_num >= 5:
            base_encouragement += " I can see your vision becoming more vivid with each answer."
        
        return base_encouragement
    
    def _save_to_memory(self, user_id: str, question_num: int, raw_answer: str, analyzed_data: Dict) -> None:
        """Save intake responses to episodic memory for authentic vision board personalization"""
        try:
            q_data = self.questions[question_num]
            
            print(f"💾 Saving vision board intake Q{question_num} to episodic memory...")
            
            # Store in episodic memory with full analysis data for personalization
            self.memory_manager.add_vision_board_intake_to_episodic_memory(
                user_id, question_num, q_data, raw_answer, analyzed_data
            )
            
            print(f"✅ Vision board intake Q{question_num} saved to episodic memory successfully!")
            
        except Exception as e:
            print(f"❌ Error saving to episodic memory: {e}")
            # Fallback to basic memory save
            try:
                basic_memory = f"Vision Board Q{question_num}: {q_data['question']}\nUser: {raw_answer}\nInsights: {', '.join(analyzed_data.get('essence_keywords', [])[:5])}"
                self.memory_manager.add_interaction(user_id, "vision_board_intake", basic_memory)
                print(f"✅ Fallback memory save successful for Q{question_num}")
            except:
                print(f"❌ All memory save methods failed for Q{question_num}")
                pass
    
    def _complete_intake(self, user_id: str, intake_data: Dict) -> str:
        """Complete the intake flow"""
        intake_data["status"] = "completed"
        intake_data["completed_at"] = datetime.now().isoformat()
        
        self._save_intake_data(user_id, intake_data)
        
        # Get template recommendation
        template_num, template_name = self.recommend_template(user_id)
        
        # Save to memory
        self.memory_manager.add_interaction(
            user_id,
            "completed vision board intake",
            f"Completed 10-question vision board intake. Recommended template: {template_name}"
        )
        
        return f"""🎉 **Intake Complete!** 

Thank you for sharing those beautiful insights! I've analyzed your responses and can see your unique vision taking shape.

✨ **Your Recommended Template:** {template_name}

Based on your answers, this template will perfectly capture your energy, aspirations, and the life you want to manifest.

🎨 **Ready to create your vision board?** Just say "Generate my vision board" and I'll create something magical just for you!

*Your vision board will be deeply personalized based on everything you've shared.* 🌟"""
    
    def _save_intake_data(self, user_id: str, data: Dict) -> None:
        """Save intake data to database"""
        try:
            # Use database to store intake data
            self.db_manager.save_vision_board_intake(user_id, data)
        except Exception as e:
            print(f"Error saving intake data: {e}")
    
    def _load_intake_data(self, user_id: str) -> Optional[Dict]:
        """Load intake data from database"""
        try:
            return self.db_manager.get_vision_board_intake(user_id)
        except Exception as e:
            print(f"Error loading intake data: {e}")
            return None
    
    def _clear_intake_data(self, user_id: str) -> None:
        """Clear existing intake data"""
        try:
            self.db_manager.clear_vision_board_intake(user_id)
        except Exception as e:
            print(f"Error clearing intake data: {e}")
    
    def get_intake_data_for_vision_board(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get processed intake data specifically formatted for vision board generation"""
        intake_data = self.db_manager.get_vision_board_intake(user_id)
        if not intake_data or not intake_data.get('answers'):
            return None
        
        # Get the analyzed responses from the answers
        analyzed_responses = list(intake_data['answers'].values())
        
        # Aggregate all the analyzed data into a comprehensive vision board context
        aggregated_data = {
            'user_goals': [],
            'visual_elements': [],
            'emotional_tone': [],
            'lifestyle_context': [],
            'color_preferences': [],
            'personal_values': [],
            'aspirations': [],
            'personality_traits': [],
            'energy_level': 'medium',
            'visual_style': 'natural',
            'authenticity_score': 8,
            'template_recommendation': self.recommend_template(user_id)[0]
        }
        
        # Combine insights from all responses
        for response in analyzed_responses:
            aggregated_data['user_goals'].extend(response.get('aspirations', []))
            aggregated_data['visual_elements'].extend(response.get('visual_metaphors', []))
            aggregated_data['emotional_tone'].extend(response.get('core_emotions', []))
            aggregated_data['lifestyle_context'].extend(response.get('lifestyle_elements', []))
            aggregated_data['color_preferences'].extend(response.get('color_palette', []))
            aggregated_data['personal_values'].extend(response.get('values_revealed', []))
            aggregated_data['aspirations'].extend(response.get('aspirations', []))
            aggregated_data['personality_traits'].extend(response.get('personality_traits', []))
        
        # Take the most recent energy level and visual style
        if analyzed_responses:
            latest_response = analyzed_responses[-1]
            aggregated_data['energy_level'] = latest_response.get('energy_level', 'medium')
            aggregated_data['visual_style'] = latest_response.get('visual_style_preference', 'natural')
            aggregated_data['authenticity_score'] = latest_response.get('authenticity_score', 8)
        
        # Remove duplicates and format for template
        for key in ['user_goals', 'visual_elements', 'emotional_tone', 'lifestyle_context', 
                   'color_preferences', 'personal_values', 'aspirations', 'personality_traits']:
            aggregated_data[key] = list(set(aggregated_data[key]))
        
        return aggregated_data
    
    def has_sufficient_data_for_vision_board(self, user_id: str) -> bool:
        """Check if user has enough data to generate a vision board without going through intake again"""
        try:
            intake_data = self.db_manager.get_vision_board_intake(user_id)
            
            if not intake_data:
                return False
            
            # Check if intake is completed
            if intake_data.get("status") == "completed":
                answers = intake_data.get("answers", {})
                
                # Minimum requirements for vision board generation
                min_required_answers = 7  # At least 7 out of 10 questions answered
                
                if len(answers) >= min_required_answers:
                    # Check if answers have meaningful analysis data
                    valid_answers = 0
                    for answer_data in answers.values():
                        if (answer_data.get("answer") and 
                            answer_data.get("core_emotions") and 
                            answer_data.get("visual_metaphors")):
                            valid_answers += 1
                    
                    if valid_answers >= min_required_answers:
                        print(f"✅ User {user_id} has sufficient data: {valid_answers} valid answers")
                        return True
            
            print(f"❌ User {user_id} does not have sufficient data for vision board")
            return False
            
        except Exception as e:
            print(f"Error checking vision board data sufficiency: {e}")
            return False
    
    def can_skip_intake(self, user_id: str) -> Tuple[bool, str]:
        """Check if user can skip intake and get explanation"""
        try:
            intake_data = self.db_manager.get_vision_board_intake(user_id)
            
            if self.has_sufficient_data_for_vision_board(user_id):
                template_num, template_name = self.recommend_template(user_id)
                last_updated = intake_data.get("completed_at", "recently")
                
                explanation = f"""✨ **Great news!** I already have your vision board profile from our previous conversation.

📊 **Your Profile Summary:**
- **Complete intake:** All questions answered
- **Recommended template:** {template_name}
- **Last updated:** {last_updated}

🎨 **Ready to create?** I can generate your personalized vision board right now, or if you'd like to update any of your preferences, just let me know what's changed in your life lately!

Would you like me to proceed with your vision board?"""
                
                return True, explanation
            
            elif intake_data and intake_data.get("answers"):
                answers_count = len(intake_data["answers"])
                explanation = f"""📝 **I have some of your vision board information** ({answers_count} responses), but I'd love to get a more complete picture.

Would you like to:
1. **Complete the remaining questions** (about {10 - answers_count} more)
2. **Start fresh** with an updated 10-question flow  
3. **Create with current data** (may be less personalized)

What feels right for you?"""
                
                return False, explanation
            
            else:
                explanation = """🎨 **Let's create your perfect vision board!**

To make sure it truly captures YOUR unique energy and dreams, I'd love to understand you better through a thoughtful 10-question conversation.

Ready to dive deep and create something magical? ✨"""
                
                return False, explanation
                
        except Exception as e:
            print(f"Error checking if can skip intake: {e}")
            return False, "Let's start with the vision board intake questions to create your perfect board!"
    
    def get_data_completeness_status(self, user_id: str) -> Dict[str, Any]:
        """Get detailed status of user's data completeness for vision board generation"""
        try:
            intake_data = self.db_manager.get_vision_board_intake(user_id)
            
            if not intake_data:
                return {
                    "has_intake": False,
                    "is_complete": False,
                    "total_answers": 0,
                    "valid_answers": 0,
                    "sufficient_for_vision_board": False,
                    "missing_themes": list(self.questions.keys()),
                    "last_updated": None,
                    "recommended_template": None
                }
            
            answers = intake_data.get("answers", {})
            total_answers = len(answers)
            valid_answers = 0
            answered_themes = []
            
            # Analyze answer quality
            for q_num, answer_data in answers.items():
                if (answer_data.get("answer") and 
                    answer_data.get("core_emotions") and 
                    answer_data.get("visual_metaphors")):
                    valid_answers += 1
                    answered_themes.append(int(q_num))
            
            missing_themes = [q for q in self.questions.keys() if q not in answered_themes]
            sufficient = self.has_sufficient_data_for_vision_board(user_id)
            
            recommended_template = None
            if sufficient:
                try:
                    template_num, template_name = self.recommend_template(user_id)
                    recommended_template = template_name
                except:
                    recommended_template = "Disciplined Achiever"
            
            return {
                "has_intake": True,
                "is_complete": intake_data.get("status") == "completed",
                "total_answers": total_answers,
                "valid_answers": valid_answers,
                "sufficient_for_vision_board": sufficient,
                "answered_themes": answered_themes,
                "missing_themes": missing_themes,
                "last_updated": intake_data.get("completed_at") or intake_data.get("started_at"),
                "recommended_template": recommended_template
            }
            
        except Exception as e:
            print(f"Error getting data completeness status: {e}")
            return {
                "has_intake": False,
                "is_complete": False,
                "total_answers": 0,
                "valid_answers": 0,
                "sufficient_for_vision_board": False,
                "missing_themes": list(self.questions.keys()),
                "last_updated": None,
                "recommended_template": None
            }

    def get_status(self, user_id: str) -> Dict[str, Any]:
        """Get current intake status and progress"""
        intake_data = self._load_intake_data(user_id)
        
        if not intake_data:
            return {
                "status": "not_started",
                "current_question": 0,
                "total_questions": len(self.questions),
                "answers_count": 0,
                "started_at": None,
                "completed_at": None
            }
        
        return {
            "status": intake_data.get("status", "not_started"),
            "current_question": intake_data.get("current_question", 0),
            "total_questions": len(self.questions),
            "answers_count": len(intake_data.get("answers", {})),
            "started_at": intake_data.get("started_at"),
            "completed_at": intake_data.get("completed_at")
        }
    
    def _create_personality_snapshot(self, user_id: str, current_question: int) -> None:
        """Create consolidated personality snapshot from questions answered so far"""
        try:
            intake_data = self.db_manager.get_vision_board_intake(user_id)
            if not intake_data or not intake_data.get('answers'):
                return
            
            answers = intake_data['answers']
            answered_questions = min(current_question, len(answers))
            
            # Aggregate insights from all answers so far
            all_emotions = []
            all_values = []
            all_aspirations = []
            all_traits = []
            all_keywords = []
            all_visual_metaphors = []
            
            for q_num in range(1, answered_questions + 1):
                answer_data = answers.get(str(q_num), {})
                all_emotions.extend(answer_data.get('core_emotions', []))
                all_values.extend(answer_data.get('values_revealed', []))
                all_aspirations.extend(answer_data.get('aspirations', []))
                all_traits.extend(answer_data.get('personality_traits', []))
                all_keywords.extend(answer_data.get('essence_keywords', []))
                all_visual_metaphors.extend(answer_data.get('visual_metaphors', []))
            
            # Create personality snapshot
            snapshot = f"""🧠 PERSONALITY SNAPSHOT - After {answered_questions}/10 Questions

🎯 CORE IDENTITY:
• Primary Emotions: {', '.join(list(set(all_emotions))[:5])}
• Core Values: {', '.join(list(set(all_values))[:5])}
• Key Aspirations: {', '.join(list(set(all_aspirations))[:5])}
• Personality Traits: {', '.join(list(set(all_traits))[:5])}

🎨 VISUAL ESSENCE:
• Symbolic Metaphors: {', '.join(list(set(all_visual_metaphors))[:5])}
• Essential Keywords: {', '.join(list(set(all_keywords))[:8])}

📊 PROGRESS: {answered_questions}/10 questions completed
🔄 This snapshot will guide the remaining questions and final vision board creation.

💡 EMERGING THEMES: The user is revealing a personality that values {', '.join(list(set(all_values))[:3])} and is drawn to {', '.join(list(set(all_visual_metaphors))[:3])} imagery."""

            # Save snapshot as high-importance memory
            self.memory_manager.save_recall_memory(
                user_id,
                snapshot,
                memory_type="personality_snapshot_comprehensive"
            )
            
            # Also save as conversation memory for context
            self.memory_manager.add_interaction(
                user_id,
                f"Personality Snapshot after {answered_questions} vision board questions",
                snapshot,
                metadata={
                    'interaction_type': 'personality_consolidation',
                    'importance': 0.95,
                    'snapshot_stage': f"after_q{answered_questions}",
                    'session_type': 'vision_board_discovery'
                }
            )
            
            print(f"✅ Created personality snapshot for user {user_id} after Q{answered_questions}")
            
        except Exception as e:
            print(f"Error creating personality snapshot: {e}")
    
    def get_user_memory_context(self, user_id: str) -> str:
        """Get relevant memory context for vision board conversations"""
        try:
            # Search for vision board related memories
            vision_memories = self.memory_manager.search_memories(
                user_id, 
                "vision board personality values aspirations emotions", 
                limit=8
            )
            
            if vision_memories:
                context = "🧠 **Your Vision Board Memory Context:**\n\n"
                for i, memory in enumerate(vision_memories, 1):
                    # Truncate long memories
                    short_memory = memory[:150] + "..." if len(memory) > 150 else memory
                    context += f"{i}. {short_memory}\n"
                
                context += "\n*This context helps me understand your journey and provide personalized guidance.*"
                return context
            
            return "Starting fresh with your vision board journey! 🎨"
            
        except Exception as e:
            print(f"Error getting memory context: {e}")
            return "Ready to explore your vision together! ✨"
    
    def load_conversation_continuity(self, user_id: str) -> Dict[str, Any]:
        """Load conversation continuity data for seamless session restoration"""
        try:
            # Get data completeness status
            status = self.get_data_completeness_status(user_id)
            
            # Load recent memory context
            memory_context = self.get_user_memory_context(user_id)
            
            # Get current intake status
            intake_status = self.get_intake_status(user_id)
            
            # Check if user can skip intake
            can_skip, skip_explanation = self.can_skip_intake(user_id)
            
            return {
                'data_status': status,
                'memory_context': memory_context,
                'intake_status': intake_status,
                'can_skip_intake': can_skip,
                'skip_explanation': skip_explanation,
                'session_continuity': True,
                'ready_for_generation': status['sufficient_for_vision_board']
            }
            
        except Exception as e:
            print(f"Error loading conversation continuity: {e}")
            return {
                'session_continuity': False,
                'error': str(e),
                'fallback_message': "Let's start your vision board journey! 🎨"
            }

    def update_user_insights_from_conversation(self, user_id: str, conversation_insights: Dict[str, Any]) -> None:
        """Update user's vision board profile based on ongoing conversation insights"""
        try:
            intake_data = self.db_manager.get_vision_board_intake(user_id)
            
            if not intake_data:
                # Create new intake data if none exists
                intake_data = {
                    "user_id": user_id,
                    "status": "in_progress",
                    "current_question": 1,
                    "started_at": datetime.now().isoformat(),
                    "answers": {},
                    "completed_at": None,
                    "conversation_insights": {}
                }
            
            # Update with new conversation insights
            if "conversation_insights" not in intake_data:
                intake_data["conversation_insights"] = {}
            
            intake_data["conversation_insights"].update(conversation_insights)
            intake_data["last_conversation_update"] = datetime.now().isoformat()
            
            # Save updated data
            self.db_manager.save_vision_board_intake(user_id, intake_data)
            
            # Also save to memory
            self.memory_manager.add_interaction(
                user_id,
                "vision_board_profile_update",
                f"Updated vision board profile with conversation insights: {json.dumps(conversation_insights)}"
            )
            
            print(f"✅ Updated vision board profile for user {user_id} with conversation insights")
            
        except Exception as e:
            print(f"Error updating user insights from conversation: {e}")
