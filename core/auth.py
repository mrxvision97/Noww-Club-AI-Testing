import streamlit as st
import os
import json
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from supabase import create_client, Client
import jwt
from passlib.context import CryptContext
import sqlite3

class AuthenticationManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
        self.algorithm = "HS256"
        self.token_expire_minutes = 60 * 24 * 7  # 7 days
        
        # Initialize authentication tables
        self.init_auth_tables()
        
        # Initialize Supabase client if credentials are provided
        self.supabase_client = None
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if supabase_url and supabase_key and supabase_url != "your_supabase_url" and supabase_key != "your_supabase_anon_key":
            try:
                self.supabase_client = create_client(supabase_url, supabase_key)
                print("✅ Supabase client initialized")
            except Exception as e:
                print(f"⚠️ Supabase initialization failed: {e}")
                self.supabase_client = None
        else:
            print("ℹ️ Supabase not configured (optional)")
    
    def init_auth_tables(self):
        """Initialize authentication-related tables"""
        conn = sqlite3.connect(self.db_manager.db_path)
        cursor = conn.cursor()
        
        # Users table for local authentication
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
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
            )
        ''')
        
        # User sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Chat sessions table for organizing conversations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_name TEXT DEFAULT 'New Chat',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Update conversations table to include chat_session_id
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                chat_session_id INTEGER,
                message_type TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (chat_session_id) REFERENCES chat_sessions (id)
            )
        ''')
        
        # Migrate existing conversations if needed
        try:
            cursor.execute("SELECT COUNT(*) FROM conversations")
            if cursor.fetchone()[0] > 0:
                cursor.execute('''
                    INSERT INTO conversations_new (user_id, message_type, content, metadata, timestamp)
                    SELECT 
                        (SELECT id FROM users WHERE email = conversations.user_id LIMIT 1) as user_id,
                        message_type, content, metadata, timestamp
                    FROM conversations
                    WHERE EXISTS (SELECT 1 FROM users WHERE email = conversations.user_id)
                ''')
                cursor.execute("DROP TABLE conversations")
                cursor.execute("ALTER TABLE conversations_new RENAME TO conversations")
        except sqlite3.Error:
            # If migration fails, just use the new table
            cursor.execute("DROP TABLE IF EXISTS conversations_new")
            cursor.execute("ALTER TABLE conversations_new RENAME TO conversations")
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str) -> str:
        """Hash a password for storing"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, user_id: int, email: str) -> str:
        """Create a JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=self.token_expire_minutes)
        to_encode = {"user_id": user_id, "email": email, "exp": expire}
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None
    
    def register_user(self, email: str, password: str, full_name: str) -> Optional[Dict[str, Any]]:
        """Register a new user with local authentication"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                return {"error": "User already exists"}
            
            # Hash password and create user
            hashed_password = self.hash_password(password)
            cursor.execute('''
                INSERT INTO users (email, hashed_password, full_name, auth_provider)
                VALUES (?, ?, ?, 'local')
            ''', (email, hashed_password, full_name))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {"user_id": user_id, "email": email, "full_name": full_name}
        except Exception as e:
            return {"error": str(e)}
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with email and password"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, email, hashed_password, full_name, avatar_url, is_active
                FROM users WHERE email = ? AND auth_provider = 'local'
            ''', (email,))
            
            user = cursor.fetchone()
            if not user:
                return None
            
            user_id, email, hashed_password, full_name, avatar_url, is_active = user
            
            if not is_active:
                return None
            
            if not self.verify_password(password, hashed_password):
                return None
            
            # Update last login
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            
            return {
                "user_id": user_id,
                "email": email,
                "full_name": full_name,
                "avatar_url": avatar_url
            }
        except Exception as e:
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user information by ID"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, email, full_name, avatar_url, auth_provider, created_at, last_login
                FROM users WHERE id = ? AND is_active = 1
            ''', (user_id,))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return {
                    "user_id": user[0],
                    "email": user[1],
                    "full_name": user[2],
                    "avatar_url": user[3],
                    "auth_provider": user[4],
                    "created_at": user[5],
                    "last_login": user[6]
                }
            return None
        except Exception as e:
            return None
    
    def create_chat_session(self, user_id: int, session_name: str = "New Chat") -> Optional[int]:
        """Create a new chat session for a user"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO chat_sessions (user_id, session_name)
                VALUES (?, ?)
            ''', (user_id, session_name))
            
            session_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return session_id
        except Exception as e:
            return None
    
    def get_user_chat_sessions(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all chat sessions for a user"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, session_name, created_at, updated_at
                FROM chat_sessions
                WHERE user_id = ? AND is_active = 1
                ORDER BY updated_at DESC
            ''', (user_id,))
            
            sessions = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "id": session[0],
                    "session_name": session[1],
                    "created_at": session[2],
                    "updated_at": session[3]
                }
                for session in sessions
            ]
        except Exception as e:
            return []
    
    def get_chat_history(self, user_id: int, chat_session_id: int = None) -> List[Dict[str, Any]]:
        """Get chat history for a user and specific session"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            if chat_session_id:
                cursor.execute('''
                    SELECT id, message_type, content, metadata, timestamp
                    FROM conversations
                    WHERE user_id = ? AND chat_session_id = ?
                    ORDER BY timestamp ASC
                ''', (user_id, chat_session_id))
            else:
                cursor.execute('''
                    SELECT id, message_type, content, metadata, timestamp
                    FROM conversations
                    WHERE user_id = ?
                    ORDER BY timestamp ASC
                ''', (user_id,))
            
            messages = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "id": msg[0],
                    "message_type": msg[1],
                    "content": msg[2],
                    "metadata": json.loads(msg[3]) if msg[3] else {},
                    "timestamp": msg[4]
                }
                for msg in messages
            ]
        except Exception as e:
            return []
    
    def save_message(self, user_id: int, chat_session_id: int, message_type: str, content: str, metadata: Dict = None):
        """Save a message to the chat history"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            # Save message
            cursor.execute('''
                INSERT INTO conversations (user_id, chat_session_id, message_type, content, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, chat_session_id, message_type, content, json.dumps(metadata) if metadata else None))
            
            # Update chat session timestamp
            cursor.execute('''
                UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (chat_session_id,))
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            return False
    
    def google_auth_flow(self):
        """Initialize Google OAuth flow"""
        google_client_id = os.getenv("GOOGLE_CLIENT_ID")
        google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        
        if not google_client_id or not google_client_secret or google_client_id == "your_google_client_id" or google_client_secret == "your_google_client_secret":
            print("ℹ️ Google OAuth not configured (optional)")
            return None
        
        try:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": google_client_id,
                        "client_secret": google_client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8501")]
                    }
                },
                scopes=["openid", "email", "profile"]
            )
            
            flow.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8501")
            return flow
        except Exception as e:
            print(f"⚠️ Google OAuth initialization failed: {e}")
            return None
    
    def create_or_get_oauth_user(self, email: str, full_name: str, avatar_url: str = None, provider: str = "google", provider_id: str = None) -> Optional[Dict[str, Any]]:
        """Create or get user from OAuth provider"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute('''
                SELECT id, email, full_name, avatar_url
                FROM users WHERE email = ?
            ''', (email,))
            
            user = cursor.fetchone()
            
            if user:
                # Update existing user
                cursor.execute('''
                    UPDATE users SET 
                        full_name = ?, 
                        avatar_url = ?, 
                        last_login = CURRENT_TIMESTAMP,
                        auth_provider = ?,
                        provider_id = ?
                    WHERE email = ?
                ''', (full_name, avatar_url, provider, provider_id, email))
                
                user_id = user[0]
            else:
                # Create new user
                cursor.execute('''
                    INSERT INTO users (email, full_name, avatar_url, auth_provider, provider_id, email_verified)
                    VALUES (?, ?, ?, ?, ?, 1)
                ''', (email, full_name, avatar_url, provider, provider_id))
                
                user_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            return {
                "user_id": user_id,
                "email": email,
                "full_name": full_name,
                "avatar_url": avatar_url
            }
        except Exception as e:
            return None
    
    def supabase_auth(self, email: str = None, password: str = None, phone: str = None, action: str = "sign_in", otp: str = None) -> Optional[Dict[str, Any]]:
        """Authenticate with Supabase - supports email, phone, and OTP verification"""
        if not self.supabase_client:
            return {"error": "Supabase authentication is not configured"}
        
        try:
            if action == "sign_up_email":
                # Email signup with email verification
                response = self.supabase_client.auth.sign_up({
                    "email": email, 
                    "password": password
                })
                if response.user:
                    return {
                        "success": True,
                        "message": "Please check your email for verification link",
                        "user": response.user
                    }
                return {"error": "Failed to create account"}
                
            elif action == "sign_up_phone":
                # Phone signup with SMS OTP
                response = self.supabase_client.auth.sign_up({
                    "phone": phone,
                    "password": password
                })
                if response.user:
                    return {
                        "success": True,
                        "message": "Please check your phone for verification code",
                        "user": response.user
                    }
                return {"error": "Failed to create account"}
                
            elif action == "sign_in_email":
                # Email signin
                response = self.supabase_client.auth.sign_in_with_password({
                    "email": email, 
                    "password": password
                })
                if response.user:
                    user_data = self.create_or_get_oauth_user(
                        email=response.user.email,
                        full_name=response.user.user_metadata.get("full_name", ""),
                        avatar_url=response.user.user_metadata.get("avatar_url"),
                        provider="supabase",
                        provider_id=response.user.id
                    )
                    return user_data
                return {"error": "Invalid credentials"}
                
            elif action == "sign_in_phone":
                # Phone signin
                response = self.supabase_client.auth.sign_in_with_password({
                    "phone": phone,
                    "password": password
                })
                if response.user:
                    user_data = self.create_or_get_oauth_user(
                        email=response.user.phone or f"{response.user.id}@phone.user",
                        full_name=response.user.user_metadata.get("full_name", "Phone User"),
                        avatar_url=response.user.user_metadata.get("avatar_url"),
                        provider="supabase_phone",
                        provider_id=response.user.id
                    )
                    return user_data
                return {"error": "Invalid credentials"}
                
            elif action == "verify_otp":
                # Verify OTP for email or phone
                response = self.supabase_client.auth.verify_otp({
                    "email": email,
                    "token": otp,
                    "type": "signup"
                }) if email else self.supabase_client.auth.verify_otp({
                    "phone": phone,
                    "token": otp,
                    "type": "sms"
                })
                
                if response.user:
                    user_data = self.create_or_get_oauth_user(
                        email=response.user.email or f"{response.user.id}@phone.user",
                        full_name=response.user.user_metadata.get("full_name", "Verified User"),
                        avatar_url=response.user.user_metadata.get("avatar_url"),
                        provider="supabase",
                        provider_id=response.user.id
                    )
                    return user_data
                return {"error": "Invalid verification code"}
                
            elif action == "resend_otp":
                # Resend OTP
                if email:
                    response = self.supabase_client.auth.resend({
                        "type": "signup",
                        "email": email
                    })
                elif phone:
                    response = self.supabase_client.auth.resend({
                        "type": "sms", 
                        "phone": phone
                    })
                return {"success": True, "message": "Verification code resent"}
                
            elif action == "google_oauth":
                # Google OAuth through Supabase
                response = self.supabase_client.auth.sign_in_with_oauth({
                    "provider": "google",
                    "options": {
                        "redirect_to": "http://localhost:8501"
                    }
                })
                return {"oauth_url": response.url}
                
        except Exception as e:
            return {"error": str(e)}
