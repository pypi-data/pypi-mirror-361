from typing import Optional
import inspect
from lite_logging.config import LogColors, LOGGING_ENABLED, LOG_LEVEL

def get_message(message: tuple, level: Optional[str]) -> Optional[tuple[str, str]]:
    """Returns the message and color for the log message

    :param tuple message: The message to print
    :param Optional[str] level: The log level.
    
    :return: The message and color for the log message
    :rtype: Optional[tuple[str, str]]"""
    level = level.upper()
    if not LOGGING_ENABLED:
        return None
    
    if level not in LOG_LEVEL or not LOG_LEVEL[level]["enabled"]:
        return None
        
    color = LOG_LEVEL[level]["color"]
    message_str = ' '.join(map(str, message))
    return message_str, color

def log(*message: tuple, level: Optional[str] = "INFO"):
    """Prints log messages with color

    :param tuple message: The message to print
    :param Optional[str] level: The log level."""
    result = get_message(message, level)
    if result is None:
        return
    message_str, color = result
    print(f"{color}[{level}] {message_str}{LogColors.ENDC}")

def log_debug(*message: tuple, level: Optional[str] = "INFO"):
    """Prints log messages with color and includes the file and line number.

    :param tuple message: The message to print
    :param Optional[str] level: The log level."""
    frame = inspect.currentframe()
    caller_frame = frame.f_back
    file_name = caller_frame.f_code.co_filename
    line_number = caller_frame.f_lineno
    debug_message = f"-> File: {file_name}, Line: {line_number}\n"
    result = get_message(message, level)
    if result is None:
        return
    message_str, color = result
    print(f"{color}{debug_message}[{level}] {message_str}{LogColors.ENDC}")