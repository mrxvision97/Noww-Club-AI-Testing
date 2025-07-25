import os
import json
import threading
import time
from typing import Dict, Any, Optional, Tuple, List
from openai import OpenAI
from core.memory import MemoryManager
from core.database import DatabaseManager
from datetime import datetime
import base64
import requests
from io import BytesIO
from PIL import Image

class VisionBoardGenerator:
    def __init__(self, db_manager: DatabaseManager, memory_manager: MemoryManager):
        self.db_manager = db_manager
        self.memory_manager = memory_manager
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Import intake manager
        from core.vision_board_intake import VisionBoardIntakeManager
        self.intake_manager = VisionBoardIntakeManager(db_manager, memory_manager)
        
        # Vision template mappings - Updated to be gender neutral
        self.templates = {
            1: {
                "name": "Disciplined Achiever",
                "gender": "Gender-Neutral",
                "age_group": "18-35",
                "tone": "Discipline, focus, achievement, high performance, silent strength",
                "prompt_file": "VisionPrompt1_Enhanced.txt"
            },
            2: {
                "name": "Creative Visionary",
                "gender": "Gender-Neutral",
                "age_group": "25-40", 
                "tone": "Creative expression, leadership visioning, intentional design, artistic flow",
                "prompt_file": "VisionPrompt2_Enhanced.txt"
            },
            3: {
                "name": "Bold Success",
                "gender": "Gender-Neutral",
                "age_group": "18-30",
                "tone": "Confidence, business success, attraction mindset, luxury achievement",
                "prompt_file": "VisionPrompt3_Enhanced.txt"
            },
            4: {
                "name": "Mindful Balance",
                "gender": "Gender-Neutral", 
                "age_group": "20-35",
                "tone": "Wellness, mindfulness, intentional living, inner peace, authentic being",
                "prompt_file": "VisionPrompt4_Enhanced.txt"
            }
        }
        
        # Performance optimization
        self._template_cache = {}
        self._persona_cache = {}
    
    def analyze_user_for_template(self, user_id: str) -> int:
        """Analyze user profile and conversation history to select best template"""
        try:
            print(f"🔍 Analyzing user profile for {user_id}...")
            
            # Get user profile and memory context
            user_profile = self.memory_manager.get_user_memory(user_id)
            print(f"📊 Retrieved user profile with {len(user_profile)} fields")
            
            # Get episodic memories using the private method
            episodic_memories = self.memory_manager._load_episodic_memories(user_id)
            print(f"💭 Found {len(episodic_memories) if episodic_memories else 0} episodic memories")
            
            # Get conversation history for long-term insights
            try:
                conversations = self.db_manager.get_recent_conversations(user_id, limit=20)
                long_term_memories = [{"content": conv.get('content', '')} for conv in conversations]
                print(f"💬 Found {len(long_term_memories)} conversation memories")
            except:
                long_term_memories = []
                print("⚠️ No conversation history found")
            
            # Extract user preferences and characteristics
            analysis_data = {
                "preferences": user_profile.get('preferences', {}),
                "habits": user_profile.get('habits', []),
                "goals": user_profile.get('goals', []),
                "conversation_topics": user_profile.get('conversation_topics', []),
                "episodic_insights": [mem.get('content', '') for mem in episodic_memories] if episodic_memories else [],
                "long_term_insights": [mem.get('content', '') for mem in long_term_memories]
            }
            print(f"🔄 Prepared analysis data with {len(analysis_data)} categories")
            
            # Use AI to analyze and select template
            print("🤖 Sending data to AI for template selection...")
            analysis_prompt = f"""
            Based on the user profile data below, determine which vision board template (1-4) would be most suitable:

            Template Options:
            1. Masculine Discipline (Male, 18-35): Discipline, silent hustle, aesthetic masculinity, high performance
            2. Creative Professional (Female, 25-40): Creative professionals, lifestyle & leadership visioning, intentional design  
            3. Bold Luxury (Unisex, 18-30): Glow-up, business success, attraction mindset, bold luxury
            4. Mindful Wellness (Unisex, 20-35): Wellness, mindfulness, intentional living, inner peace

            User Data:
            {json.dumps(analysis_data, indent=2)}

            Return only the template number (1, 2, 3, or 4) that best matches this user's personality, goals, and interests.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.3,
                max_tokens=10
            )
            
            response_text = response.choices[0].message.content.strip()
            print(f"🎯 AI template selection response: {response_text}")
            
            # Extract just the number from the response
            import re
            numbers = re.findall(r'\b[1-4]\b', response_text)
            if numbers:
                template_num = int(numbers[0])
                selected_template = template_num if template_num in [1, 2, 3, 4] else 3
                print(f"✅ Template {selected_template} selected: {self.templates[selected_template]['name']}")
                return selected_template
            else:
                print("⚠️ No valid template number found, defaulting to template 3")
                return 3  # Default template
            
        except Exception as e:
            print(f"Error analyzing user for template: {e}")
            return 3  # Default template
    
    def extract_user_persona(self, user_id: str) -> Dict[str, Any]:
        """Extract comprehensive user persona from memory and profile"""
        try:
            # Get comprehensive user data
            user_profile = self.memory_manager.get_user_memory(user_id)
            
            # Get episodic memories using the private method
            episodic_memories = self.memory_manager._load_episodic_memories(user_id)
            
            # Get conversation history for long-term insights
            try:
                # Try to get recent conversations from database
                conversations = self.db_manager.get_recent_conversations(user_id, limit=50)
                long_term_memories = [{"content": conv.get('content', '')} for conv in conversations]
            except:
                # Fallback to empty list
                long_term_memories = []
            
            # Compile all data for persona extraction
            all_data = {
                "profile": user_profile,
                "recent_conversations": [mem.get('content', '') for mem in episodic_memories[-20:]] if episodic_memories else [],
                "important_memories": [mem.get('content', '') for mem in long_term_memories],
                "habits": user_profile.get('habits', []),
                "goals": user_profile.get('goals', [])
            }
            
            # Use AI to extract structured persona
            persona_prompt = f"""
            Based on the comprehensive user data below, extract a detailed persona in this exact JSON format:

            {{
                "name": "User's name if mentioned, or generate appropriate name",
                "age": "Estimated age or age range",
                "identity": "Core identity description (2-3 sentences)",
                "aspirations": [
                    "List of 5-8 key aspirations, goals, and dreams mentioned or inferred"
                ],
                "values": [
                    "List of 4-6 core values based on conversations and preferences"
                ],
                "interests": [
                    "List of hobbies, interests, and passion areas"
                ],
                "current_focus": "What they're currently working on or focused on",
                "lifestyle": "Lifestyle preferences and patterns",
                "personality_traits": [
                    "Key personality traits observed"
                ]
            }}

            User Data:
            {json.dumps(all_data, indent=2)}

            Return only the JSON object, no additional text.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": persona_prompt}],
                temperature=0.3,
                max_tokens=800
            )
            
            persona_text = response.choices[0].message.content.strip()
            # Extract JSON from response
            start_idx = persona_text.find('{')
            end_idx = persona_text.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                persona_json = persona_text[start_idx:end_idx]
                return json.loads(persona_json)
            else:
                raise ValueError("Could not extract JSON from response")
                
        except Exception as e:
            print(f"Error extracting user persona: {e}")
            # Return default persona
            return {
                "name": "User",
                "age": "25-30",
                "identity": "An ambitious individual focused on personal growth and achieving their dreams.",
                "aspirations": [
                    "Achieve personal growth and development",
                    "Build meaningful relationships",
                    "Create financial stability",
                    "Live a fulfilling and purposeful life"
                ],
                "values": ["Growth", "Authenticity", "Success", "Balance"],
                "interests": ["Personal development", "Learning", "Wellness"],
                "current_focus": "Working towards personal and professional goals",
                "lifestyle": "Balanced approach to work and personal life",
                "personality_traits": ["Ambitious", "Thoughtful", "Determined"]
            }
    
    def load_template_prompt(self, template_num: int) -> Optional[str]:
        """Load template prompt with caching for performance"""
        try:
            # Check cache first
            if template_num in self._template_cache:
                print(f"📋 Using cached template {template_num}")
                return self._template_cache[template_num]
            
            if template_num not in self.templates:
                print(f"❌ Template {template_num} not found")
                return None
            
            template_info = self.templates[template_num]
            prompt_file = template_info.get("prompt_file")
            
            if not prompt_file:
                print(f"❌ No prompt file specified for template {template_num}")
                return None
            
            # Load from file
            prompt_path = prompt_file
            if not os.path.exists(prompt_path):
                prompt_path = os.path.join(os.getcwd(), prompt_file)
            
            if not os.path.exists(prompt_path):
                print(f"❌ Prompt file not found: {prompt_file}")
                return None
            
            with open(prompt_path, 'r', encoding='utf-8') as file:
                prompt_content = file.read()
            
            # Cache the result
            self._template_cache[template_num] = prompt_content
            print(f"✅ Template {template_num} loaded and cached")
            
            return prompt_content
            
        except Exception as e:
            print(f"❌ Error loading template {template_num}: {e}")
            return None
        """Load the vision prompt template from file"""
        try:
            template_info = self.templates[template_num]
            prompt_file = template_info["prompt_file"]
            
            # Get the root directory (where the app.py is located)
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            prompt_path = os.path.join(root_dir, prompt_file)
            
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
                
        except Exception as e:
            print(f"Error loading template prompt: {e}")
            return ""
    
    def customize_prompt_with_persona(self, template_prompt: str, user_persona: Dict[str, Any]) -> str:
        """Customize the template prompt with user's persona data"""
        try:
            # Replace sample persona with actual user persona
            customized_prompt = template_prompt
            
            # Create user persona section
            persona_section = f"""
🧑‍💼 User Persona (Customized):
Name: {user_persona.get('name', 'User')}
Age: {user_persona.get('age', '25-30')}
Identity: {user_persona.get('identity', '')}
Current Focus: {user_persona.get('current_focus', '')}
Lifestyle: {user_persona.get('lifestyle', '')}

Core Values: {', '.join(user_persona.get('values', []))}
Key Interests: {', '.join(user_persona.get('interests', []))}
Personality Traits: {', '.join(user_persona.get('personality_traits', []))}

Aspirations for 2025:
"""
            
            # Add aspirations
            for aspiration in user_persona.get('aspirations', []):
                persona_section += f"- {aspiration}\n"
            
            # Replace the sample persona in the template
            # Look for persona sections and replace them
            lines = customized_prompt.split('\n')
            new_lines = []
            in_persona_section = False
            persona_replaced = False
            
            for line in lines:
                if ('Persona' in line and '🧑‍💼' in line) or ('Name:' in line and not persona_replaced):
                    if not persona_replaced:
                        new_lines.append(persona_section)
                        persona_replaced = True
                        in_persona_section = True
                    continue
                elif in_persona_section and line.strip() and not line.startswith(('🎯', '📝', '✨', 'Theme', 'Sections')):
                    continue  # Skip old persona content
                elif line.startswith(('🎯', '📝', '✨', 'Theme', 'Sections')) or persona_replaced:
                    in_persona_section = False
                    new_lines.append(line)
                else:
                    new_lines.append(line)
            
            customized_prompt = '\n'.join(new_lines)
            
            # If no persona section was found, prepend the persona
            if not persona_replaced:
                customized_prompt = persona_section + "\n\n" + customized_prompt
            
            return customized_prompt
            
        except Exception as e:
            print(f"Error customizing prompt: {e}")
            return template_prompt
    
    def generate_vision_board(self, user_id: str) -> Tuple[Optional[str], Optional[str]]:
        """Generate a vision board for the user - requires completed intake"""
        try:
            print(f"🎨 Starting vision board generation for user {user_id}")
            
            # Step 1: Check if intake is completed
            print("✅ Step 1: Checking vision board intake completion...")
            if not self.intake_manager.is_intake_complete(user_id):
                print("❌ Vision board intake not completed")
                return None, "intake_required"
            
            print("✅ Intake completed - proceeding with generation")
            
            # Step 2: Get intake answers and recommend template
            print("📊 Step 2: Getting intake answers and selecting template...")
            intake_answers = self.intake_manager.get_completed_answers(user_id)
            template_num, template_name = self.intake_manager.recommend_template(user_id)
            print(f"✅ Selected template {template_num}: {template_name}")
            
            # Step 3: Create persona from intake answers
            print("👤 Step 3: Creating persona from intake answers...")
            user_persona = self.extract_persona_from_intake(user_id, intake_answers)
            user_persona['user_id'] = user_id  # Add user_id for episodic memory access
            print(f"✅ Created persona for vision board generation")
            
            # Step 4: Load and customize template prompt
            print("📝 Step 4: Loading and customizing template prompt...")
            template_prompt = self.load_template_prompt(template_num)
            if not template_prompt:
                raise ValueError(f"Could not load template {template_num}")
            
            customized_prompt = self.customize_prompt_with_intake_data(template_prompt, user_persona, intake_answers)
            print(f"✅ Customized prompt ready (Length: {len(customized_prompt)} characters)")
            
            # Step 5: Generate image with GPT-Image-1
            print("🎨 Step 5: Generating image with GPT-Image-1...")
            print("⏳ This may take 10-30 seconds for high-quality image generation...")
            
            # Generate image using GPT-Image-1 with enhanced quality settings
            result = self._generate_gpt_image_1(customized_prompt)
            
            if not result:
                raise ValueError("Failed to generate image with GPT-Image-1")
            
            # Convert base64 image to URL for consistency with existing code
            image_url = self._save_base64_image_temporarily(result['image_data'])
            
            print(f"✅ GPT-Image-1 image generation completed successfully!")
            print(f"⚡ Generation time: {result.get('generation_time', 0):.2f} seconds")
            print(f"🎯 Quality: {result.get('quality', 'high')} | Size: {result.get('size', '1024x1024')}")
            if result.get('revised_prompt'):
                print(f"📝 Revised prompt used for better results")
            print(f"🖼️ Image saved temporarily for display")
            
            # Step 6: Save to memory (delayed to avoid triggering app restart)
            print("💾 Step 6: Scheduling memory save...")
            # Use threading to delay the save operation and avoid triggering Streamlit restart
            threading.Thread(
                target=self._delayed_save_vision_board_to_memory,
                args=(user_id, template_num, user_persona, image_url),
                daemon=True
            ).start()
            print("✅ Vision board save scheduled successfully!")
            
            print("🎉 VISION BOARD GENERATION COMPLETE!")
            print(f"📊 Final Result: Template '{self.templates[template_num]['name']}' for user {user_id}")
            
            return image_url, self.templates[template_num]['name']
            
        except Exception as e:
            print(f"❌ Error generating vision board: {e}")
            import traceback
            traceback.print_exc()
            return None, None
    
    def extract_persona_from_intake(self, user_id: str, intake_answers: Dict[str, Any]) -> Dict[str, Any]:
        """Extract comprehensive user persona from episodic memory intake data for authentic personalization"""
        try:
            print("🧠 Creating deep persona from episodic memory intake data...")
            
            # Get vision board intake memories from episodic memory
            episodic_intake_memories = self.memory_manager.get_vision_board_intake_memories(user_id)
            
            if not episodic_intake_memories:
                print("⚠️ No episodic intake memories found, using database fallback...")
                return self._extract_persona_from_database_fallback(user_id, intake_answers)
            
            print(f"📖 Found {len(episodic_intake_memories)} episodic intake memories")
            
            # Compile all authentic user responses and analysis
            all_raw_responses = []
            all_emotions = []
            all_visual_metaphors = []
            all_colors = []
            all_lifestyle_elements = []
            all_values = []
            all_aspirations = []
            all_traits = []
            all_keywords = []
            all_specific_mentions = []
            all_symbolic_elements = []
            energy_levels = []
            visual_styles = []
            authenticity_scores = []
            
            # Extract data from each episodic memory
            for memory in episodic_intake_memories:
                raw_response = memory.get('raw_user_response', '')
                all_raw_responses.append(raw_response)
                
                # Also extract from raw response for key themes
                response_lower = raw_response.lower()
                
                # Extract travel themes from raw text
                if any(travel_word in response_lower for travel_word in ['travel', 'country', 'countries', 'culture', 'explore', 'city', 'world', 'international', 'global']):
                    all_specific_mentions.append("travel and cultural exploration")
                
                # Extract mindfulness themes from raw text
                if any(mindful_word in response_lower for mindful_word in ['meditat', 'mindful', 'calm', 'peace', 'zen', 'tranquil', 'serene', 'balance', 'breath']):
                    all_specific_mentions.append("mindfulness and inner peace")
                
                # Extract tech themes from raw text
                if any(tech_word in response_lower for tech_word in ['tech', 'technolog', 'code', 'coding', 'ai', 'software', 'digital', 'innovation', 'startup']):
                    all_specific_mentions.append("technology and innovation")
                
                analysis = memory.get('vision_analysis', {})
                
                all_emotions.extend(analysis.get('core_emotions', []))
                all_visual_metaphors.extend(analysis.get('visual_metaphors', []))
                all_colors.extend(analysis.get('color_palette', []))
                all_lifestyle_elements.extend(analysis.get('lifestyle_elements', []))
                all_values.extend(analysis.get('values_revealed', []))
                all_aspirations.extend(analysis.get('aspirations', []))
                all_traits.extend(analysis.get('personality_traits', []))
                all_keywords.extend(analysis.get('essence_keywords', []))
                all_specific_mentions.extend(analysis.get('specific_mentions', []))
                all_symbolic_elements.extend(analysis.get('symbolic_elements', []))
                
                if analysis.get('energy_level'):
                    energy_levels.append(analysis['energy_level'])
                if analysis.get('visual_style_preference'):
                    visual_styles.append(analysis['visual_style_preference'])
                if analysis.get('authenticity_score'):
                    try:
                        score = int(str(analysis['authenticity_score']).replace('/10', ''))
                        authenticity_scores.append(score)
                    except:
                        authenticity_scores.append(8)
            
            # Create comprehensive authentic data summary
            authentic_user_story = "\n\n".join([
                f"Q{memory.get('question_number', i+1)} ({memory.get('question_theme', 'unknown')}): {memory.get('raw_user_response', '')}"
                for i, memory in enumerate(episodic_intake_memories)
            ])
            
            # Determine dominant patterns (not generic, but based on user's actual words)
            dominant_emotions = list(dict.fromkeys(all_emotions))[:6]
            key_visual_symbols = list(dict.fromkeys(all_visual_metaphors))[:8]
            color_mood = list(dict.fromkeys(all_colors))[:6]
            lifestyle_context = list(dict.fromkeys(all_lifestyle_elements))[:6]
            core_values = list(dict.fromkeys(all_values))[:5]
            life_aspirations = list(dict.fromkeys(all_aspirations))[:8]
            personality_essence = list(dict.fromkeys(all_traits))[:6]
            essence_words = list(dict.fromkeys(all_keywords))[:12]
            specific_mentions = list(dict.fromkeys(all_specific_mentions))[:10]
            symbolic_elements = list(dict.fromkeys(all_symbolic_elements))[:8]
            
            # Extract authentic themes organically from user's actual words
            combined_text = " ".join(all_raw_responses).lower()
            
            # Extract key themes organically without forcing specific categories
            # This captures whatever the user actually mentioned, not predetermined themes
            words = combined_text.split()
            important_phrases = []
            
            # Look for meaningful phrases and concepts in user's actual responses
            for memory in episodic_intake_memories:
                raw_response = memory.get('raw_user_response', '')
                analysis = memory.get('vision_analysis', {})
                
                # Extract user's specific mentions and manifestation focus
                user_specifics = analysis.get('specific_mentions', [])
                manifestation_items = analysis.get('manifestation_focus', [])
                
                # Add authentic user elements to aspirations and symbols
                for item in user_specifics + manifestation_items:
                    if item and len(item.strip()) > 2:
                        if item not in life_aspirations:
                            life_aspirations.append(item)
                        if item not in key_visual_symbols:
                            key_visual_symbols.append(item)
                
                # Extract authentic emotional and symbolic elements
                for emotion in analysis.get('core_emotions', []):
                    if emotion not in dominant_emotions:
                        dominant_emotions.append(emotion)
                
                for symbol in analysis.get('symbolic_elements', []):
                    if symbol not in symbolic_elements:
                        symbolic_elements.append(symbol)
            
            # Determine overall patterns
            dominant_energy = max(set(energy_levels), key=energy_levels.count) if energy_levels else "medium"
            preferred_style = max(set(visual_styles), key=visual_styles.count) if visual_styles else "natural"
            avg_authenticity = sum(authenticity_scores) / len(authenticity_scores) if authenticity_scores else 8
            
            # Create persona that captures the USER'S ACTUAL WORDS AND RESPONSES
            persona_prompt = f"""
            Based on these AUTHENTIC user responses from vision board intake, create a deeply personalized persona that captures their actual voice, dreams, and essence:
            
            COMPLETE USER STORY FROM INTAKE:
            {authentic_user_story}
            
            EXTRACTED AUTHENTIC PATTERNS:
            - Dominant emotions expressed: {', '.join(dominant_emotions)}
            - Visual symbols they mentioned: {', '.join(key_visual_symbols)}
            - Colors that resonate with them: {', '.join(color_mood)}
            - Lifestyle elements they value: {', '.join(lifestyle_context)}
            - Core values they revealed: {', '.join(core_values)}
            - Their specific aspirations: {', '.join(life_aspirations)}
            - Personality traits shown: {', '.join(personality_essence)}
            - Their essence keywords: {', '.join(essence_words)}
            - Specific things they mentioned: {', '.join(specific_mentions)}
            - Their symbolic elements: {', '.join(symbolic_elements)}
            - Energy level: {dominant_energy}
            - Visual style preference: {preferred_style}
            - Authenticity score: {avg_authenticity:.1f}/10
            
            Create a persona that AUTHENTICALLY represents this person based on their ACTUAL responses. 
            Use their specific words, emotions, and aspirations - don't make it generic.
            
            Return JSON format with comprehensive categorization:
            {{
                "name": "User",
                "age": "estimated from responses",
                "authentic_voice": "description using their actual tone and expressions",
                "core_identity": "who they really are based on their words",
                "dominant_emotions": {json.dumps(dominant_emotions[:4])},
                "life_aspirations": {json.dumps(life_aspirations[:6])},
                "visual_symbols": {json.dumps(key_visual_symbols[:6])},
                "color_palette": {json.dumps(color_mood[:4])},
                "lifestyle_desires": {json.dumps(lifestyle_context[:4])},
                "core_values": {json.dumps(core_values[:4])},
                "personality_traits": {json.dumps(personality_essence[:4])},
                "specific_mentions": {json.dumps(specific_mentions[:8])},
                "symbolic_elements": {json.dumps(symbolic_elements[:4])},
                "energy_vibe": "{dominant_energy}",
                "visual_style": "{preferred_style}",
                "authenticity_level": {avg_authenticity:.1f},
                "unique_essence": "what makes them uniquely them based on responses",
                "manifestation_focus": "what they specifically want to manifest",
                "authentic_themes": "main themes from their actual responses",
                "personal_story": "their unique story based on intake responses"
            }}
            
            IMPORTANT: Ensure travel themes go into 'life_aspirations' or 'visual_symbols' if mentioned.
            Ensure mindfulness themes go into 'dominant_emotions' or 'visual_symbols' if mentioned.
            Ensure tech themes go into 'life_aspirations' or 'visual_symbols' if mentioned.
            
            Make this persona deeply authentic to their actual responses, not generic vision board content.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": persona_prompt}],
                response_format={"type": "json_object"},
                temperature=0.2  # Low temperature for consistency with user's actual responses
            )
            
            persona = json.loads(response.choices[0].message.content)
            
            # Add metadata and preserve user_id
            persona["user_id"] = user_id  # Ensure user_id is preserved
            persona["created_from_episodic_memory"] = True
            persona["intake_responses_count"] = len(episodic_intake_memories)
            persona["creation_date"] = datetime.now().isoformat()
            
            print(f"✅ AUTHENTIC persona created from {len(episodic_intake_memories)} episodic memories")
            print(f"   🎭 Identity: {persona.get('core_identity', 'Authentic self')}")
            print(f"   � Aspirations: {len(persona.get('life_aspirations', []))} specific goals")
            print(f"   � Visual symbols: {len(persona.get('visual_symbols', []))} personal elements")
            print(f"   � Authenticity: {persona.get('authenticity_level', 8)}/10")
            print(f"   � Energy: {persona.get('energy_vibe', 'balanced')} | Style: {persona.get('visual_style', 'natural')}")
            
            return persona
            
        except Exception as e:
            print(f"❌ Error creating authentic persona from episodic memory: {e}")
            import traceback
            traceback.print_exc()
            return self._extract_persona_from_database_fallback(user_id, intake_answers)
    
    def _extract_persona_from_database_fallback(self, user_id: str, intake_answers: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback method when episodic memory is not available"""
        try:
            print("🔄 Using database fallback for persona creation...")
            
            # Get data from intake answers (database format)
            all_insights = {}
            raw_answers = []
            
            for q_num, answer_data in intake_answers.items():
                if isinstance(answer_data, dict):
                    raw_answers.append(answer_data.get("answer", ""))
                    
                    # Collect analysis data
                    for key, value in answer_data.items():
                        if key not in ["answer", "theme", "timestamp", "question_number", "analyzed_at"]:
                            if key not in all_insights:
                                all_insights[key] = []
                            if isinstance(value, list):
                                all_insights[key].extend([str(item) for item in value])
                            else:
                                all_insights[key].append(str(value))
            
            return {
                "name": "User",
                "age": "25-35",
                "authentic_voice": "Thoughtful individual sharing their genuine aspirations",
                "core_identity": "Someone on a meaningful journey of personal growth",
                "dominant_emotions": all_insights.get("core_emotions", ["hopeful", "determined"])[:4],
                "life_aspirations": all_insights.get("aspirations", ["personal development", "meaningful life"])[:6],
                "visual_symbols": all_insights.get("visual_metaphors", ["growth", "journey", "strength"])[:6],
                "color_palette": all_insights.get("color_palette", ["inspiring blues", "warm earth tones"])[:4],
                "lifestyle_desires": all_insights.get("lifestyle_elements", ["balanced living", "meaningful spaces"])[:4],
                "core_values": all_insights.get("values_revealed", ["authenticity", "growth", "purpose"])[:4],
                "personality_traits": all_insights.get("personality_traits", ["thoughtful", "genuine"])[:4],
                "energy_vibe": "balanced",
                "visual_style": "natural",
                "authenticity_level": 7.0,
                "user_id": user_id,  # Preserve user_id
                "created_from_episodic_memory": False,
                "fallback_used": True
            }
            
        except Exception as e:
            print(f"❌ Database fallback also failed: {e}")
            # Ultimate fallback
            return {
                "name": "User",
                "age": "25-35",
                "authentic_voice": "Authentic individual on a growth journey",
                "core_identity": "Someone seeking meaningful personal development",
                "dominant_emotions": ["hopeful", "determined"],
                "life_aspirations": ["personal growth", "meaningful life"],
                "visual_symbols": ["journey", "growth"],
                "color_palette": ["inspiring"],
                "lifestyle_desires": ["balanced"],
                "core_values": ["authenticity"],
                "personality_traits": ["genuine"],
                "energy_vibe": "balanced",
                "visual_style": "natural",
                "authenticity_level": 6.0,
                "ultimate_fallback": True
            }
    
    def create_enhanced_llm_prompt(self, persona: Dict, intake_answers: Dict[str, Any]) -> str:
        """NEW ENHANCED APPROACH: Create sophisticated vision board prompt using LLM analysis of user's intake responses"""
        try:
            print("🚀 Using ENHANCED LLM approach for vision board prompt generation...")
            
            # Step 1: Collect all user intake data
            user_id = persona.get('user_id', 'user')
            
            # Get episodic intake memories if available
            if hasattr(self, 'memory_manager'):
                episodic_intake_memories = self.memory_manager.get_vision_board_intake_memories(user_id)
                if episodic_intake_memories:
                    print(f"📖 Found {len(episodic_intake_memories)} episodic intake memories")
                    # Extract Q&A pairs from episodic memories
                    qa_pairs = []
                    for memory in episodic_intake_memories:
                        question_num = memory.get('question_number', 1)
                        raw_response = memory.get('raw_user_response', '')
                        # Get the actual question from our questions dict
                        if question_num in self.intake_manager.questions:
                            question_text = self.intake_manager.questions[question_num]['question']
                            qa_pairs.append(f"Q{question_num}: {question_text}\nA: {raw_response}")
                else:
                    print("⚠️ No episodic memories - extracting from intake answers")
                    qa_pairs = self._extract_qa_from_intake_answers(intake_answers)
            else:
                print("🔄 Extracting Q&A from intake answers directly...")
                qa_pairs = self._extract_qa_from_intake_answers(intake_answers)
            
            if not qa_pairs:
                print("⚠️ No Q&A data found - using fallback approach")
                return None
            
            # Step 2: Use LLM to create sophisticated prompt based on user's complete intake responses
            print("🧠 Using LLM to generate sophisticated vision board prompt...")
            
            comprehensive_user_data = "\n\n".join(qa_pairs)
            
            llm_prompt_generator = f"""You are a top creative director for modern lifestyle magazines like Vogue, Elle, and GQ. You specialize in creating stunning contemporary vision board collages that look like they belong in the latest issues of premium lifestyle publications.

Based on the user's personal intake responses below, create a MODERN, magazine-quality vision board prompt that will generate a trendy, aspirational visual representation of their authentic self and dreams.

USER'S PERSONAL RESPONSES:
{comprehensive_user_data}

CONTEMPORARY PERSONALITY PROFILE:
- Core Identity: {persona.get('core_identity', 'Modern visionary')}
- Current Vibes: {', '.join(persona.get('dominant_emotions', ['confident energy']))}
- Life Goals: {', '.join(persona.get('life_aspirations', ['authentic success']))}
- Visual Elements: {', '.join(persona.get('visual_symbols', ['upward momentum']))}
- Color Mood: {', '.join(persona.get('color_palette', ['contemporary neutrals']))}
- Values: {', '.join(persona.get('core_values', ['authenticity', 'growth']))}
- Energy Level: {persona.get('energy_vibe', 'dynamic flow')}
- Style Preference: {persona.get('visual_style', 'modern minimalism')}

🎨 MODERN MAGAZINE CREATIVE BRIEF:
Create a CONTEMPORARY vision board that feels fresh, current, and aspirational. This should be:

1. **TRENDY AESTHETICS**: Use current design trends - clean layouts, bold typography, contemporary photography that feels Instagram-ready and Pinterest-worthy

2. **LIFESTYLE STORYTELLING**: Each section tells their story in a modern, relatable way - think lifestyle blogger meets high-end magazine spread

3. **PERSONAL BRANDING**: Create visual elements that feel like their personal brand - authentic, current, and sophisticated without being pretentious

4. **CONTEMPORARY SYMBOLS**: Transform their responses into modern visual metaphors that feel relevant to today's culture and aesthetics

5. **SOCIAL MEDIA READY**: Design elements that would look amazing shared on Instagram or Pinterest - contemporary, aspirational, and personally meaningful

6. **MODERN TECHNIQUES**: Use current design approaches:
   - Clean, readable typography (think modern sans-serif fonts)
   - Handwritten elements for personal quotes and key phrases
   - Contemporary color palettes and gradients
   - Modern photography styles (natural light, lifestyle-focused)
   - Creative layout trends (asymmetrical but balanced, organic shapes)
   - Trendy textures and mixed media effects
   - Hand-lettered calligraphy for meaningful words

7. **ASPIRATIONAL LIFESTYLE**: Premium but accessible - the kind of vision board a lifestyle influencer would create

8. **AUTHENTIC CONTEMPORARY**: Every element should feel genuinely theirs while being visually current and appealing

CREATIVE EXECUTION FOR MODERN MAGAZINES:
- 8-10 dynamic organic shapes in contemporary composition (rounded rectangles, soft circles, flowing curves, creative polygons)
- Each shape represents a different aspect of their modern lifestyle
- Include 3-4 stylish text elements using THEIR actual words in trendy fonts AND handwritten script
- Integrate 2-3 contemporary human elements that feel relatable and aspirational
- Use modern design techniques (clean photography + stylish typography + handwritten elements + contemporary colors)
- Add handwritten quotes or affirmations in elegant script
- Color story that feels current and personally authentic
- Lighting that's natural and Instagram-worthy
- Creative layouts that break traditional grid patterns
- Details that make it share-worthy on social media

CONTEMPORARY TECHNICAL SPECS:
- Shot with modern digital photography for crisp, contemporary feel
- Professional but accessible styling (not overly formal)
- Typography that's trendy and highly readable PLUS handwritten elements
- Hand-lettered quotes and affirmations using elegant script
- Creative layouts that break traditional boundaries
- Lighting that feels natural and current
- Composition following modern design principles with creative freedom
- Mixed media approach combining photography, typography, and handwriting
- Each element positioned for maximum visual impact and creativity

This isn't just a vision board - it's a MODERN LIFESTYLE MANIFESTO that captures who they're becoming in today's world. Make them think "This is exactly my vibe and my future."

Create the contemporary magazine prompt now:"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # Using the most advanced model
                messages=[{"role": "user", "content": llm_prompt_generator}],
                temperature=0.7,  # Higher creativity for artistic innovation
                max_tokens=2000  # Increased for more detailed prompts
            )
            
            sophisticated_prompt = response.choices[0].message.content.strip()
            
            # CREATIVE ENHANCEMENT PASS: Add final personalization layer
            print("🎭 Adding final creative enhancement pass...")
            try:
                enhancement_prompt = f"""You are reviewing a vision board prompt for final artistic refinement. The user's most powerful quotes were:

