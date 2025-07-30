"""Legacy script for backward compatibility.

This script provides the same functionality as before but now uses
the chatscope library internally.
"""

import logging
from chatscope import ChatGPTAnalyzer
from chatscope.exceptions import ChatGPTAnalyzerError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# For backward compatibility, we'll create a wrapper that maintains the old interface
class LegacyChatGPTAnalyzer:
    def __init__(self):
        """Initialize the ChatGPT conversation analyzer."""
        try:
            self.analyzer = ChatGPTAnalyzer()
            logger.info("ChatGPT Analyzer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize analyzer: {e}")
            raise
    
    def analyze(self, input_file: str = "conversations.json"):
        """Main analysis pipeline - delegates to the new library."""
        try:
            results = self.analyzer.analyze(input_file)
            logger.info("Analysis completed successfully using chatscope library!")
            return results
        except ChatGPTAnalyzerError as e:
            logger.error(f"Analysis failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

def main():
    """Main function to run the analysis."""
    import sys
    
    print("Note: This script now uses the chatscope library internally.")
    print("For more features, consider using the library directly or the CLI tool.")
    print("Run 'pip install -e .' to install the library, then use 'chatscope --help'\n")
    
    # Get input file from command line arguments or use default
    input_file = sys.argv[1] if len(sys.argv) > 1 else "conversations.json"
    
    analyzer = LegacyChatGPTAnalyzer()
    analyzer.analyze(input_file)

if __name__ == "__main__":
    main()