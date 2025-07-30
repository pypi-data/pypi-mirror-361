"""Main analyzer module for ChatGPT conversation analysis."""

import json
import os
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Any, Optional
import time
import logging

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

try:
    import openai
except ImportError:
    openai = None

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

from .exceptions import APIError, DataError, ConfigurationError

# Configure logging
logger = logging.getLogger(__name__)


class ChatGPTAnalyzer:
    """Analyze and categorize ChatGPT conversation exports."""
    
    DEFAULT_CATEGORIES = [
        "Programming",
        "Artificial Intelligence",
        "Psychology / Personal Development",
        "Philosophy",
        "Astrology / Esoteric",
        "Work / Career",
        "Health",
        "Education",
        "Other"
    ]
    
    def __init__(self, api_key: Optional[str] = None, categories: Optional[List[str]] = None,
                 batch_size: int = 20, delay_between_requests: float = 1.0,
                 max_tokens_per_request: int = 4000):
        """Initialize the ChatGPT conversation analyzer.
        
        Args:
            api_key: OpenAI API key. If None, will try to load from environment.
            categories: List of categories to use. If None, uses default categories.
            batch_size: Number of titles to process in each API request.
            delay_between_requests: Delay in seconds between API requests.
            max_tokens_per_request: Maximum tokens per API request.
            
        Raises:
            ConfigurationError: If OpenAI API key is not provided or found.
            ImportError: If required dependencies are not installed.
        """
        # Check dependencies
        if openai is None:
            raise ImportError("openai package is required. Install with: pip install openai")
        
        # Load environment variables if dotenv is available
        if load_dotenv is not None:
            load_dotenv()
        
        # Set up API key
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ConfigurationError(
                "OpenAI API key not found. Please provide it as a parameter or set OPENAI_API_KEY environment variable."
            )
        
        openai.api_key = self.api_key
        
        # Set up categories
        self.categories = categories or self.DEFAULT_CATEGORIES.copy()
        
        # Rate limiting parameters
        self.batch_size = batch_size
        self.delay_between_requests = delay_between_requests
        self.max_tokens_per_request = max_tokens_per_request
    
    def load_conversations(self, file_path: str) -> List[Dict[str, Any]]:
        """Load conversations from JSON file.
        
        Args:
            file_path: Path to the conversations JSON file.
            
        Returns:
            List of conversation dictionaries.
            
        Raises:
            DataError: If file cannot be loaded or parsed.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            if not isinstance(data, list):
                raise DataError("Conversations file must contain a JSON array")
            
            logger.info(f"Loaded {len(data)} conversations from {file_path}")
            return data
            
        except FileNotFoundError:
            raise DataError(f"File {file_path} not found")
        except json.JSONDecodeError as e:
            raise DataError(f"Invalid JSON format in {file_path}: {e}")
        except Exception as e:
            raise DataError(f"Error loading conversations: {e}")
    
    def extract_unique_titles(self, conversations: List[Dict[str, Any]]) -> List[str]:
        """Extract unique conversation titles.
        
        Args:
            conversations: List of conversation dictionaries.
            
        Returns:
            List of unique conversation titles.
        """
        titles = set()
        for conv in conversations:
            if isinstance(conv, dict) and 'title' in conv and conv['title']:
                title = conv['title'].strip()
                if title:  # Only add non-empty titles
                    titles.add(title)
        
        unique_titles = list(titles)
        logger.info(f"Found {len(unique_titles)} unique conversation titles")
        return unique_titles
    
    def create_categorization_prompt(self, titles: List[str]) -> str:
        """Create a prompt for GPT to categorize conversation titles.
        
        Args:
            titles: List of conversation titles to categorize.
            
        Returns:
            Formatted prompt string.
        """
        categories_str = "\n".join([f"- {cat}" for cat in self.categories])
        titles_str = "\n".join([f"{i+1}. {title}" for i, title in enumerate(titles)])
        
        prompt = f"""Please categorize the following ChatGPT conversation titles into one of these categories:

{categories_str}

Conversation titles to categorize:
{titles_str}

