# Noww Club AI - Cloud Deployment Guide

## 🚀 Quick Start

This repository contains a Streamlit-based AI chatbot with memory, vision board generation, and personalized interactions.

## 📋 Environment Variables Required

The following environment variables must be set in your cloud deployment platform:

### Required API Keys
- `OPENAI_API_KEY` - Your OpenAI API key
- `PINECONE_API_KEY` - Pinecone vector database API key
- `PINECONE_ENVIRONMENT` - Pinecone environment (e.g., "gcp-starter")
- `SERP_API_KEY` - SerpAPI key for web search functionality

### Authentication (Optional but recommended)
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_ANON_KEY` - Supabase anonymous key
- `GOOGLE_CLIENT_ID` - Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth client secret

## 🌐 Deployment Platforms

### Render.com
1. Connect your GitHub repository
2. Use the provided `render.yaml` configuration
3. Add environment variables in Render dashboard
4. Deploy automatically

### Heroku
1. Create new Heroku app
2. Connect GitHub repository
3. Add environment variables in Heroku dashboard
4. Uses `Procfile` for deployment configuration

### Streamlit Cloud
1. Connect repository to Streamlit Cloud
2. Add secrets in Streamlit Cloud dashboard
3. Deploy with one click

## 🛠️ Local Development

1. Clone the repository:
```bash
git clone https://github.com/mrxvision97/Noww-Club-AI-Testing.git
cd Noww-Club-AI-Testing
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file with your API keys:
```env
OPENAI_API_KEY=your_openai_key_here
PINECONE_API_KEY=your_pinecone_key_here
PINECONE_ENVIRONMENT=your_pinecone_env_here
SERP_API_KEY=your_serp_key_here
```

5. Run the application:
```bash
streamlit run app.py
```

## 📁 Project Structure

```
├── app.py                 # Main Streamlit application
├── core/                  # Core application modules
│   ├── auth.py           # Authentication management
│   ├── database.py       # Database operations
│   ├── memory.py         # Memory system
│   ├── session_manager.py # Session management
│   └── smart_agent.py    # AI agent logic
├── ui/                   # User interface components
│   ├── auth_interface.py # Authentication UI
│   ├── chat_interface.py # Chat UI
│   └── sidebar.py        # Sidebar components
├── requirements.txt      # Python dependencies
├── render.yaml          # Render.com deployment config
├── Procfile             # Heroku deployment config
└── runtime.txt          # Python version specification
```

## 🔧 Features

- 🤖 AI-powered chat interface with memory
- 🎨 Vision board generation
- 👤 User authentication (Email, Phone, OAuth)
- 🔍 Web search integration
- 💾 Persistent memory across sessions
- 📱 Responsive design

## 🚨 Important Notes

- Ensure all required environment variables are set before deployment
- The application creates a local SQLite database for user data
- Vector embeddings are stored in Pinecone for memory functionality
- OAuth requires proper redirect URI configuration

## 📞 Support

For deployment issues or questions, please create an issue in this repository.
