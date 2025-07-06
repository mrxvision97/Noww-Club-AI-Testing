# Noww Club AI - Authentication & User Management

## 🚀 New Features Added

### 🔐 Complete Authentication System
- **User Registration & Login**: Secure local authentication with password hashing
- **Google OAuth Integration**: Sign in with Google account
- **Supabase Authentication**: Enterprise-grade authentication
- **JWT Session Management**: Secure session handling with automatic token refresh
- **Password Security**: Bcrypt hashing with strength validation

### 👤 User Management
- **Personal User Profiles**: Each user has their own profile and preferences
- **Persistent Sessions**: Users stay logged in across browser sessions
- **User Profile Management**: Customizable profiles with avatars and preferences

### 💬 Chat Session Management
- **Multiple Chat Sessions**: Users can create and manage multiple chat conversations
- **Chat History**: All conversations are saved and accessible
- **Session Switching**: Easy switching between different chat sessions
- **Chat Renaming**: Users can rename their chat sessions
- **Session Deletion**: Clean up old conversations

### 🧠 Personalized AI Experience
- **Memory Per User**: AI remembers each user's preferences and history
- **Personalized Responses**: AI adapts to individual user patterns
- **User-Specific Goals & Habits**: Personal tracking for each user
- **Individual Analytics**: Personalized insights and progress tracking

## 🛠️ Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Configuration
Copy `.env.example` to `.env` and configure:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional Authentication
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8501

SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key

JWT_SECRET_KEY=your_jwt_secret_key_here
```

### 3. Quick Setup
Run the setup script:
```bash
python setup_auth.py
```

### 4. Manual Setup (Alternative)
```bash
# Create necessary directories
mkdir -p user_profiles vector_stores logs temp data database

# Initialize database
python -c "from core.database import DatabaseManager; from core.auth import AuthenticationManager; db=DatabaseManager(); auth=AuthenticationManager(db)"

# Run the application
streamlit run app.py
```

## 🔑 Authentication Methods

### 1. Local Authentication
- Email/password registration
- Secure password hashing with bcrypt
- Password strength validation
- Email validation

### 2. Google OAuth
Set up Google OAuth in [Google Cloud Console](https://console.cloud.google.com/):
1. Create a new project or select existing
2. Enable Google+ API
3. Create OAuth 2.0 credentials
4. Add authorized redirect URIs
5. Update .env with client ID and secret

### 3. Supabase Authentication
Set up Supabase project:
1. Create account at [supabase.com](https://supabase.com)
2. Create new project
3. Get URL and anon key from Settings > API
4. Update .env with Supabase credentials

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT,
    full_name TEXT,
    avatar_url TEXT,
    auth_provider TEXT DEFAULT 'local',
    provider_id TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    email_verified BOOLEAN DEFAULT 0
);
```

### Chat Sessions Table
```sql
CREATE TABLE chat_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_name TEXT DEFAULT 'New Chat',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

### Conversations Table
```sql
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    chat_session_id INTEGER,
    message_type TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (chat_session_id) REFERENCES chat_sessions (id)
);
```

## 🎯 Usage

### For Users
1. **Registration**: Create account with email/password or use OAuth
2. **Login**: Sign in with your credentials
3. **Chat**: Start conversations that are automatically saved
4. **Sessions**: Create multiple chat sessions for different topics
5. **History**: Access all your previous conversations
6. **Profile**: Manage your profile and preferences

### For Developers
```python
# Initialize authentication system
from core.auth import AuthenticationManager
from core.session_manager import SessionManager

auth_manager = AuthenticationManager(db_manager)
session_manager = SessionManager(auth_manager)

# Register user
result = auth_manager.register_user(email, password, full_name)

# Authenticate user
user_info = auth_manager.authenticate_user(email, password)

# Create chat session
session_id = auth_manager.create_chat_session(user_id, "My Chat")

# Save message
auth_manager.save_message(user_id, session_id, "user", "Hello!")
```

## 🔧 Architecture

### Core Components
- **AuthenticationManager**: Handles user registration, login, and OAuth
- **SessionManager**: Manages user sessions and chat history
- **AuthInterface**: UI components for authentication
- **DatabaseManager**: Enhanced with user and session tables

### Security Features
- Password hashing with bcrypt
- JWT tokens for session management
- CSRF protection
- Input validation and sanitization
- Session timeout handling

### Session Management
- Persistent login across browser sessions
- Automatic session refresh
- Secure session storage
- Multi-device support

## 🚀 Production Deployment

### Environment Variables
Set these in your production environment:
```env
OPENAI_API_KEY=your_production_openai_key
JWT_SECRET_KEY=your_secure_jwt_secret
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=https://yourdomain.com
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### Security Considerations
- Use strong JWT secret keys
- Enable HTTPS in production
- Set up proper CORS policies
- Regular security updates
- Monitor authentication logs

## 🔍 Testing

### Default Admin User
The setup script creates a default admin user:
- Email: `admin@nowwclub.ai`
- Password: `admin123`
- **⚠️ Change this password in production!**

### Test Authentication
```python
python -c "
from core.database import DatabaseManager
from core.auth import AuthenticationManager

db = DatabaseManager()
auth = AuthenticationManager(db)

# Test user creation
result = auth.register_user('test@example.com', 'password123', 'Test User')
print('Registration:', result)

# Test authentication
user = auth.authenticate_user('test@example.com', 'password123')
print('Authentication:', user)
"
```

## 📈 Features Overview

### ✅ Implemented
- User registration and login
- Google OAuth integration
- Supabase authentication
- JWT session management
- Multiple chat sessions per user
- Persistent chat history
- User profile management
- Password security validation
- Session switching and management

### 🔄 Future Enhancements
- Email verification
- Password reset functionality
- Two-factor authentication
- Social login (Facebook, Twitter)
- User role management
- API rate limiting
- Advanced session analytics
- Multi-language support

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For issues or questions:
- Create an issue on GitHub
- Email: support@nowwclub.ai
- Documentation: Check the inline code comments

---

**🎉 Your enterprise-level chatbot is now ready with full authentication and user management!**
