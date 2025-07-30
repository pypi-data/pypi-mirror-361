#!/usr/bin/env python3
"""
Command Line Interface for Brave DeepSeek Book Search
"""

import os
import argparse
import json
from .search import BookSearch
from .models import SearchConfig


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Search for books using Brave Search + DeepSeek LLM"
    )
    
    parser.add_argument(
        "query", 
        help="Book title, author, or both (e.g. 'Dune Frank Herbert')"
    )
    
    parser.add_argument(
        "--deepseek-key",
        default=os.getenv("DEEPSEEK_API_KEY"),
        help="DeepSeek API key (or set DEEPSEEK_API_KEY env var)"
    )
    
    parser.add_argument(
        "--brave-key", 
        default=os.getenv("BRAVE_API_KEY"),
        help="Brave Search API key (or set BRAVE_API_KEY env var)"
    )
    
    parser.add_argument(
        "--max-results",
        type=int,
        default=10,
        help="Maximum number of search results to analyze"
    )
    
    parser.add_argument(
        "--countries",
        nargs="+",
        default=["usa", "uk", "france", "germany", "russia"],
        help="Countries to search in"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true", 
        help="Enable debug mode"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON"
    )
    
    args = parser.parse_args()
    
    # Validate API keys
    if not args.deepseek_key:
        print("❌ DeepSeek API key required. Set DEEPSEEK_API_KEY env var or use --deepseek-key")
        return 1
        
    if not args.brave_key:
        print("❌ Brave API key required. Set BRAVE_API_KEY env var or use --brave-key") 
        return 1
    
    # Create search configuration
    config = SearchConfig(
        max_results=args.max_results,
        countries=args.countries,
        debug_mode=args.debug
    )
    
    # Initialize search
    search = BookSearch(
        deepseek_api_key=args.deepseek_key,
        brave_api_key=args.brave_key,
        config=config
    )
    
    # Perform search
    print(f"🔍 Searching for: {args.query}")
    result = search.find_book(args.query)
    
    # Output results
    if args.json:
        # JSON output
        output = {
            "title": result.title,
            "author": result.author, 
            "description": result.description,
            "success": result.success,
            "error": result.error
        }
        print(json.dumps(output, indent=2))
    else:
        # Human-readable output
        if result.success:
            print("\n📚 Book Information:")
            print(f"Title: {result.title}")
            print(f"Author: {result.author}")
            print(f"\nDescription:")
            print(result.description)
        else:
            print(f"❌ Search failed: {result.error}")
            return 1
    
    return 0


if __name__ == "__main__":
    exit(main())