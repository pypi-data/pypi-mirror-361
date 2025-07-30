"""Custom exceptions for ChatGPT Analyzer."""


class ChatGPTAnalyzerError(Exception):
    """Base exception class for ChatGPT Analyzer."""
    pass


class APIError(ChatGPTAnalyzerError):
    """Raised when OpenAI API requests fail."""
    pass


class DataError(ChatGPTAnalyzerError):
    """Raised when there are issues with input data."""
    pass


class ConfigurationError(ChatGPTAnalyzerError):
    """Raised when there are configuration issues."""
    pass