KEY USER EXPRESSIONS:
{', '.join([qa.split('A: ')[1] for qa in qa_pairs[:3] if 'A: ' in qa])}

CURRENT PROMPT TO ENHANCE:
{sophisticated_prompt[:800]}...

Add ONE final creative enhancement that makes this vision board uniquely theirs:
1. Suggest one specific artistic technique (hand-lettering style, photography filter, texture overlay)
2. Propose one meaningful symbolic element from their responses
3. Recommend one sophisticated color treatment or lighting mood
4. Keep the enhancement to 100-150 words maximum

Enhancement:"""

                enhancement_response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",  # Faster model for quick enhancement
                    messages=[{"role": "user", "content": enhancement_prompt}],
                    temperature=0.8,  # Higher creativity for final touches
                    max_tokens=200
                )
                
                creative_enhancement = enhancement_response.choices[0].message.content.strip()
                sophisticated_prompt = f"{sophisticated_prompt}\n\n🎨 FINAL CREATIVE TOUCH:\n{creative_enhancement}"
                
            except Exception as e:
                print(f"⚠️ Creative enhancement failed, using base prompt: {e}")
            
            # Add advanced technical and artistic requirements for museum-quality output
            enhanced_prompt = f"""{sophisticated_prompt}

�️ MUSEUM-QUALITY TECHNICAL SPECIFICATIONS:

