#!/usr/bin/env python3
"""
Script to migrate vision board intake data to episodic memory
"""
import sys
sys.path.append('.')

from core.database import DatabaseManager
from core.memory import MemoryManager
import json

def migrate_intake_to_episodic():
    """Migrate existing vision board intake data to episodic memory"""
    print("🔧 MIGRATING VISION BOARD INTAKE TO EPISODIC MEMORY")
    print("=" * 60)
    
    # Initialize components
    db_manager = DatabaseManager()
    memory_manager = MemoryManager(db_manager)
    
    # Get all users with vision board intake data
    import sqlite3
    conn = sqlite3.connect('noww_club.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT user_id, intake_data FROM vision_board_intake WHERE json_extract(intake_data, '$.status') = 'completed'")
    users_data = cursor.fetchall()
    
    print(f"📊 Found {len(users_data)} users with completed intake data")
    
    for user_id, data_json in users_data:
        try:
            print(f"\n👤 Processing user: {user_id}")
            
            # Parse the JSON data
            data = json.loads(data_json)
            answers = data.get('answers', {})
            
            print(f"   📝 Found {len(answers)} answers to migrate")
            
            # Migrate each answer to episodic memory
            for q_num_str, answer_data in answers.items():
                try:
                    q_num = int(q_num_str)
                    
                    # Create episodic memory entry
                    episodic_entry = {
                        'user_id': user_id,
                        'memory_type': 'vision_board_intake',
                        'question_number': q_num,
                        'question_theme': answer_data.get('theme', ''),
                        'raw_user_response': answer_data.get('answer', ''),
                        'vision_analysis': {
                            'core_emotions': answer_data.get('core_emotions', []),
                            'visual_metaphors': answer_data.get('visual_metaphors', []),
                            'color_palette': answer_data.get('color_palette', []),
                            'lifestyle_elements': answer_data.get('lifestyle_elements', []),
                            'values_revealed': answer_data.get('values_revealed', []),
                            'aspirations': answer_data.get('aspirations', []),
                            'personality_traits': answer_data.get('personality_traits', []),
                            'essence_keywords': answer_data.get('essence_keywords', []),
                            'energy_level': answer_data.get('energy_level', 'medium'),
                            'authenticity_score': answer_data.get('authenticity_score', '8'),
                            'visual_style_preference': answer_data.get('visual_style_preference', 'natural'),
                            'specific_mentions': [],  # Can be extracted from answer if needed
                        },
                        'timestamp': answer_data.get('analyzed_at', data.get('completed_at', '')),
                        'importance': 0.9,  # High importance for vision board data
                        'emotional_intensity': 'high'
                    }
                    
                    # Store in Pinecone
                    memory_manager.pinecone_store.store_memory(
                        user_id=user_id,
                        content=f"Vision Board Q{q_num}: {answer_data.get('answer', '')}",
                        metadata=episodic_entry
                    )
                    
                    print(f"   ✅ Migrated Q{q_num}: {answer_data.get('theme', 'Unknown theme')}")
                    
                except Exception as e:
                    print(f"   ❌ Error migrating Q{q_num_str}: {e}")
            
            print(f"   🎉 Successfully migrated {len(answers)} memories for {user_id}")
            
        except Exception as e:
            print(f"   ❌ Error processing user {user_id}: {e}")
    
    conn.close()
    print("\n" + "=" * 60)
    print("🎉 Migration complete!")

if __name__ == "__main__":
    migrate_intake_to_episodic()
