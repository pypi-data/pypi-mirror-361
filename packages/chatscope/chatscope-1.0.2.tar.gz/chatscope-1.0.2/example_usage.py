#!/usr/bin/env python3
"""Example usage of ChatGPT Analyzer library."""

import os
from chatscope import ChatGPTAnalyzer
from chatscope.exceptions import ChatGPTAnalyzerError


def basic_example():
    """Basic usage example."""
    print("=== Basic Example ===")
    
    try:
        # Initialize analyzer with default settings
        analyzer = ChatGPTAnalyzer()
        
        # Run analysis
        results = analyzer.analyze('conversations_example.json')
        
        # Print results
        print(f"Total conversations analyzed: {results['total_conversations']}")
        print("\nCategory breakdown:")
        for category, count in results['counts'].items():
            if count > 0:
                print(f"  {category}: {count}")
        
        print(f"\nChart saved to: {results['chart_path']}")
        print(f"Results saved to: {results['results_path']}")
        
    except ChatGPTAnalyzerError as e:
        print(f"Analysis error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def custom_categories_example():
    """Example with custom categories."""
    print("\n=== Custom Categories Example ===")
    
    custom_categories = [
        "Work Projects",
        "Personal Learning",
        "Creative Writing",
        "Technical Support",
        "General Questions",
        "Other"
    ]
    
    try:
        analyzer = ChatGPTAnalyzer(categories=custom_categories)
        
        results = analyzer.analyze(
            'conversations_example.json',
            output_chart='custom_categories_chart.png',
            output_results='custom_results.json',
            show_plot=False  # Don't show plot in example
        )
        
        print(f"Analysis completed with {len(custom_categories)} custom categories")
        print("Custom categories used:")
        for category in custom_categories:
            count = results['counts'].get(category, 0)
            print(f"  {category}: {count}")
            
    except ChatGPTAnalyzerError as e:
        print(f"Analysis error: {e}")


def rate_limiting_example():
    """Example with custom rate limiting settings."""
    print("\n=== Rate Limiting Example ===")
    
    try:
        # Configure for slower, more conservative API usage
        analyzer = ChatGPTAnalyzer(
            batch_size=5,  # Smaller batches
            delay_between_requests=2.0,  # Longer delays
            max_tokens_per_request=2000  # Fewer tokens per request
        )
        
        print("Analyzer configured with conservative rate limiting:")
        print(f"  Batch size: {analyzer.batch_size}")
        print(f"  Delay between requests: {analyzer.delay_between_requests}s")
        print(f"  Max tokens per request: {analyzer.max_tokens_per_request}")
        
        # Note: This would make actual API calls, so we'll skip the analysis
        print("\n(Skipping actual analysis in this example)")
        
    except ChatGPTAnalyzerError as e:
        print(f"Configuration error: {e}")


def step_by_step_example():
    """Example showing step-by-step analysis."""
    print("\n=== Step-by-Step Example ===")
    
    try:
        analyzer = ChatGPTAnalyzer()
        
        # Step 1: Load conversations
        print("Step 1: Loading conversations...")
        conversations = analyzer.load_conversations('conversations_example.json')
        print(f"Loaded {len(conversations)} conversations")
        
        # Step 2: Extract titles
        print("\nStep 2: Extracting unique titles...")
        titles = analyzer.extract_unique_titles(conversations)
        print(f"Found {len(titles)} unique titles")
        print("Sample titles:")
        for title in titles[:3]:  # Show first 3 titles
            print(f"  - {title}")
        
        # Step 3: Show what the categorization prompt looks like
        print("\nStep 3: Sample categorization prompt:")
        sample_titles = titles[:2]  # Use first 2 titles for demo
        prompt = analyzer.create_categorization_prompt(sample_titles)
        print("Prompt preview (first 200 chars):")
        print(prompt[:200] + "...")
        
        print("\n(Skipping API calls in this example)")
        
    except ChatGPTAnalyzerError as e:
        print(f"Analysis error: {e}")


def main():
    """Run all examples."""
    print("ChatGPT Analyzer - Usage Examples")
    print("=" * 40)
    
    # Check if example file exists
    if not os.path.exists('conversations_example.json'):
        print("Warning: conversations_example.json not found.")
        print("Some examples may not work without this file.")
        print()
    
    # Check if API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("Warning: OPENAI_API_KEY not set.")
        print("API-dependent examples will fail without this.")
        print()
    
    # Run examples
    basic_example()
    custom_categories_example()
    rate_limiting_example()
    step_by_step_example()
    
    print("\n=== Examples Complete ===")
    print("For more information, see the README.md file.")


if __name__ == "__main__":
    main()