import openai
import base64
import io
from PIL import Image
import requests
import time
from typing import Optional, Dict, Any, List
import random
import json
from dataclasses import dataclass
from enum import Enum


class VisionBoardTheme(Enum):
    SELF_MINDSET = "🧠 Self & Mindset"
    WORK_SKILLS_MONEY = "💼 Work, Skills & Money"
    HEALTH_ENERGY_BODY = "🏃‍♀️ Health, Energy & Body"
    RELATIONSHIPS_COMMUNITY = "💞 Relationships & Community"
    SPACE_SURROUNDINGS = "🏡 Space & Surroundings"
    EXPLORATION_DREAMS = "🌏 Exploration, Expression & Dreams"


@dataclass
class VisionBoardQuestion:
    id: int
    theme: VisionBoardTheme
    question: str
    purpose: str


class VisionBoardQuestions:
    """Complete set of vision board questions organized by themes"""
    
    def __init__(self):
        self.questions = [
            # Self & Mindset
            VisionBoardQuestion(1, VisionBoardTheme.SELF_MINDSET, 
                              "If you could describe your current season in one word or phrase, what would it be?", 
                              "understand emotional state"),
            VisionBoardQuestion(2, VisionBoardTheme.SELF_MINDSET, 
                              "What's something you've started healing or unlearning recently?", 
                              "identify growth areas"),
            VisionBoardQuestion(3, VisionBoardTheme.SELF_MINDSET, 
                              "What belief about yourself are you ready to outgrow?", 
                              "overcome limiting beliefs"),
            VisionBoardQuestion(4, VisionBoardTheme.SELF_MINDSET, 
                              "When do you feel most grounded or calm?", 
                              "identify peace sources"),
            VisionBoardQuestion(5, VisionBoardTheme.SELF_MINDSET, 
                              "What's a feeling you want more of in your life right now?", 
                              "define emotional goals"),
            
            # Work, Skills & Money
            VisionBoardQuestion(6, VisionBoardTheme.WORK_SKILLS_MONEY, 
                              "What's something you want to be known for 3 years from now?", 
                              "define professional legacy"),
            VisionBoardQuestion(7, VisionBoardTheme.WORK_SKILLS_MONEY, 
                              "What's a skill you're building (or want to build) that excites you?", 
                              "identify skill development"),
            VisionBoardQuestion(8, VisionBoardTheme.WORK_SKILLS_MONEY, 
                              "If you had unlimited money for one month — what would you spend it on, just for you?", 
                              "explore money desires"),
            VisionBoardQuestion(9, VisionBoardTheme.WORK_SKILLS_MONEY, 
                              "What does 'success' look like for you that isn't about status?", 
                              "define personal success"),
            VisionBoardQuestion(10, VisionBoardTheme.WORK_SKILLS_MONEY, 
                               "How do you want to feel about money this year?", 
                               "improve money mindset"),
            
            # Health, Energy & Body
            VisionBoardQuestion(11, VisionBoardTheme.HEALTH_ENERGY_BODY, 
                              "How does your body feel most days — what's one shift you'd like to make?", 
                              "assess physical wellbeing"),
            VisionBoardQuestion(12, VisionBoardTheme.HEALTH_ENERGY_BODY, 
                              "What's a small habit that makes you feel alive when you do it?", 
                              "identify energy boosters"),
            VisionBoardQuestion(13, VisionBoardTheme.HEALTH_ENERGY_BODY, 
                              "What does 'taking care of yourself' mean to you right now?", 
                              "define self-care"),
            VisionBoardQuestion(14, VisionBoardTheme.HEALTH_ENERGY_BODY, 
                              "What's your ideal morning or night routine vibe (even if it's aspirational)?", 
                              "explore routine preferences"),
            
            # Relationships & Community
            VisionBoardQuestion(15, VisionBoardTheme.RELATIONSHIPS_COMMUNITY, 
                              "Who or what makes you feel most *you* when you're around them?", 
                              "identify authentic connections"),
            VisionBoardQuestion(16, VisionBoardTheme.RELATIONSHIPS_COMMUNITY, 
                              "What's one boundary you want to protect this year?", 
                              "establish healthy boundaries"),
            VisionBoardQuestion(17, VisionBoardTheme.RELATIONSHIPS_COMMUNITY, 
                              "Are you craving deeper friendships, more solitude, or both?", 
                              "balance social needs"),
            VisionBoardQuestion(18, VisionBoardTheme.RELATIONSHIPS_COMMUNITY, 
                              "If your love life had a playlist title right now, what would it be?", 
                              "explore romantic aspirations"),
            VisionBoardQuestion(19, VisionBoardTheme.RELATIONSHIPS_COMMUNITY, 
                              "What kind of people do you want to attract or grow with?", 
                              "define relationship goals"),
            
            # Space & Surroundings
            VisionBoardQuestion(20, VisionBoardTheme.SPACE_SURROUNDINGS, 
                              "What would your dream living space feel like — not look like, *feel* like?", 
                              "explore spatial emotions"),
            VisionBoardQuestion(21, VisionBoardTheme.SPACE_SURROUNDINGS, 
                              "Which corner of your current environment feels most *yours*?", 
                              "identify personal spaces"),
            VisionBoardQuestion(22, VisionBoardTheme.SPACE_SURROUNDINGS, 
                              "Is there something in your space you've been meaning to change or upgrade?", 
                              "identify improvement areas"),
            VisionBoardQuestion(23, VisionBoardTheme.SPACE_SURROUNDINGS, 
                              "What sounds, colors, or smells help you feel at ease in a space?", 
                              "define comfort elements"),
            
            # Exploration, Expression & Dreams
            VisionBoardQuestion(24, VisionBoardTheme.EXPLORATION_DREAMS, 
                              "What part of you is ready to be expressed more?", 
                              "identify hidden talents"),
            VisionBoardQuestion(25, VisionBoardTheme.EXPLORATION_DREAMS, 
                              "What's something you secretly want to try, create, or learn?", 
                              "explore secret desires"),
            VisionBoardQuestion(26, VisionBoardTheme.EXPLORATION_DREAMS, 
                              "Where would you go if you could take a solo trip tomorrow — and why?", 
                              "explore travel aspirations"),
            VisionBoardQuestion(27, VisionBoardTheme.EXPLORATION_DREAMS, 
                              "If you could have a month completely to yourself, what would you do with it?", 
                              "explore personal time usage"),
            VisionBoardQuestion(28, VisionBoardTheme.EXPLORATION_DREAMS, 
                              "What's one thing you're scared to admit you want?", 
                              "uncover deep desires"),
        ]
    
    def get_all_questions(self) -> List[VisionBoardQuestion]:
        return self.questions
    
    def get_questions_by_theme(self, theme: VisionBoardTheme) -> List[VisionBoardQuestion]:
        return [q for q in self.questions if q.theme == theme]
    
    def get_random_questions(self, count: int) -> List[VisionBoardQuestion]:
        return random.sample(self.questions, min(count, len(self.questions)))


