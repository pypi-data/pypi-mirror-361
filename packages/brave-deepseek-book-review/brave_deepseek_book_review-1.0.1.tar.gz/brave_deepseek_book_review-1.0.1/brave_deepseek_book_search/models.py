"""
Data models for book search results
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class BookResult:
    """Result of a book search"""
    title: str
    author: str
    description: str
    language: str
    countries_searched: List[str]
    success: bool
    raw_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass  
class SearchConfig:
    """Configuration for book search"""
    max_results: int = 10
    countries: List[str] = None
    debug_mode: bool = False
    model: str = "deepseek-chat"
    
    def __post_init__(self):
        if self.countries is None:
            self.countries = ['usa', 'uk', 'france', 'germany', 'russia']