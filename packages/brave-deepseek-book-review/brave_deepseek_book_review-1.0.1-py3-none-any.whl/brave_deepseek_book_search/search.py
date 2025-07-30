"""
Core BookSearch class - simplified interface for library usage
"""

import os
import json
import requests
from typing import List, Optional, Dict, Any
from .models import BookResult, SearchConfig


class BookSearch:
    """
    Simple interface for intelligent book search using Brave + DeepSeek
    
    Example:
        search = BookSearch(deepseek_api_key="...", brave_api_key="...")
        result = search.find_book("Dune Frank Herbert")
        print(result.description)
    """
    
    def __init__(
        self, 
        deepseek_api_key: str,
        brave_api_key: str,
        config: Optional[SearchConfig] = None
    ):
        """
        Initialize the book search
        
        Args:
            deepseek_api_key: DeepSeek API key
            brave_api_key: Brave Search API key  
            config: Optional search configuration
        """
        self.deepseek_api_key = deepseek_api_key
        self.brave_api_key = brave_api_key
        self.config = config or SearchConfig()
        
        # API endpoints
        self.deepseek_url = "https://api.deepseek.com/v1/chat/completions"
        self.brave_url = "https://api.search.brave.com/res/v1/web/search"
        
        # Headers
        self.deepseek_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {deepseek_api_key}"
        }
        self.brave_headers = {
            "Accept": "application/json",
            "X-Subscription-Token": brave_api_key
        }
    
    def find_book(self, query: str, config: Optional[SearchConfig] = None) -> BookResult:
        """
        Find information about a book
        
        Args:
            query: Book title, author, or both (e.g. "Dune Frank Herbert")
            config: Optional search configuration
            
        Returns:
            BookResult with book information
        """
        search_config = config or self.config
        
        try:
            # Step 1: Search with Brave
            search_results = self._search_with_brave(query, search_config.max_results)
            
            # Step 2: Analyze with DeepSeek
            description = self._analyze_with_deepseek(query, search_results)
            
            # Step 3: Extract title/author (simplified)
            title, author = self._extract_title_author(query)
            
            return BookResult(
                title=title,
                author=author,
                description=description,
                language="english",  # Simplified for demo
                countries_searched=search_config.countries,
                success=True,
                raw_data={
                    "brave_results": search_results,
                    "query": query
                }
            )
            
        except Exception as e:
            return BookResult(
                title="Unknown",
                author="Unknown", 
                description="",
                language="english",
                countries_searched=search_config.countries,
                success=False,
                error=str(e)
            )
    
    def _search_with_brave(self, query: str, max_results: int) -> Dict[str, Any]:
        """Search for book information using Brave API"""
        params = {
            'q': f'"{query}" book',
            'count': max_results,
            'result_filter': 'web'
        }
        
        response = requests.get(
            self.brave_url,
            headers=self.brave_headers,
            params=params,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def _analyze_with_deepseek(self, query: str, search_results: Dict[str, Any]) -> str:
        """Analyze search results with DeepSeek to create book description"""
        
        # Extract web results for analysis  
        web_results = search_results.get('web', {}).get('results', [])
        context = ""
        
        for result in web_results[:5]:  # Use top 5 results
            title = result.get('title', '')
            snippet = result.get('description', '')
            context += f"Title: {title}\nDescription: {snippet}\n\n"
        
        prompt = f"""
        Based on the following search results about "{query}", create a comprehensive book description.
        Include: title, author, genre, plot summary, publication details, and critical reception.
        
        Search Results:
        {context}
        
        Format as a clear, readable description:
        """
        
        data = {
            "model": self.config.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        response = requests.post(
            self.deepseek_url,
            headers=self.deepseek_headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content']
    
    def _extract_title_author(self, query: str) -> tuple[str, str]:
        """Simple extraction of title and author from query"""
        # This is a simplified version - the real implementation would be more sophisticated
        parts = query.split()
        if len(parts) >= 2:
            # Assume first part is title, last part is author
            title = " ".join(parts[:-1]) 
            author = parts[-1]
            return title, author
        return query, "Unknown"