class PersonaGenerator:
    """Generate diverse user personas with different characteristics"""
    
    PERSONAS = [
        {
            "name": "Creative Sarah",
            "age": 28,
            "personality": "artistic, introspective, seeks authenticity",
            "life_stage": "career transition, exploring creativity",
            "values": ["self-expression", "meaningful work", "personal growth"],
            "challenges": ["imposter syndrome", "financial stability", "work-life balance"]
        },
        {
            "name": "Ambitious Marcus",
            "age": 35,
            "personality": "driven, goal-oriented, leadership-focused",
            "life_stage": "climbing corporate ladder, building wealth",
            "values": ["achievement", "financial success", "professional recognition"],
            "challenges": ["burnout", "relationships", "work-life balance"]
        },
        {
            "name": "Wellness Emma",
            "age": 31,
            "personality": "mindful, health-conscious, community-oriented",
            "life_stage": "focusing on holistic wellbeing, building community",
            "values": ["health", "balance", "authentic connections"],
            "challenges": ["setting boundaries", "career direction", "financial goals"]
        },
        {
            "name": "Explorer Jake",
            "age": 26,
            "personality": "adventurous, curious, freedom-seeking",
            "life_stage": "exploring the world, defining independence",
            "values": ["freedom", "experiences", "personal discovery"],
            "challenges": ["commitment", "financial planning", "career focus"]
        },
        {
            "name": "Balanced Lisa",
            "age": 33,
            "personality": "practical, nurturing, stability-focused",
            "life_stage": "building stable life, nurturing relationships",
            "values": ["stability", "family", "security"],
            "challenges": ["personal time", "career growth", "self-care"]
        }
    ]
    
    @classmethod
    def get_random_persona(cls):
        return random.choice(cls.PERSONAS)
    
    @classmethod
    def get_persona_by_name(cls, name: str):
        return next((p for p in cls.PERSONAS if p["name"] == name), None)


