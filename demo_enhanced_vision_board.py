#!/usr/bin/env python3
"""
Demo of Enhanced Vision Board Generation using your example data
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def show_enhanced_prompt_demo():
    """Show the enhanced prompt generated from your example"""
    print("🎨 ENHANCED VISION BOARD GENERATION DEMO")
    print("=" * 60)
    print("Using your exact example data from the request...")
    print()
    
    # Your exact example data
    example_qa = [
        ("If you had to bring more of just one feeling into your life right now — what would it be?", 
         "Unshakable clarity."),
        ("Three years from now — what do you want people to know you for?", 
         "For building mind-bending AI that actually improves lives."),
        ("What's a skill you're building (or dreaming of building) that excites you?", 
         "Mastering emotional intelligence in human-AI interactions."),
        ("Right now, what does 'taking care of yourself' look like for you?", 
         "Setting brutal boundaries, sleeping like it's a job, and walking without my phone."),
        ("What kind of people do you want to attract, grow with, or be surrounded by?", 
         "Bold visionaries who are kind, curious, and obsessed with evolving."),
        ("Who or what makes you feel most 'you' when you're around them?", 
         "Deep convos with close friends, late-night coding sprints, and lo-fi beats in quiet corners."),
        ("If you closed your eyes and stepped into your dream living space — what does it FEEL like?", 
         "It feels like calm ambition — focused, free, and flowing with creative energy."),
        ("What part of you is ready to be expressed more?", 
         "My unapologetic ambition — the part that dreams outrageously and actually executes."),
        ("What's something you secretly want to try, create, or learn?", 
         "Designing an AI-powered short film that captures raw human emotions."),
        ("What's one thing you're a little scared to admit you want — but you do want it?", 
         "I want global recognition for creating something revolutionary.")
    ]
    
    print("📝 YOUR INTAKE RESPONSES:")
    print("-" * 40)
    for i, (q, a) in enumerate(example_qa, 1):
        print(f"Q{i}: {q}")
        print(f"A: {a}")
        print()
    
    print("🤖 NOW GENERATING ENHANCED VISION BOARD PROMPT...")
    print("=" * 60)
    
    try:
        from core.database import DatabaseManager
        from core.memory import MemoryManager
        from core.vision_board_generator import VisionBoardGenerator
        
        # Initialize components
        db_manager = DatabaseManager()
        memory_manager = MemoryManager(db_manager)
        vision_generator = VisionBoardGenerator(db_manager, memory_manager)
        
        # Create persona from your example
        persona = {
            "user_id": "demo_user",
            "core_identity": "Bold visionary focused on building mind-bending AI that improves lives",
            "dominant_emotions": ["unshakable clarity", "focused ambition", "creative innovation"],
            "life_aspirations": [
                "Building mind-bending AI that actually improves lives",
                "Global recognition for creating something revolutionary", 
                "Mastering emotional intelligence in human-AI interactions",
                "Designing an AI-powered short film that captures raw human emotions"
            ],
            "visual_symbols": ["eye of digital storm", "calm ambition", "creative energy flow"],
            "color_palette": ["calm ambition tones", "focused energy", "creative flow colors"],
            "lifestyle_desires": ["deep convos with close friends", "late-night coding sprints", "lo-fi beats"],
            "core_values": ["brutal boundaries", "unapologetic ambition", "bold visionary thinking"],
            "energy_vibe": "calm ambition", 
            "visual_style": "focused and flowing"
        }
        
        # Create intake answers
        intake_answers = {}
        for i, (q, a) in enumerate(example_qa, 1):
            intake_answers[str(i)] = {
                "answer": a,
                "theme": f"theme_{i}",
                "timestamp": "2024-01-15T10:30:00"
            }
        
        # Generate enhanced prompt
        enhanced_prompt = vision_generator.create_enhanced_llm_prompt(persona, intake_answers)
        
        if enhanced_prompt:
            print("✅ ENHANCED PROMPT GENERATED!")
            print(f"📏 Length: {len(enhanced_prompt)} characters")
            print()
            print("🎨 GENERATED VISION BOARD PROMPT:")
            print("=" * 60)
            print(enhanced_prompt)
            print("=" * 60)
            print()
            print("🆚 COMPARISON:")
            print("❌ OLD: Generic template with {USER_GOALS} placeholders")
            print("✅ NEW: Sophisticated 5000+ character prompt based on YOUR actual responses")
            print()
            print("🎯 RESULT: Vision board will authentically reflect YOUR unique vision!")
            
        else:
            print("❌ Failed to generate enhanced prompt")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    show_enhanced_prompt_demo()
