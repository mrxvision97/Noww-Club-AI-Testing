#!/usr/bin/env python3
"""
Test script for the authentication system
"""

import os
import sys
from dotenv import load_dotenv

def test_imports():
    """Test if all imports work correctly"""
    print("🔍 Testing imports...")
    
    try:
        from core.database import DatabaseManager
        print("✅ DatabaseManager imported successfully")
        
        from core.auth import AuthenticationManager
        print("✅ AuthenticationManager imported successfully")
        
        from core.session_manager import SessionManager
        print("✅ SessionManager imported successfully")
        
        from ui.auth_interface import AuthInterface
        print("✅ AuthInterface imported successfully")
        
        print("✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_database_creation():
    """Test database creation and initialization"""
    print("\n🔧 Testing database creation...")
    
    try:
        from core.database import DatabaseManager
        from core.auth import AuthenticationManager
        
        # Initialize database
        db_manager = DatabaseManager()
        print("✅ Database manager initialized")
        
        # Initialize authentication
        auth_manager = AuthenticationManager(db_manager)
        print("✅ Authentication manager initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Database creation error: {e}")
        return False

def test_user_creation():
    """Test user creation functionality"""
    print("\n👤 Testing user creation...")
    
    try:
        from core.database import DatabaseManager
        from core.auth import AuthenticationManager
        
        db_manager = DatabaseManager()
        auth_manager = AuthenticationManager(db_manager)
        
        # Test user creation
        result = auth_manager.register_user(
            email="test@example.com",
            password="TestPassword123!",
            full_name="Test User"
        )
        
        if "error" in result:
            if "already exists" in result["error"]:
                print("✅ User already exists (expected)")
            else:
                print(f"❌ User creation error: {result['error']}")
                return False
        else:
            print("✅ User created successfully")
        
        # Test authentication
        user = auth_manager.authenticate_user("test@example.com", "TestPassword123!")
        if user:
            print("✅ User authentication successful")
        else:
            print("❌ User authentication failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ User creation error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Noww Club AI Authentication System")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed!")
        return False
    
    # Test database creation
    if not test_database_creation():
        print("\n❌ Database tests failed!")
        return False
    
    # Test user creation
    if not test_user_creation():
        print("\n❌ User creation tests failed!")
        return False
    
    print("\n🎉 All tests passed!")
    print("=" * 50)
    print("✅ Authentication system is working correctly")
    print("🚀 You can now run: streamlit run app.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
