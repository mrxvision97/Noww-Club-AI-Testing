#!/usr/bin/env python3
"""
Setup script for Noww Club AI with Authentication System
This script initializes the database and sets up the authentication system.
"""

import os
import sys
import sqlite3
import json
from datetime import datetime
import secrets
from pathlib import Path

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("📝 Creating .env file...")
        
        # Generate a random JWT secret key
        jwt_secret = secrets.token_urlsafe(32)
        
        env_content = f"""# Environment Variables for Noww Club AI

# Required Variables
OPENAI_API_KEY=your_openai_api_key_here

# Authentication Configuration
JWT_SECRET_KEY={jwt_secret}

# Optional Google OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8501

# Optional Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key

# Database Configuration
DATABASE_URL=sqlite:///noww_club.db

# Environment
ENVIRONMENT=development
DEBUG=True
"""
        
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print("✅ Created .env file with random JWT secret key")
        print("⚠️  Please set your OPENAI_API_KEY in the .env file")
        return True
    else:
        print("📄 .env file already exists")
        return False

def setup_directories():
    """Setup required directories"""
    directories = [
        'user_profiles',
        'vector_stores',
        'logs',
        'temp',
        'data',
        'database'
    ]
    
    print("📁 Setting up directories...")
    
    for directory in directories:
        try:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                print(f"✅ Created directory: {directory}")
            else:
                print(f"📁 Directory already exists: {directory}")
        except Exception as e:
            print(f"❌ Error creating directory {directory}: {e}")
            return False
    
    return True

def initialize_database():
    """Initialize the database with all required tables"""
    print("🗄️  Initializing database...")
    
    try:
        # Import the database manager to initialize tables
        from core.database import DatabaseManager
        from core.auth import AuthenticationManager
        
        db_manager = DatabaseManager()
        auth_manager = AuthenticationManager(db_manager)
        
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

def create_default_user():
    """Create a default admin user for testing"""
    print("👤 Creating default admin user...")
    
    try:
        from core.database import DatabaseManager
        from core.auth import AuthenticationManager
        
        db_manager = DatabaseManager()
        auth_manager = AuthenticationManager(db_manager)
        
        # Check if admin user already exists
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE email = ?", ("admin@nowwclub.ai",))
        existing_user = cursor.fetchone()
        
        if not existing_user:
            # Create admin user
            result = auth_manager.register_user(
                email="admin@nowwclub.ai",
                password="admin123",
                full_name="Admin User"
            )
            
            if "error" not in result:
                print("✅ Default admin user created:")
                print("   📧 Email: admin@nowwclub.ai")
                print("   🔒 Password: admin123")
                print("   ⚠️  Please change the password after first login")
            else:
                print(f"❌ Error creating admin user: {result['error']}")
                return False
        else:
            print("👤 Admin user already exists")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating default user: {e}")
        return False

def create_sample_data():
    """Create sample data files"""
    print("📄 Creating sample data files...")
    
    try:
        # Create default user profile
        default_profile_path = os.path.join('user_profiles', 'default_user_profile.json')
        if not os.path.exists(default_profile_path):
            default_profile = {
                "user_id": "default_user",
                "preferences": {
                    "notification_time": "09:00",
                    "timezone": "UTC",
                    "language": "en"
                },
                "habits": [],
                "goals": [],
                "conversation_topics": [],
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
            
            with open(default_profile_path, 'w', encoding='utf-8') as f:
                json.dump(default_profile, f, indent=2)
            print("✅ Created default user profile")
        
        # Create vector store placeholder
        vector_store_path = os.path.join('vector_stores', '.gitkeep')
        if not os.path.exists(vector_store_path):
            with open(vector_store_path, 'w') as f:
                f.write("# Vector stores will be created here\n")
            print("✅ Created vector store placeholder")
        
        # Create logs file
        logs_path = os.path.join('logs', 'app.log')
        if not os.path.exists(logs_path):
            with open(logs_path, 'w') as f:
                f.write(f"Application setup completed at {datetime.now().isoformat()}\n")
            print("✅ Created log file")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        return False

def verify_installation():
    """Verify that all components are working"""
    print("🔍 Verifying installation...")
    
    try:
        # Test imports
        from core.auth import AuthenticationManager
        from core.session_manager import SessionManager
        from ui.auth_interface import AuthInterface
        
        print("✅ All authentication modules imported successfully")
        
        # Test database connection
        from core.database import DatabaseManager
        db_manager = DatabaseManager()
        
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('users', 'user_sessions', 'chat_sessions', 'conversations')
        """)
        
        tables = cursor.fetchall()
        expected_tables = ['users', 'user_sessions', 'chat_sessions', 'conversations']
        
        if len(tables) == len(expected_tables):
            print("✅ All required database tables exist")
        else:
            print(f"⚠️  Missing tables: {set(expected_tables) - {t[0] for t in tables}}")
        
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Installation verification failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Starting Noww Club AI Authentication Setup...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Error: app.py not found. Please run this script from the project root directory.")
        sys.exit(1)
    
    # Setup steps
    steps = [
        ("Creating .env file", create_env_file),
        ("Setting up directories", setup_directories),
        ("Initializing database", initialize_database),
        ("Creating default user", create_default_user),
        ("Creating sample data", create_sample_data),
        ("Verifying installation", verify_installation),
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        try:
            if not step_func():
                failed_steps.append(step_name)
        except Exception as e:
            print(f"❌ {step_name} failed: {e}")
            failed_steps.append(step_name)
    
    print("\n" + "=" * 50)
    
    if not failed_steps:
        print("🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Set your OPENAI_API_KEY in the .env file")
        print("2. (Optional) Configure Google OAuth or Supabase credentials")
        print("3. Run the application with: streamlit run app.py")
        print("4. Login with admin@nowwclub.ai / admin123")
        print("5. Create new user accounts or enable OAuth authentication")
        
        print("\n🔐 Authentication Features:")
        print("• User registration and login")
        print("• Persistent chat sessions")
        print("• Individual user profiles")
        print("• Session management")
        print("• Optional OAuth integration")
        
    else:
        print(f"❌ Setup failed. The following steps had errors:")
        for step in failed_steps:
            print(f"   - {step}")
        print("\nPlease fix the errors and run the setup again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
    """Set up the database with proper schema"""
    print("🔧 Setting up database...")
    
    # Import and initialize database manager
    from core.database import DatabaseManager
    from core.auth import AuthenticationManager
    
    # Initialize database
    db_manager = DatabaseManager()
    auth_manager = AuthenticationManager(db_manager)
    
    print("✅ Database setup completed")

def create_sample_env():
    """Create a sample .env file if it doesn't exist"""
    env_file = Path('.env')
    
    if not env_file.exists():
        env_example = Path('.env.example')
        if env_example.exists():
            env_file.write_text(env_example.read_text())
            print("✅ Created .env file from template")
            print("📝 Please edit .env file with your actual API keys")
        else:
            # Create basic .env file
            env_content = """# Noww Club AI Environment Variables
OPENAI_API_KEY=your_openai_api_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8501
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
"""
            env_file.write_text(env_content)
            print("✅ Created basic .env file")
            print("📝 Please edit .env file with your actual API keys")
    else:
        print("✅ .env file already exists")

def install_requirements():
    """Install Python requirements"""
    print("📦 Installing requirements...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        print("Please run: pip install -r requirements.txt")
        return False
    return True

def check_environment():
    """Check if all required environment variables are set"""
    print("🔍 Checking environment configuration...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['OPENAI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var) or os.getenv(var) == f"your_{var.lower()}":
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please update your .env file with the correct values")
        return False
    
    print("✅ Environment configuration looks good")
    return True

def create_default_user():
    """Create a default admin user for testing"""
    print("👤 Creating default admin user...")
    
    try:
        from core.database import DatabaseManager
        from core.auth import AuthenticationManager
        
        db_manager = DatabaseManager()
        auth_manager = AuthenticationManager(db_manager)
        
        # Create default admin user
        result = auth_manager.register_user(
            email="admin@nowwclub.ai",
            password="admin123",
            full_name="Noww Club Admin"
        )
        
        if "error" not in result:
            print("✅ Default admin user created")
            print("📧 Email: admin@nowwclub.ai")
            print("🔒 Password: admin123")
            print("⚠️  Please change this password in production!")
        else:
            print(f"ℹ️  Admin user may already exist: {result['error']}")
    except Exception as e:
        print(f"❌ Error creating default user: {e}")

def main():
    """Main setup function"""
    print("🚀 Setting up Noww Club AI with Authentication...")
    print("=" * 50)
    
    # Create directories
    create_directories()
    
    # Create sample environment file
    create_sample_env()
    
    # Install requirements
    if not install_requirements():
        return False
    
    # Set up database
    setup_database()
    
    # Check environment
    if not check_environment():
        print("\n❌ Setup incomplete. Please fix the environment variables and run again.")
        return False
    
    # Create default user
    create_default_user()
    
    print("\n🎉 Setup completed successfully!")
    print("=" * 50)
    print("📋 Next steps:")
    print("1. Edit .env file with your actual API keys")
    print("2. Run: streamlit run app.py")
    print("3. Open browser to http://localhost:8501")
    print("4. Sign in with admin@nowwclub.ai / admin123 (change password!)")
    print("\n🔐 Authentication features:")
    print("- User registration and login")
    print("- Google OAuth integration")
    print("- Supabase authentication")
    print("- Persistent chat sessions")
    print("- Per-user chat history")
    print("- Personalized AI responses")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
