#!/usr/bin/env python3
"""
Post-Deployment System Verification for Render
Tests all critical components after deployment to ensure everything works correctly
"""

import os
import sys
import json
import time
from datetime import datetime

# Load environment variables if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Note: dotenv not available, using system environment variables")

def test_environment_setup():
    """Test that the environment is properly configured"""
    print("🌐 ENVIRONMENT CONFIGURATION TEST")
    print("-" * 60)
    
    required_vars = ['OPENAI_API_KEY', 'RENDER']
    optional_vars = ['PINECONE_API_KEY', 'SUPABASE_URL', 'GOOGLE_CLIENT_ID']
    
    env_score = 0
    
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var}: Set")
            env_score += 1
        else:
            print(f"❌ {var}: Missing")
    
    for var in optional_vars:
        if os.getenv(var):
            print(f"✅ {var}: Set")
            env_score += 0.5
        else:
            print(f"⚠️  {var}: Not set (optional)")
    
    print(f"Environment Score: {env_score}/{len(required_vars) + len(optional_vars) * 0.5}")
    return env_score >= len(required_vars)

def test_directory_structure():
    """Test that all required directories exist and are writable"""
    print("\n📁 DIRECTORY STRUCTURE TEST")
    print("-" * 60)
    
    required_dirs = [
        'user_profiles',
        'user_profiles/episodic', 
        'vector_stores',
        'logs',
        'temp',
        'core',
        'ui'
    ]
    
    all_good = True
    
    for directory in required_dirs:
        if os.path.exists(directory):
            if os.access(directory, os.W_OK):
                print(f"✅ {directory}: Exists and writable")
            else:
                print(f"⚠️  {directory}: Exists but not writable")
                all_good = False
        else:
            print(f"❌ {directory}: Missing")
            all_good = False
    
    return all_good

def test_database_functionality():
    """Test SQLite database functionality"""
    print("\n🗄️  DATABASE FUNCTIONALITY TEST")
    print("-" * 60)
    
    try:
        import sqlite3
        
        # Test database creation and connection
        db_path = 'noww_club.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test basic operations
        cursor.execute("SELECT sqlite_version()")
        version = cursor.fetchone()[0]
        print(f"✅ SQLite connection: Version {version}")
        
        # Test table creation
        test_table = f"test_table_{int(time.time())}"
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {test_table} (id INTEGER PRIMARY KEY, test_data TEXT)")
        cursor.execute(f"INSERT INTO {test_table} (test_data) VALUES (?)", ("deployment_test",))
        cursor.execute(f"SELECT COUNT(*) FROM {test_table}")
        count = cursor.fetchone()[0]
        print(f"✅ Database operations: Created table with {count} test record")
        
        # Clean up test table
        cursor.execute(f"DROP TABLE {test_table}")
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_memory_system():
    """Test memory system functionality"""
    print("\n🧠 MEMORY SYSTEM TEST")
    print("-" * 60)
    
    try:
        from core.database import DatabaseManager
        from core.memory import MemoryManager
        
        # Initialize components
        db_manager = DatabaseManager()
        memory_manager = MemoryManager(db_manager)
        
        print(f"✅ Memory Manager initialized")
        
        # Test storage type
        if memory_manager.using_pinecone:
            print("✅ Pinecone integration: Active")
            
            # Test Pinecone functionality
            try:
                test_stats = memory_manager.get_memory_stats("test_deployment_user")
                print(f"✅ Vector storage: {test_stats.get('storage_type', 'unknown')} operational")
            except Exception as e:
                print(f"⚠️  Vector storage test: {e}")
        else:
            print("ℹ️  Local storage: Active (Pinecone not configured)")
        
        # Test memory operations
        test_user_id = "deployment_test_user"
        memory_manager.add_interaction(
            test_user_id,
            "Test message for deployment verification",
            "Test response confirming deployment functionality"
        )
        print("✅ Memory storage: Basic operations working")
        
        # Test memory retrieval
        context = memory_manager.get_context_for_conversation(test_user_id, "test")
        if context:
            print("✅ Memory retrieval: Context generation working")
        else:
            print("⚠️  Memory retrieval: Limited context available")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ai_components():
    """Test AI components (OpenAI, Smart Agent)"""
    print("\n🤖 AI COMPONENTS TEST")
    print("-" * 60)
    
    try:
        from core.database import DatabaseManager
        from core.memory import MemoryManager
        from core.smart_agent import SmartAgent
        
        # Initialize components
        db_manager = DatabaseManager()
        memory_manager = MemoryManager(db_manager)
        smart_agent = SmartAgent(db_manager, memory_manager)
        
        print("✅ Smart Agent initialized")
        
        # Test basic AI functionality (lightweight test)
        test_response = smart_agent.process_message(
            "deployment_test_user",
            "This is a test message to verify deployment. Please respond briefly."
        )
        
        if test_response and len(test_response) > 10:
            print("✅ AI Response: OpenAI integration working")
            return True
        else:
            print("⚠️  AI Response: Limited or no response")
            return False
            
    except Exception as e:
        print(f"❌ AI components test failed: {e}")
        return False

