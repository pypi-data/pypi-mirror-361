"""Command-line interface for ChatGPT Analyzer."""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from .analyzer import ChatGPTAnalyzer
from .exceptions import ChatGPTAnalyzerError


def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Analyze and categorize ChatGPT conversation exports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s conversations.json
  %(prog)s -i conversations.json -o results.png --no-show
  %(prog)s --api-key sk-... --batch-size 10 conversations.json

For more information, visit: https://github.com/22wojciech/chatscope
"""
    )
    
    # Input/Output arguments
    parser.add_argument(
        "input_file",
        help="Path to the conversations JSON file"
    )
    parser.add_argument(
        "-o", "--output-chart",
        default="conversation_categories.png",
        help="Output path for the chart (default: conversation_categories.png)"
    )
    parser.add_argument(
        "-r", "--output-results",
        default="categorization_results.json",
        help="Output path for detailed results (default: categorization_results.json)"
    )
    
    # API configuration
    parser.add_argument(
        "--api-key",
        help="OpenAI API key (can also be set via OPENAI_API_KEY environment variable)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=20,
        help="Number of titles to process in each API request (default: 20)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay in seconds between API requests (default: 1.0)"
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=4000,
        help="Maximum tokens per API request (default: 4000)"
    )
    
    # Categories
    parser.add_argument(
        "--categories",
        nargs="+",
        help="Custom categories to use (space-separated)"
    )
    
    # Display options
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Don't display the chart after creation"
    )
    parser.add_argument(
        "--figsize",
        nargs=2,
        type=float,
        default=[12, 8],
        metavar=("WIDTH", "HEIGHT"),
        help="Figure size for the chart (default: 12 8)"
    )
    
    # Logging
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress all output except errors"
    )
    
    return parser


def validate_args(args: argparse.Namespace) -> None:
    """Validate command-line arguments."""
    # Check if input file exists
    input_path = Path(args.input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {args.input_file}")
    
    if not input_path.is_file():
        raise ValueError(f"Input path is not a file: {args.input_file}")
    
    # Validate batch size
    if args.batch_size <= 0:
        raise ValueError("Batch size must be positive")
    
    # Validate delay
    if args.delay < 0:
        raise ValueError("Delay must be non-negative")
    
    # Validate max tokens
    if args.max_tokens <= 0:
        raise ValueError("Max tokens must be positive")
    
    # Validate figure size
    if any(size <= 0 for size in args.figsize):
        raise ValueError("Figure size dimensions must be positive")
    
    # Check for conflicting quiet/verbose flags
    if args.quiet and args.verbose:
        raise ValueError("Cannot use both --quiet and --verbose flags")


def main(argv: Optional[list] = None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)
    
    try:
        # Validate arguments
        validate_args(args)
        
        # Set up logging
        if not args.quiet:
            setup_logging(args.verbose)
        else:
            logging.disable(logging.CRITICAL)
        
        # Create analyzer
        analyzer = ChatGPTAnalyzer(
            api_key=args.api_key,
            categories=args.categories,
            batch_size=args.batch_size,
            delay_between_requests=args.delay,
            max_tokens_per_request=args.max_tokens
        )
        
        # Run analysis
        results = analyzer.analyze(
            input_file=args.input_file,
            output_chart=args.output_chart,
            output_results=args.output_results,
            show_plot=not args.no_show
        )
        
        # Print summary if not quiet
        if not args.quiet:
            print("\n" + "="*50)
            print("ANALYSIS COMPLETE")
            print("="*50)
            print(f"Total conversations analyzed: {results['total_conversations']}")
            print(f"Chart saved to: {results['chart_path']}")
            print(f"Detailed results saved to: {results['results_path']}")
            print("\nCategory breakdown:")
            for category, count in results['counts'].items():
                if count > 0:
                    print(f"  {category}: {count}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        return 130
    except ChatGPTAnalyzerError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())