class ChatbotSimulator:
    """Simulates a chatbot with varying levels of question coverage"""
    
    def __init__(self, openai_api_key: str = None):
        self.openai_client = openai.OpenAI(api_key=openai_api_key) if openai_api_key else None
        self.questions_db = VisionBoardQuestions()
        
    def generate_answer_for_persona(self, question: VisionBoardQuestion, persona: dict) -> str:
        """Generate contextual answer based on persona characteristics"""
        
        # Pre-defined answer templates based on persona types and question themes
        answer_templates = {
            VisionBoardTheme.SELF_MINDSET: {
                "Creative Sarah": [
                    "I'm in a season of artistic awakening and authentic self-discovery",
                    "I'm unlearning the need to please everyone and embracing my unique voice",
                    "I'm ready to outgrow the belief that I'm not 'real' artist",
                    "I feel most grounded when I'm creating in my studio with soft music",
                    "I want more confidence and creative flow in my daily life"
                ],
                "Ambitious Marcus": [
                    "I'm in a season of strategic growth and leadership development",
                    "I'm unlearning the need to control every outcome",
                    "I'm ready to outgrow the belief that vulnerability equals weakness",
                    "I feel most grounded during my morning workout routine",
                    "I want more inner peace and authentic confidence"
                ],
                "Wellness Emma": [
                    "I'm in a season of deep healing and holistic alignment",
                    "I'm unlearning perfectionism and embracing gentle progress",
                    "I'm ready to outgrow the belief that I need to heal everyone",
                    "I feel most grounded during meditation and nature walks",
                    "I want more presence and mindful awareness"
                ],
                "Explorer Jake": [
                    "I'm in a season of discovery and boundless possibility",
                    "I'm unlearning the fear of commitment and embracing depth",
                    "I'm ready to outgrow the belief that I need to have it all figured out",
                    "I feel most grounded when I'm exploring new places",
                    "I want more adventure and meaningful experiences"
                ],
                "Balanced Lisa": [
                    "I'm in a season of gentle growth and steady progress",
                    "I'm unlearning the need to be everything to everyone",
                    "I'm ready to outgrow the belief that self-care is selfish",
                    "I feel most grounded during quiet family moments",
                    "I want more balance and peaceful contentment"
                ]
            },
            VisionBoardTheme.WORK_SKILLS_MONEY: {
                "Creative Sarah": [
                    "I want to be known for creating meaningful art that inspires others",
                    "I'm building my digital art and storytelling skills",
                    "I'd invest in art supplies, workshops, and a beautiful studio space",
                    "Success means having creative freedom and impacting people through my work",
                    "I want to feel abundant and worthy of financial success"
                ],
                "Ambitious Marcus": [
                    "I want to be known for innovative leadership and mentoring others",
                    "I'm building strategic thinking and team leadership skills",
                    "I'd invest in premium experiences, networking, and business ventures",
                    "Success means creating lasting impact and building wealth",
                    "I want to feel confident and strategic about money"
                ],
                "Wellness Emma": [
                    "I want to be known for helping others achieve holistic wellness",
                    "I'm building coaching and healing modalities skills",
                    "I'd invest in wellness retreats, training, and healing practices",
                    "Success means helping people transform their lives naturally",
                    "I want to feel aligned and grateful about money flow"
                ],
                "Explorer Jake": [
                    "I want to be known for inspiring others to live adventurously",
                    "I'm building travel writing and photography skills",
                    "I'd invest in travel experiences, gear, and adventure activities",
                    "Success means freedom to explore and share experiences",
                    "I want to feel free and abundant about money"
                ],
                "Balanced Lisa": [
                    "I want to be known for reliable excellence and supporting others",
                    "I'm building project management and communication skills",
                    "I'd invest in home improvements, family experiences, and education",
                    "Success means stability, growth, and work-life harmony",
                    "I want to feel secure and wise about money"
                ]
            },
            VisionBoardTheme.HEALTH_ENERGY_BODY: {
                "Creative Sarah": [
                    "My body feels creative but sometimes tense from hunching over work",
                    "Dancing to music makes me feel most alive and free",
                    "Taking care of myself means honoring my creative rhythms",
                    "Ideal morning: gentle stretching, journaling, and herbal tea"
                ],
                "Ambitious Marcus": [
                    "My body feels strong but sometimes stressed from intense work",
                    "High-intensity workouts make me feel most alive and focused",
                    "Taking care of myself means maintaining peak performance",
                    "Ideal morning: workout, protein shake, and goal review"
                ],
                "Wellness Emma": [
                    "My body feels generally good but craves more movement",
                    "Yoga and nature walks make me feel most alive and connected",
                    "Taking care of myself means listening to my body's needs",
                    "Ideal morning: meditation, gentle yoga, and nourishing breakfast"
                ],
                "Explorer Jake": [
                    "My body feels energetic but sometimes restless from routine",
                    "Outdoor activities and adventures make me feel most alive",
                    "Taking care of myself means staying active and exploring",
                    "Ideal morning: outdoor run, fresh air, and adventure planning"
                ],
                "Balanced Lisa": [
                    "My body feels okay but needs more consistent self-care",
                    "Simple walks and gentle movement make me feel most alive",
                    "Taking care of myself means creating sustainable routines",
                    "Ideal morning: quiet tea time, gentle stretching, and planning"
                ]
            },
            VisionBoardTheme.RELATIONSHIPS_COMMUNITY: {
                "Creative Sarah": [
                    "Other artists and deep thinkers make me feel most authentically me",
                    "I want to protect my creative time from social obligations",
                    "I'm craving deeper friendships with fellow creatives",
                    "My love life playlist: 'Beautiful Chaos and Authentic Connection'",
                    "I want to attract other authentic, creative, growth-minded people"
                ],
                "Ambitious Marcus": [
                    "High-achieving, motivated people make me feel most myself",
                    "I want to protect my personal time from work demands",
                    "I'm craving deeper friendships beyond networking",
                    "My love life playlist: 'Power Couple Goals and Deep Connection'",
                    "I want to attract ambitious, supportive, growth-oriented people"
                ],
                "Wellness Emma": [
                    "Conscious, mindful people make me feel most authentic",
                    "I want to protect my energy from negative influences",
                    "I'm craving both deeper friendships and peaceful solitude",
                    "My love life playlist: 'Mindful Love and Sacred Connection'",
                    "I want to attract conscious, caring, spiritually-aligned people"
                ],
                "Explorer Jake": [
                    "Fellow adventurers and free spirits make me feel most myself",
                    "I want to protect my freedom from controlling relationships",
                    "I'm craving deeper friendships with adventure buddies",
                    "My love life playlist: 'Wild Hearts and Free Spirits'",
                    "I want to attract independent, adventurous, open-minded people"
                ],
                "Balanced Lisa": [
                    "Reliable, caring people make me feel most myself",
                    "I want to protect family time from work and social pressure",
                    "I'm craving deeper friendships with like-minded parents",
                    "My love life playlist: 'Steady Love and Growing Together'",
                    "I want to attract stable, family-oriented, supportive people"
                ]
            },
            VisionBoardTheme.SPACE_SURROUNDINGS: {
                "Creative Sarah": [
                    "My dream space feels inspiring, artistic, and creatively alive",
                    "My art corner with easel and supplies feels most mine",
                    "I want to upgrade my studio lighting and organization",
                    "I love soft music, warm colors, and the smell of art supplies"
                ],
                "Ambitious Marcus": [
                    "My dream space feels powerful, organized, and success-oriented",
                    "My home office with awards and vision board feels most mine",
                    "I want to upgrade my workspace technology and furniture",
                    "I love silence, bold colors, and the smell of leather and coffee"
                ],
                "Wellness Emma": [
                    "My dream space feels peaceful, natural, and harmoniously balanced",
                    "My meditation corner with plants and crystals feels most mine",
                    "I want to add more plants and natural elements throughout",
                    "I love nature sounds, earth tones, and the smell of essential oils"
                ],
                "Explorer Jake": [
                    "My dream space feels adventurous, flexible, and travel-ready",
                    "My travel gear corner with maps and photos feels most mine",
                    "I want to create a better travel planning and gear storage area",
                    "I love ambient sounds, vibrant colors, and the smell of adventure"
                ],
                "Balanced Lisa": [
                    "My dream space feels cozy, organized, and family-friendly",
                    "My reading nook with family photos feels most mine",
                    "I want to organize the playroom and create a better family space",
                    "I love gentle music, warm colors, and the smell of home cooking"
                ]
            },
            VisionBoardTheme.EXPLORATION_DREAMS: {
                "Creative Sarah": [
                    "My artistic voice and creative courage are ready to be expressed more",
                    "I secretly want to try writing a graphic novel",
                    "I'd go to Paris to explore art museums and find inspiration",
                    "I'd spend a month creating art without any commercial pressure",
                    "I'm scared to admit I want to be a recognized artist"
                ],
                "Ambitious Marcus": [
                    "My visionary leadership and authentic self are ready to be expressed more",
                    "I secretly want to try starting my own consulting company",
                    "I'd go to Silicon Valley to network and explore opportunities",
                    "I'd spend a month strategizing and building my business empire",
                    "I'm scared to admit I want to be genuinely loved for who I am"
                ],
                "Wellness Emma": [
                    "My healing gifts and spiritual wisdom are ready to be expressed more",
                    "I secretly want to try leading wellness retreats",
                    "I'd go to Bali for a spiritual retreat and healing experience",
                    "I'd spend a month in meditation, nature, and healing practices",
                    "I'm scared to admit I want to be seen as a powerful healer"
                ],
                "Explorer Jake": [
                    "My adventurous spirit and storytelling abilities are ready to be expressed more",
                    "I secretly want to try writing a travel blog or documentary",
                    "I'd go to New Zealand for epic adventures and breathtaking landscapes",
                    "I'd spend a month exploring remote places and documenting experiences",
                    "I'm scared to admit I want deep, committed love without losing freedom"
                ],
                "Balanced Lisa": [
                    "My nurturing wisdom and quiet strength are ready to be expressed more",
                    "I secretly want to try teaching or mentoring others",
                    "I'd go to a peaceful mountain cabin for solitude and reflection",
                    "I'd spend a month reading, reflecting, and planning my future",
                    "I'm scared to admit I want recognition for my contributions"
                ]
            }
        }
        
        # Get answers for the persona and theme
        theme_answers = answer_templates.get(question.theme, {})
        persona_answers = theme_answers.get(persona["name"], [])
        
        if persona_answers:
            # Map question IDs to specific answers
            question_index = (question.id - 1) % len(persona_answers)
            return persona_answers[question_index]
        
        # Fallback generic answer
        return f"I'm exploring this area of my life and looking for growth and positive change."
    
    def simulate_chatbot_knowledge(self, available_question_count: int, persona: dict) -> Dict[int, str]:
        """Simulate a chatbot that can answer only a subset of questions"""
        
        # Select random questions that the bot can answer
        available_questions = self.questions_db.get_random_questions(available_question_count)
        
        # Generate answers for available questions
        answers = {}
        for question in available_questions:
            answer = self.generate_answer_for_persona(question, persona)
            answers[question.id] = {
                "question": question.question,
                "answer": answer,
                "theme": question.theme.value
            }
        
        return answers