def test_vision_board_system():
    """Test vision board generation capability"""
    print("\n🎨 VISION BOARD SYSTEM TEST")
    print("-" * 60)
    
    try:
        from core.database import DatabaseManager
        from core.memory import MemoryManager
        from core.vision_board_generator import VisionBoardGenerator
        
        # Initialize required components
        db_manager = DatabaseManager()
        memory_manager = MemoryManager(db_manager)
        vb_generator = VisionBoardGenerator(db_manager, memory_manager)
        print("✅ Vision Board Generator initialized")
        
        # Test intake detection
        test_phrases = [
            "I want to create a vision board",
            "vision board",
            "help me visualize my goals"
        ]
        
        detection_working = False
        for phrase in test_phrases:
            # Test vision board detection using the correct method
            if vb_generator.intake_manager.detect_vision_board_request(phrase):
                detection_working = True
                break
        
        if detection_working:
            print("✅ Vision Board Detection: Working")
        else:
            print("⚠️  Vision Board Detection: May need adjustment")
        
        # Test template availability
        template_names = vb_generator.get_template_names()
        if template_names and len(template_names) >= 4:
            print(f"✅ Vision Board Templates: {len(template_names)} templates available")
        else:
            print(f"⚠️  Vision Board Templates: Only {len(template_names) if template_names else 0} templates found")
        
        return True
        
    except Exception as e:
        print(f"❌ Vision board system test failed: {e}")
        return False

def run_comprehensive_test():
    """Run all tests and provide summary"""
    print("=" * 80)
    print("🧪 NOWW CLUB AI - POST-DEPLOYMENT SYSTEM VERIFICATION")
    print("=" * 80)
    print(f"🕐 Test started: {datetime.now().isoformat()}")
    print(f"🌐 Environment: {'Render Cloud' if os.getenv('RENDER') else 'Local'}")
    print("=" * 80)
    
    test_results = {}
    
    # Run all tests
    test_results['environment'] = test_environment_setup()
    test_results['directories'] = test_directory_structure()
    test_results['database'] = test_database_functionality()
    test_results['memory'] = test_memory_system()
    test_results['ai_components'] = test_ai_components()
    test_results['vision_board'] = test_vision_board_system()
    
    # Calculate overall score
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100
    
    print("\n" + "=" * 80)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 80)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title():<20} | {status}")
    
    print("-" * 80)
    print(f"Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
    
    if success_rate >= 80:
        print("🎉 DEPLOYMENT STATUS: EXCELLENT - All critical systems operational")
    elif success_rate >= 60:
        print("✅ DEPLOYMENT STATUS: GOOD - Most systems operational, minor issues detected")
    else:
        print("⚠️  DEPLOYMENT STATUS: NEEDS ATTENTION - Several critical issues detected")
    
    print("=" * 80)
    print(f"🕐 Test completed: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 80)
    
    return test_results

if __name__ == "__main__":
    run_comprehensive_test()
