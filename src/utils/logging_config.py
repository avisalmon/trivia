import logging
import logging.handlers
import os
from datetime import datetime

def setup_logging():
    """Configure logging for the application"""
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Generate log filename with timestamp
    log_file = os.path.join(logs_dir, f'trivia_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # File handler with rotation
            logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=1024 * 1024,  # 1MB
                backupCount=5
            ),
            # Console handler
            logging.StreamHandler()
        ]
    )
    
    # Set specific log levels for different modules
    logging.getLogger('openai').setLevel(logging.WARNING)
    logging.getLogger('PyQt6').setLevel(logging.WARNING)
    
    # Log startup information
    logger = logging.getLogger(__name__)
    logger.info("Logging system initialized")
    logger.info(f"Log file: {log_file}")
    
    return logger 