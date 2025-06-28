# Noww Club AI - Local Setup

A friendly AI companion for habit tracking, goal setting, and personal assistance.

## Quick Start

### Option 1: Automated Setup (Recommended)

```bash
python setup_local.py
```

This script will:
- Install system dependencies
- Create environment file
- Install Python packages
- Set up optional features

### Option 2: Manual Setup

#### 1. Install Dependencies

```bash
pip install -r local_requirements.txt
```

#### 2. Set Environment Variables

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

Get your API key from: https://platform.openai.com/api-keys

#### 3. Run the Application

```bash
streamlit run app.py --server.port 5000
```

The app will be available at `http://localhost:5000`

## Optional Features

### Voice Capabilities
To enable voice input/output:

```bash
# On Ubuntu/Debian
sudo apt-get install portaudio19-dev python3-dev

# Install Python packages
pip install speechrecognition pyttsx3 pyaudio
```

### Memory System
The AI uses an advanced in-memory system for conversation context:

- **Long-term Memory**: LangGraph InMemoryStore for semantic search
- **Short-term Memory**: ConversationSummaryMemory for recent context
- **No External Dependencies**: Fast, reliable, self-contained memory

No additional setup required - memory works out of the box!

## Features

- **Friendly AI Chat**: Natural conversation with memory
- **Habit Tracking**: Build positive routines
- **Goal Setting**: Set and track objectives  
- **Smart Reminders**: Never miss important tasks
- **Web Search**: Get current information
- **Voice Interface**: Speech input/output (optional)
- **Advanced Memory**: In-memory conversation recall with semantic search

## Project Structure

```
├── app.py                 # Main Streamlit application
├── core/                  # Core AI and business logic
│   ├── smart_agent.py     # Main AI agent
│   ├── database.py        # SQLite database manager
│   ├── memory.py          # In-memory conversation system
│   ├── notification_system.py  # Real-time notifications
│   └── voice_handler.py   # Voice capabilities (optional)
├── ui/                    # User interface components
│   ├── chat_interface.py  # Chat UI
│   ├── sidebar.py         # Dashboard sidebar
│   └── analytics.py       # Data visualization
└── utils/                 # Utility functions
    └── notifications.py   # Notification helpers
```

## Configuration

The app creates these files automatically:
- `noww_club.db` - SQLite database
- `user_profiles/` - User profile storage (JSON files)

All memory is handled in-memory for optimal performance.

## Troubleshooting

### Missing OpenAI API Key
Make sure you have a valid OpenAI API key in your `.env` file.

### Voice Features Not Working
Voice features require additional system dependencies. See Optional Features section above.

### Database Issues
Delete `noww_club.db` to reset the database if you encounter issues.

## Development

The application uses:
- **Frontend**: Streamlit with custom CSS
- **Backend**: Python with LangChain and OpenAI
- **Database**: SQLite for data persistence
- **Memory**: LangGraph InMemoryStore + ConversationSummaryMemory
- **Scheduling**: APScheduler for notifications

For more details, see `replit.md` for technical architecture.