CANVAS & COMPOSITION:
- Dimensions: Exactly 1024x1024 pixels with 40px elegant margins
- Layout: Sophisticated organic composition using flowing, dynamic shapes with intentional white space for visual breathing room
- Visual flow: Elements should guide the eye in a deliberate journey across the board
- Shapes: Use creative organic forms - circles, ovals, hexagons, flowing curves, asymmetrical polygons
- NO rectangular boxes - embrace dynamic shapes that enhance the visual narrative

PHOTOGRAPHY EXCELLENCE:
- Equipment: Shot on Hasselblad or Phase One medium format for ultimate image quality
- Lighting: Natural golden hour mixed with studio strobes for dimensional depth
- Color grading: Professional film-look color correction with subtle grain texture
- Focus: Selective depth of field to create visual hierarchy and emotional focal points

ARTISTIC INTEGRATION:
- Mixed media: Seamlessly blend photography, watercolor textures, and digital illustration
- Handwriting: Include 2-3 elegant calligraphy elements using user's actual words
- Typography: Custom lettering that feels hand-crafted by a master artist
- Textures: Paper grain, fabric weaves, metallic accents, organic imperfections

HUMAN ELEMENTS:
- Include 2-4 carefully chosen human figures that feel meaningful to user's story
- Diverse representation of mentors, collaborators, audience, or inspiring figures
- Emotional authenticity in expressions and body language
- Lighting on people should feel cinematic and intentional

