"""
Brave DeepSeek Book Search - A pip installable Python package for intelligent book search

Usage:
    from brave_deepseek_book_search import BookSearch
    
    search = BookSearch(
        deepseek_api_key="your_key",
        brave_api_key="your_key"
    )
    
    result = search.find_book("Dune Frank Herbert")
    print(result.description)
"""

from .search import BookSearch
from .models import BookResult, SearchConfig

__version__ = "1.0.0"
__author__ = "Brave-DeepSeek Team"

__all__ = ["BookSearch", "BookResult", "SearchConfig"]