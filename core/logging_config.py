#!/usr/bin/env python3
"""
Logging Configuration for NowwClub AI
Reduces verbose logging from external libraries while keeping important app logs
"""

import logging
import os

def setup_logging(log_level: str = "WARNING"):
    """
    Setup logging configuration to reduce verbose output
    
    Args:
        log_level: Logging level for the app (DEBUG, INFO, WARNING, ERROR)
    """
    
    # Get log level from environment or use default
    app_log_level = os.getenv('LOG_LEVEL', log_level).upper()
    
    # Configure root logger with minimal level
    logging.basicConfig(
        level=logging.WARNING,  # Set high level for root to reduce noise
        format='%(levelname)s:%(name)s:%(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    # Set specific levels for noisy libraries
    logging.getLogger('httpx').setLevel(logging.WARNING)      # Reduce HTTP request logs
    logging.getLogger('urllib3').setLevel(logging.WARNING)    # Reduce connection logs
    logging.getLogger('requests').setLevel(logging.WARNING)   # Reduce requests logs
    logging.getLogger('apscheduler').setLevel(logging.ERROR)  # Only show errors from scheduler
    logging.getLogger('apscheduler.executors.default').setLevel(logging.ERROR)
    logging.getLogger('apscheduler.scheduler').setLevel(logging.ERROR)
    logging.getLogger('openai').setLevel(logging.WARNING)     # Reduce OpenAI API logs
    logging.getLogger('pinecone').setLevel(logging.WARNING)   # Reduce Pinecone logs
    
    # Set app-specific loggers to desired level
    app_loggers = [
        'core.serp_search',
        'core.memory',
        'core.smart_agent',
        'core.vision_board_generator',
        '__main__'
    ]
    
    for logger_name in app_loggers:
        app_logger = logging.getLogger(logger_name)
        app_logger.setLevel(getattr(logging, app_log_level, logging.WARNING))
    
    print(f"✅ Logging configured - App level: {app_log_level}, External libraries: WARNING/ERROR")

def set_quiet_mode():
    """Set ultra-quiet mode - only show errors"""
    setup_logging("ERROR")
    
    # Even more restrictive for production
    logging.getLogger('httpx').setLevel(logging.CRITICAL)
    logging.getLogger('apscheduler').setLevel(logging.CRITICAL)
    logging.getLogger('urllib3').setLevel(logging.CRITICAL)
    logging.getLogger('requests').setLevel(logging.CRITICAL)
    
    print("🔇 Quiet mode enabled - only critical errors will be shown")

def set_debug_mode():
    """Set debug mode - show detailed logs"""
    setup_logging("DEBUG")
    
    # Allow some INFO logs for debugging
    logging.getLogger('httpx').setLevel(logging.INFO)
    logging.getLogger('apscheduler.executors.default').setLevel(logging.INFO)
    
    print("🐛 Debug mode enabled - detailed logs will be shown")

if __name__ == "__main__":
    # Test the logging configuration
    setup_logging()
    
    # Test different loggers
    test_logger = logging.getLogger('core.test')
    test_logger.info("This should show if app logging is INFO or DEBUG")
    test_logger.warning("This warning should always show")
    
    httpx_logger = logging.getLogger('httpx')
    httpx_logger.info("This httpx info should NOT show")
    httpx_logger.warning("This httpx warning should show")
    
    print("Logging configuration test complete!")