class VisionBoardGenerator:
    """Generate vision boards using GPT-Image-1 based on available answers"""
    
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        
    def create_vision_board_prompt(self, persona: dict, available_answers: Dict[int, str]) -> str:
        """Create a dynamic, optimized prompt for vision board generation"""
        
        # Analyze available answers to understand key themes
        themes_covered = set()
        key_elements = []
        
        for answer_data in available_answers.values():
            themes_covered.add(answer_data["theme"])
            key_elements.append(answer_data["answer"])
        
        # Build dynamic prompt based on available information
        prompt_parts = []
        
        # Base prompt
        prompt_parts.append(f"Create a beautiful, inspiring vision board for {persona['name']}, a {persona['age']}-year-old person who is {persona['personality']}.")
        
        # Add theme-specific elements based on available answers
        if "🧠 Self & Mindset" in themes_covered:
            mindset_elements = [ans["answer"] for ans in available_answers.values() if ans["theme"] == "🧠 Self & Mindset"]
            prompt_parts.append(f"Inner world: Include symbols representing {', '.join(mindset_elements[:2])}.")
        
        if "💼 Work, Skills & Money" in themes_covered:
            work_elements = [ans["answer"] for ans in available_answers.values() if ans["theme"] == "💼 Work, Skills & Money"]
            prompt_parts.append(f"Professional aspirations: Include elements representing {', '.join(work_elements[:2])}.")
        
        if "🏃‍♀️ Health, Energy & Body" in themes_covered:
            health_elements = [ans["answer"] for ans in available_answers.values() if ans["theme"] == "🏃‍♀️ Health, Energy & Body"]
            prompt_parts.append(f"Wellness and vitality: Include imagery representing {', '.join(health_elements[:2])}.")
        
        if "💞 Relationships & Community" in themes_covered:
            relationship_elements = [ans["answer"] for ans in available_answers.values() if ans["theme"] == "💞 Relationships & Community"]
            prompt_parts.append(f"Connections and community: Include symbols representing {', '.join(relationship_elements[:2])}.")
        
        if "🏡 Space & Surroundings" in themes_covered:
            space_elements = [ans["answer"] for ans in available_answers.values() if ans["theme"] == "🏡 Space & Surroundings"]
            prompt_parts.append(f"Environment and space: Include elements representing {', '.join(space_elements[:2])}.")
        
        if "🌏 Exploration, Expression & Dreams" in themes_covered:
            dream_elements = [ans["answer"] for ans in available_answers.values() if ans["theme"] == "🌏 Exploration, Expression & Dreams"]
            prompt_parts.append(f"Dreams and exploration: Include imagery representing {', '.join(dream_elements[:2])}.")
        
        # Add overall style and composition
        prompt_parts.append("Style: Create a cohesive, aesthetically pleasing vision board with a collage-like composition.")
        prompt_parts.append("Visual elements: Include inspirational imagery, soft textures, beautiful typography, and harmonious colors.")
        prompt_parts.append("Mood: Uplifting, aspirational, and personally meaningful.")
        prompt_parts.append("Composition: Arrange elements in a balanced, visually appealing way that tells a story of growth and possibility.")
        
        return " ".join(prompt_parts)
    
    def generate_vision_board(self, persona: dict, available_answers: Dict[int, str]) -> Optional[Dict[str, Any]]:
        """Generate a vision board image based on persona and available answers"""
        
        try:
            # Create dynamic prompt
            prompt = self.create_vision_board_prompt(persona, available_answers)
            
            print(f"🎨 Generated prompt for {persona['name']}'s vision board:")
            print(f"📝 {prompt}\n")
            
            # Generate image
            start_time = time.time()
            
            response = self.client.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                size="1024x1024",
                quality="high",
                output_format="jpeg"
            )
            
            generation_time = time.time() - start_time
            
            # Process response
            img_obj = response.data[0] if response.data else None
            if not img_obj:
                print("❌ No image was generated")
                return None
                
            image_url = getattr(img_obj, 'url', None)
            image_b64 = getattr(img_obj, 'b64_json', None)
            revised_prompt = getattr(img_obj, 'revised_prompt', None)
            
            if image_url:
                img_response = requests.get(image_url)
                img_response.raise_for_status()
                image_bytes = img_response.content
                image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            
            return {
                "image_data": image_b64,
                "generation_time": generation_time,
                "original_prompt": prompt,
                "revised_prompt": revised_prompt,
                "persona": persona,
                "available_answers": available_answers,
                "questions_answered": len(available_answers),
                "themes_covered": len(set(ans["theme"] for ans in available_answers.values()))
            }
            
        except Exception as e:
            print(f"❌ Vision board generation failed: {str(e)}")
            return None


