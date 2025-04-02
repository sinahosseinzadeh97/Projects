#!/usr/bin/env python
"""
Command Line Interface for the AI research system.
"""
import argparse
import json
import time
from typing import Dict, Any

from core.agent_orchestrator import AgentOrchestrator
from utils.caching import cache_manager
from config import DEFAULT_LLM_PROVIDER, DEFAULT_LLM_MODEL


def print_json(data: Dict[str, Any]) -> None:
    """
    Pretty print JSON data.
    
    Args:
        data: The data to print
    """
    print(json.dumps(data, indent=2))


def main():
    """Main function for the CLI."""
    # Set up argument parser
    parser = argparse.ArgumentParser(description="AI Research System CLI")
    parser.add_argument("query", nargs="?", help="Entity to research")
    parser.add_argument("--clear-cache", action="store_true", help="Clear the cache before running")
    parser.add_argument("--provider", default=DEFAULT_LLM_PROVIDER, help="LLM provider to use")
    parser.add_argument("--model", default=DEFAULT_LLM_MODEL, help="LLM model to use")
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Clear cache command
    clear_parser = subparsers.add_parser("clear-cache", help="Clear the cache")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle clear-cache command
    if args.command == "clear-cache" or args.clear_cache:
        cache_manager.clear()
        print("Cache cleared.")
        if args.command == "clear-cache":
            return
    
    # Require a query for research
    if not args.query:
        parser.print_help()
        return
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator(
        llm_provider=args.provider,
        llm_model=args.model
    )
    
    # Process the query
    print(f"Researching: {args.query}")
    start_time = time.time()
    
    try:
        results = orchestrator.process_query(args.query)
        
        # Print results
        print("\nResults:")
        print_json(results)
        
        # Print processing time
        print(f"\nTotal processing time: {time.time() - start_time:.2f} seconds")
    
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
