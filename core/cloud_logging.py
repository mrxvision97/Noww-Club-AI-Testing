#!/usr/bin/env python3
"""
Cloud Logging Enhancement for Render Deployment
Ensures all important logs are visible in cloud deployment
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Any, Dict


class CloudLogger:
    """Enhanced logging for cloud deployment visibility"""
    
    def __init__(self):
        self.is_cloud = os.getenv('RENDER') or os.getenv('PYTHON_ENV') == 'production'
        self.app_name = "NowwClubAI"
        
    def log_startup_info(self):
        """Log comprehensive startup information"""
        info = {
            "timestamp": datetime.now().isoformat(),
            "app_name": self.app_name,
            "environment": "cloud" if self.is_cloud else "local",
            "platform": sys.platform,
            "python_version": sys.version.split()[0],
            "working_directory": os.getcwd(),
            "environment_variables": self._get_safe_env_vars()
        }
        
        print("=" * 70)
        print(f"🚀 {self.app_name.upper()} STARTUP LOG")
        print("=" * 70)
        
        for key, value in info.items():
            if key == "environment_variables":
                print(f"🔐 Environment Variables:")
                for env_key, env_value in value.items():
                    print(f"   • {env_key}: {env_value}")
            else:
                print(f"📊 {key.replace('_', ' ').title()}: {value}")
        
        print("=" * 70)
        
    def _get_safe_env_vars(self) -> Dict[str, str]:
        """Get environment variables with sensitive data masked"""
        important_vars = [
            'OPENAI_API_KEY', 'PINECONE_API_KEY', 'GOOGLE_CLIENT_ID',
            'GOOGLE_CLIENT_SECRET', 'SUPABASE_URL', 'SUPABASE_KEY',
            'JWT_SECRET_KEY', 'RENDER', 'PYTHON_ENV'
        ]
        
        safe_vars = {}
        for var in important_vars:
            value = os.getenv(var)
            if value:
                if 'KEY' in var or 'SECRET' in var:
                    safe_vars[var] = f"***{value[-4:]}" if len(value) > 4 else "***SET***"
                else:
                    safe_vars[var] = value
            else:
                safe_vars[var] = "❌ NOT_SET"
                
        return safe_vars
    
    def log_component_status(self, component: str, status: str, details: str = "", error: Exception = None):
        """Log component initialization status with consistent formatting"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if status.upper() == "SUCCESS":
            icon = "✅"
            level = "INFO"
        elif status.upper() == "ERROR":
            icon = "❌"
            level = "ERROR"
        elif status.upper() == "WARNING":
            icon = "⚠️"
            level = "WARN"
        else:
            icon = "ℹ️"
            level = "INFO"
        
        log_msg = f"[{timestamp}] {icon} {component:<25} | {status:<8} | {details}"
        print(log_msg)
        
        # If there's an error, also print the exception details
        if error and self.is_cloud:
            print(f"     💥 Error Details: {str(error)}")
            
        # For cloud deployment, also use standard logging
        if self.is_cloud:
            logger = logging.getLogger(component.lower().replace(' ', '_'))
            if status.upper() == "ERROR":
                logger.error(f"{component} failed: {details} - {error}")
            elif status.upper() == "WARNING":
                logger.warning(f"{component} warning: {details}")
            else:
                logger.info(f"{component} initialized: {details}")
    
    def log_memory_status(self, using_pinecone: bool, details: str = ""):
        """Special logging for memory system status"""
        if using_pinecone:
            self.log_component_status(
                "Memory System", 
                "SUCCESS", 
                f"Pinecone Active - {details}"
            )
            print("     🌐 Vector search enabled")
            print("     💾 Semantic memory active")
            print("     🔍 Smart context retrieval ready")
        else:
            self.log_component_status(
                "Memory System", 
                "SUCCESS", 
                f"Local Fallback - {details}"
            )
            print("     📁 File-based storage active")
            print("     ⚠️  Limited semantic search")
            print("     💡 Consider adding PINECONE_API_KEY for enhanced features")
    
    def log_environment_check(self, missing_required: list, missing_optional: list):
        """Log environment variable check results"""
        print("\n🔍 ENVIRONMENT VALIDATION")
        print("-" * 60)
        
        if not missing_required:
            print("✅ All required environment variables are set")
        else:
            print(f"❌ Missing required variables: {', '.join(missing_required)}")
            
        if missing_optional:
            print(f"⚠️  Missing optional variables: {len(missing_optional)} items")
            for var in missing_optional:
                print(f"     • {var}")
        else:
            print("✅ All optional environment variables are set")
            
        print("-" * 60)
    
    def log_app_ready(self, components_count: int):
        """Log when app is fully ready"""
        print("\n🎉 APPLICATION READY")
        print("=" * 60)
        print(f"✅ {components_count} components initialized successfully")
        print("🌐 Web interface available")
        print("🤖 AI assistant ready")
        print("💬 Chat system operational")
        print("🎨 Vision board generator active")
        print("👤 User authentication enabled")
        print("=" * 60)
        print(f"🕐 Startup completed at {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)

# Global cloud logger instance
cloud_logger = CloudLogger()