class VisionBoardTester:
    """Main testing class to evaluate vision board generation with varying question coverage"""
    
    def __init__(self, openai_api_key: str):
        self.chatbot = ChatbotSimulator(openai_api_key)
        self.vision_generator = VisionBoardGenerator(openai_api_key)
        self.questions_db = VisionBoardQuestions()
        
    def run_comprehensive_test(self, persona_name: str = None, question_counts: List[int] = None) -> Dict[str, Any]:
        """Run comprehensive tests with different question coverage levels"""
        
        # Default test parameters
        if question_counts is None:
            question_counts = [3, 5, 7, 10, 15, 20]
        
        # Get persona
        if persona_name:
            persona = PersonaGenerator.get_persona_by_name(persona_name)
        else:
            persona = PersonaGenerator.get_random_persona()
        
        if not persona:
            print("❌ Invalid persona name")
            return {}
        
        print(f"🧑‍💼 Testing with persona: {persona['name']}")
        print(f"📊 Personality: {persona['personality']}")
        print(f"🎯 Life stage: {persona['life_stage']}")
        print(f"💝 Values: {', '.join(persona['values'])}")
        print(f"⚡ Challenges: {', '.join(persona['challenges'])}\n")
        
        test_results = {
            "persona": persona,
            "test_results": []
        }
        
        for question_count in question_counts:
            print(f"🔍 Testing with {question_count} questions answered...")
            
            # Simulate chatbot knowledge
            available_answers = self.chatbot.simulate_chatbot_knowledge(question_count, persona)
            
            # Display available answers
            print(f"📋 Available answers:")
            for qid, answer_data in available_answers.items():
                print(f"  Q{qid}: {answer_data['question'][:50]}...")
                print(f"  A{qid}: {answer_data['answer']}")
                print(f"  Theme: {answer_data['theme']}\n")
            
            # Generate vision board
            vision_result = self.vision_generator.generate_vision_board(persona, available_answers)
            
            if vision_result:
                # Save the vision board
                timestamp = int(time.time())
                filename = f"vision_board_{persona['name'].replace(' ', '_')}_{question_count}q_{timestamp}.jpeg"
                
                try:
                    image_bytes = base64.b64decode(vision_result['image_data'])
                    image = Image.open(io.BytesIO(image_bytes))
                    image.save(filename)
                    print(f"✅ Vision board saved as: {filename}")
                    
                    # Add to test results
                    test_results["test_results"].append({
                        "question_count": question_count,
                        "themes_covered": vision_result["themes_covered"],
                        "generation_time": vision_result["generation_time"],
                        "filename": filename,
                        "available_answers": available_answers,
                        "success": True
                    })
                    
                    print(f"⏱️  Generation time: {vision_result['generation_time']:.2f} seconds")
                    print(f"🎨 Themes covered: {vision_result['themes_covered']}")
                    
                except Exception as e:
                    print(f"❌ Failed to save vision board: {str(e)}")
                    test_results["test_results"].append({
                        "question_count": question_count,
                        "success": False,
                        "error": str(e)
                    })
            else:
                print(f"❌ Failed to generate vision board for {question_count} questions")
                test_results["test_results"].append({
                    "question_count": question_count,
                    "success": False,
                    "error": "Generation failed"
                })
            
            print("=" * 60)
        
        return test_results
    
    def run_theme_coverage_test(self, persona_name: str = None) -> Dict[str, Any]:
        """Test how vision boards change as different themes are covered"""
        
        # Get persona
        if persona_name:
            persona = PersonaGenerator.get_persona_by_name(persona_name)
        else:
            persona = PersonaGenerator.get_random_persona()
        
        print(f"🎯 Testing theme coverage progression for {persona['name']}\n")
        
        themes = list(VisionBoardTheme)
        test_results = {
            "persona": persona,
            "theme_progression": []
        }
        
        # Test cumulative theme coverage
        for i in range(1, len(themes) + 1):
            current_themes = themes[:i]
            
            # Get one question from each theme
            available_answers = {}
            question_id = 1
            
            for theme in current_themes:
                theme_questions = self.questions_db.get_questions_by_theme(theme)
                if theme_questions:
                    selected_question = random.choice(theme_questions)
                    answer = self.chatbot.generate_answer_for_persona(selected_question, persona)
                    available_answers[question_id] = {
                        "question": selected_question.question,
                        "answer": answer,
                        "theme": theme.value
                    }
                    question_id += 1
            
            print(f"🔍 Testing with {len(current_themes)} themes: {[t.value for t in current_themes]}")
            
            # Generate vision board
            vision_result = self.vision_generator.generate_vision_board(persona, available_answers)
            
            if vision_result:
                timestamp = int(time.time())
                filename = f"theme_test_{persona['name'].replace(' ', '_')}_{len(current_themes)}themes_{timestamp}.jpeg"
                
                try:
                    image_bytes = base64.b64decode(vision_result['image_data'])
                    image = Image.open(io.BytesIO(image_bytes))
                    image.save(filename)
                    
                    test_results["theme_progression"].append({
                        "themes_count": len(current_themes),
                        "themes_covered": [t.value for t in current_themes],
                        "filename": filename,
                        "generation_time": vision_result["generation_time"],
                        "success": True
                    })
                    
                    print(f"✅ Saved: {filename}")
                    
                except Exception as e:
                    print(f"❌ Failed to save: {str(e)}")
            
            print("-" * 40)
        
        return test_results
    
    def generate_test_report(self, test_results: Dict[str, Any]) -> str:
        """Generate a comprehensive test report"""
        
        report = []
        report.append("=" * 60)
        report.append("VISION BOARD GENERATION TEST REPORT")
        report.append("=" * 60)
        
        persona = test_results["persona"]
        report.append(f"👤 Persona: {persona['name']}")
        report.append(f"🎭 Personality: {persona['personality']}")
        report.append(f"🎯 Life Stage: {persona['life_stage']}")
        report.append(f"💝 Values: {', '.join(persona['values'])}")
        report.append(f"⚡ Challenges: {', '.join(persona['challenges'])}")
        report.append("")
        
        if "test_results" in test_results:
            report.append("📊 QUESTION COVERAGE TEST RESULTS:")
            report.append("-" * 40)
            
            successful_tests = [r for r in test_results["test_results"] if r.get("success", False)]
            failed_tests = [r for r in test_results["test_results"] if not r.get("success", False)]
            
            report.append(f"✅ Successful generations: {len(successful_tests)}")
            report.append(f"❌ Failed generations: {len(failed_tests)}")
            
            if successful_tests:
                avg_time = sum(r["generation_time"] for r in successful_tests) / len(successful_tests)
                report.append(f"⏱️  Average generation time: {avg_time:.2f} seconds")
                
                report.append("\n📈 Results by question count:")
                for result in successful_tests:
                    report.append(f"  • {result['question_count']} questions → {result['themes_covered']} themes → {result['filename']}")
        
        if "theme_progression" in test_results:
            report.append("\n🎨 THEME COVERAGE PROGRESSION:")
            report.append("-" * 40)
            
            for result in test_results["theme_progression"]:
                if result["success"]:
                    report.append(f"  • {result['themes_count']} themes → {result['filename']}")
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)


