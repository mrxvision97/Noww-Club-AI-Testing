# Noww Club AI - Replit Development Guide

## Overview

Noww Club AI is a modular, AI-powered digital companion application built with Streamlit as the frontend and Python backend powered by LangGraph, LangChain, and OpenAI. The application serves as a personal assistant that helps users manage habits, set goals, schedule reminders, and provides emotional support through conversational AI.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit (version 1.46.0+)
- **UI Components**: 
  - Chat interface with styled message bubbles
  - Sidebar dashboard with quick stats and analytics
  - Analytics dashboard with mood tracking and progress visualization
- **State Management**: Streamlit session state for maintaining conversation flow and user context

### Backend Architecture
- **Core Framework**: SmartAgent - single intelligent LLM agent handling all interactions
- **LLM Integration**: OpenAI GPT-4o model for natural language processing and data extraction
- **Memory System**: Two-tier memory architecture using LangChain
  - Short-term: ConversationBufferWindowMemory (last 10 interactions)
  - Long-term: ConversationSummaryMemory for conversation summaries
- **Flow Management**: Intelligent data extraction from user messages regardless of format or length

### Data Storage Solutions
- **Primary Database**: SQLite with custom DatabaseManager class
- **Tables**:
  - `flows`: Persistent state management for multi-turn conversations
  - `user_profiles`: User profile data stored as JSON
  - `conversations`: Message history and metadata
- **File Storage**: JSON files for user memory profiles and prompt templates

## Key Components

### Core Modules
1. **DatabaseManager** (`core/database.py`): SQLite database operations and schema management
2. **MemoryManager** (`core/memory.py`): Two-tier memory system with LangChain integration
3. **SmartAgent** (`core/smart_agent.py`): Main intelligent agent handling all user interactions
4. **UserProfileManager** (`core/user_profile.py`): User data aggregation and statistics calculation
5. **VectorStore** (`core/vector_store.py`): ChromaDB vector database for semantic search and RAG
6. **NotificationSystem** (`core/notification_system.py`): Real-time scheduling and notification management
7. **VoiceHandler** (`core/voice_handler.py`): Speech recognition and text-to-speech capabilities

### AI Capabilities
1. **Intelligent Data Extraction**: Automatically extracts habit/goal/reminder data from any user message format
2. **Vector-Enhanced RAG**: ChromaDB integration for semantic search and improved context understanding
3. **Contextual Conversations**: Maintains conversation context and handles topic changes naturally
4. **Emotional Support**: Provides empathetic responses and mood tracking
5. **Multi-turn Flows**: Manages incomplete information collection seamlessly
6. **Voice Interface**: Speech-to-text input and text-to-speech output capabilities
7. **Real-time Notifications**: Scheduled reminders and notifications with background processing

### UI Components
1. **ChatInterface** (`ui/chat_interface.py`): Main conversation interface with styled chat bubbles
2. **SidebarInterface** (`ui/sidebar.py`): Dashboard with quick stats and settings
3. **AnalyticsDashboard** (`ui/analytics.py`): Data visualization for mood trends and habit tracking

### Utilities
1. **NotificationManager** (`utils/notifications.py`): Mock cron scheduler for reminders
2. **PromptLoader** (`utils/prompt_loader.py`): Template management for AI prompts

## Data Flow

### Conversation Flow
1. User message received through ChatInterface
2. SmartAgent processes message with full context and user profile
3. Intelligent extraction of data from user message (any format/length)
4. Automatic creation of habits/goals/reminders when sufficient data is provided
5. Natural follow-up questions for missing required information
6. Memory updates in both short-term and long-term systems

### Data Processing
- **Flexible Input**: Accepts any message format from single words to paragraphs
- **Smart Extraction**: Uses GPT-4o to extract structured data from natural language
- **Step-by-Step Questioning**: Asks for information one field at a time for better user experience
- **Required Fields**: 
  - Habits: name (first), frequency (second), then optional fields one by one
  - Goals: name (first), target_date (second), then optional fields one by one  
  - Reminders: text (first), time (second), then optional fields one by one
- **Contextual Responses**: Maintains conversation flow and handles topic changes naturally

## External Dependencies

### AI Services
- **OpenAI API**: GPT-4o model for all LLM operations
- **API Key**: Required environment variable `OPENAI_API_KEY`

### Python Packages
- `streamlit>=1.46.0`: Web application framework
- `langchain>=0.3.26`: LLM framework and memory management
- `langchain-openai>=0.3.25`: OpenAI integration
- `langgraph>=0.4.8`: State graph management
- `pandas>=2.3.0`: Data manipulation for analytics
- `plotly>=6.1.2`: Interactive charts and visualizations

### Development Tools
- **uv**: Python package manager (lock file present)
- **Nix**: Development environment (Python 3.11)

## Deployment Strategy

### Replit Configuration
- **Target**: Autoscale deployment
- **Runtime**: Python 3.11 with Nix environment
- **Port**: 5000 (configured for Streamlit server)
- **Entry Point**: `streamlit run app.py --server.port 5000`

### Environment Setup
- Requires `OPENAI_API_KEY` environment variable
- SQLite database created automatically on first run
- Prompt templates loaded from `prompts/` directory
- User profiles stored in `user_profiles/` directory

### Scalibility Considerations
- SQLite suitable for development and small-scale deployment
- Memory management designed for single-user sessions
- Notification system uses thread-based mock scheduler
- Database schema supports multi-user architecture

## Changelog
- June 23, 2025: Initial setup with complex state graph system
- June 23, 2025: Redesigned with SmartAgent - single intelligent LLM handling all interactions with natural data extraction
- June 23, 2025: Added vector database integration (ChromaDB), real-time notification system, and voice input/output capabilities
- June 23, 2025: Major personality overhaul - transformed from robotic assistant to friendly companion with enhanced memory recall and natural conversation flow

## User Preferences

- **Communication Style**: Casual, friendly, and human-like - like talking to a close friend
- **Conversation Approach**: Remember everything, reference past conversations naturally
- **Personality**: Warm, playful, trustworthy - users should feel comfortable joking around
- **Memory Priority**: Always recall and reference previous conversations when relevant
- **Response Style**: Avoid robotic templates, don't constantly mention capabilities unless asked
- **User Experience**: Make users feel like they're chatting with their bestie, not a formal assistant