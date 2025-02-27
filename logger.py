import logging
import time

logging.basicConfig(filename='usage.log', level=logging.INFO)

def log_usage(model_name, tokens_used, success, time_taken):
    status = "Success" if success else "Fail"
    log_message = f"Model: {model_name}, Tokens: {tokens_used}, Status: {status}, Time: {time_taken:.2f}s"
    logging.info(log_message)

def log_error(error_message):
    logging.error(f"Error: {error_message}")