# Example usage and testing functions
def main():
    """Main function to run comprehensive tests"""
    
    # Replace with your actual OpenAI API key
    API_KEY = "your-openai-api-key-here"
    
    if API_KEY == "your-openai-api-key-here":
        print("⚠️  Please set your OpenAI API key in the API_KEY variable")
        return
    
    # Initialize tester
    tester = VisionBoardTester(API_KEY)
    
    print("🚀 Starting Vision Board Generation Tests\n")
    
    # Test 1: Comprehensive question coverage test
    print("🔬 TEST 1: Question Coverage Analysis")
    print("=" * 50)
    
    test_results = tester.run_comprehensive_test(
        persona_name="Creative Sarah",  # or None for random
        question_counts=[3, 5, 8, 12, 16, 20]
    )
    
    # Generate and display report
    report = tester.generate_test_report(test_results)
    print(report)
    
    # Test 2: Theme coverage progression
    print("\n🔬 TEST 2: Theme Coverage Progression")
    print("=" * 50)
    
    theme_test_results = tester.run_theme_coverage_test("Wellness Emma")
    theme_report = tester.generate_test_report(theme_test_results)
    print(theme_report)
    
    # Test 3: Multi-persona comparison
    print("\n🔬 TEST 3: Multi-Persona Comparison")
    print("=" * 50)
    
    personas_to_test = ["Creative Sarah", "Ambitious Marcus", "Explorer Jake"]
    
    for persona_name in personas_to_test:
        print(f"\n👤 Testing {persona_name}...")
        persona_results = tester.run_comprehensive_test(
            persona_name=persona_name,
            question_counts=[5, 10, 15]
        )
        
        # Quick summary
        successful = sum(1 for r in persona_results["test_results"] if r.get("success", False))
        print(f"✅ {persona_name}: {successful}/3 vision boards generated successfully")


