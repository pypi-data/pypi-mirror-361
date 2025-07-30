#!/usr/bin/env python3
"""
Test script to verify the chatscope library functionality.
"""

import os
from chatscope import ChatGPTAnalyzer
from chatscope.exceptions import ChatGPTAnalyzerError

def test_basic_functionality():
    """Test basic library functionality without API calls."""
    print("=== Testing ChatGPT Analyzer Library ===")
    
    try:
        # Initialize analyzer
        analyzer = ChatGPTAnalyzer()
        print("✓ Library initialized successfully")
        
        # Test loading conversations
        conversations = analyzer.load_conversations('conversations_example.json')
        print(f"✓ Loaded {len(conversations)} conversations")
        
        # Test extracting titles
        titles = analyzer.extract_unique_titles(conversations)
        print(f"✓ Extracted {len(titles)} unique titles:")
        for i, title in enumerate(titles, 1):
            print(f"  {i}. {title}")
        
        # Test chart creation (without API)
        print("\n✓ Testing chart creation with mock data...")
        mock_counts = {
            'Programming': 1,
            'Artificial Intelligence': 1,
            'Psychology / Personal Development': 1,
            'Other': 0
        }
        
        chart_path = analyzer.create_bar_chart(
            mock_counts,
            output_path='test_chart.png',
            show_plot=False
        )
        print(f"✓ Chart created successfully: {chart_path}")
        
        print("\n=== All tests passed! ===")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def test_with_api():
    """Test with actual API if key is available."""
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key or api_key == 'your_openai_api_key_here':
        print("\n=== API Test Skipped ===")
        print("To test with OpenAI API, set a valid OPENAI_API_KEY in .env file")
        return
    
    print("\n=== Testing with OpenAI API ===")
    try:
        analyzer = ChatGPTAnalyzer()
        results = analyzer.analyze(
            'conversations_example.json',
            output_chart='api_test_chart.png',
            output_results='api_test_results.json'
        )
        
        print("✓ API analysis completed successfully")
        print(f"✓ Total conversations: {results['total_conversations']}")
        print("✓ Category breakdown:")
        for category, count in results['counts'].items():
            if count > 0:
                print(f"  {category}: {count}")
                
    except ChatGPTAnalyzerError as e:
        print(f"✗ API test failed: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

if __name__ == '__main__':
    # Test basic functionality
    success = test_basic_functionality()
    
    # Test with API if available
    test_with_api()
    
    print("\n=== Test Summary ===")
    if success:
        print("✓ Library is working correctly!")
        print("\nNext steps:")
        print("1. Add your OpenAI API key to .env file for full functionality")
        print("2. Try: chatscope --help")
        print("3. Run: chatscope conversations_example.json")
    else:
        print("✗ Some tests failed. Please check the error messages above.")