COLOR MASTERY:
- Sophisticated palette derived from user's responses and personality
- Color psychology that supports their emotional journey
- Gradient transitions that feel organic and purposeful
- Metallic accents (gold, copper, silver) used sparingly for emphasis

PREMIUM DETAILS:
- Every text element must be perfectly legible and grammatically flawless
- Shadows and highlights that create realistic depth and dimension
- Organic edges and torn paper effects for authenticity
- Hidden symbolic details that reward close examination
- Professional retouching standards throughout

ARTISTIC COHESION:
- All elements must feel curated by someone who deeply understands the user
- Visual narrative that tells their complete story across all sections
- Consistent artistic voice while varying techniques for visual interest
- Balance between aspiration and authenticity

FINAL VALIDATION:
- Could this hang in a contemporary art gallery? 
- Would the user frame this as a cherished art piece?
- Does every element serve their authentic story?
- Is this worthy of a luxury lifestyle magazine cover?

Create a personal masterpiece that captures their soul."""
            
            print("✅ MODERN MAGAZINE-QUALITY LLM-generated prompt created!")
            print(f"   📏 Prompt length: {len(enhanced_prompt)} characters")
            print(f"   🎨 Contemporary magazine design for: {persona.get('core_identity', 'user')}")
            print(f"   🌟 Based on {len(qa_pairs)} authentic intake responses")
            print(f"   📱 Modern lifestyle magazine specifications included")
            print(f"   ⚡ Advanced GPT-4o + contemporary enhancement system")
            print(f"   � Instagram-worthy artistic direction applied")
            
            return enhanced_prompt
            
        except Exception as e:
            print(f"❌ Error creating sophisticated LLM prompt: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_qa_from_intake_answers(self, intake_answers: Dict[str, Any]) -> List[str]:
        """Extract Q&A pairs from intake answers database format"""
        qa_pairs = []
        try:
            for q_num, answer_data in intake_answers.items():
                if isinstance(answer_data, dict) and 'answer' in answer_data:
                    # Get the question from our questions dict
                    question_num = int(q_num) if str(q_num).isdigit() else 1
                    if question_num in self.intake_manager.questions:
                        question_text = self.intake_manager.questions[question_num]['question']
                        user_answer = answer_data['answer']
                        qa_pairs.append(f"Q{question_num}: {question_text}\nA: {user_answer}")
        except Exception as e:
            print(f"⚠️ Error extracting Q&A pairs: {e}")
        
        return qa_pairs

    def customize_prompt_with_intake_data(self, template_prompt: str, persona: Dict, intake_answers: Dict[str, Any]) -> str:
        """Create personalized vision board prompt - NOW USING ENHANCED LLM APPROACH"""
        try:
            print("🎨 Creating personalized vision board prompt with ENHANCED approach...")
            
            # Try the enhanced LLM approach first
            enhanced_prompt = self.create_enhanced_llm_prompt(persona, intake_answers)
            
            if enhanced_prompt:
                print("✅ Using ENHANCED LLM-generated prompt")
                return enhanced_prompt
            else:
                print("⚠️ Enhanced approach failed, falling back to original method...")
            
            # FALLBACK: Original method
            
            # Use intake_answers directly if memory_manager not available
            if hasattr(self, 'memory_manager'):
                # Get detailed episodic memory data
                episodic_intake_memories = self.memory_manager.get_vision_board_intake_memories(persona.get('user_id', 'user'))
                
                if not episodic_intake_memories:
                    print("⚠️ No episodic memories - using intake answers")
                    # Use intake_answers for authentic responses
                    authentic_responses = intake_answers.get('responses', [])
                else:
                    # Extract from episodic memories
                    authentic_responses = []
                    for memory in episodic_intake_memories:
                        raw_response = memory.get('raw_user_response', '')
                        authentic_responses.append(raw_response)
            else:
                print("� Using intake answers directly...")
                authentic_responses = intake_answers.get('responses', [])
            
            if not authentic_responses:
                print("⚠️ No authentic responses - using persona fallback")
                return self._customize_prompt_with_persona_fallback(template_prompt, persona)
            
            # Extract authentic user data from responses and persona
            user_emotions = persona.get('emotions', ['clarity', 'confidence', 'innovation'])
            user_visual_symbols = persona.get('visual_symbols', ['mountain peak', 'compass', 'ascending stairs'])
            user_colors = persona.get('colors', ['deep charcoal', 'warm gold', 'sophisticated white'])
            user_lifestyle = persona.get('lifestyle', ['premium experiences', 'cutting-edge technology'])
            user_values = persona.get('values', ['authenticity', 'excellence', 'innovation'])
            user_aspirations = persona.get('aspirations', ['revolutionary innovation', 'global recognition'])
            user_specific_mentions = persona.get('specific_mentions', ['AI breakthrough', 'emotional intelligence'])
            
            print(f"📖 Processing {len(authentic_responses)} authentic responses...")
            print(f"🎨 User colors: {user_colors}")
            print(f"🌟 User aspirations: {user_aspirations}")
            print(f"💫 User emotions: {user_emotions}")
            
            # CREATE THE MAGAZINE-STYLE COLLAGE PROMPT
            # This completely replaces any template prompt with sophisticated magazine-quality instructions
            
            print(f"✅ Extracted authentic data:")
            print(f"   💫 Emotions: {user_emotions[:3]}")
            print(f"   🎨 Colors: {user_colors[:3]}")
            print(f"   🌟 Aspirations: {user_aspirations[:3]}")
            print(f"   🏠 Lifestyle: {user_lifestyle[:3]}")
            
            # Create completely personalized prompt that BREAKS AWAY from generic templates
            completely_authentic_prompt = f"""🎨 CREATE A PREMIUM MAGAZINE-STYLE VISION BOARD COLLAGE