def run_quick_test():
    """Quick test function for development"""
    
    API_KEY = "your-openai-api-key-here"
    
    if API_KEY == "your-openai-api-key-here":
        print("⚠️  Please set your OpenAI API key")
        return
    
    tester = VisionBoardTester(API_KEY)
    
    # Quick test with random persona and 5 questions
    print("🚀 Quick Vision Board Test")
    print("=" * 30)
    
    test_results = tester.run_comprehensive_test(
        persona_name=None,  # Random persona
        question_counts=[5]  # Just one test
    )
    
    if test_results["test_results"] and test_results["test_results"][0].get("success"):
        print("✅ Quick test successful!")
        print(f"📁 Vision board saved as: {test_results['test_results'][0]['filename']}")
    else:
        print("❌ Quick test failed")


def demonstrate_dynamic_prompting():
    """Demonstrate how prompts change based on available answers"""
    
    API_KEY = "your-openai-api-key-here"
    
    if API_KEY == "your-openai-api-key-here":
        print("⚠️  Please set your OpenAI API key")
        return
    
    tester = VisionBoardTester(API_KEY)
    persona = PersonaGenerator.get_persona_by_name("Creative Sarah")
    
    print("🎨 DYNAMIC PROMPT DEMONSTRATION")
    print("=" * 50)
    print(f"Persona: {persona['name']}\n")
    
    # Test different question counts and show how prompts evolve
    for question_count in [3, 7, 12]:
        print(f"📝 Prompt for {question_count} questions:")
        print("-" * 30)
        
        available_answers = tester.chatbot.simulate_chatbot_knowledge(question_count, persona)
        prompt = tester.vision_generator.create_vision_board_prompt(persona, available_answers)
        
        print(f"🎯 {prompt}\n")
        print("📋 Based on answers:")
        for qid, answer_data in available_answers.items():
            print(f"  • {answer_data['theme']}: {answer_data['answer'][:60]}...")
        
        print("\n" + "=" * 50 + "\n")


