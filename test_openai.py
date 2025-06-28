#!/usr/bin/env python3
"""
Simple test to check OpenAI API key and embeddings
"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_api_key():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ No OpenAI API key found")
        print("Please set OPENAI_API_KEY in your .env file")
        return False
    
    print(f"✅ OpenAI API key found: {api_key[:10]}...")
    
    # Test OpenAI connection
    try:
        from langchain_openai import OpenAIEmbeddings
        print("Testing embeddings initialization...")
        
        embeddings = OpenAIEmbeddings(api_key=api_key)
        print("✅ Embeddings initialized successfully")
        
        # Test a simple embedding
        print("Testing embedding generation...")
        test_result = embeddings.embed_query("Hello world")
        print(f"✅ Embedding test successful - dimension: {len(test_result)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error with embeddings: {e}")
        return False

if __name__ == "__main__":
    test_api_key()
