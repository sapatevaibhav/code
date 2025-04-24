"""
Utility functions for code processing and token counting
"""
import sys
import os

# Add the code_chunker lib to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

try:
    # Try to import from the code_chunker library
    from lib.code_chunker.utils import count_tokens
except ImportError:
    # Fallback implementation if the import fails
    def count_tokens(text, encoding_name="gpt-4"):
        """
        Fallback implementation for token counting.
        This is a simple approximation that can be used when tiktoken is not available.
        For accurate results, install tiktoken and use the original count_tokens function.
        """
        # Simple approximation: roughly 4 characters per token
        return len(text) // 4 + 1

# Export the function
__all__ = ['count_tokens']
