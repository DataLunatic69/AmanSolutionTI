import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    """Configure application logging"""

    
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

   
    log_file = os.path.join(log_dir, 'usage.log')
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=1024 * 1024,  # 1MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)

    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

   
    root_logger = logging.getLogger('')
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    logging.info("Logging setup complete")

def log_usage(model_name, tokens_used, success, time_taken):
    """Log model usage statistics"""
    status = "Success" if success else "Fail"
    log_message = (
        f"Model: {model_name}, "
        f"Tokens: {tokens_used}, "
        f"Status: {status}, "
        f"Time: {time_taken:.2f}s"
    )
    logging.info(log_message)

def log_error(error_message):
    """Log error messages"""
    logging.error(f"Error: {error_message}")
