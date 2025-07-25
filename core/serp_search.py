#!/usr/bin/env python3
"""
SERP API Search Utility for Google Search Integration
Replaces DuckDuckGo with Google Search via SERP API using requests
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
import time
import logging

# Set up logging - only for this module, not global
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create handler only if logger doesn't have one
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False  # Prevent propagation to avoid duplicate logs

class SerpAPISearchWrapper:
    """
    SERP API wrapper for Google Search that provides the same interface
    as DuckDuckGo search but with better reliability and formatting
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize SERP API wrapper
        
        Args:
            api_key: SERP API key (if not provided, will try to get from environment)
        """
        self.api_key = api_key or os.getenv('SERPAPI_KEY', '051294694f51455477f571c4000f2c0b2c9ba7495d97f1db0624252e64689d20')
        self.base_url = "https://serpapi.com/search"
        
        if not self.api_key:
            raise ValueError("SERP API key is required. Set SERPAPI_KEY environment variable or pass api_key parameter.")
        
        logger.info("✅ SERP API initialized with Google Search")
    
    def search(self, query: str, num_results: int = 10, **kwargs) -> str:
        """
        Perform Google search using SERP API
        
        Args:
            query: Search query
            num_results: Number of results to return (default 10)
            **kwargs: Additional search parameters
            
        Returns:
            Formatted search results string compatible with DuckDuckGo format
        """
        try:
            logger.info(f"🔍 Performing Google search via SERP API: '{query}'")
            
            # Prepare search parameters
            params = {
                "engine": "google",
                "q": query,
                "api_key": self.api_key,
                "num": min(num_results, 10),  # Google limits to 10 per page
                "hl": kwargs.get("language", "en"),
                "gl": kwargs.get("country", "us"),
                "safe": "active",  # Safe search on
                "output": "json"
            }
            
            # Add optional parameters
            if "location" in kwargs:
                params["location"] = kwargs["location"]
            
            # Make the API request
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            results = response.json()
            
            # Check for errors
            if "error" in results:
                logger.error(f"❌ SERP API error: {results['error']}")
                return f"Search error: {results['error']}"
            
            # Format results in DuckDuckGo-compatible format
            formatted_results = self._format_search_results(results, query)
            
            organic_count = len(results.get('organic_results', []))
            logger.info(f"✅ Successfully retrieved {organic_count} results")
            return formatted_results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error during SERP API search: {e}")
            return f"Network error: {str(e)}. Please check your internet connection."
        except Exception as e:
            logger.error(f"❌ Error during SERP API search: {e}")
            return f"Search failed: {str(e)}. Please try again with a different query."
    
    def _format_search_results(self, results: Dict[str, Any], query: str) -> str:
        """
        Format SERP API results to match DuckDuckGo output format
        
        Args:
            results: Raw SERP API results
            query: Original search query
            
        Returns:
            Formatted results string
        """
        try:
            formatted_output = []
            
            # Add search metadata
            search_info = results.get("search_information", {})
            total_results = search_info.get("total_results", "Unknown")
            
            formatted_output.append(f"🔍 **Google Search Results for: '{query}'**")
            formatted_output.append(f"📊 **Total Results:** {total_results:,} results" if str(total_results).isdigit() else f"📊 **Total Results:** {total_results}")
            formatted_output.append("")
            
            # Process organic results
            organic_results = results.get("organic_results", [])
            
            if not organic_results:
                return "No search results found for this query. Please try different keywords."
            
            for idx, result in enumerate(organic_results, 1):
                title = result.get("title", "No title")
                link = result.get("link", "No link")
                snippet = result.get("snippet", "No description available")
                displayed_link = result.get("displayed_link", link)
                
                # Clean up snippet (remove extra whitespace and newlines)
                snippet = " ".join(snippet.split())
                
                # Limit snippet length for readability
                if len(snippet) > 200:
                    snippet = snippet[:197] + "..."
                
                formatted_output.append(f"**{idx}. {title}**")
                formatted_output.append(f"🔗 {displayed_link}")
                formatted_output.append(f"📝 {snippet}")
                formatted_output.append("")
            
            # Add related questions if available
            related_questions = results.get("related_questions", [])
            if related_questions:
                formatted_output.append("❓ **Related Questions:**")
                for i, question in enumerate(related_questions[:3], 1):
                    q_text = question.get("question", "")
                    if q_text:
                        formatted_output.append(f"{i}. {q_text}")
                formatted_output.append("")
            
            # Add related searches if available
            related_searches = results.get("related_searches", [])
            if related_searches:
                formatted_output.append("🔗 **Related Searches:**")
                related_terms = [rs.get("query", "") for rs in related_searches[:5] if rs.get("query")]
                if related_terms:
                    formatted_output.append(" • ".join(related_terms))
                formatted_output.append("")
            
            # Add knowledge graph if available
            knowledge_graph = results.get("knowledge_graph", {})
            if knowledge_graph:
                kg_title = knowledge_graph.get("title", "")
                kg_description = knowledge_graph.get("description", "")
                if kg_title and kg_description:
                    formatted_output.append("🧠 **Knowledge Graph:**")
                    formatted_output.append(f"**{kg_title}**")
                    # Limit description length
                    if len(kg_description) > 300:
                        kg_description = kg_description[:297] + "..."
                    formatted_output.append(f"{kg_description}")
                    formatted_output.append("")
            
            # Add answer box if available
            answer_box = results.get("answer_box", {})
            if answer_box:
                ab_answer = answer_box.get("answer", "")
                ab_title = answer_box.get("title", "")
                if ab_answer:
                    formatted_output.append("💡 **Quick Answer:**")
                    if ab_title:
                        formatted_output.append(f"**{ab_title}**")
                    # Limit answer length
                    if len(ab_answer) > 300:
                        ab_answer = ab_answer[:297] + "..."
                    formatted_output.append(f"{ab_answer}")
                    formatted_output.append("")
            
            # Join all formatted output
            final_output = "\n".join(formatted_output)
            
            # Ensure output is not too long (limit to ~4000 characters for AI processing)
            if len(final_output) > 4000:
                final_output = final_output[:3997] + "..."
            
            return final_output
            
        except Exception as e:
            logger.error(f"❌ Error formatting search results: {e}")
            return f"Error formatting search results: {str(e)}"
    
    def run(self, query: str) -> str:
        """
        Run search - compatibility method for DuckDuckGo interface
        
        Args:
            query: Search query
            
        Returns:
            Formatted search results
        """
        return self.search(query)

class SerpAPISearchRun:
    """
    Drop-in replacement for DuckDuckGoSearchRun that uses SERP API
    """
    
    def __init__(self, api_wrapper: Optional[SerpAPISearchWrapper] = None, **kwargs):
        """
        Initialize SERP API search runner
        
        Args:
            api_wrapper: SerpAPISearchWrapper instance
            **kwargs: Additional configuration
        """
        self.api_wrapper = api_wrapper or SerpAPISearchWrapper()
        self.max_results = kwargs.get("max_results", 10)
    
    def run(self, query: str) -> str:
        """
        Execute search and return formatted results
        
        Args:
            query: Search query
            
        Returns:
            Formatted search results string
        """
        return self.api_wrapper.search(query, num_results=self.max_results)

# Utility functions for easy integration
def create_serp_search_tool(max_results: int = 10, **kwargs) -> SerpAPISearchRun:
    """
    Create a SERP API search tool with specified configuration
    
    Args:
        max_results: Maximum number of results to return
        **kwargs: Additional configuration
        
    Returns:
        SerpAPISearchRun instance
    """
    wrapper = SerpAPISearchWrapper()
    return SerpAPISearchRun(api_wrapper=wrapper, max_results=max_results, **kwargs)

def perform_google_search(query: str, num_results: int = 10) -> str:
    """
    Quick utility function to perform a Google search
    
    Args:
        query: Search query
        num_results: Number of results to return
        
    Returns:
        Formatted search results
    """
    wrapper = SerpAPISearchWrapper()
    return wrapper.search(query, num_results=num_results)

# Test function
def test_serp_search():
    """Test the SERP API search functionality"""
    try:
        print("🧪 Testing SERP API Google Search...")
        
        # Test basic search
        wrapper = SerpAPISearchWrapper()
        results = wrapper.search("artificial intelligence latest news", num_results=5)
        
        print("✅ Test Results:")
        print(results[:1000] + "..." if len(results) > 1000 else results)
        print(f"\n📏 Total response length: {len(results)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_serp_search()