def test_single_persona(persona_name: str, question_count: int = 5):
    """Simple function to test a single persona with specific question count"""
    
    API_KEY = "your-openai-api-key-here"
    
    if API_KEY == "your-openai-api-key-here":
        print("⚠️  Please set your OpenAI API key")
        return
    
    print(f"🧑‍💼 Testing {persona_name} with {question_count} questions")
    print("=" * 50)
    
    tester = VisionBoardTester(API_KEY)
    
    # Run test
    test_results = tester.run_comprehensive_test(
        persona_name=persona_name,
        question_counts=[question_count]
    )
    
    # Show results
    if test_results["test_results"] and test_results["test_results"][0].get("success"):
        result = test_results["test_results"][0]
        print(f"✅ Success! Vision board generated in {result['generation_time']:.2f} seconds")
        print(f"📁 Saved as: {result['filename']}")
        print(f"🎨 Themes covered: {result['themes_covered']}")
        
        # Show which questions were answered
        print("\n📋 Questions answered:")
        for qid, answer_data in result['available_answers'].items():
            print(f"  • {answer_data['theme']}: {answer_data['answer'][:60]}...")
    else:
        print("❌ Test failed")


def compare_personas_single_test(question_count: int = 5):
    """Compare all personas with same question count"""
    
    API_KEY = "your-openai-api-key-here"
    
    if API_KEY == "your-openai-api-key-here":
        print("⚠️  Please set your OpenAI API key")
        return
    
    personas = ["Creative Sarah", "Ambitious Marcus", "Wellness Emma", "Explorer Jake", "Balanced Lisa"]
    tester = VisionBoardTester(API_KEY)
    
    print(f"🔍 Comparing all personas with {question_count} questions each")
    print("=" * 60)
    
    for persona_name in personas:
        print(f"\n👤 Testing {persona_name}...")
        
        test_results = tester.run_comprehensive_test(
            persona_name=persona_name,
            question_counts=[question_count]
        )
        
        if test_results["test_results"] and test_results["test_results"][0].get("success"):
            result = test_results["test_results"][0]
            print(f"✅ Success! Generated in {result['generation_time']:.2f}s → {result['filename']}")
        else:
            print(f"❌ Failed for {persona_name}")


if __name__ == "__main__":
    # Choose which test to run:
    
    # Test single persona (EASIEST)
    test_single_persona("Creative Sarah", 5)
    
    # Compare all personas
    # compare_personas_single_test(7)
    
    # Full comprehensive test
    # main()
    
    # Quick single test
    # run_quick_test()
    
    # Demonstrate dynamic prompting
    # demonstrate_dynamic_prompting()