CRITICAL: Create a sophisticated collage exactly like the reference template - multiple rectangular image sections with elegant typography overlays, cohesive color palette, and premium magazine aesthetic.

📖 USER'S AUTHENTIC VISION (FROM INTAKE RESPONSES):
{chr(10).join(authentic_responses)}

🎯 EXACT LAYOUT STRUCTURE - MAGAZINE COLLAGE STYLE:

**TECHNICAL SPECIFICATIONS:**
- Canvas: Perfect 1024x1024 square
- Margins: 50px padding on all sides  
- Style: Premium lifestyle magazine collage
- Quality: Ultra-sharp, DSLR photography
- Layout: 6-8 dynamic organic shapes in flowing composition (circles, ovals, hexagons, curved forms)

**COLOR PALETTE (USER'S AUTHENTIC COLORS):**
Primary Colors: {', '.join(user_colors[:3]) if user_colors else 'warm earth tones, soft whites, deep charcoal'}
Accent Colors: {', '.join(user_colors[3:6]) if len(user_colors) > 3 else 'gold highlights, rich blacks'}
Background: Sophisticated neutral tones that complement user's palette
Typography: Elegant serif for main text, clean sans-serif for quotes

**CREATIVE LAYOUT SECTIONS:**

**TOP LEFT ORGANIC SHAPE (25% of layout):**
- Content: Main user identity symbol - {user_visual_symbols[0] if user_visual_symbols else 'mountain peak'}
- Background: {user_colors[0] if user_colors else 'deep charcoal'} with subtle texture
- Text Overlay: "{user_emotions[0].title() if user_emotions else 'Clarity'}" in elegant serif font
- Handwritten Element: Personal affirmation in flowing script
- Style: Moody, professional photography with creative shape border

**TOP RIGHT CURVED SECTION (20% of layout):**
- Content: Lifestyle scene representing - {user_lifestyle[0] if user_lifestyle else 'focused workspace'}
- Include elements: {', '.join(user_specific_mentions[:2]) if user_specific_mentions else 'modern technology, clean aesthetics'}
- Text: "{self._extract_short_quote(authentic_responses, 0)}"
- Handwritten Quote: User's actual words in elegant handwriting
- Style: Natural lighting, aspirational with soft rounded edges

**MIDDLE LEFT HEXAGON (20% of layout):**
- Content: Symbol for user's core value - {user_values[0] if user_values else 'growth'}
- Visual: {user_visual_symbols[1] if len(user_visual_symbols) > 1 else 'compass'} in minimalist style
- Text: "2025" or relevant year in bold numerals
- Handwritten Touch: Personal date or milestone in script
- Background: Clean, minimal with geometric shape

**MIDDLE RIGHT CIRCLE (15% of layout):**
- Content: User's aspiration visualization - {user_aspirations[0] if user_aspirations else 'achievement symbol'}
- Include: Professional setting that reflects user's goals
- Text: "{self._extract_short_quote(authentic_responses, 1)}"
- Handwritten Dream: Key aspiration in beautiful calligraphy
- Style: Premium, sophisticated in circular frame

**BOTTOM LEFT FLOWING SHAPE (20% of layout):**
- Content: Growth metaphor - {user_visual_symbols[2] if len(user_visual_symbols) > 2 else 'ascending stairs'}
- Represents: User's journey toward {user_aspirations[1] if len(user_aspirations) > 1 else 'their vision'}
- Text: "{user_emotions[1].title() if len(user_emotions) > 1 else 'Focused'}" 
- Handwritten Mantra: Personal power phrase in script
- Style: Symbolic, powerful with organic flowing border

**FLOATING ELEMENTS & CREATIVE ACCENTS:**
- Handwritten typography: "{self._extract_short_quote(authentic_responses, 2)}" in elegant script
- Accent symbols: {', '.join(user_visual_symbols[3:5]) if len(user_visual_symbols) > 3 else 'minimalist icons'}
- Color highlights: {user_colors[1] if len(user_colors) > 1 else 'warm gold'} accents throughout
- Hand-drawn elements: Small doodles, arrows, or decorative flourishes

**CENTRAL UNIFYING ELEMENT:**
- Large handwritten overlay: "{user_values[0].title() if user_values else 'Authentic Success'}" in beautiful calligraphy
- Or user's main aspiration: "{user_aspirations[0] if user_aspirations else 'Revolutionary Vision'}" in script
- Style: Bold, confident handwriting as the focal point

🎨 PREMIUM EXECUTION REQUIREMENTS:

**PHOTOGRAPHY STANDARDS:**
- Use ONLY authentic DSLR-quality photography
- Natural lighting with professional color grading
- Every image should look magazine-ready
- NO AI-generated faces or obvious CGI
- Crisp focus, proper depth of field

**TYPOGRAPHY & HANDWRITING EXCELLENCE:**
- All text perfectly spelled and grammatically correct
- Elegant serif fonts for main statements
- Clean sans-serif for accent text
- Beautiful handwritten elements for personal quotes and affirmations
- Hand-lettered calligraphy for key phrases and mantras
- Perfect contrast against backgrounds
- All text fully readable and well-positioned
- Mix of modern typography and elegant handwriting
- Handwritten elements should feel authentic and personal

**COLOR HARMONY:**
- Sophisticated palette based on user's authentic colors: {', '.join(user_colors)}
- Rich, saturated colors that feel expensive
- Intentional color flow between sections
- Gold/warm accents for premium feel

**CREATIVE LAYOUT PRECISION:**
- Every element FULLY visible within 1024x1024 canvas
- 50px margins maintained on all sides
- No cropping of text, images, or handwriting at edges
- Perfect spacing and visual hierarchy
- Creative flow between all sections using organic shapes
- Handwritten elements integrated seamlessly
- Mixed layout styles (geometric and organic shapes)
- Cohesive composition despite creative freedom

**CONTENT AUTHENTICITY:**
- Every element reflects user's actual responses
- Symbols represent their specific mentions: {', '.join(user_specific_mentions[:3])}
- Colors match their authentic palette: {', '.join(user_colors[:3])}
- Text quotes derived from their actual words
- Lifestyle elements reflect their real preferences: {', '.join(user_lifestyle[:3])}

🔥 USER'S AUTHENTIC ENERGY TO CAPTURE:
Based on their responses, this person embodies: {', '.join(user_emotions[:3]) if user_emotions else 'clarity, ambition, innovation'}
Their core values: {', '.join(user_values[:3]) if user_values else 'growth, authenticity, impact'}
Their aspirations: {', '.join(user_aspirations[:3]) if user_aspirations else 'revolutionary achievement, global recognition'}

The final vision board must feel like a premium lifestyle magazine spread that tells THEIR unique story through sophisticated visual design and authentic personal elements.

FINAL QUALITY CHECK:
✓ Magazine-quality photography throughout
✓ All text perfectly readable and spelled correctly  
✓ User's authentic colors, symbols, and aspirations featured
✓ Premium typography hierarchy maintained
✓ Perfect 1024x1024 canvas with proper margins
✓ Cohesive, sophisticated aesthetic
✓ NO generic stock photo elements
✓ Every section tells part of user's authentic story"""

            print("✅ COMPLETELY AUTHENTIC prompt created!")
            print(f"   � Using user's colors: {user_colors[:3]}")
            print(f"   � Reflecting user's symbols: {user_visual_symbols[:3]}")
            print(f"   💫 Showing user's aspirations: {user_aspirations[:3]}")
            print(f"   🔥 Breaking away from generic black/gold aesthetic!")
            
            return completely_authentic_prompt
            
        except Exception as e:
            print(f"❌ Error creating authentic prompt: {e}")
            import traceback
            traceback.print_exc()
            return self._customize_prompt_with_persona_fallback(template_prompt, persona)
    
    def _customize_prompt_with_persona_fallback(self, template_prompt: str, persona: Dict) -> str:
        """Fallback prompt customization when episodic memory is not available"""
        try:
            print("🔄 Using persona fallback for prompt customization...")
            
            # Extract available persona data
            user_colors = persona.get('color_palette', ['inspiring blues', 'warm earth tones'])
            user_symbols = persona.get('visual_symbols', ['growth', 'journey'])
            user_aspirations = persona.get('life_aspirations', ['personal development'])
            user_emotions = persona.get('dominant_emotions', ['hopeful'])
            
            fallback_prompt = f"""
Create a personalized vision board based on this user's persona:

**User's Authentic Profile:**
- Core identity: {persona.get('core_identity', 'authentic individual')}
- Energy vibe: {persona.get('energy_vibe', 'balanced')}
- Visual style: {persona.get('visual_style', 'natural')}

**Personalization Elements:**
- Colors: {', '.join(user_colors)}
- Symbols: {', '.join(user_symbols)}
- Aspirations: {', '.join(user_aspirations)}
- Emotions: {', '.join(user_emotions)}

**Visual Requirements:**
- Use the user's preferred colors: {', '.join(user_colors)}
- Include personal symbols: {', '.join(user_symbols)}
- Reflect their aspirations: {', '.join(user_aspirations)}
- Capture their energy: {persona.get('energy_vibe', 'balanced')}

Create a vision board that authentically represents this person's unique journey and dreams.
Complete 1024x1024 layout with all elements fully visible.
"""
            
            return fallback_prompt
            
        except Exception as e:
            print(f"❌ Fallback prompt customization failed: {e}")
            return template_prompt
    
    def _create_intelligent_template_mappings(self, emotions, symbols, colors, lifestyle, values, aspirations, traits, energy, style):
        """Intelligently map user persona data to template-specific elements"""
        try:
            # Map emotions to template-appropriate primary focus
            primary_emotion_map = {
                "peaceful": "SERENITY", "confident": "DISCIPLINE", "determined": "FOCUS",
                "inspired": "VISION", "motivated": "DRIVE", "creative": "INNOVATION",
                "spiritual": "MINDFULNESS", "ambitious": "ACHIEVEMENT", "focused": "PRECISION"
            }
            
            primary_emotion = next((primary_emotion_map.get(emotion, emotion.upper()) 
                                  for emotion in emotions if emotion in primary_emotion_map), 
                                 emotions[0].upper() if emotions else "DISCIPLINE")
            
            # Map aspirations to achievement symbols
            achievement_symbol_map = {
                "business": "luxury car, modern office, success symbols",
                "entrepreneur": "premium workspace, growth charts, success indicators", 
                "travel": "private jet, elegant luggage, world destinations",
                "wellness": "spa elements, healthy lifestyle, balance symbols",
                "spiritual": "meditation spaces, sacred symbols, mindful elements",
                "creative": "artistic tools, inspiration boards, creative spaces",
                "financial": "premium assets, wealth symbols, abundance indicators"
            }
            
            achievement_symbols = []
            for aspiration in aspirations:
                for key, symbols_list in achievement_symbol_map.items():
                    if key in aspiration.lower():
                        achievement_symbols.append(symbols_list)
                        break
            
            # Create intelligent descriptions
            mappings = {
                "aesthetic_description": f"{style} aesthetic with {', '.join(colors[:2])} tones reflecting {energy} energy",
                "energy_description": f"{energy} energy expressing {', '.join(emotions[:2])} qualities",
                "key_symbols": ', '.join(symbols[:5]),
                "primary_emotion": primary_emotion,
                "color_description": f"{', '.join(colors[:3])} palette matching {emotions[0] if emotions else 'balanced'} mood",
                "lifestyle_description": ', '.join(lifestyle[:3]),
                "symbol_list": ', '.join(symbols[:4]),
                "values_for_template": ', '.join(values[:3]),
                "aspirations_for_template": ', '.join(aspirations[:3]),
                "achievement_symbols": '; '.join(achievement_symbols[:2]) if achievement_symbols else "premium lifestyle elements"
            }
            
            return mappings
            
        except Exception as e:
            print(f"Error creating template mappings: {e}")
            # Fallback mappings
            return {
                "aesthetic_description": f"{style} style with inspiring colors",
                "energy_description": f"{energy} energy",
                "key_symbols": ', '.join(symbols[:3]) if symbols else "growth, success, balance",
                "primary_emotion": emotions[0].upper() if emotions else "FOCUS",
                "color_description": ', '.join(colors[:3]) if colors else "sophisticated earth tones",
                "lifestyle_description": ', '.join(lifestyle[:3]) if lifestyle else "balanced, intentional living",
                "symbol_list": ', '.join(symbols[:4]) if symbols else "meaningful symbols",
                "values_for_template": ', '.join(values[:3]) if values else "growth, authenticity, purpose",
                "aspirations_for_template": ', '.join(aspirations[:3]) if aspirations else "success, fulfillment, growth",
                "achievement_symbols": "premium lifestyle elements reflecting personal success"
            }
    
    def _generate_gpt_image_1(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Generate image using GPT-Image-1 model with enhanced quality and complete layout
        
        Args:
            prompt (str): Text description of the image to generate
            
        Returns:
            Dict containing image data and metadata, or None if generation fails
        """
        try:
            start_time = time.time()
            
            # Enhance prompt to ensure complete vision board layout
            enhanced_prompt = f"""
CRITICAL TECHNICAL REQUIREMENTS:
- Create a COMPLETE vision board with NO text or images cut off at edges
- Ensure ALL elements are FULLY VISIBLE within the 1024x1024 square canvas
- Leave adequate margin/padding around all edges (at least 50 pixels)
- Design should be PERFECTLY CENTERED and BALANCED
- NO text should be partially cut or cropped at top, bottom, left, or right
- ALL images and graphics should be completely within the visible area
- Create a cohesive, well-organized collage layout that fits entirely within bounds

PREMIUM VISUAL QUALITY REQUIREMENTS:
- Use ONLY authentic, DSLR-quality photography (no AI-generated faces or obvious CGI)
- Images should look professionally shot with natural lighting and realistic depth of field
- Avoid overlapping human faces or distorted facial features
- Use high-resolution, crisp imagery with excellent composition
- Employ sophisticated color grading and professional photo editing aesthetics
- Create magazine-quality layouts with premium typography and spacing
- Ensure natural skin tones and realistic human expressions when people are included
- Use authentic lifestyle photography that looks genuine and aspirational

CREATIVE DESIGN EXCELLENCE:
- Follow sophisticated design principles like those in premium lifestyle magazines
- Create visual hierarchy with varied image sizes and strategic white space
- Use elegant, readable typography PLUS beautiful handwritten elements
- Include hand-lettered quotes, affirmations, and personal mantras
- Employ a cohesive color palette that feels intentional and harmonious
- Balance different visual elements (text, images, graphics, handwriting) expertly
- Create depth and visual interest through creative shapes and composition
- Use organic, flowing layouts that break traditional grid patterns
- Avoid generic stock photo aesthetics - aim for editorial-quality imagery
- Mix modern typography with authentic handwriting for personal touch
- Make it feel like a curated art piece with creative freedom

VISION BOARD CONTENT:
{prompt}

AUTHENTIC PHOTOGRAPHY STYLE:
- Natural outdoor settings with beautiful lighting
- Genuine candid moments and authentic emotions
- Professional portrait photography with proper depth of field
- Lifestyle imagery that feels real and achievable
- No obvious AI artifacts, synthetic faces, or unnatural poses
- Use warm, natural color tones that feel inviting and inspiring
- Capture moments that feel spontaneous and genuine
- Employ professional composition techniques (rule of thirds, leading lines, etc.)

FINAL QUALITY CHECK:
- Every element must look professionally crafted and intentionally placed
- The overall aesthetic should rival high-end lifestyle publications
- Colors should be harmonious and emotionally resonant
- Typography should be clean, modern, and perfectly readable
- The composition should guide the eye naturally through the design
- It should feel like something someone would proudly display in their home or office
"""
            
            print("🎨 Generating complete vision board with enhanced layout...")
            
            # Use GPT-Image-1 with optimal settings for complete vision boards
            response = self.openai_client.images.generate(
                model="gpt-image-1",
                prompt=enhanced_prompt,
                size="1024x1024",  
                quality="high",   
                output_format="png"  
            )
            
            generation_time = time.time() - start_time
            
            # Get the generated image
            img_obj = response.data[0] if response.data else None
            if not img_obj:
                print("❌ No image was generated by GPT-Image-1")
                return None
                
            image_url = getattr(img_obj, 'url', None)
            image_b64 = getattr(img_obj, 'b64_json', None)
            revised_prompt = getattr(img_obj, 'revised_prompt', None)
            
            if not image_url and not image_b64:
                msg = "❌ No image was generated by GPT-Image-1. This may be due to a rejected prompt, API access issue, or quota limits."
                if revised_prompt:
                    msg += f"\n📝 Revised prompt: {revised_prompt}"
                print(msg)
                return None
                
            # If we have a URL, fetch the image and convert to base64
            if image_url:
                print("📥 Downloading generated complete vision board...")
                img_response = requests.get(image_url)
                img_response.raise_for_status()
                image_bytes = img_response.content
                
                # Post-process to ensure complete layout
                print("🔧 Ensuring complete vision board layout...")
                processed_bytes = self._ensure_complete_vision_board_layout(image_bytes)
                image_b64 = base64.b64encode(processed_bytes).decode('utf-8')
                print("✅ Vision board layout verified and optimized!")
            
            return {
                "image_data": image_b64,
                "generation_time": generation_time,
                "model": "gpt-image-1",
                "prompt": enhanced_prompt,
                "revised_prompt": revised_prompt,
                "size": "1024x1024",
                "quality": "high",
                "format": "png"
            }
            
        except Exception as e:
            error_msg = str(e)
            if 'moderation_blocked' in error_msg or 'safety system' in error_msg:
                print("⚠️ Your prompt was blocked by OpenAI's safety system. Please try rephrasing your prompt to avoid sensitive or ambiguous content.")
            else:
                print(f"❌ GPT-Image-1 generation failed: {error_msg}")
            return None
    
    def _ensure_complete_vision_board_layout(self, image_bytes: bytes) -> bytes:
        """
        Ensure vision board meets technical requirements:
        - Perfect 1024x1024 square with 50px margin on all sides
        - All elements fully visible, no cropping at edges
        - High quality with proper composition
        """
        try:
            from PIL import Image, ImageDraw
            import io
            
            # Load the image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Ensure it's exactly 1024x1024
            if image.size != (1024, 1024):
                print(f"📐 Resizing from {image.size} to 1024x1024...")
                image = image.resize((1024, 1024), Image.LANCZOS)
            
            # Create a new image with 50px margin as specified in requirements
            margin = 50
            canvas_size = 1024
            content_size = canvas_size - (2 * margin)
            
            # Create new canvas with white background
            canvas = Image.new('RGB', (canvas_size, canvas_size), 'white')
            
            # Resize content to fit within margins (924x924 content area)
            content_image = image.resize((content_size, content_size), Image.LANCZOS)
            
            # Paste content with 50px margin on all sides
            canvas.paste(content_image, (margin, margin))
            
            # Convert back to bytes with high quality
            output = io.BytesIO()
            canvas.save(output, format='PNG', quality=95, optimize=True)
            
            print("✅ Vision board optimized: 1024x1024 with 50px margins, all elements fully visible")
            return output.getvalue()
            
        except Exception as e:
            print(f"❌ Error optimizing vision board layout: {e}")
            # Return original if processing fails
            return image_bytes
    
    def _save_base64_image_temporarily(self, base64_string: str) -> str:
        """
        Save base64 image to temporary file and return file URL for display
        
        Args:
            base64_string (str): Base64 encoded image data
            
        Returns:
            str: File path or data URL for image display
        """
        try:
            # Create temp directory if it doesn't exist
            temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "temp")
            os.makedirs(temp_dir, exist_ok=True)
            
            # Generate unique filename
            timestamp = int(time.time())
            filename = f"vision_board_{timestamp}.png"
            filepath = os.path.join(temp_dir, filename)
            
            # Convert base64 to image and save
            image_bytes = base64.b64decode(base64_string)
            image = Image.open(BytesIO(image_bytes))
            
            # Save with high quality
            image.save(filepath, "PNG", optimize=True)
            print(f"💾 Image saved temporarily: {filename}")
            
            # Return data URL for immediate display (works better with Streamlit)
            return f"data:image/png;base64,{base64_string}"
            
        except Exception as e:
            print(f"❌ Failed to save base64 image: {str(e)}")
            # Return the base64 data URL as fallback
            return f"data:image/png;base64,{base64_string}"
    
    def _base64_to_image(self, base64_string: str) -> Image.Image:
        """Convert base64 string to PIL Image"""
        try:
            image_bytes = base64.b64decode(base64_string)
            return Image.open(BytesIO(image_bytes))
        except Exception as e:
            print(f"❌ Failed to convert base64 to image: {str(e)}")
            return None
    
    def _ensure_complete_vision_board(self, image_bytes: bytes) -> bytes:
        """Post-process image to ensure complete vision board layout"""
        try:
            # Open the image
            img = Image.open(BytesIO(image_bytes))
            width, height = img.size
            
            # If already 1024x1024, return as is
            if width == 1024 and height == 1024:
                return image_bytes
            
            # Create a 1024x1024 canvas with white background
            canvas = Image.new('RGB', (1024, 1024), 'white')
            
            # Calculate positioning to center the image
            if width > height:
                # Landscape - fit to width
                new_width = 1024
                new_height = int((height * 1024) / width)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                x = 0
                y = (1024 - new_height) // 2
            else:
                # Portrait or square - fit to height
                new_height = 1024
                new_width = int((width * 1024) / height)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                x = (1024 - new_width) // 2
                y = 0
            
            # Paste the image onto the canvas
            canvas.paste(img, (x, y))
            
            # Save to bytes
            output = BytesIO()
            canvas.save(output, format='PNG', quality=95)
            return output.getvalue()
            
        except Exception as e:
            print(f"Warning: Could not process image: {e}")
            return image_bytes

    def _delayed_save_vision_board_to_memory(self, user_id: str, template_num: int, persona: Dict, image_url: str):
        """Save vision board creation to user's memory with delay to avoid Streamlit restart"""
        try:
            # Wait 3 seconds to allow download to complete and avoid file watcher conflicts
            time.sleep(3)
            print("💾 Executing delayed memory save...")
            self._save_vision_board_to_memory(user_id, template_num, persona, image_url)
            print("✅ Delayed vision board save completed successfully!")
        except Exception as e:
            print(f"Error in delayed save: {e}")
    
    def _save_vision_board_to_memory(self, user_id: str, template_num: int, persona: Dict, image_url: str):
        """Save vision board creation to enhanced memory system with comprehensive context"""
        try:
            print(f"💾 Starting enhanced memory save for vision board...")
            
            # Get intake data for comprehensive context
            intake_data = self.intake_manager.get_intake_data_for_vision_board(user_id)
            template_name = self.templates[template_num]['name']
            
            # Create comprehensive vision board memory entry
            vision_board_memory = f"""🎨 **VISION BOARD CREATED SUCCESSFULLY**

📊 **Board Details:**
• Template: {template_name} (Template {template_num})
• Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
• User: {user_id}

🎯 **Persona Summary:**
• Core Identity: {persona.get('core_identity', 'Authentic self')}
• Life Goals: {', '.join(persona.get('life_goals', [])[:3])}
• Visual Style: {persona.get('visual_style', 'Natural')}
• Energy Level: {persona.get('energy_level', 'Balanced')}
• Primary Values: {', '.join(persona.get('core_values', [])[:3])}

🎨 **Visual Elements:**
• Color Palette: {persona.get('color_palette', 'Harmonious colors')}
• Mood: {persona.get('mood', 'Inspiring')}
• Aesthetic: {persona.get('aesthetic', 'Clean and purposeful')}

🌟 **Manifestation Focus:**
{chr(10).join([f"• {goal}" for goal in persona.get('manifestation_goals', [])[:5]])}

This vision board represents the user's authentic aspirations and will serve as their north star for personal growth and manifestation."""

            # Save using enhanced memory system
            self.memory_manager.add_interaction(
                user_id,
                f"Created vision board with {template_name} template",
                vision_board_memory,
                metadata={
                    'interaction_type': 'vision_board_creation',
                    'template_name': template_name,
                    'template_number': template_num,
                    'importance': 1.0,
                    'session_type': 'creative_manifestation',
                    'image_url': image_url,
                    'creation_date': datetime.now().isoformat()
                }
            )
            
            # Enhance memory with comprehensive vision board data
            if intake_data:
                vision_board_data = {
                    'template_name': template_name,
                    'template_number': template_num,
                    'user_goals': intake_data.get('user_goals', []),
                    'visual_elements': intake_data.get('visual_elements', []),
                    'emotional_tone': intake_data.get('emotional_tone', []),
                    'lifestyle_context': intake_data.get('lifestyle_context', []),
                    'color_preferences': intake_data.get('color_preferences', []),
                    'personal_values': intake_data.get('personal_values', []),
                    'aspirations': intake_data.get('aspirations', []),
                    'personality_traits': intake_data.get('personality_traits', []),
                    'energy_level': intake_data.get('energy_level', 'medium'),
                    'visual_style': intake_data.get('visual_style', 'natural'),
                    'authenticity_score': intake_data.get('authenticity_score', 8),
                    'created_at': datetime.now().isoformat(),
                    'image_url': image_url
                }
                
                # Use enhanced memory storage
                self.memory_manager.enhance_vision_board_memory(user_id, vision_board_data)
            
            # Save vision board record to database
            try:
                vision_board_record = {
                    'user_id': user_id,
                    'template_number': template_num,
                    'template_name': template_name,
                    'image_url': image_url,
                    'persona_data': json.dumps(persona),
                    'created_at': datetime.now().isoformat(),
                    'status': 'completed'
                }
                
                # Save to database
                self.db_manager.save_conversation(
                    user_id, 
                    "system", 
                    f"Vision board generated: {json.dumps(vision_board_record)}"
                )
                
            except Exception as db_error:
                print(f"⚠️ Database save warning: {db_error}")
                # Continue even if database save fails
            
            # Create achievement memory
            achievement_memory = f"""🏆 **ACHIEVEMENT UNLOCKED: Vision Board Created!**

You've successfully completed your personalized vision board journey with the {template_name} template. This represents:

✨ **Your Authentic Self**: Based on deep personal insights from 10 thoughtful questions
🎯 **Your Clear Vision**: Crystallized goals and aspirations for your future
🎨 **Your Personal Style**: Visual representation that resonates with your energy
💫 **Your Manifestation Tool**: A powerful reference for daily inspiration

This vision board is uniquely YOURS - created from your authentic responses and deepest aspirations. Use it to stay connected to your vision and manifest the life you're creating!"""

            # Save achievement memory
            self.memory_manager.save_recall_memory(
                user_id,
                achievement_memory,
                memory_type="vision_board_achievement"
            )
            
            print(f"✅ Enhanced memory save completed for user {user_id}")
            print(f"   💾 Saved: Main memory, enhanced memory, achievement record")
            print(f"   🎨 Template: {template_name}")
            
        except Exception as e:
            print(f"❌ Error in enhanced memory save: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback basic save
            try:
                basic_memory = f"Created vision board with {self.templates[template_num]['name']} template. Image saved successfully."
                self.memory_manager.add_interaction(
                    user_id,
                    "vision_board_creation",
                    basic_memory
                )
                print(f"✅ Fallback memory save successful")
            except:
                print(f"❌ Even fallback memory save failed")
    
    def download_image(self, image_url: str) -> Optional[bytes]:
        """Download image from URL and return as bytes"""
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"Error downloading image: {e}")
            return None
        
    def _ensure_complete_vision_board(self, image_bytes: bytes) -> bytes:
        """
        Post-process the vision board to ensure it's complete and well-framed
        
        Args:
            image_bytes (bytes): Original image bytes
            
        Returns:
            bytes: Processed image bytes with guaranteed complete layout
        """
        try:
            # Open the image
            image = Image.open(BytesIO(image_bytes))
            
            # Ensure it's RGB mode
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Get original dimensions
            width, height = image.size
            
            # Check if image needs padding to ensure complete visibility
            # Add a subtle border/padding if needed
            padding = 20  # Add 20 pixels padding to ensure nothing is cut
            
            if width <= 1024 and height <= 1024:
                # Create a new image with padding
                new_width = min(1024, width + (padding * 2))
                new_height = min(1024, height + (padding * 2))
                
                # Create white background
                new_image = Image.new('RGB', (new_width, new_height), 'white')
                
                # Calculate centering position
                x_offset = (new_width - width) // 2
                y_offset = (new_height - height) // 2
                
                # Paste the original image centered
                new_image.paste(image, (x_offset, y_offset))
                image = new_image
            
            # Convert back to bytes
            output_buffer = BytesIO()
            image.save(output_buffer, format='PNG', optimize=True, quality=95)
            return output_buffer.getvalue()
            
        except Exception as e:
            print(f"⚠️ Post-processing failed, using original: {str(e)}")
            return image_bytes

    def _extract_short_quote(self, responses, index=0):
        """Extract a short, impactful quote from user responses."""
        if not responses or index >= len(responses):
            return "Dreams to Reality"
        
        response = responses[index]
        # Extract key phrases or create inspiring quotes from user's words
        words = response.split()
        
        # Look for powerful words/phrases
        powerful_words = []
        for word in words:
            if word.lower() in ['clarity', 'unstoppable', 'revolutionary', 'breakthrough', 
                               'innovation', 'success', 'growth', 'achievement', 'vision',
                               'excellence', 'mastery', 'freedom', 'abundance', 'impact']:
                powerful_words.append(word.title())
        
        if powerful_words:
            if len(powerful_words) == 1:
                return powerful_words[0]
            elif len(powerful_words) == 2:
                return f"{powerful_words[0]} & {powerful_words[1]}"
            else:
                return f"{powerful_words[0]} · {powerful_words[1]}"
        
        # Fallback to short phrases
        if len(words) <= 3:
            return response.title()
        elif len(words) <= 6:
            return ' '.join(words[:3]).title()
        else:
            # Extract meaningful short phrase
            return ' '.join(words[:2]).title()