Please respond with a JSON object where each key is a title and each value is the assigned category. Use the exact category names provided above. Example format:
{{
    "Title 1": "Programming",
    "Title 2": "Health",
    "Title 3": "Other"
}}

Response:"""
        
        return prompt
    
    def categorize_titles_batch(self, titles: List[str]) -> Dict[str, str]:
        """Categorize a batch of titles using OpenAI API.
        
        Args:
            titles: List of titles to categorize.
            
        Returns:
            Dictionary mapping titles to categories.
            
        Raises:
            APIError: If API request fails.
        """
        if not titles:
            return {}
        
        prompt = self.create_categorization_prompt(titles)
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that categorizes conversation topics accurately. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens_per_request,
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to extract JSON from the response
            if content.startswith('```json'):
                content = content[7:-3].strip()
            elif content.startswith('```'):
                content = content[3:-3].strip()
            
            categorization = json.loads(content)
            
            # Validate that all titles are categorized
            missing_titles = set(titles) - set(categorization.keys())
            if missing_titles:
                logger.warning(f"Some titles were not categorized: {missing_titles}")
                for title in missing_titles:
                    categorization[title] = "Other"
            
            logger.info(f"Successfully categorized {len(categorization)} titles")
            return categorization
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            # Fallback: assign all to "Other"
            return {title: "Other" for title in titles}
        except Exception as e:
            logger.error(f"API request failed: {e}")
            raise APIError(f"Failed to categorize titles: {e}")
    
    def categorize_all_titles(self, titles: List[str]) -> Dict[str, str]:
        """Categorize all titles with batching and rate limiting.
        
        Args:
            titles: List of all titles to categorize.
            
        Returns:
            Dictionary mapping all titles to categories.
        """
        if not titles:
            return {}
        
        all_categorizations = {}
        
        # Process titles in batches
        total_batches = (len(titles) - 1) // self.batch_size + 1
        
        for i in range(0, len(titles), self.batch_size):
            batch = titles[i:i + self.batch_size]
            batch_num = i // self.batch_size + 1
            
            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} titles)")
            
            try:
                batch_categorizations = self.categorize_titles_batch(batch)
                all_categorizations.update(batch_categorizations)
            except APIError as e:
                logger.error(f"Failed to process batch {batch_num}: {e}")
                # Fallback: assign batch to "Other"
                for title in batch:
                    all_categorizations[title] = "Other"
            
            # Rate limiting
            if i + self.batch_size < len(titles):
                time.sleep(self.delay_between_requests)
        
        return all_categorizations
    
    def create_category_dictionary(self, categorizations: Dict[str, str]) -> Dict[str, List[str]]:
        """Create a dictionary with categories as keys and lists of titles as values.
        
        Args:
            categorizations: Dictionary mapping titles to categories.
            
        Returns:
            Dictionary with categories as keys and title lists as values.
        """
        category_dict = defaultdict(list)
        
        for title, category in categorizations.items():
            # Ensure category is valid
            if category not in self.categories:
                logger.warning(f"Unknown category '{category}' for title '{title}', assigning to 'Other'")
                category = "Other"
            category_dict[category].append(title)
        
        # Convert to regular dict and ensure all categories are present
        result = {}
        for category in self.categories:
            result[category] = category_dict.get(category, [])
        
        return result
    
    def count_conversations_by_category(self, category_dict: Dict[str, List[str]]) -> Dict[str, int]:
        """Count conversations in each category.
        
        Args:
            category_dict: Dictionary with categories and title lists.
            
        Returns:
            Dictionary with categories and their counts.
        """
        counts = {category: len(titles) for category, titles in category_dict.items()}
        
        logger.info("Conversation counts by category:")
        for category, count in counts.items():
            if count > 0:
                logger.info(f"  {category}: {count}")
        
        return counts
    
    def create_bar_chart(self, counts: Dict[str, int], output_path: str = "conversation_categories.png",
                        figsize: tuple = (12, 8), show_plot: bool = True) -> Optional[str]:
        """Create and save a bar chart of conversation categories.
        
        Args:
            counts: Dictionary with category counts.
            output_path: Path to save the chart.
            figsize: Figure size as (width, height).
            show_plot: Whether to display the plot.
            
        Returns:
            Path to saved chart or None if matplotlib is not available.
            
        Raises:
            ImportError: If matplotlib is not installed.
        """
        if plt is None:
            raise ImportError("matplotlib is required for plotting. Install with: pip install matplotlib")
        
        # Filter out categories with 0 conversations for cleaner visualization
        filtered_counts = {k: v for k, v in counts.items() if v > 0}
        
        if not filtered_counts:
            logger.warning("No conversations to plot")
            return None
        
        # Sort by count (descending)
        sorted_items = sorted(filtered_counts.items(), key=lambda x: x[1], reverse=True)
        categories, values = zip(*sorted_items)
        
        # Create the plot
        plt.figure(figsize=figsize)
        bars = plt.bar(categories, values, color='skyblue', edgecolor='navy', alpha=0.7)
        
        # Customize the plot
        plt.title('ChatGPT Conversations by Category', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Categories', fontsize=12, fontweight='bold')
        plt.ylabel('Number of Conversations', fontsize=12, fontweight='bold')
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45, ha='right')
        
        # Add value labels on top of bars
        for bar, value in zip(bars, values):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    str(value), ha='center', va='bottom', fontweight='bold')
        
        # Add grid for better readability
        plt.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Adjust layout to prevent label cutoff
        plt.tight_layout()
        
        # Save the plot
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"Chart saved as {output_path}")
        
        # Show the plot
        if show_plot:
            plt.show()
        
        return output_path
    
    def save_results(self, category_dict: Dict[str, List[str]], counts: Dict[str, int], 
                    output_file: str = "categorization_results.json") -> str:
        """Save categorization results to a JSON file.
        
        Args:
            category_dict: Dictionary with categories and title lists.
            counts: Dictionary with category counts.
            output_file: Path to save results.
            
        Returns:
            Path to saved results file.
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_conversations": sum(counts.values()),
            "categories": category_dict,
            "counts": counts,
            "analyzer_version": "1.0.0"
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to {output_file}")
        return output_file
    
    def analyze(self, input_file: str = "conversations.json", 
               output_chart: str = "conversation_categories.png",
               output_results: str = "categorization_results.json",
               show_plot: bool = True) -> Dict[str, Any]:
        """Main analysis pipeline.
        
        Args:
            input_file: Path to conversations JSON file.
            output_chart: Path to save the chart.
            output_results: Path to save detailed results.
            show_plot: Whether to display the plot.
            
        Returns:
            Dictionary with analysis results.
            
        Raises:
            DataError: If input data is invalid.
            APIError: If API requests fail.
        """
        logger.info("Starting ChatGPT conversation analysis...")
        
        try:
            # Step 1: Load conversations
            conversations = self.load_conversations(input_file)
            
            # Step 2: Extract unique titles
            unique_titles = self.extract_unique_titles(conversations)
            
            if not unique_titles:
                raise DataError("No conversation titles found in the input file")
            
            # Step 3: Categorize titles using OpenAI API
            logger.info("Categorizing conversations using OpenAI API...")
            categorizations = self.categorize_all_titles(unique_titles)
            
            # Step 4: Create category dictionary
            category_dict = self.create_category_dictionary(categorizations)
            
            # Step 5: Count conversations by category
            counts = self.count_conversations_by_category(category_dict)
            
            # Step 6: Create and save bar chart
            chart_path = None
            if plt is not None:
                chart_path = self.create_bar_chart(counts, output_chart, show_plot=show_plot)
            else:
                logger.warning("matplotlib not available, skipping chart creation")
            
            # Step 7: Save results
            results_path = self.save_results(category_dict, counts, output_results)
            
            logger.info("Analysis completed successfully!")
            
            return {
                "total_conversations": len(unique_titles),
                "categories": category_dict,
                "counts": counts,
                "chart_path": chart_path,
                "results_path": results_path
            }
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise