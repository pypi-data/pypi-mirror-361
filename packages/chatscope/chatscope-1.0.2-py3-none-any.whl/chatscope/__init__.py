"""ChatGPT Conversation Analyzer

A Python library for analyzing and categorizing ChatGPT conversation exports.
"""

from .analyzer import ChatGPTAnalyzer
from .exceptions import ChatGPTAnalyzerError, APIError, DataError

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__description__ = "Analyze and categorize ChatGPT conversation exports using OpenAI API"

__all__ = [
    "ChatGPTAnalyzer",
    "ChatGPTAnalyzerError",
    "APIError",
    "DataError",
]